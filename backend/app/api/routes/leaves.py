from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.leave import Leave
from app.models.employee import Employee
from app.models.activity_log import ActivityLog
from app.models.user import User
from pydantic import BaseModel
from typing import Optional
from datetime import date
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class LeaveCreate(BaseModel):
    employee_id: int
    leave_type: str  # sick|casual|annual
    start_date: date
    end_date: date
    reason: Optional[str] = None


class LeaveUpdate(BaseModel):
    status: str  # approved|rejected


@router.post("/")
def create_leave(data: LeaveCreate, db: Session = Depends(get_db)):
    """Submit a leave request"""
    employee = db.query(Employee).filter(Employee.id == data.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    if data.leave_type not in ("sick", "casual", "annual"):
        raise HTTPException(status_code=400, detail="Invalid leave type")

    if data.end_date < data.start_date:
        raise HTTPException(status_code=400, detail="End date must be after start date")

    days = (data.end_date - data.start_date).days + 1

    leave = Leave(
        employee_id=data.employee_id,
        leave_type=data.leave_type,
        start_date=data.start_date,
        end_date=data.end_date,
        days=days,
        reason=data.reason,
        status="pending",
    )
    db.add(leave)

    db.add(ActivityLog(
        entity_type="leave", entity_id=0, action="leave_requested",
        description=f"{employee.name} requested {days} day(s) {data.leave_type} leave",
        actor=employee.name,
    ))

    db.commit()
    db.refresh(leave)
    return serialize_leave(leave, db)


@router.get("/")
def get_leaves(
    status: Optional[str] = None,
    employee_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Get all leave requests with optional filters"""
    query = db.query(Leave)
    if status:
        query = query.filter(Leave.status == status)
    if employee_id:
        query = query.filter(Leave.employee_id == employee_id)

    leaves = query.order_by(Leave.created_at.desc()).all()
    return [serialize_leave(l, db) for l in leaves]


@router.put("/{leave_id}")
def update_leave(
    leave_id: int,
    data: LeaveUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approve or reject a leave request"""
    leave = db.query(Leave).filter(Leave.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")

    if leave.status != "pending":
        raise HTTPException(status_code=400, detail="Can only update pending leave requests")

    if data.status not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="Status must be approved or rejected")

    leave.status = data.status

    employee = db.query(Employee).filter(Employee.id == leave.employee_id).first()
    emp_name = employee.name if employee else f"EMP-{leave.employee_id}"

    db.add(ActivityLog(
        entity_type="leave", entity_id=leave_id, action=f"leave_{data.status}",
        description=f"Leave request {data.status} for {emp_name} by {current_user.name}",
        actor=current_user.name or current_user.email,
    ))

    db.commit()
    db.refresh(leave)
    return serialize_leave(leave, db)


@router.delete("/{leave_id}")
def delete_leave(leave_id: int, db: Session = Depends(get_db)):
    """Delete a leave request"""
    leave = db.query(Leave).filter(Leave.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")
    db.delete(leave)
    db.commit()
    return {"message": "Leave request deleted"}


def serialize_leave(leave: Leave, db: Session) -> dict:
    employee = db.query(Employee).filter(Employee.id == leave.employee_id).first()
    return {
        "id": leave.id,
        "employee_id": leave.employee_id,
        "employee_name": employee.name if employee else f"EMP-{leave.employee_id}",
        "leave_type": leave.leave_type,
        "start_date": str(leave.start_date) if leave.start_date else None,
        "end_date": str(leave.end_date) if leave.end_date else None,
        "days": leave.days,
        "reason": leave.reason,
        "status": leave.status,
        "created_at": str(leave.created_at) if leave.created_at else None,
    }
