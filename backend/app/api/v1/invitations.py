import secrets
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_password_hash, create_access_token
from app.api.deps import (
    get_current_user, get_current_org, require_admin,
    ORGANISATION_ADMIN, CONTENT_CREATOR
)
from app.models import (
    User, Organisation, OrganisationMembership, Invitation,
    normalize_role, utc_now
)
from app.schemas import (
    InvitationCreate, InvitationRead, InvitationAccept,
    InvitationValidateResponse, Token, UserRead, OrganisationRead
)

router = APIRouter(prefix="/invitations", tags=["Invitations"])

@router.post("", response_model=InvitationRead)
def create_invitation(
    request: InvitationCreate,
    org: Organisation = Depends(get_current_org),
    admin_membership: OrganisationMembership = Depends(require_admin),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin invites a team member to the organisation.
    Note: In development/demo mode, invitations return the token directly in the API response
    since no external email provider is configured.
    """
    canonical_role = normalize_role(request.role)
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    # Check if there is an existing unused invitation for this email in this org
    existing_invite = db.query(Invitation).filter(
        Invitation.organisation_id == org.id,
        Invitation.invited_email == request.invited_email.lower(),
        Invitation.is_used == False,
        Invitation.expires_at > datetime.now(timezone.utc)
    ).first()

    if existing_invite:
        # Update existing invitation
        existing_invite.token = token
        existing_invite.role = canonical_role
        existing_invite.expires_at = expires_at
        db.commit()
        db.refresh(existing_invite)
        return existing_invite

    invitation = Invitation(
        organisation_id=org.id,
        invited_email=request.invited_email.lower(),
        role=canonical_role,
        token=token,
        invited_by_user_id=current_user.id,
        is_used=False,
        expires_at=expires_at
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    return invitation

@router.get("", response_model=List[InvitationRead])
def list_invitations(
    org: Organisation = Depends(get_current_org),
    admin_membership: OrganisationMembership = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List pending/recent invitations for the current organization."""
    return db.query(Invitation).filter(
        Invitation.organisation_id == org.id
    ).order_by(Invitation.created_at.desc()).all()

@router.delete("/{invitation_id}")
def revoke_invitation(
    invitation_id: str,
    org: Organisation = Depends(get_current_org),
    admin_membership: OrganisationMembership = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Revoke a pending invitation."""
    invite = db.query(Invitation).filter(
        Invitation.id == invitation_id,
        Invitation.organisation_id == org.id
    ).first()
    if not invite:
        raise HTTPException(status_code=404, detail="Invitation not found")
    db.delete(invite)
    db.commit()
    return {"message": "Invitation revoked successfully"}

@router.get("/validate/{token}", response_model=InvitationValidateResponse)
def validate_invitation(token: str, db: Session = Depends(get_db)):
    """Validate an invitation token before accepting it."""
    invite = db.query(Invitation).filter(
        Invitation.token == token,
        Invitation.is_used == False
    ).first()

    if not invite:
        raise HTTPException(status_code=404, detail="Invalid or already used invitation token")

    now = datetime.now(timezone.utc)
    # Handle timezone comparison
    expires_at = invite.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < now:
        raise HTTPException(status_code=400, detail="This invitation has expired")

    org = db.query(Organisation).filter(Organisation.id == invite.organisation_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Associated organisation no longer exists")

    return InvitationValidateResponse(
        organisation_name=org.name,
        organisation_id=org.id,
        invited_email=invite.invited_email,
        role=invite.role,
        expires_at=expires_at
    )

@router.post("/accept/{token}", response_model=Token)
def accept_invitation(token: str, request: InvitationAccept, db: Session = Depends(get_db)):
    """Accept an invitation, creating or linking a user account and adding them to the organisation."""
    invite = db.query(Invitation).filter(
        Invitation.token == token,
        Invitation.is_used == False
    ).first()

    if not invite:
        raise HTTPException(status_code=404, detail="Invalid or already used invitation token")

    now = datetime.now(timezone.utc)
    expires_at = invite.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < now:
        raise HTTPException(status_code=400, detail="This invitation has expired")

    org = db.query(Organisation).filter(Organisation.id == invite.organisation_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Associated organisation no longer exists")

    # Find or create user
    user = db.query(User).filter(User.email == invite.invited_email).first()
    if not user:
        user = User(
            email=invite.invited_email,
            hashed_password=get_password_hash(request.password),
            full_name=request.full_name
        )
        db.add(user)
        db.flush()

    # Find or create membership
    membership = db.query(OrganisationMembership).filter(
        OrganisationMembership.organisation_id == org.id,
        OrganisationMembership.user_id == user.id
    ).first()

    if membership:
        membership.is_active = True
        membership.role = invite.role
    else:
        membership = OrganisationMembership(
            organisation_id=org.id,
            user_id=user.id,
            role=invite.role,
            is_active=True
        )
        db.add(membership)

    # Mark invitation as used
    invite.is_used = True
    db.commit()

    access_token = create_access_token(subject=user.id)
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserRead.model_validate(user),
        organisation=OrganisationRead.model_validate(org),
        role=normalize_role(membership.role)
    )
