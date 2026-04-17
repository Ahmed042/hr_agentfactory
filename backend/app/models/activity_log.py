from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False)  # candidate|employee|interview|job_posting
    entity_id = Column(Integer, nullable=False)
    action = Column(String(100), nullable=False)  # created|updated|status_changed|email_sent|etc
    description = Column(Text)
    actor = Column(String(255))  # who performed the action
    action_metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
