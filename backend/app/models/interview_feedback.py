from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class InterviewFeedback(Base):
    __tablename__ = "interview_feedback"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    interviewer_name = Column(String(255))
    technical_score = Column(Integer)  # 1-10
    communication_score = Column(Integer)  # 1-10
    cultural_fit_score = Column(Integer)  # 1-10
    overall_score = Column(Integer)  # 1-10
    strengths = Column(Text)
    weaknesses = Column(Text)
    recommendation = Column(String(50))  # strong_hire|hire|no_hire|strong_no_hire
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
