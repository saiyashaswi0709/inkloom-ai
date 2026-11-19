from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import (
    get_current_user, get_current_org, get_current_membership,
    ORGANISATION_ADMIN, BRAND_MANAGER, CONTENT_CREATOR, REVIEWER, ANALYST
)
from app.models import (
    User, Organisation, OrganisationMembership, Submission, SubmissionStatus,
    Revision, AuditLog, normalize_role
)
from app.schemas import (
    SubmissionCreate, SubmissionUpdate, SubmissionRead, RevisionRead
)

router = APIRouter(prefix="/submissions", tags=["Submissions"])

@router.get("", response_model=List[SubmissionRead])
def list_submissions(
    status_filter: Optional[SubmissionStatus] = None,
    org: Organisation = Depends(get_current_org),
    membership: OrganisationMembership = Depends(get_current_membership),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_role = normalize_role(membership.role)
    query = db.query(Submission).filter(Submission.organisation_id == org.id)

    # Content creators only see their own submissions
    if user_role == CONTENT_CREATOR:
        query = query.filter(Submission.user_id == current_user.id)

    if status_filter:
        query = query.filter(Submission.status == status_filter)

    results = query.order_by(Submission.created_at.desc()).all()

    # Analyst cannot view raw confidential content
    if user_role == ANALYST:
        for sub in results:
            sub.original_text = "[Confidential - Analyst Access Redacted]"
            sub.current_text = "[Confidential - Analyst Access Redacted]"

    return results

@router.post("", response_model=SubmissionRead)
def create_submission(
    payload: SubmissionCreate,
    org: Organisation = Depends(get_current_org),
    membership: OrganisationMembership = Depends(get_current_membership),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_role = normalize_role(membership.role)
    if user_role == ANALYST:
        raise HTTPException(status_code=403, detail="Analysts have read-only aggregated access")

    sub = Submission(
        organisation_id=org.id,
        user_id=current_user.id,
        title=payload.title,
        content_type=payload.content_type,
        original_text=payload.content,
        current_text=payload.content,
        status=SubmissionStatus.DRAFT
    )
    db.add(sub)
    db.flush()

    rev = Revision(
        submission_id=sub.id,
        user_id=current_user.id,
        revision_number=1,
        text_content=payload.content,
        change_summary="Initial draft created"
    )
    db.add(rev)

    audit = AuditLog(
        organisation_id=org.id,
        user_id=current_user.id,
        action="SUBMISSION_CREATED",
        resource_type="submission",
        resource_id=sub.id,
        details={"title": sub.title}
    )
    db.add(audit)

    db.commit()
    db.refresh(sub)
    return sub

@router.get("/{submission_id}", response_model=SubmissionRead)
def get_submission(
    submission_id: str,
    org: Organisation = Depends(get_current_org),
    membership: OrganisationMembership = Depends(get_current_membership),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_role = normalize_role(membership.role)
    sub = db.query(Submission).filter(
        Submission.id == submission_id,
        Submission.organisation_id == org.id
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")

    # Content creator can only view their own
    if user_role == CONTENT_CREATOR and sub.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Content Creators can only view their own submissions")

    # Analyst raw text protection
    if user_role == ANALYST:
        sub.original_text = "[Confidential - Analyst Access Redacted]"
        sub.current_text = "[Confidential - Analyst Access Redacted]"

    return sub

@router.put("/{submission_id}", response_model=SubmissionRead)
def update_submission(
    submission_id: str,
    payload: SubmissionUpdate,
    org: Organisation = Depends(get_current_org),
    membership: OrganisationMembership = Depends(get_current_membership),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_role = normalize_role(membership.role)
    if user_role == ANALYST:
        raise HTTPException(status_code=403, detail="Analysts cannot modify submissions")

    sub = db.query(Submission).filter(
        Submission.id == submission_id,
        Submission.organisation_id == org.id
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")

    if user_role == CONTENT_CREATOR and sub.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own submissions")

    text_changed = False
    if payload.title is not None:
        sub.title = payload.title
    if payload.current_text is not None and payload.current_text != sub.current_text:
        sub.current_text = payload.current_text
        text_changed = True
    if payload.status is not None:
        sub.status = payload.status

    if text_changed:
        next_rev = len(sub.revisions) + 1
        rev = Revision(
            submission_id=sub.id,
            user_id=current_user.id,
            revision_number=next_rev,
            text_content=sub.current_text,
            change_summary="Manual content update"
        )
        db.add(rev)

    db.commit()
    db.refresh(sub)
    return sub

@router.post("/{submission_id}/submit-for-review", response_model=SubmissionRead)
def submit_for_review(
    submission_id: str,
    org: Organisation = Depends(get_current_org),
    membership: OrganisationMembership = Depends(get_current_membership),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_role = normalize_role(membership.role)
    sub = db.query(Submission).filter(
        Submission.id == submission_id,
        Submission.organisation_id == org.id
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")

    if user_role == CONTENT_CREATOR and sub.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only submit your own content for review")

    sub.status = SubmissionStatus.IN_REVIEW
    db.commit()
    db.refresh(sub)
    return sub
