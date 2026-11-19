from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_org
from app.models import (
    User, Organisation, CorrectionSuggestion, CorrectionStatus,
    Finding, AnalysisReport, Submission, Revision, SubmissionStatus
)
from app.schemas import CorrectionSuggestionRead, CorrectionSuggestionUpdate

router = APIRouter(prefix="/corrections", tags=["Smart Corrections"])

@router.put("/{suggestion_id}", response_model=CorrectionSuggestionRead)
def update_correction_status(
    suggestion_id: str,
    payload: CorrectionSuggestionUpdate,
    org: Organisation = Depends(get_current_org),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cs = db.query(CorrectionSuggestion).join(Finding).join(AnalysisReport).filter(
        CorrectionSuggestion.id == suggestion_id,
        AnalysisReport.organisation_id == org.id
    ).first()

    if not cs:
        raise HTTPException(status_code=404, detail="Correction suggestion not found")

    finding = cs.finding
    report = finding.report
    submission = report.submission

    # Enforce decision idempotency: prevent duplicate decision records and duplicate revisions
    if cs.status == payload.status:
        return cs

    if cs.status in [CorrectionStatus.ACCEPTED, CorrectionStatus.EDITED, CorrectionStatus.REJECTED]:
        # Finding is already decided; prevent duplicate revisions or duplicate decisions
        return cs

    cs.status = payload.status
    if payload.user_edited_text is not None:
        cs.user_edited_text = payload.user_edited_text

    # If ACCEPTED or EDITED, apply change to submission.current_text and record Revision
    replacement_text = cs.user_edited_text if (payload.status == CorrectionStatus.EDITED and cs.user_edited_text) else cs.suggested_replacement

    if payload.status in [CorrectionStatus.ACCEPTED, CorrectionStatus.EDITED]:
        # Replace original sentence or problematic text in current text
        orig = cs.original_sentence or finding.problematic_text
        if orig in submission.current_text:
            submission.current_text = submission.current_text.replace(orig, replacement_text, 1)
        elif finding.problematic_text in submission.current_text:
            submission.current_text = submission.current_text.replace(finding.problematic_text, replacement_text, 1)

        finding.is_resolved = True

        # Create persistent revision
        next_rev = len(submission.revisions) + 1
        rev = Revision(
            submission_id=submission.id,
            user_id=current_user.id,
            revision_number=next_rev,
            text_content=submission.current_text,
            change_summary=f"Applied correction for finding: {finding.problematic_text[:30]}..."
        )
        db.add(rev)

    elif payload.status == CorrectionStatus.REJECTED:
        finding.is_resolved = False

    db.commit()
    db.refresh(cs)
    return cs
