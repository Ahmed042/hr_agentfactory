import os
import tempfile
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import logging

logger = logging.getLogger(__name__)


def generate_payslip_pdf(employee_data: dict, salary_data: dict) -> str:
    """Generate a PDF payslip and return the file path"""

    temp_dir = tempfile.mkdtemp()
    filename = f"payslip_{employee_data.get('name', 'employee').replace(' ', '_')}_{salary_data.get('month', 'unknown')}.pdf"
    filepath = os.path.join(temp_dir, filename)

    doc = SimpleDocTemplate(filepath, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=18, textColor=colors.HexColor('#1E3A8A'), spaceAfter=6)
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#64748B'), spaceAfter=20)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#1E3A8A'), spaceBefore=15, spaceAfter=8)

    elements = []

    # Header
    elements.append(Paragraph("HR AgentFactory", title_style))
    elements.append(Paragraph("Employee Payslip", subtitle_style))
    elements.append(Spacer(1, 10))

    # Employee Info
    elements.append(Paragraph("Employee Information", heading_style))
    emp_info = [
        ["Employee Name:", employee_data.get("name", "N/A"), "Employee ID:", employee_data.get("employee_id", f"EMP-{employee_data.get('id', '')}") ],
        ["Email:", employee_data.get("email", "N/A"), "Department:", employee_data.get("department", "N/A")],
        ["Role:", employee_data.get("role", "N/A"), "Pay Period:", salary_data.get("month", "N/A")],
    ]
    emp_table = Table(emp_info, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 2.5*inch])
    emp_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#64748B')),
        ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#64748B')),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTNAME', (3, 0), (3, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(emp_table)
    elements.append(Spacer(1, 15))

    # Earnings
    elements.append(Paragraph("Earnings", heading_style))
    gross = salary_data.get("gross_salary", 0)
    earnings_data = [
        ["Description", "Amount"],
        ["Gross Salary (Monthly)", f"${gross:,.2f}"],
        ["Annual Salary", f"${gross * 12:,.2f}"],
    ]
    earnings_table = Table(earnings_data, colWidths=[5*inch, 3*inch])
    earnings_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(earnings_table)
    elements.append(Spacer(1, 15))

    # Deductions
    elements.append(Paragraph("Deductions", heading_style))
    deductions_data = [
        ["Description", "Rate", "Amount"],
        ["Federal Income Tax", "", f"${salary_data.get('federal_tax', 0):,.2f}"],
        ["State Income Tax", "~5%", f"${salary_data.get('state_tax', 0):,.2f}"],
        ["Social Security (OASDI)", "6.2%", f"${salary_data.get('social_security', 0):,.2f}"],
        ["Medicare", "1.45%", f"${salary_data.get('medicare', 0):,.2f}"],
        ["Health Insurance", "", f"${salary_data.get('health_insurance', 0):,.2f}"],
        ["401(k) Contribution", "", f"${salary_data.get('retirement_401k', 0):,.2f}"],
        ["Total Deductions", "", f"${salary_data.get('total_deductions', 0):,.2f}"],
    ]
    ded_table = Table(deductions_data, colWidths=[4*inch, 1*inch, 3*inch])
    ded_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EF4444')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#FEE2E2')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    elements.append(ded_table)
    elements.append(Spacer(1, 20))

    # Net Pay
    elements.append(Paragraph("Net Pay", heading_style))
    net_data = [
        ["Net Pay (Take Home)", f"${salary_data.get('net_salary', 0):,.2f}"],
    ]
    net_table = Table(net_data, colWidths=[5*inch, 3*inch])
    net_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10B981')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(net_table)
    elements.append(Spacer(1, 30))

    # Footer
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#94A3B8'), alignment=TA_CENTER)
    elements.append(Paragraph("This is a system-generated payslip. For questions, contact HR.", footer_style))
    elements.append(Paragraph("Powered by HR AgentFactory", footer_style))

    doc.build(elements)
    logger.info(f"Payslip PDF generated: {filepath}")
    return filepath
