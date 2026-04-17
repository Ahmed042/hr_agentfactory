from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.job_posting import JobPosting
from app.models.candidate import Candidate
from app.models.activity_log import ActivityLog
from app.models.email import Email
from app.models.ai_action import AIAction
from app.services.email_service import email_service
from app.ai.brain import ai_brain
from pydantic import BaseModel, EmailStr
from typing import Optional, List

router = APIRouter()


class PublicJobResponse(BaseModel):
    id: int
    title: str
    department: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    description: Optional[str] = None
    responsibilities: Optional[str] = None
    required_qualifications: Optional[str] = None
    preferred_qualifications: Optional[str] = None
    benefits: Optional[str] = None
    skills_required: Optional[List[str]] = None
    is_remote: Optional[bool] = False

    class Config:
        from_attributes = True


class ApplicationSubmit(BaseModel):
    job_id: int
    name: str
    email: EmailStr
    phone: Optional[str] = None
    resume_text: Optional[str] = None
    cover_letter: Optional[str] = None
    location: Optional[str] = None
    experience_years: Optional[int] = None
    expected_salary: Optional[int] = None
    skills: Optional[List[str]] = None


@router.get("/careers")
def get_public_jobs(department: str = None, search: str = None, db: Session = Depends(get_db)):
    """Public: List all active job postings"""
    query = db.query(JobPosting).filter(JobPosting.status == "active")
    if department:
        query = query.filter(JobPosting.department == department)
    if search:
        query = query.filter(
            (JobPosting.title.ilike(f"%{search}%")) |
            (JobPosting.description.ilike(f"%{search}%"))
        )
    jobs = query.order_by(JobPosting.created_at.desc()).all()
    return jobs


@router.get("/careers/{job_id}")
def get_public_job(job_id: int, db: Session = Depends(get_db)):
    """Public: Get single job posting details"""
    job = db.query(JobPosting).filter(
        JobPosting.id == job_id,
        JobPosting.status == "active"
    ).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/careers/{job_id}/apply")
async def apply_to_job(job_id: int, data: ApplicationSubmit, db: Session = Depends(get_db)):
    """Public: Submit job application"""
    # Verify job exists
    job = db.query(JobPosting).filter(JobPosting.id == job_id, JobPosting.status == "active").first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or no longer accepting applications")

    # Check duplicate
    existing = db.query(Candidate).filter(Candidate.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already applied. We'll be in touch!")

    # Create candidate
    candidate = Candidate(
        email=data.email,
        name=data.name,
        phone=data.phone,
        job_role=job.title,
        source="careers_page",
        location=data.location,
        experience_years=data.experience_years,
        expected_salary=data.expected_salary,
        skills=data.skills,
        resume_text=data.resume_text,
        status="applied",
        stage="applied",
        job_posting_id=job_id,
        has_resume=bool(data.resume_text),
        has_cover_letter=bool(data.cover_letter),
    )
    db.add(candidate)

    # Increment application count
    job.applications_count = (job.applications_count or 0) + 1
    db.commit()
    db.refresh(candidate)

    # AI screen candidate if resume provided
    ai_score = 50
    ai_decision = "proceed"
    if data.resume_text and len(data.resume_text) > 50:
        try:
            ai_result = await ai_brain.analyze_candidate(data.resume_text, job.title)
            ai_score = ai_result.get("score", 50)
            ai_decision = ai_result.get("decision", "proceed")
            candidate.ai_score = ai_score
            candidate.ai_reasoning = ai_result.get("reasoning", "")

            if ai_decision == "reject":
                candidate.status = "rejected"
                candidate.stage = "rejected"
        except Exception:
            pass

    # Send appropriate email
    if ai_decision == "reject" and ai_score < 50:
        email_subject = f"RE: Your Application for {job.title}"
        email_body = (
            f"Dear {data.name},\n\n"
            f"Thank you for your interest in the {job.title} position and for taking the time to apply.\n\n"
            f"After careful review, we've decided to move forward with other candidates whose experience "
            f"more closely matches our current needs.\n\n"
            f"We encourage you to apply for future openings that match your skills and experience.\n\n"
            f"Best regards,\nHR Team"
        )
    else:
        email_subject = f"Application Received - {job.title}"
        email_body = (
            f"Dear {data.name},\n\n"
            f"Thank you for applying to the {job.title} position!\n\n"
            f"We've received your application and our team will review it shortly. "
            f"We typically respond within 3-5 business days.\n\n"
            f"Best regards,\nHR Team"
        )

    await email_service.send_email(to_email=data.email, subject=email_subject, body=email_body)

    # Log email
    email_log = Email(
        candidate_id=candidate.id,
        thread_id=f"app-{candidate.id}",
        direction="outbound",
        from_email="hr@company.com",
        to_email=data.email,
        subject=email_subject,
        body=email_body,
        ai_action="auto_response",
        is_read=True,
    )
    db.add(email_log)

    # Log AI action
    ai_action = AIAction(
        candidate_id=candidate.id,
        action_type="auto_screening",
        reasoning=f"AI scored {ai_score}/100 - {ai_decision}",
        action_metadata={"score": ai_score, "decision": ai_decision, "source": "careers_page"},
    )
    db.add(ai_action)

    # Activity log
    activity = ActivityLog(
        entity_type="candidate",
        entity_id=candidate.id,
        action="applied_from_careers",
        description=f"{data.name} applied for {job.title} via careers page (AI Score: {ai_score})",
        actor="public",
    )
    db.add(activity)

    db.commit()

    return {
        "success": True,
        "message": "Application submitted successfully! Check your email for confirmation.",
        "candidate_id": candidate.id,
    }
