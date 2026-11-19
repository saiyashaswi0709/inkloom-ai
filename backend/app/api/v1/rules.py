from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_org, require_brand_or_admin
from app.models import User, Organisation, BrandRule, RuleType
from app.schemas import BrandRuleCreate, BrandRuleUpdate, BrandRuleRead

router = APIRouter(prefix="/rules", tags=["Brand Rules & Terminology"])

@router.get("", response_model=List[BrandRuleRead])
def list_brand_rules(
    rule_type: Optional[RuleType] = None,
    org: Organisation = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    query = db.query(BrandRule).filter(
        BrandRule.organisation_id == org.id,
        BrandRule.is_active == True
    )
    if rule_type:
        query = query.filter(BrandRule.rule_type == rule_type)
    return query.order_by(BrandRule.created_at.desc()).all()

@router.post("", response_model=BrandRuleRead)
def create_brand_rule(
    payload: BrandRuleCreate,
    org: Organisation = Depends(get_current_org),
    _brand_guard = Depends(require_brand_or_admin),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rule = BrandRule(
        organisation_id=org.id,
        rule_type=payload.rule_type,
        prohibited_term=payload.prohibited_term,
        preferred_term=payload.preferred_term,
        pattern=payload.pattern,
        explanation=payload.explanation,
        severity=payload.severity,
        is_active=True
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule

@router.put("/{rule_id}", response_model=BrandRuleRead)
def update_brand_rule(
    rule_id: str,
    payload: BrandRuleUpdate,
    org: Organisation = Depends(get_current_org),
    _brand_guard = Depends(require_brand_or_admin),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rule = db.query(BrandRule).filter(
        BrandRule.id == rule_id,
        BrandRule.organisation_id == org.id
    ).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Brand rule not found")

    if payload.rule_type is not None:
        rule.rule_type = payload.rule_type
    if payload.prohibited_term is not None:
        rule.prohibited_term = payload.prohibited_term
    if payload.preferred_term is not None:
        rule.preferred_term = payload.preferred_term
    if payload.pattern is not None:
        rule.pattern = payload.pattern
    if payload.explanation is not None:
        rule.explanation = payload.explanation
    if payload.severity is not None:
        rule.severity = payload.severity
    if payload.is_active is not None:
        rule.is_active = payload.is_active

    db.commit()
    db.refresh(rule)
    return rule

@router.delete("/{rule_id}")
def delete_brand_rule(
    rule_id: str,
    org: Organisation = Depends(get_current_org),
    _brand_guard = Depends(require_brand_or_admin),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rule = db.query(BrandRule).filter(
        BrandRule.id == rule_id,
        BrandRule.organisation_id == org.id
    ).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Brand rule not found")
    db.delete(rule)
    db.commit()
    return {"message": "Brand rule removed"}
