from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.core.database import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    budget = Column(DECIMAL(12, 2))
    head_name = Column(String(255))
    head_employee_id = Column(Integer, ForeignKey("employees.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
