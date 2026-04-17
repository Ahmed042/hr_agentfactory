from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    thread_id = Column(String(255))  # Group emails into threads
    direction = Column(String(10))  # inbound|outbound
    from_email = Column(String(255))
    to_email = Column(String(255))
    subject = Column(Text)
    body = Column(Text)
    ai_action = Column(String(100))
    is_read = Column(Boolean, default=False)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
