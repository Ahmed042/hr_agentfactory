from sqlalchemy.orm import Session
from app.models.candidate import Candidate
from app.models.email import Email
from app.models.ai_action import AIAction
from app.models.activity_log import ActivityLog
from app.services.email_service import email_service
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CandidateService:

    async def create_candidate(
        self,
        db: Session,
        email: str,
        job_role: str,
        name: str = None,
        phone: str = None,
        source: str = None,
        location: str = None,
        experience_years: int = None,
        expected_salary: int = None,
        skills: list = None,
    ):
        """Create new candidate, send welcome email, log everything"""

        existing = db.query(Candidate).filter(Candidate.email == email).first()
        if existing:
            return {"error": "Candidate already exists"}

        candidate_name = name or email.split("@")[0].replace(".", " ").title()

        candidate = Candidate(
            email=email,
            name=candidate_name,
            phone=phone,
            job_role=job_role,
            source=source,
            location=location,
            experience_years=experience_years,
            expected_salary=expected_salary,
            skills=skills,
            status="applied",
            stage="applied",
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)

        # Send welcome email via SMTP
        email_subject = f"Application Received - {job_role} Position"
        email_body = (
            f"Dear {candidate_name},\n\n"
            f"Thank you for applying to the {job_role} position at our company.\n\n"
            f"We have received your application and our team will review it shortly. "
            f"To proceed with your application, please submit the following documents:\n\n"
            f"1. Updated Resume\n"
            f"2. Cover Letter\n"
            f"3. Professional References (2-3)\n\n"
            f"We will get back to you within 3-5 business days.\n\n"
            f"Best regards,\nHR Team"
        )

        email_sent = await email_service.send_email(
            to_email=email,
            subject=email_subject,
            body=email_body,
        )

        # Log email to database
        email_log = Email(
            candidate_id=candidate.id,
            direction="outbound",
            subject=email_subject,
            body=email_body,
            ai_action="sent_welcome",
        )
        db.add(email_log)

        # Log AI action
        ai_action = AIAction(
            candidate_id=candidate.id,
            action_type="candidate_created",
            reasoning=f"New candidate registered. Welcome email {'sent' if email_sent else 'queued'}.",
            action_metadata={"email": email, "job_role": job_role, "source": source, "email_sent": email_sent},
        )
        db.add(ai_action)

        # Log activity
        activity = ActivityLog(
            entity_type="candidate",
            entity_id=candidate.id,
            action="created",
            description=f"New candidate: {candidate_name} applied for {job_role}",
            actor="system",
            action_metadata={"source": source, "email_sent": email_sent},
        )
        db.add(activity)

        candidate.next_action_at = datetime.now() + timedelta(days=3)
        db.commit()

        logger.info(f"Candidate created: {email} | Email sent: {email_sent}")
        return {"success": True, "candidate_id": candidate.id, "email_sent": email_sent}

    def get_candidates(self, db: Session, status: str = None):
        query = db.query(Candidate)
        if status:
            query = query.filter(Candidate.status == status)
        return query.order_by(Candidate.applied_at.desc()).all()

    def get_candidate_by_email(self, db: Session, email: str):
        return db.query(Candidate).filter(Candidate.email == email).first()


candidate_service = CandidateService()
