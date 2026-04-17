from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.candidate_note import CandidateNote
from app.models.activity_log import ActivityLog
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class NoteCreate(BaseModel):
    candidate_id: int
    author: str = "HR Admin"
    content: str
    note_type: str = "general"


@router.post("/")
def create_note(data: NoteCreate, db: Session = Depends(get_db)):
    note = CandidateNote(**data.model_dump())
    db.add(note)

    log = ActivityLog(
        entity_type="candidate",
        entity_id=data.candidate_id,
        action="note_added",
        description=f"Note added by {data.author}",
        actor=data.author,
    )
    db.add(log)
    db.commit()
    db.refresh(note)
    return note


@router.get("/{candidate_id}")
def get_notes(candidate_id: int, db: Session = Depends(get_db)):
    return db.query(CandidateNote).filter(
        CandidateNote.candidate_id == candidate_id
    ).order_by(CandidateNote.created_at.desc()).all()


@router.delete("/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(CandidateNote).filter(CandidateNote.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
    return {"message": "Note deleted"}
