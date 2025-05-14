# app/services/email.py
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails."""

    def __init__(self):
        """Initialize the email service."""
        self.smtp_server = settings.EMAIL.SMTP_SERVER
        self.smtp_port = settings.EMAIL.SMTP_PORT
        self.username = settings.EMAIL.USERNAME
        self.password = settings.EMAIL.PASSWORD
        self.use_tls = settings.EMAIL.USE_TLS
        self.from_email = settings.EMAIL.FROM_EMAIL

    async def send_email(self, to_emails, subject, body_html, body_text=None, cc_emails=None, bcc_emails=None):
        """Send an email.

        Args:
            to_emails: List of recipient email addresses.
            subject: Email subject.
            body_html: HTML content of the email.
            body_text: Plain text content of the email (optional).
            cc_emails: List of CC email addresses (optional).
            bcc_emails: List of BCC email addresses (optional).

        Returns:
            bool: True if email was sent successfully, False otherwise.
        """
        try:
            # Create message container
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = ', '.join(to_emails)

            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)

            # Attach plain text and HTML parts
            if body_text:
                msg.attach(MIMEText(body_text, 'plain'))

            msg.attach(MIMEText(body_html, 'html'))

            # Determine all recipients
            all_recipients = to_emails.copy()
            if cc_emails:
                all_recipients.extend(cc_emails)
            if bcc_emails:
                all_recipients.extend(bcc_emails)

            # Connect to SMTP server
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()

                server.login(self.username, self.password)
                server.sendmail(self.from_email, all_recipients, msg.as_string())

            logger.info(f"Email sent successfully to {', '.join(to_emails)}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False


email_service = EmailService()
