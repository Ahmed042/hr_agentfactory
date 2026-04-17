from sqlalchemy import Column, Integer, String, DECIMAL, Date, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.core.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(50))

    # Job Details
    employee_id = Column(String(50), unique=True)
    role = Column(String(100))
    department_id = Column(Integer, ForeignKey("departments.id"))
    salary = Column(DECIMAL(12, 2))
    joining_date = Column(Date)
    employment_type = Column(String(50))  # full_time|part_time|contract

    # Personal Info (US)
    ssn_last_four = Column(String(4))  # Only store last 4 digits
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(10))
    emergency_contact = Column(String(255))

    # Banking
    bank_name = Column(String(100))
    routing_number = Column(String(50))
    account_number = Column(String(100))

    # Benefits
    health_insurance = Column(String(50), default="none")  # none|basic|premium|family
    retirement_401k = Column(DECIMAL(5, 2), default=0)  # percentage contribution

    # Status
    status = Column(String(50), default="active")  # active|on_leave|resigned|terminated

    created_at = Column(DateTime(timezone=True), server_default=func.now())
