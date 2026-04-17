from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.department import Department
from app.models.employee import Employee
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class DepartmentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    budget: Optional[float] = None
    head_name: Optional[str] = None


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    budget: Optional[float] = None
    head_name: Optional[str] = None


@router.get("/")
def get_departments(db: Session = Depends(get_db)):
    departments = db.query(Department).all()
    result = []
    for dept in departments:
        emp_count = db.query(Employee).filter(Employee.department_id == dept.id).count()
        result.append({
            "id": dept.id,
            "name": dept.name,
            "description": dept.description,
            "budget": float(dept.budget) if dept.budget else None,
            "head_name": dept.head_name,
            "employee_count": emp_count,
            "created_at": str(dept.created_at) if dept.created_at else None,
        })
    return result


@router.post("/")
def create_department(data: DepartmentCreate, db: Session = Depends(get_db)):
    dept = Department(**data.model_dump())
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


@router.put("/{dept_id}")
def update_department(dept_id: int, data: DepartmentUpdate, db: Session = Depends(get_db)):
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    for key, value in data.model_dump(exclude_none=True).items():
        setattr(dept, key, value)
    db.commit()
    db.refresh(dept)
    return dept


@router.delete("/{dept_id}")
def delete_department(dept_id: int, db: Session = Depends(get_db)):
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    db.delete(dept)
    db.commit()
    return {"message": "Department deleted"}
