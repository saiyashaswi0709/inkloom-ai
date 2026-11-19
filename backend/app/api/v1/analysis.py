import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_org
from app.models import (
    User, Organisation, Submission, SubmissionStatus, BrandRule,
    BrandGuideline, GuidelineChunk, ApprovedFact, AnalysisReport,
    Finding, FindingSeverity, FindingType, CorrectionSuggestion,
    CorrectionStatus, RuleType
)
from app.schemas import AnalysisReportRead
from app.services.brand_checker import BrandChecker
from app.services.guideline_retriever import GuidelineRetriever
from app.services.evidence_validator import EvidenceValidator
from app.services.correction_engine import CorrectionEngine
from app.services.nemotron_service import nemotron_service

logger = logging.getLogger("inkloom.analysis")
router = APIRouter(prefix="/analysis", tags=["Content Analysis"])

class RunAnalysisRequest(BaseModel):
    submission_id: str

@router.post("/run", response_model=AnalysisReportRead)
async def run_analysis(
    payload: RunAnalysisRequest,
    org: Organisation = Depends(get_current_org),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    submission = db.query(Submission).filter(
        Submission.id == payload.submission_id,
        Submission.organisation_id == org.id
    ).first()

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    content_text = submission.current_text or submission.original_text
    if not content_text.strip():
        raise HTTPException(status_code=400, detail="Content text cannot be empty for analysis")

    # 1. Fetch organisation rules, guideline chunks, and approved facts
    rules = db.query(BrandRule).filter(
        BrandRule.organisation_id == org.id,
        BrandRule.is_active == True
    ).all()

    all_chunks = db.query(GuidelineChunk).join(BrandGuideline).filter(
        BrandGuideline.organisation_id == org.id,
        BrandGuideline.status == "active"
    ).all()

    all_facts = db.query(ApprovedFact).filter(
        ApprovedFact.organisation_id == org.id,
        ApprovedFact.is_active == True
    ).all()

    # 2. Deterministic Rule Matching
    deterministic_matches = BrandChecker.check_content(content_text, rules)

    # 3. Context Retrieval
    relevant_chunks = GuidelineRetriever.retrieve_relevant_chunks(content_text, all_chunks, top_k=6)
    relevant_facts = GuidelineRetriever.retrieve_relevant_facts(content_text, all_facts, top_k=8)

    # 4. Nemotron AI Analysis
    nemotron_result = await nemotron_service.analyze_content(
        content=content_text,
        content_type=submission.content_type,
        guideline_chunks=relevant_chunks,
        approved_facts=relevant_facts
    )

    # 5. Assemble Findings & Deduplicate
    created_findings: List[Finding] = []
    seen_snippets = set()

    # Create AnalysisReport container
    report = AnalysisReport(
        submission_id=submission.id,
        organisation_id=org.id,
        overall_score=100.0,
        rules_checked_count=len(rules),
        model_used=nemotron_service.model if nemotron_result else "Deterministic-RuleEngine"
    )
    db.add(report)
    db.flush()

    # Process Deterministic matches first (ground truth guarantees)
    for dm in deterministic_matches:
        snippet_key = dm.problematic_text.lower().strip()
        seen_snippets.add(snippet_key)

        finding_type = FindingType.RESTRICTED_PHRASE if dm.rule_type == RuleType.RESTRICTED_PHRASE else FindingType.TERMINOLOGY
        
        # Determine surrounding sentence for focused correction
        surrounding_sentence = CorrectionEngine.extract_surrounding_sentence(content_text, dm.start_pos, dm.end_pos)
        suggested_sentence = CorrectionEngine.build_deterministic_correction(
            sentence=surrounding_sentence,
            problematic_text=dm.problematic_text,
            preferred_term=dm.preferred_term,
            rule_explanation=dm.explanation
        )

        f = Finding(
            report_id=report.id,
            rule_id=dm.rule_id,
            finding_type=finding_type,
            severity=dm.severity,
            problematic_text=dm.problematic_text,
            start_pos=dm.start_pos,
            end_pos=dm.end_pos,
            explanation=dm.explanation,
            citation_source="Organisation Brand Rules",
            citation_section=f"Rule: {dm.preferred_term or dm.problematic_text}"
        )
        db.add(f)
        db.flush()

        # Add correction suggestion
        cs = CorrectionSuggestion(
            finding_id=f.id,
            original_sentence=surrounding_sentence,
            suggested_replacement=suggested_sentence,
            intent_explanation=f"Replaces '{dm.problematic_text}' with approved brand term '{dm.preferred_term}'.",
            status=CorrectionStatus.PENDING
        )
        db.add(cs)
        created_findings.append(f)

    # Process Nemotron AI findings if available
    unverified_count = 0
    if nemotron_result and "findings" in nemotron_result:
        for ai_item in nemotron_result.get("findings", []):
            raw_snippet = ai_item.get("problematic_text", "").strip()
            if not raw_snippet or raw_snippet.lower() in seen_snippets:
                continue

            seen_snippets.add(raw_snippet.lower())

            # Find snippet positions in content_text
            pos = content_text.lower().find(raw_snippet.lower())
            start_pos = pos if pos != -1 else None
            end_pos = (pos + len(raw_snippet)) if pos != -1 else None

            # Validate evidence against actual database records
            is_valid, val_source, val_section, chunk_id = EvidenceValidator.validate_citation(
                citation_source=ai_item.get("citation_source"),
                citation_section=ai_item.get("citation_section"),
                claimed_evidence_text=ai_item.get("explanation"),
                available_chunks=relevant_chunks,
                available_facts=relevant_facts
            )

            # Map finding type & severity
            raw_type = ai_item.get("finding_type", "guideline_violation").lower()
            if not is_valid and "claim" in raw_type:
                ft = FindingType.UNSUPPORTED_CLAIM
                unverified_count += 1
            elif "unsupported" in raw_type or "claim" in raw_type:
                ft = FindingType.UNSUPPORTED_CLAIM
                unverified_count += 1
            elif "tone" in raw_type:
                ft = FindingType.TONE_INCONSISTENCY
            elif "restricted" in raw_type:
                ft = FindingType.RESTRICTED_PHRASE
            elif "terminology" in raw_type:
                ft = FindingType.TERMINOLOGY
            else:
                ft = FindingType.GUIDELINE_VIOLATION

            raw_sev = ai_item.get("severity", "medium").lower()
            severity_map = {
                "critical": FindingSeverity.CRITICAL,
                "high": FindingSeverity.HIGH,
                "medium": FindingSeverity.MEDIUM,
                "low": FindingSeverity.LOW,
                "info": FindingSeverity.INFO
            }
            sev = severity_map.get(raw_sev, FindingSeverity.MEDIUM)

            f = Finding(
                report_id=report.id,
                guideline_chunk_id=chunk_id,
                finding_type=ft,
                severity=sev,
                problematic_text=raw_snippet,
                start_pos=start_pos,
                end_pos=end_pos,
                explanation=ai_item.get("explanation", "Potential guideline deviation identified."),
                citation_source=val_source,
                citation_section=val_section,
                citation_chunk_id=chunk_id
            )
            db.add(f)
            db.flush()

            # Smart correction
            orig_sent = ai_item.get("suggested_sentence") or CorrectionEngine.extract_surrounding_sentence(content_text, start_pos or 0, end_pos or 0)
            cs = CorrectionSuggestion(
                finding_id=f.id,
                original_sentence=CorrectionEngine.extract_surrounding_sentence(content_text, start_pos or 0, end_pos or 0) or raw_snippet,
                suggested_replacement=ai_item.get("suggested_sentence", raw_snippet),
                intent_explanation=ai_item.get("intent_explanation", "Preserves author intent while aligning with verified brand guidelines."),
                status=CorrectionStatus.PENDING
            )
            db.add(cs)
            created_findings.append(f)

    # 6. Calculate Adherence Score
    score = 100.0
    for f in created_findings:
        if f.severity == FindingSeverity.CRITICAL:
            score -= 20.0
        elif f.severity == FindingSeverity.HIGH:
            score -= 12.0
        elif f.severity == FindingSeverity.MEDIUM:
            score -= 6.0
        elif f.severity == FindingSeverity.LOW:
            score -= 3.0
    
    score = max(0.0, min(100.0, score))
    report.overall_score = round(score, 1)
    report.violations_count = len(created_findings)
    report.unverified_claims_count = unverified_count
    
    if nemotron_result and nemotron_result.get("summary"):
        report.summary = nemotron_result.get("summary")
    else:
        report.summary = (
            f"Governance review completed. Found {len(created_findings)} brand violations across "
            f"{len(rules)} active rules and stored guidelines. Brand adherence index: {report.overall_score}%."
        )

    # 7. Update Submission Status
    if len(created_findings) > 0:
        submission.status = SubmissionStatus.NEEDS_CHANGES
    else:
        submission.status = SubmissionStatus.READY_FOR_REVIEW

    db.commit()
    db.refresh(report)
    return report
