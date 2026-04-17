from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.core.database import Base


class Leave(Base):
    __tablename__ = "leaves"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    leave_type = Column(String(50))  # sick|casual|annual
    start_date = Column(Date)
    end_date = Column(Date)
    days = Column(Integer)
    reason = Column(Text)
    status = Column(String(50), default="pending")  # pending|approved|rejected
    approved_by = Column(Integer, ForeignKey("employees.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
