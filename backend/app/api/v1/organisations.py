from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import (
    get_current_user, get_current_org, require_admin, get_current_membership
)
from app.models import User, Organisation, OrganisationMembership, normalize_role
from app.schemas import (
    OrganisationRead, OrganisationCreate, OrganisationMemberRead, AddMemberRequest, UserRead
)

router = APIRouter(prefix="/organisations", tags=["Organisations"])

@router.get("/current", response_model=OrganisationRead)
def get_current_organisation_details(org: Organisation = Depends(get_current_org)):
    return org

@router.put("/current", response_model=OrganisationRead)
def update_current_organisation(
    update_data: OrganisationCreate,
    org: Organisation = Depends(get_current_org),
    admin_membership: OrganisationMembership = Depends(require_admin),
    db: Session = Depends(get_db)
):
    org.name = update_data.name
    if update_data.description is not None:
        org.description = update_data.description
    db.commit()
    db.refresh(org)
    return org

@router.get("/members", response_model=List[OrganisationMemberRead])
def list_organisation_members(
    org: Organisation = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    memberships = db.query(OrganisationMembership).filter(
        OrganisationMembership.organisation_id == org.id,
        OrganisationMembership.is_active == True
    ).all()
    # Normalize roles for response
    for m in memberships:
        m.role = normalize_role(m.role)
    return memberships

@router.post("/members", response_model=OrganisationMemberRead)
def add_organisation_member(
    request: AddMemberRequest,
    org: Organisation = Depends(get_current_org),
    admin_membership: OrganisationMembership = Depends(require_admin),
    db: Session = Depends(get_db)
):
    target_user = db.query(User).filter(User.email == request.email).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User with this email not found")

    canonical_role = normalize_role(request.role)
    existing = db.query(OrganisationMembership).filter(
        OrganisationMembership.organisation_id == org.id,
        OrganisationMembership.user_id == target_user.id
    ).first()

    if existing:
        existing.is_active = True
        existing.role = canonical_role
        db.commit()
        db.refresh(existing)
        existing.role = normalize_role(existing.role)
        return existing

    new_membership = OrganisationMembership(
        organisation_id=org.id,
        user_id=target_user.id,
        role=canonical_role
    )
    db.add(new_membership)
    db.commit()
    db.refresh(new_membership)
    new_membership.role = normalize_role(new_membership.role)
    return new_membership

@router.delete("/members/{user_id}")
def remove_organisation_member(
    user_id: str,
    org: Organisation = Depends(get_current_org),
    admin_membership: OrganisationMembership = Depends(require_admin),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot remove yourself as organization administrator")

    membership = db.query(OrganisationMembership).filter(
        OrganisationMembership.organisation_id == org.id,
        OrganisationMembership.user_id == user_id
    ).first()

    if not membership:
        raise HTTPException(status_code=404, detail="Member not found in this organisation")

    membership.is_active = False
    db.commit()
    return {"message": "Member removed successfully"}
