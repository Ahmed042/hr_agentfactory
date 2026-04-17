from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class CandidateNote(Base):
    __tablename__ = "candidate_notes"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    author = Column(String(255))
    content = Column(Text, nullable=False)
    note_type = Column(String(50), default="general")  # general|interview|feedback|internal
    created_at = Column(DateTime(timezone=True), server_default=func.now())
