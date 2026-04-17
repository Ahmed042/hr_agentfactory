from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.core.database import Base


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    interview_round = Column(Integer, default=1)  # 1, 2, 3...
    interview_type = Column(String(50), default="technical")  # screening|technical|hr|cultural|final
    interviewer_name = Column(String(255))
    interviewer_email = Column(String(255))
    scheduled_at = Column(DateTime(timezone=True))
    duration_minutes = Column(Integer, default=45)
    meeting_link = Column(Text)
    location = Column(String(255))
    interviewer_notes = Column(Text)
    result = Column(String(50), default="pending")  # pending|passed|failed|cancelled|no_show
    conducted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
