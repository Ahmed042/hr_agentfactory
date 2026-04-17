from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.employee import Employee
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class EmployeeCreate(BaseModel):
    email: str
    name: str
    role: str
    department_id: Optional[int] = None
    salary: Optional[float] = 0
    employment_type: str = "full_time"


def serialize_employee(emp):
    """Convert Employee ORM object to JSON-safe dict"""
    return {
        "id": emp.id,
        "email": emp.email,
        "name": emp.name,
        "phone": emp.phone,
        "employee_id": emp.employee_id,
        "role": emp.role,
        "department_id": emp.department_id,
        "salary": float(emp.salary) if emp.salary else 0,
        "joining_date": str(emp.joining_date) if emp.joining_date else None,
        "employment_type": emp.employment_type,
        "status": emp.status,
        "health_insurance": emp.health_insurance,
        "retirement_401k": float(emp.retirement_401k) if emp.retirement_401k else 0,
        "created_at": str(emp.created_at) if emp.created_at else None,
    }


@router.post("/")
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    """Create new employee"""
    logger.info(f"=== EMPLOYEE CREATE === {employee.model_dump()}")
    new_employee = Employee(**employee.model_dump(exclude_none=True))
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return serialize_employee(new_employee)


@router.get("/")
def get_employees(db: Session = Depends(get_db)):
    """Get all employees"""
    employees = db.query(Employee).filter(Employee.status == "active").all()
    return [serialize_employee(emp) for emp in employees]
