from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255))
    phone = Column(String(50))
    job_role = Column(String(100))
    source = Column(String(100))  # linkedin|indeed|referral|website|careers_page|direct
    location = Column(String(255))
    experience_years = Column(Integer)
    current_salary = Column(Integer)
    expected_salary = Column(Integer)
    skills = Column(JSON)
    tags = Column(JSON)
    resume_text = Column(Text)  # Extracted resume text

    # Pipeline stage
    stage = Column(String(50), default="applied")
    status = Column(String(50), default="applied", index=True)
    ai_score = Column(Integer)
    ai_reasoning = Column(Text)

    # Document Checklist (US)
    has_cv = Column(Boolean, default=False)
    has_resume = Column(Boolean, default=False)
    has_cover_letter = Column(Boolean, default=False)
    has_references = Column(Boolean, default=False)

    # Timeline
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    last_contact = Column(DateTime(timezone=True))
    next_action_at = Column(DateTime(timezone=True))
    hired_at = Column(DateTime(timezone=True))

    # Job posting link
    job_posting_id = Column(Integer, ForeignKey("job_postings.id"))

    # If hired
    employee_id = Column(Integer, ForeignKey("employees.id"))
