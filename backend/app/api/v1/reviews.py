from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_org, require_reviewer
from app.models import (
    User, Organisation, Submission, SubmissionStatus, Review,
    ReviewDecision, OrganisationMembership, AuditLog
)
from app.schemas import ReviewCreate, ReviewRead, SubmissionRead

router = APIRouter(prefix="/reviews", tags=["Review Centre"])

@router.get("/queue", response_model=List[SubmissionRead])
def get_review_queue(
    org: Organisation = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    """Lists all submissions currently in review or ready for review."""
    return db.query(Submission).filter(
        Submission.organisation_id == org.id,
        Submission.status.in_([SubmissionStatus.IN_REVIEW, SubmissionStatus.READY_FOR_REVIEW, SubmissionStatus.NEEDS_CHANGES])
    ).order_by(Submission.updated_at.desc()).all()

@router.post("", response_model=ReviewRead)
def submit_review(
    payload: ReviewCreate,
    submission_id: str,
    reviewer_membership: OrganisationMembership = Depends(require_reviewer),
    org: Organisation = Depends(get_current_org),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sub = db.query(Submission).filter(
        Submission.id == submission_id,
        Submission.organisation_id == org.id
    ).first()

    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")

    review = Review(
        submission_id=sub.id,
        reviewer_id=current_user.id,
        decision=payload.decision,
        comments=payload.comments,
        feedback_tags=payload.feedback_tags or []
    )
    db.add(review)

    # Update submission status according to decision
    if payload.decision == ReviewDecision.APPROVED:
        sub.status = SubmissionStatus.APPROVED
    else:
        sub.status = SubmissionStatus.CHANGES_REQUESTED

    audit = AuditLog(
        organisation_id=org.id,
        user_id=current_user.id,
        action=f"REVIEW_{payload.decision.value.upper()}",
        resource_type="submission",
        resource_id=sub.id,
        details={"decision": payload.decision.value, "comments": payload.comments}
    )
    db.add(audit)

    db.commit()
    db.refresh(review)
    
    review_read = ReviewRead.model_validate(review)
    review_read.reviewer_name = current_user.full_name
    return review_read
