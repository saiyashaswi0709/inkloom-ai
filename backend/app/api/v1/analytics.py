from typing import Dict, List, Any
from datetime import timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.api.deps import get_current_org
from app.models import (
    Organisation, Submission, SubmissionStatus, AnalysisReport,
    Finding, FindingSeverity, FindingType, AuditLog
)
from app.schemas import AnalyticsSummary

router = APIRouter(prefix="/analytics", tags=["Governance Analytics"])

@router.get("/summary", response_model=AnalyticsSummary)
def get_governance_analytics(
    org: Organisation = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    # Total submissions
    total_submissions = db.query(Submission).filter(Submission.organisation_id == org.id).count()
    approved_submissions = db.query(Submission).filter(
        Submission.organisation_id == org.id,
        Submission.status == SubmissionStatus.APPROVED
    ).count()
    pending_submissions = db.query(Submission).filter(
        Submission.organisation_id == org.id,
        Submission.status.in_([SubmissionStatus.DRAFT, SubmissionStatus.ANALYSED, SubmissionStatus.NEEDS_CHANGES, SubmissionStatus.IN_REVIEW])
    ).count()

    # Average score
    avg_score_res = db.query(func.avg(AnalysisReport.overall_score)).filter(
        AnalysisReport.organisation_id == org.id
    ).scalar()
    avg_score = round(float(avg_score_res), 1) if avg_score_res is not None else 100.0

    # Violations by category / finding type
    findings_q = db.query(Finding.finding_type, func.count(Finding.id)).join(AnalysisReport).filter(
        AnalysisReport.organisation_id == org.id
    ).group_by(Finding.finding_type).all()

    violations_by_category = {str(ft.value): count for ft, count in findings_q}
    for cat in ["terminology", "restricted_phrase", "unsupported_claim", "tone_inconsistency", "guideline_violation"]:
        if cat not in violations_by_category:
            violations_by_category[cat] = 0

    # Violations by severity
    sev_q = db.query(Finding.severity, func.count(Finding.id)).join(AnalysisReport).filter(
        AnalysisReport.organisation_id == org.id
    ).group_by(Finding.severity).all()

    violations_by_severity = {str(sev.value): count for sev, count in sev_q}
    for s in ["critical", "high", "medium", "low", "info"]:
        if s not in violations_by_severity:
            violations_by_severity[s] = 0

    # Top recurring prohibited terms / snippets
    terms_q = db.query(Finding.problematic_text, func.count(Finding.id).label("count")).join(AnalysisReport).filter(
        AnalysisReport.organisation_id == org.id
    ).group_by(Finding.problematic_text).order_by(func.count(Finding.id).desc()).limit(5).all()

    top_recurring_prohibited_terms = [
        {"term": term, "occurrences": count} for term, count in terms_q
    ]

    # Recent Audit Activity
    recent_logs = db.query(AuditLog).filter(
        AuditLog.organisation_id == org.id
    ).order_by(AuditLog.created_at.desc()).limit(8).all()

    recent_activity = [
        {
            "id": log.id,
            "action": log.action,
            "resource_type": log.resource_type,
            "created_at": (log.created_at.replace(tzinfo=timezone.utc) if log.created_at.tzinfo is None else log.created_at).isoformat().replace("+00:00", "Z"),
            "details": log.details or {}
        }
        for log in recent_logs
    ]

    # Dynamic actionable recommendations based on actual data
    recommendations: List[str] = []
    if violations_by_category.get("restricted_phrase", 0) > 2:
        recommendations.append("High frequency of prohibited marketing phrases detected. Run an enablement session on approved terminology.")
    if violations_by_category.get("unsupported_claim", 0) > 0:
        recommendations.append(f"Identified {violations_by_category.get('unsupported_claim')} unverified factual statements. Update the Approved Corporate Facts knowledge base with recent audit sources.")
    if avg_score < 80.0:
        recommendations.append("Organisation brand adherence index is below target threshold (80%). Implement mandatory pre-review automated checks.")
    if not recommendations:
        recommendations.append("Brand alignment is strong across active channels. Continue tracking quarterly compliance.")

    return AnalyticsSummary(
        total_submissions=total_submissions,
        approved_submissions=approved_submissions,
        pending_submissions=pending_submissions,
        average_adherence_score=avg_score,
        violations_by_category=violations_by_category,
        violations_by_severity=violations_by_severity,
        top_recurring_prohibited_terms=top_recurring_prohibited_terms,
        recent_activity=recent_activity,
        actionable_recommendations=recommendations
    )
