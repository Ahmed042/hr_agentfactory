from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    employee_id = Column(Integer, ForeignKey("employees.id"))
    type = Column(String(50))  # cv|cnic|certificate|contract|offer_letter
    file_url = Column(Text)
    file_name = Column(String(255))
    ai_validated = Column(Boolean, default=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
