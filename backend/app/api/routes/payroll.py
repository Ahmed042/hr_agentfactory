from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.salary import Salary
from app.models.employee import Employee
from pydantic import BaseModel
from typing import Optional
from datetime import date
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class PayrollGenerate(BaseModel):
    month: str  # 2026-04
    employee_id: Optional[int] = None  # None = generate for all


@router.get("/")
def get_salaries(month: str = None, db: Session = Depends(get_db)):
    query = db.query(Salary)
    if month:
        query = query.filter(Salary.month == month)
    salaries = query.order_by(Salary.created_at.desc()).all()

    result = []
    for s in salaries:
        emp = db.query(Employee).filter(Employee.id == s.employee_id).first()
        result.append({
            "id": s.id,
            "employee_id": s.employee_id,
            "employee_name": emp.name if emp else f"EMP-{s.employee_id}",
            "employee_role": emp.role if emp else "",
            "month": s.month,
            "gross_salary": float(s.gross_salary) if s.gross_salary else 0,
            "federal_tax": float(s.federal_tax) if s.federal_tax else 0,
            "state_tax": float(s.state_tax) if s.state_tax else 0,
            "social_security": float(s.social_security) if s.social_security else 0,
            "medicare": float(s.medicare) if s.medicare else 0,
            "health_insurance": float(s.health_insurance) if s.health_insurance else 0,
            "retirement_401k": float(s.retirement_401k) if s.retirement_401k else 0,
            "total_deductions": float(s.total_deductions) if s.total_deductions else 0,
            "net_salary": float(s.net_salary) if s.net_salary else 0,
            "payment_status": s.payment_status,
            "payment_date": str(s.payment_date) if s.payment_date else None,
        })
    return result


@router.post("/generate")
def generate_payroll(data: PayrollGenerate, db: Session = Depends(get_db)):
    """Generate payslips with US tax calculations"""
    if data.employee_id:
        employees = db.query(Employee).filter(Employee.id == data.employee_id, Employee.status == "active").all()
    else:
        employees = db.query(Employee).filter(Employee.status == "active").all()

    generated = []
    for emp in employees:
        # Check if already generated
        existing = db.query(Salary).filter(
            Salary.employee_id == emp.id, Salary.month == data.month
        ).first()
        if existing:
            continue

        annual = float(emp.salary or 0)
        monthly_gross = round(annual / 12, 2)

        # US Tax Calculations (simplified)
        # Federal tax (estimated bracket)
        if annual <= 11600:
            fed_rate = 0.10
        elif annual <= 47150:
            fed_rate = 0.12
        elif annual <= 100525:
            fed_rate = 0.22
        elif annual <= 191950:
            fed_rate = 0.24
        elif annual <= 243725:
            fed_rate = 0.32
        elif annual <= 609350:
            fed_rate = 0.35
        else:
            fed_rate = 0.37

        federal_tax = round(monthly_gross * fed_rate, 2)
        state_tax = round(monthly_gross * 0.05, 2)  # ~5% avg state tax
        social_security = round(monthly_gross * 0.062, 2)  # 6.2%
        medicare = round(monthly_gross * 0.0145, 2)  # 1.45%

        # Benefits
        health_costs = {"none": 0, "basic": 200, "premium": 450, "family": 800}
        health = health_costs.get(emp.health_insurance or "none", 0)
        retirement = round(monthly_gross * float(emp.retirement_401k or 0) / 100, 2)

        total_deductions = round(federal_tax + state_tax + social_security + medicare + health + retirement, 2)
        net = round(monthly_gross - total_deductions, 2)

        salary = Salary(
            employee_id=emp.id,
            month=data.month,
            gross_salary=monthly_gross,
            federal_tax=federal_tax,
            state_tax=state_tax,
            social_security=social_security,
            medicare=medicare,
            health_insurance=health,
            retirement_401k=retirement,
            total_deductions=total_deductions,
            net_salary=net,
            payment_status="pending",
        )
        db.add(salary)
        generated.append({"employee": emp.name, "gross": monthly_gross, "net": net})

    db.commit()
    return {"generated": len(generated), "payslips": generated, "month": data.month}


@router.post("/send-payslips")
async def send_payslips(month: str, db: Session = Depends(get_db)):
    """Generate PDF payslips and email them to employees"""
    from app.services.payslip_generator import generate_payslip_pdf
    from app.services.email_service import email_service
    from app.models.email import Email as EmailModel
    import os

    salaries = db.query(Salary).filter(Salary.month == month).all()
    if not salaries:
        return {"error": "No payslips found for this month. Generate payroll first."}

    sent = []
    failed = []

    for s in salaries:
        emp = db.query(Employee).filter(Employee.id == s.employee_id).first()
        if not emp or not emp.email:
            failed.append({"employee_id": s.employee_id, "reason": "No email"})
            continue

        salary_data = {
            "month": s.month,
            "gross_salary": float(s.gross_salary or 0),
            "federal_tax": float(s.federal_tax or 0),
            "state_tax": float(s.state_tax or 0),
            "social_security": float(s.social_security or 0),
            "medicare": float(s.medicare or 0),
            "health_insurance": float(s.health_insurance or 0),
            "retirement_401k": float(s.retirement_401k or 0),
            "total_deductions": float(s.total_deductions or 0),
            "net_salary": float(s.net_salary or 0),
        }

        employee_data = {
            "id": emp.id,
            "name": emp.name,
            "email": emp.email,
            "role": emp.role or "",
            "employee_id": emp.employee_id or f"EMP-{emp.id}",
            "department": "",
        }

        try:
            pdf_path = generate_payslip_pdf(employee_data, salary_data)

            email_body = (
                f"Dear {emp.name},\n\n"
                f"Please find attached your payslip for {month}.\n\n"
                f"Gross Pay: ${salary_data['gross_salary']:,.2f}\n"
                f"Total Deductions: ${salary_data['total_deductions']:,.2f}\n"
                f"Net Pay: ${salary_data['net_salary']:,.2f}\n\n"
                f"If you have any questions, please contact HR.\n\n"
                f"Best regards,\nHR Team"
            )

            email_sent = await email_service.send_email_with_attachment(
                to_email=emp.email,
                subject=f"Your Payslip - {month}",
                body=email_body,
                file_path=pdf_path,
                file_name=f"payslip_{month}.pdf",
            )

            s.payment_status = "paid"
            sent.append({"employee": emp.name, "email": emp.email, "sent": email_sent})

            # Cleanup PDF
            os.unlink(pdf_path)
            os.rmdir(os.path.dirname(pdf_path))

        except Exception as e:
            failed.append({"employee": emp.name, "reason": str(e)})

    db.commit()
    return {"sent": len(sent), "failed": len(failed), "details": sent, "errors": failed}
