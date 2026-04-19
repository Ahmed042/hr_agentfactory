"""Async email tasks using Celery"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import logging

from app.core.celery_app import celery_app
from app.core.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_async(self, to_email: str, subject: str, body: str):
    """Send email asynchronously via Celery"""
    if not settings.EMAIL_USER or not settings.EMAIL_PASS:
        logger.info(f"[ASYNC EMAIL LOG] To: {to_email} | Subject: {subject}")
        return {"status": "logged", "to": to_email}

    try:
        message = MIMEMultipart("alternative")
        message["From"] = f"HR AgentFactory <{settings.EMAIL_FROM or settings.EMAIL_USER}>"
        message["To"] = to_email
        message["Subject"] = subject

        html_content = f"""
        <div style="font-family: 'Inter', Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #1E3A8A; color: white; padding: 20px 24px; border-radius: 8px 8px 0 0;">
                <h2 style="margin: 0; font-size: 18px;">HR AgentFactory</h2>
            </div>
            <div style="background: #ffffff; padding: 24px; border: 1px solid #e2e8f0; border-top: none; border-radius: 0 0 8px 8px;">
                <div style="color: #1e293b; font-size: 14px; line-height: 1.6;">
                    {body.replace(chr(10), '<br>')}
                </div>
            </div>
        </div>
        """
        message.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(settings.EMAIL_USER, settings.EMAIL_PASS)
            server.sendmail(settings.EMAIL_FROM or settings.EMAIL_USER, to_email, message.as_string())

        logger.info(f"[ASYNC] Email sent to {to_email}")
        return {"status": "sent", "to": to_email}

    except Exception as e:
        logger.error(f"[ASYNC] Email failed: {e}")
        raise self.retry(exc=e)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_with_attachment_async(self, to_email: str, subject: str, body: str, file_path: str, file_name: str):
    """Send email with attachment asynchronously"""
    if not settings.EMAIL_USER or not settings.EMAIL_PASS:
        logger.info(f"[ASYNC EMAIL LOG] To: {to_email} | Attachment: {file_name}")
        return {"status": "logged", "to": to_email}

    try:
        message = MIMEMultipart()
        message["From"] = f"HR AgentFactory <{settings.EMAIL_FROM or settings.EMAIL_USER}>"
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))

        with open(file_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={file_name}")
            message.attach(part)

        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(settings.EMAIL_USER, settings.EMAIL_PASS)
            server.sendmail(settings.EMAIL_FROM or settings.EMAIL_USER, to_email, message.as_string())

        logger.info(f"[ASYNC] Email with attachment sent to {to_email}")
        return {"status": "sent", "to": to_email}

    except Exception as e:
        logger.error(f"[ASYNC] Email with attachment failed: {e}")
        raise self.retry(exc=e)
