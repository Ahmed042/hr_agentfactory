from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class JobPosting(Base):
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    department = Column(String(100))
    location = Column(String(255))
    employment_type = Column(String(50))  # full_time|part_time|contract|internship
    experience_level = Column(String(50))  # entry|mid|senior|lead
    salary_min = Column(Integer)
    salary_max = Column(Integer)

    # AI-generated content
    description = Column(Text)
    responsibilities = Column(Text)
    required_qualifications = Column(Text)
    preferred_qualifications = Column(Text)
    benefits = Column(Text)

    skills_required = Column(JSON)  # ["Python", "React", "AWS"]
    status = Column(String(50), default="draft")  # draft|active|paused|closed
    applications_count = Column(Integer, default=0)
    is_remote = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    closes_at = Column(DateTime(timezone=True))
