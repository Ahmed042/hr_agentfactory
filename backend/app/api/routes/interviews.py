from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.interview import Interview
from app.models.interview_feedback import InterviewFeedback
from app.models.candidate import Candidate
from app.models.activity_log import ActivityLog
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter()


class InterviewCreate(BaseModel):
    candidate_id: int
    interview_round: int = 1
    interview_type: str = "technical"
    interviewer_name: Optional[str] = None
    interviewer_email: Optional[str] = None
    scheduled_at: datetime
    duration_minutes: int = 45
    meeting_link: Optional[str] = None
    location: Optional[str] = None


class InterviewUpdate(BaseModel):
    result: Optional[str] = None
    interviewer_notes: Optional[str] = None
    conducted_at: Optional[datetime] = None


class FeedbackCreate(BaseModel):
    interview_id: int
    candidate_id: int
    interviewer_name: str
    technical_score: int = 5
    communication_score: int = 5
    cultural_fit_score: int = 5
    overall_score: int = 5
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    recommendation: str = "hire"
    notes: Optional[str] = None


@router.post("/")
def create_interview(data: InterviewCreate, db: Session = Depends(get_db)):
    interview = Interview(**data.model_dump())
    db.add(interview)

    # Update candidate stage
    candidate = db.query(Candidate).filter(Candidate.id == data.candidate_id).first()
    if candidate:
        candidate.stage = "technical" if data.interview_type == "technical" else "hr"
        candidate.status = "interview"

    # Log activity
    log = ActivityLog(
        entity_type="interview",
        entity_id=data.candidate_id,
        action="interview_scheduled",
        description=f"Round {data.interview_round} {data.interview_type} interview scheduled",
        actor="system",
    )
    db.add(log)
    db.commit()
    db.refresh(interview)
    return interview


@router.get("/")
def get_interviews(candidate_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Interview)
    if candidate_id:
        query = query.filter(Interview.candidate_id == candidate_id)
    return query.order_by(Interview.scheduled_at.desc()).all()


@router.put("/{interview_id}")
def update_interview(interview_id: int, data: InterviewUpdate, db: Session = Depends(get_db)):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    for key, value in data.model_dump(exclude_none=True).items():
        setattr(interview, key, value)

    db.commit()
    db.refresh(interview)
    return interview


@router.post("/feedback")
def create_feedback(data: FeedbackCreate, db: Session = Depends(get_db)):
    feedback = InterviewFeedback(**data.model_dump())
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


@router.get("/feedback/{candidate_id}")
def get_feedback(candidate_id: int, db: Session = Depends(get_db)):
    return db.query(InterviewFeedback).filter(
        InterviewFeedback.candidate_id == candidate_id
    ).all()
