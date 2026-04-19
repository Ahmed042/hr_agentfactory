import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.document import Document
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".png", ".jpg", ".jpeg", ".txt"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    candidate_id: Optional[int] = Form(None),
    employee_id: Optional[int] = Form(None),
    doc_type: str = Form("cv"),
    db: Session = Depends(get_db),
):
    """Upload a document for a candidate or employee"""
    if not candidate_id and not employee_id:
        raise HTTPException(status_code=400, detail="Must provide candidate_id or employee_id")

    if doc_type not in ("cv", "cnic", "certificate", "contract", "offer_letter", "cover_letter", "reference", "other"):
        raise HTTPException(status_code=400, detail="Invalid document type")

    # Validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    # Read and validate file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max 10MB.")

    # Generate unique filename
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as f:
        f.write(content)

    doc = Document(
        candidate_id=candidate_id,
        employee_id=employee_id,
        type=doc_type,
        file_url=unique_name,
        file_name=file.filename,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    logger.info(f"Document uploaded: {file.filename} -> {unique_name}")
    return {
        "id": doc.id,
        "file_name": doc.file_name,
        "type": doc.type,
        "candidate_id": doc.candidate_id,
        "employee_id": doc.employee_id,
        "uploaded_at": str(doc.uploaded_at),
    }


@router.get("/")
def get_documents(
    candidate_id: Optional[int] = None,
    employee_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """List documents with optional filters"""
    query = db.query(Document)
    if candidate_id:
        query = query.filter(Document.candidate_id == candidate_id)
    if employee_id:
        query = query.filter(Document.employee_id == employee_id)
    docs = query.order_by(Document.uploaded_at.desc()).all()
    return [
        {
            "id": d.id,
            "file_name": d.file_name,
            "type": d.type,
            "candidate_id": d.candidate_id,
            "employee_id": d.employee_id,
            "uploaded_at": str(d.uploaded_at) if d.uploaded_at else None,
        }
        for d in docs
    ]


@router.get("/download/{doc_id}")
def download_document(doc_id: int, db: Session = Depends(get_db)):
    """Download a document by ID"""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    file_path = os.path.join(UPLOAD_DIR, doc.file_url)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(file_path, filename=doc.file_name)


@router.delete("/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    """Delete a document"""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Remove file from disk
    file_path = os.path.join(UPLOAD_DIR, doc.file_url)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.delete(doc)
    db.commit()
    return {"message": "Document deleted"}
