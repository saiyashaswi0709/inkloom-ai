from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_org, require_brand_or_admin
from app.models import User, Organisation, ApprovedFact
from app.schemas import ApprovedFactCreate, ApprovedFactUpdate, ApprovedFactRead

router = APIRouter(prefix="/facts", tags=["Approved Facts"])

@router.get("", response_model=List[ApprovedFactRead])
def list_approved_facts(
    category: Optional[str] = None,
    org: Organisation = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    query = db.query(ApprovedFact).filter(
        ApprovedFact.organisation_id == org.id,
        ApprovedFact.is_active == True
    )
    if category:
        query = query.filter(ApprovedFact.category == category)
    return query.order_by(ApprovedFact.created_at.desc()).all()

@router.post("", response_model=ApprovedFactRead)
def create_approved_fact(
    payload: ApprovedFactCreate,
    org: Organisation = Depends(get_current_org),
    _brand_guard = Depends(require_brand_or_admin),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    fact = ApprovedFact(
        organisation_id=org.id,
        statement=payload.statement,
        category=payload.category,
        verification_source=payload.verification_source,
        valid_from=payload.valid_from,
        valid_until=payload.valid_until,
        is_active=True
    )
    db.add(fact)
    db.commit()
    db.refresh(fact)
    return fact

@router.put("/{fact_id}", response_model=ApprovedFactRead)
def update_approved_fact(
    fact_id: str,
    payload: ApprovedFactUpdate,
    org: Organisation = Depends(get_current_org),
    _brand_guard = Depends(require_brand_or_admin),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    fact = db.query(ApprovedFact).filter(
        ApprovedFact.id == fact_id,
        ApprovedFact.organisation_id == org.id
    ).first()
    if not fact:
        raise HTTPException(status_code=404, detail="Approved fact not found")

    if payload.statement is not None:
        fact.statement = payload.statement
    if payload.category is not None:
        fact.category = payload.category
    if payload.verification_source is not None:
        fact.verification_source = payload.verification_source
    if payload.is_active is not None:
        fact.is_active = payload.is_active

    db.commit()
    db.refresh(fact)
    return fact

@router.delete("/{fact_id}")
def delete_approved_fact(
    fact_id: str,
    org: Organisation = Depends(get_current_org),
    _brand_guard = Depends(require_brand_or_admin),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    fact = db.query(ApprovedFact).filter(
        ApprovedFact.id == fact_id,
        ApprovedFact.organisation_id == org.id
    ).first()
    if not fact:
        raise HTTPException(status_code=404, detail="Approved fact not found")
    db.delete(fact)
    db.commit()
    return {"message": "Approved fact removed"}
