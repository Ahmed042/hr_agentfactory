from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class AIAction(Base):
    __tablename__ = "ai_actions"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    action_type = Column(String(100))
    reasoning = Column(Text)
    action_metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
