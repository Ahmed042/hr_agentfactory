from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.document_template import DocumentTemplate
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class TemplateCreate(BaseModel):
    name: str
    template_type: str = "offer_letter"
    content: Optional[str] = ""
    description: Optional[str] = None
    is_active: bool = True


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    template_type: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


@router.post("/")
def create_template(data: TemplateCreate, db: Session = Depends(get_db)):
    template = DocumentTemplate(**data.model_dump())
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.get("/")
def get_templates(template_type: str = None, db: Session = Depends(get_db)):
    query = db.query(DocumentTemplate)
    if template_type:
        query = query.filter(DocumentTemplate.template_type == template_type)
    return query.order_by(DocumentTemplate.created_at.desc()).all()


@router.get("/{template_id}")
def get_template(template_id: int, db: Session = Depends(get_db)):
    template = db.query(DocumentTemplate).filter(DocumentTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.put("/{template_id}")
def update_template(template_id: int, data: TemplateUpdate, db: Session = Depends(get_db)):
    template = db.query(DocumentTemplate).filter(DocumentTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    for key, value in data.model_dump(exclude_none=True).items():
        setattr(template, key, value)

    db.commit()
    db.refresh(template)
    return template


@router.delete("/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    template = db.query(DocumentTemplate).filter(DocumentTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    db.delete(template)
    db.commit()
    return {"message": "Template deleted"}
