from sqlalchemy import Column, Integer, String, DECIMAL, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class Salary(Base):
    __tablename__ = "salaries"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    month = Column(String(7), nullable=False)  # 2026-04

    # Earnings
    gross_salary = Column(DECIMAL(12, 2))

    # US Tax Deductions
    federal_tax = Column(DECIMAL(12, 2), default=0)
    state_tax = Column(DECIMAL(12, 2), default=0)
    social_security = Column(DECIMAL(12, 2), default=0)  # 6.2%
    medicare = Column(DECIMAL(12, 2), default=0)  # 1.45%

    # Benefits Deductions
    health_insurance = Column(DECIMAL(12, 2), default=0)
    retirement_401k = Column(DECIMAL(12, 2), default=0)

    # Totals
    total_deductions = Column(DECIMAL(12, 2), default=0)
    net_salary = Column(DECIMAL(12, 2))

    payment_status = Column(String(50), default="pending")  # pending|paid
    payment_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
