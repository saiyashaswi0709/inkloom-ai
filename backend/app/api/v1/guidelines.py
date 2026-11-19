from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_org, require_brand_or_admin
from app.models import User, Organisation, BrandGuideline, GuidelineChunk
from app.schemas import BrandGuidelineCreate, BrandGuidelineRead, BrandGuidelineUpdate
from app.services.document_processor import DocumentProcessor

router = APIRouter(prefix="/guidelines", tags=["Brand Guidelines"])

@router.get("", response_model=List[BrandGuidelineRead])
def list_brand_guidelines(
    category: Optional[str] = None,
    org: Organisation = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    query = db.query(BrandGuideline).filter(BrandGuideline.organisation_id == org.id)
    if category:
        query = query.filter(BrandGuideline.category == category)
    return query.order_by(BrandGuideline.created_at.desc()).all()

@router.post("", response_model=BrandGuidelineRead)
def create_brand_guideline(
    payload: BrandGuidelineCreate,
    org: Organisation = Depends(get_current_org),
    _brand_guard = Depends(require_brand_or_admin),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    guideline = BrandGuideline(
        organisation_id=org.id,
        title=payload.title,
        category=payload.category,
        description=payload.description,
        source_document_name=payload.source_document_name,
        status="active"
    )
    db.add(guideline)
    db.flush()

    if payload.chunks:
        for idx, c in enumerate(payload.chunks):
            chunk = GuidelineChunk(
                guideline_id=guideline.id,
                section_name=c.section_name,
                page_number=c.page_number,
                content=c.content,
                chunk_index=idx
            )
            db.add(chunk)

    db.commit()
    db.refresh(guideline)
    return guideline

@router.post("/upload", response_model=BrandGuidelineRead)
async def upload_guideline_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form("General"),
    org: Organisation = Depends(get_current_org),
    _brand_guard = Depends(require_brand_or_admin),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        extracted_chunks = DocumentProcessor.process_file(contents, file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    guideline = BrandGuideline(
        organisation_id=org.id,
        title=title,
        category=category,
        description=f"Uploaded from document '{file.filename}' with {len(extracted_chunks)} sections extracted.",
        source_document_name=file.filename,
        status="active"
    )
    db.add(guideline)
    db.flush()

    for item in extracted_chunks:
        chunk = GuidelineChunk(
            guideline_id=guideline.id,
            section_name=item.get("section_name", "Section"),
            page_number=item.get("page_number", 1),
            content=item.get("content", ""),
            chunk_index=item.get("chunk_index", 0)
        )
        db.add(chunk)

    db.commit()
    db.refresh(guideline)
    return guideline

@router.get("/{guideline_id}", response_model=BrandGuidelineRead)
def get_guideline(
    guideline_id: str,
    org: Organisation = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    guideline = db.query(BrandGuideline).filter(
        BrandGuideline.id == guideline_id,
        BrandGuideline.organisation_id == org.id
    ).first()
    if not guideline:
        raise HTTPException(status_code=404, detail="Guideline not found")
    return guideline

@router.delete("/{guideline_id}")
def delete_guideline(
    guideline_id: str,
    org: Organisation = Depends(get_current_org),
    _brand_guard = Depends(require_brand_or_admin),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    guideline = db.query(BrandGuideline).filter(
        BrandGuideline.id == guideline_id,
        BrandGuideline.organisation_id == org.id
    ).first()
    if not guideline:
        raise HTTPException(status_code=404, detail="Guideline not found")
    db.delete(guideline)
    db.commit()
    return {"message": "Guideline successfully deleted"}
