from typing import Generator, Optional, List
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import oauth2_scheme, decode_access_token
from app.models import User, Organisation, OrganisationMembership, normalize_role

# Canonical role constants
ORGANISATION_ADMIN = "ORGANISATION_ADMIN"
BRAND_MANAGER = "BRAND_MANAGER"
CONTENT_CREATOR = "CONTENT_CREATOR"
REVIEWER = "REVIEWER"
ANALYST = "ANALYST"

ALL_ROLES = [ORGANISATION_ADMIN, BRAND_MANAGER, CONTENT_CREATOR, REVIEWER, ANALYST]
ADMIN_ROLES = [ORGANISATION_ADMIN]
BRAND_ROLES = [ORGANISATION_ADMIN, BRAND_MANAGER]
REVIEW_ROLES = [ORGANISATION_ADMIN, BRAND_MANAGER, REVIEWER]
READ_ALL_ROLES = [ORGANISATION_ADMIN, BRAND_MANAGER, REVIEWER, ANALYST]


def get_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)
) -> User:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or account deactivated",
        )
    return user


def get_current_org(
    x_org_id: Optional[str] = Header(None, alias="X-Organisation-Id"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Organisation:
    """Finds user's active organisation. Uses header if supplied, else user's primary membership."""
    if x_org_id:
        membership = db.query(OrganisationMembership).filter(
            OrganisationMembership.organisation_id == x_org_id,
            OrganisationMembership.user_id == current_user.id,
            OrganisationMembership.is_active == True
        ).first()
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to requested organisation"
            )
        return membership.organisation

    # Fallback to user's first active membership
    membership = db.query(OrganisationMembership).filter(
        OrganisationMembership.user_id == current_user.id,
        OrganisationMembership.is_active == True
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active organisation membership found for user"
        )
    return membership.organisation


def get_current_membership(
    org: Organisation = Depends(get_current_org),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> OrganisationMembership:
    """Returns the active membership for the current user in the resolved org."""
    membership = db.query(OrganisationMembership).filter(
        OrganisationMembership.organisation_id == org.id,
        OrganisationMembership.user_id == current_user.id,
        OrganisationMembership.is_active == True
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="No active membership in this organisation")
    return membership


def get_normalized_role(membership: OrganisationMembership = Depends(get_current_membership)) -> str:
    return normalize_role(membership.role)


def require_roles(*allowed_roles: str):
    """Factory: returns a dependency that checks membership role against allowed_roles."""
    def _check(
        membership: OrganisationMembership = Depends(get_current_membership)
    ) -> OrganisationMembership:
        normalized = normalize_role(membership.role)
        if normalized not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{normalized}' does not have permission for this action"
            )
        return membership
    return Depends(_check)


# Convenience pre-built guards
def require_admin(membership: OrganisationMembership = Depends(get_current_membership)) -> OrganisationMembership:
    if normalize_role(membership.role) != ORGANISATION_ADMIN:
        raise HTTPException(403, detail="Organisation Admin authority required")
    return membership


def require_brand_or_admin(membership: OrganisationMembership = Depends(get_current_membership)) -> OrganisationMembership:
    if normalize_role(membership.role) not in BRAND_ROLES:
        raise HTTPException(403, detail="Brand Manager or Admin authority required")
    return membership


def require_reviewer(membership: OrganisationMembership = Depends(get_current_membership)) -> OrganisationMembership:
    """Restricts action exclusively to Reviewers, Brand Managers, or Admins."""
    if normalize_role(membership.role) not in REVIEW_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Reviewer authority required to approve or request changes"
        )
    return membership
