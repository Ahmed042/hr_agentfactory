import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.host = settings.EMAIL_HOST
        self.port = settings.EMAIL_PORT
        self.user = settings.EMAIL_USER
        self.password = settings.EMAIL_PASS
        self.from_email = settings.EMAIL_FROM or settings.EMAIL_USER

    def is_configured(self) -> bool:
        return bool(self.user and self.password)

    async def send_email(self, to_email: str, subject: str, body: str, html: bool = True) -> bool:
        """Send email via Gmail SMTP"""
        if not self.is_configured():
            logger.info(f"[EMAIL LOG] To: {to_email} | Subject: {subject} | Body: {body[:200]}")
            return True

        try:
            message = MIMEMultipart("alternative")
            message["From"] = f"HR AgentFactory <{self.from_email}>"
            message["To"] = to_email
            message["Subject"] = subject

            if html:
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
                    <div style="text-align: center; padding: 16px; color: #94a3b8; font-size: 11px;">
                        Sent via HR AgentFactory
                    </div>
                </div>
                """
                message.attach(MIMEText(html_content, "html"))
            else:
                message.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(self.host, self.port) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(self.user, self.password)
                server.sendmail(self.from_email, to_email, message.as_string())

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"SMTP email failed: {e}")
            return False

    async def send_email_with_attachment(self, to_email: str, subject: str, body: str, file_path: str, file_name: str) -> bool:
        """Send email with attachment via SMTP"""
        if not self.is_configured():
            logger.info(f"[EMAIL LOG] To: {to_email} | Attachment: {file_name}")
            return True

        try:
            message = MIMEMultipart()
            message["From"] = f"HR AgentFactory <{self.from_email}>"
            message["To"] = to_email
            message["Subject"] = subject
            message.attach(MIMEText(body, "html"))

            with open(file_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename={file_name}")
                message.attach(part)

            with smtplib.SMTP(self.host, self.port) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(self.user, self.password)
                server.sendmail(self.from_email, to_email, message.as_string())

            logger.info(f"Email with attachment sent to {to_email}")
            return True

        except Exception as e:
            logger.error(f"SMTP attachment email failed: {e}")
            return False


email_service = EmailService()
