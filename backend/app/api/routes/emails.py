from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func as sqlfunc
from app.core.database import get_db
from app.models.email import Email
from app.models.candidate import Candidate
from app.services.email_service import email_service
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class EmailReply(BaseModel):
    candidate_id: int
    subject: str
    body: str


@router.get("/inbox")
def get_inbox(db: Session = Depends(get_db)):
    """Get all email threads grouped by candidate"""
    # Get latest email per candidate with counts
    candidates_with_emails = (
        db.query(
            Candidate.id,
            Candidate.name,
            Candidate.email,
            Candidate.job_role,
            sqlfunc.count(Email.id).label("email_count"),
            sqlfunc.max(Email.sent_at).label("last_email"),
        )
        .join(Email, Email.candidate_id == Candidate.id)
        .group_by(Candidate.id)
        .order_by(sqlfunc.max(Email.sent_at).desc())
        .all()
    )

    threads = []
    for row in candidates_with_emails:
        # Get latest email for preview
        latest = db.query(Email).filter(
            Email.candidate_id == row.id
        ).order_by(Email.sent_at.desc()).first()

        threads.append({
            "candidate_id": row.id,
            "candidate_name": row.name or row.email.split("@")[0],
            "candidate_email": row.email,
            "job_role": row.job_role,
            "email_count": row.email_count,
            "last_email": str(row.last_email) if row.last_email else None,
            "latest_subject": latest.subject if latest else "",
            "latest_preview": (latest.body or "")[:100] if latest else "",
            "latest_direction": latest.direction if latest else "",
        })

    return threads


@router.get("/thread/{candidate_id}")
def get_thread(candidate_id: int, db: Session = Depends(get_db)):
    """Get all emails for a candidate (thread view)"""
    emails = db.query(Email).filter(
        Email.candidate_id == candidate_id
    ).order_by(Email.sent_at.asc()).all()

    # Mark as read
    db.query(Email).filter(
        Email.candidate_id == candidate_id,
        Email.is_read == False
    ).update({"is_read": True})
    db.commit()

    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    return {
        "candidate": {
            "id": candidate.id if candidate else candidate_id,
            "name": candidate.name if candidate else "Unknown",
            "email": candidate.email if candidate else "",
            "job_role": candidate.job_role if candidate else "",
        },
        "emails": [
            {
                "id": e.id,
                "direction": e.direction,
                "from_email": e.from_email,
                "to_email": e.to_email,
                "subject": e.subject,
                "body": e.body,
                "ai_action": e.ai_action,
                "is_read": e.is_read,
                "sent_at": str(e.sent_at) if e.sent_at else None,
            }
            for e in emails
        ],
    }


@router.post("/reply")
async def send_reply(data: EmailReply, db: Session = Depends(get_db)):
    """Send email reply to candidate"""
    candidate = db.query(Candidate).filter(Candidate.id == data.candidate_id).first()
    if not candidate:
        return {"error": "Candidate not found"}

    sent = await email_service.send_email(
        to_email=candidate.email,
        subject=data.subject,
        body=data.body,
    )

    email_log = Email(
        candidate_id=candidate.id,
        thread_id=f"app-{candidate.id}",
        direction="outbound",
        from_email="hr@company.com",
        to_email=candidate.email,
        subject=data.subject,
        body=data.body,
        ai_action="manual_reply",
        is_read=True,
    )
    db.add(email_log)
    db.commit()

    return {"success": True, "email_sent": sent}
