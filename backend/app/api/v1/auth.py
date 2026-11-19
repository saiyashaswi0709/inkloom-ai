from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models import User, Organisation, OrganisationMembership, UserRole, normalize_role
from app.schemas import Token, LoginRequest, UserCreate, UserRead, OrganisationRead
from app.api.deps import get_current_user
from app.services.nemotron_service import nemotron_service
from app.services.demo_seed import seed_demo_data

router = APIRouter(prefix="/auth", tags=["Authentication"])

class DemoLoginRequest(BaseModel):
    role: str = "reviewer" # "reviewer" or "creator"

@router.post("/login", response_model=Token)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get primary organisation
    membership = db.query(OrganisationMembership).filter(
        OrganisationMembership.user_id == user.id,
        OrganisationMembership.is_active == True
    ).first()

    org = membership.organisation if membership else None
    role = normalize_role(membership.role) if membership else "CONTENT_CREATOR"

    access_token = create_access_token(subject=user.id)
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserRead.model_validate(user),
        organisation=OrganisationRead.model_validate(org) if org else None,
        role=role
    )

@router.post("/demo-login", response_model=Token)
def demo_login(request: DemoLoginRequest, db: Session = Depends(get_db)):
    """One-click instant login for judges and reviewers to test the platform without manual setup."""
    # Ensure demo organization and seed data are ready
    seed_demo_data(db)

    target_email = "reviewer@inkloom.ai" if request.role.lower() == "reviewer" else "creator@inkloom.ai"
    user = db.query(User).filter(User.email == target_email).first()

    if not user:
        raise HTTPException(status_code=500, detail="Demo account initialization error")

    membership = db.query(OrganisationMembership).filter(
        OrganisationMembership.user_id == user.id,
        OrganisationMembership.is_active == True
    ).first()

    org = membership.organisation if membership else None
    role = normalize_role(membership.role) if membership else request.role.upper()

    access_token = create_access_token(subject=user.id)
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserRead.model_validate(user),
        organisation=OrganisationRead.model_validate(org) if org else None,
        role=role
    )

@router.post("/register", response_model=Token)
def register(request: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already registered")

    user = User(
        email=request.email,
        hashed_password=get_password_hash(request.password),
        full_name=request.full_name
    )
    db.add(user)
    db.flush()

    # Create new organisation for the registered user
    org_name = request.organisation_name or f"{request.full_name}'s Organisation"
    slug = org_name.lower().replace(" ", "-")[:40] + "-" + user.id[:6]
    org = Organisation(name=org_name, slug=slug)
    db.add(org)
    db.flush()

    membership = OrganisationMembership(
        user_id=user.id,
        organisation_id=org.id,
        role="ORGANISATION_ADMIN"
    )
    db.add(membership)
    db.commit()

    access_token = create_access_token(subject=user.id)
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserRead.model_validate(user),
        organisation=OrganisationRead.model_validate(org),
        role="ORGANISATION_ADMIN"
    )

@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/validate-ai")
async def validate_ai():
    """Safely checks NVIDIA Nemotron / OpenRouter integration status without logging credentials."""
    status_info = await nemotron_service.validate_connection()
    return status_info
