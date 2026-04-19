"""Async payroll tasks using Celery"""
import logging
from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def generate_payslips_async(self, month: str):
    """Generate payslips for all employees asynchronously"""
    from app.core.database import SessionLocal
    from app.models.salary import Salary
    from app.models.employee import Employee
    from app.services.payslip_generator import generate_payslip_pdf
    from app.tasks.email_tasks import send_email_with_attachment_async
    import os

    db = SessionLocal()
    try:
        salaries = db.query(Salary).filter(Salary.month == month).all()
        results = []

        for s in salaries:
            emp = db.query(Employee).filter(Employee.id == s.employee_id).first()
            if not emp or not emp.email:
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

            pdf_path = generate_payslip_pdf(employee_data, salary_data)

            email_body = (
                f"Dear {emp.name},<br><br>"
                f"Please find attached your payslip for {month}.<br><br>"
                f"Gross Pay: ${salary_data['gross_salary']:,.2f}<br>"
                f"Total Deductions: ${salary_data['total_deductions']:,.2f}<br>"
                f"Net Pay: ${salary_data['net_salary']:,.2f}<br><br>"
                f"Best regards,<br>HR Team"
            )

            # Queue email sending
            send_email_with_attachment_async.delay(
                to_email=emp.email,
                subject=f"Your Payslip - {month}",
                body=email_body,
                file_path=pdf_path,
                file_name=f"payslip_{month}.pdf",
            )

            s.payment_status = "paid"
            results.append(emp.name)

        db.commit()
        return {"sent": len(results), "employees": results}

    finally:
        db.close()
