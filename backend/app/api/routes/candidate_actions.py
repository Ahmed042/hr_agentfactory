from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.candidate import Candidate
from app.models.email import Email
from app.models.interview import Interview
from app.models.ai_action import AIAction
from app.models.activity_log import ActivityLog
from app.services.email_service import email_service
from app.ai.brain import ai_brain
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class ActionRequest(BaseModel):
    candidate_id: int
    notes: Optional[str] = None


class InterviewRequest(BaseModel):
    candidate_id: int
    interview_type: str = "technical"
    interviewer_name: Optional[str] = None
    preferred_date: Optional[str] = None
    duration_minutes: int = 45


class OfferRequest(BaseModel):
    candidate_id: int
    salary: float
    start_date: str
    role: Optional[str] = None


@router.post("/approve")
async def approve_candidate(data: ActionRequest, db: Session = Depends(get_db)):
    """Approve candidate and send interview request email"""
    candidate = db.query(Candidate).filter(Candidate.id == data.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    candidate.status = "screening"
    candidate.stage = "screening"

    # AI generates personalized email
    email_body = await ai_brain.generate_email(
        context={"name": candidate.name or candidate.email.split("@")[0], "job_role": candidate.job_role},
        email_type="welcome"
    )

    email_subject = f"Great News! Next Steps for {candidate.job_role} Position"

    sent = await email_service.send_email(
        to_email=candidate.email,
        subject=email_subject,
        body=email_body,
    )

    # Log email
    db.add(Email(
        candidate_id=candidate.id, thread_id=f"app-{candidate.id}",
        direction="outbound", from_email="hr@company.com", to_email=candidate.email,
        subject=email_subject, body=email_body, ai_action="approved_candidate", is_read=True,
    ))

    db.add(ActivityLog(
        entity_type="candidate", entity_id=candidate.id, action="approved",
        description=f"Candidate approved. Welcome email {'sent' if sent else 'queued'}.",
        actor="admin",
    ))

    db.commit()
    return {"success": True, "email_sent": sent, "status": "screening"}


@router.post("/reject")
async def reject_candidate(data: ActionRequest, db: Session = Depends(get_db)):
    """Reject candidate and send rejection email"""
    candidate = db.query(Candidate).filter(Candidate.id == data.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    candidate.status = "rejected"
    candidate.stage = "rejected"

    email_body = await ai_brain.generate_email(
        context={"name": candidate.name or candidate.email.split("@")[0], "job_role": candidate.job_role},
        email_type="rejection"
    )

    email_subject = f"Update on Your Application - {candidate.job_role}"

    sent = await email_service.send_email(to_email=candidate.email, subject=email_subject, body=email_body)

    db.add(Email(
        candidate_id=candidate.id, thread_id=f"app-{candidate.id}",
        direction="outbound", from_email="hr@company.com", to_email=candidate.email,
        subject=email_subject, body=email_body, ai_action="rejection_sent", is_read=True,
    ))

    db.add(ActivityLog(
        entity_type="candidate", entity_id=candidate.id, action="rejected",
        description=f"Candidate rejected. Rejection email {'sent' if sent else 'queued'}.",
        actor="admin",
    ))

    db.commit()
    return {"success": True, "email_sent": sent, "status": "rejected"}


@router.post("/request-interview")
async def request_interview(data: InterviewRequest, db: Session = Depends(get_db)):
    """Send interview request email and create interview record"""
    candidate = db.query(Candidate).filter(Candidate.id == data.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    candidate.status = "interview"
    candidate.stage = data.interview_type

    # Generate time slots
    now = datetime.now()
    next_week = now + timedelta(days=(7 - now.weekday()))  # Next Monday
    slot1 = next_week.replace(hour=10, minute=0).strftime("%A, %B %d at 10:00 AM EST")
    slot2 = (next_week + timedelta(days=1)).replace(hour=14, minute=0).strftime("%A, %B %d at 2:00 PM EST")
    slot3 = (next_week + timedelta(days=2)).replace(hour=11, minute=0).strftime("%A, %B %d at 11:00 AM EST")

    email_body = await ai_brain.generate_email(
        context={
            "name": candidate.name or candidate.email.split("@")[0],
            "job_role": candidate.job_role,
            "slot1": slot1, "slot2": slot2, "slot3": slot3,
        },
        email_type="interview"
    )

    email_subject = f"Interview Invitation - {candidate.job_role} Position"

    sent = await email_service.send_email(to_email=candidate.email, subject=email_subject, body=email_body)

    # Create interview record
    scheduled_at = next_week.replace(hour=10, minute=0)
    interview = Interview(
        candidate_id=candidate.id,
        interview_round=1,
        interview_type=data.interview_type,
        interviewer_name=data.interviewer_name or "HR Team",
        scheduled_at=scheduled_at,
        duration_minutes=data.duration_minutes,
        result="pending",
    )
    db.add(interview)

    db.add(Email(
        candidate_id=candidate.id, thread_id=f"app-{candidate.id}",
        direction="outbound", from_email="hr@company.com", to_email=candidate.email,
        subject=email_subject, body=email_body, ai_action="interview_request", is_read=True,
    ))

    db.add(ActivityLog(
        entity_type="candidate", entity_id=candidate.id, action="interview_requested",
        description=f"Interview request sent for {data.interview_type} round.",
        actor="admin",
    ))

    db.commit()
    return {"success": True, "email_sent": sent, "status": "interview", "interview_type": data.interview_type}


@router.post("/send-offer")
async def send_offer(data: OfferRequest, db: Session = Depends(get_db)):
    """Send offer letter email"""
    candidate = db.query(Candidate).filter(Candidate.id == data.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    candidate.status = "offer"
    candidate.stage = "offer"

    role = data.role or candidate.job_role

    email_body = await ai_brain.generate_email(
        context={
            "name": candidate.name or candidate.email.split("@")[0],
            "role": role,
            "salary": f"{data.salary:,.0f}",
            "start_date": data.start_date,
        },
        email_type="offer"
    )

    email_subject = f"Job Offer - {role} Position"

    sent = await email_service.send_email(to_email=candidate.email, subject=email_subject, body=email_body)

    db.add(Email(
        candidate_id=candidate.id, thread_id=f"app-{candidate.id}",
        direction="outbound", from_email="hr@company.com", to_email=candidate.email,
        subject=email_subject, body=email_body, ai_action="offer_sent", is_read=True,
    ))

    db.add(ActivityLog(
        entity_type="candidate", entity_id=candidate.id, action="offer_sent",
        description=f"Offer letter sent: {role} at ${data.salary:,.0f}/year, starting {data.start_date}.",
        actor="admin",
    ))

    db.commit()
    return {"success": True, "email_sent": sent, "status": "offer"}


@router.post("/mark-hired")
async def mark_hired(data: ActionRequest, db: Session = Depends(get_db)):
    """Mark candidate as hired"""
    candidate = db.query(Candidate).filter(Candidate.id == data.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    candidate.status = "hired"
    candidate.stage = "hired"
    candidate.hired_at = datetime.now()

    # Send onboarding email
    email_body = await ai_brain.generate_email(
        context={"name": candidate.name or candidate.email.split("@")[0], "role": candidate.job_role},
        email_type="onboarding"
    )

    sent = await email_service.send_email(
        to_email=candidate.email,
        subject=f"Welcome to the Team! - Onboarding Information",
        body=email_body,
    )

    db.add(Email(
        candidate_id=candidate.id, thread_id=f"app-{candidate.id}",
        direction="outbound", from_email="hr@company.com", to_email=candidate.email,
        subject="Welcome to the Team!", body=email_body, ai_action="onboarding_sent", is_read=True,
    ))

    db.add(ActivityLog(
        entity_type="candidate", entity_id=candidate.id, action="hired",
        description=f"Candidate marked as hired. Onboarding email sent.",
        actor="admin",
    ))

    db.commit()
    return {"success": True, "email_sent": sent, "status": "hired"}
