"""
Email Service
Handles sending emails using SMTP
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
from jinja2 import Template

from app.core.config import settings
from atams.exceptions import BadRequestException


class EmailService:
    def __init__(self):
        self.smtp_server = settings.MAIL_SERVER
        self.smtp_port = settings.MAIL_PORT
        self.username = settings.MAIL_USERNAME
        self.password = settings.MAIL_PASSWORD
        self.from_email = settings.MAIL_FROM
        self.from_name = settings.MAIL_FROM_NAME
        self.use_tls = settings.MAIL_USE_TLS
        self.use_ssl = settings.MAIL_USE_SSL

    def _validate_config(self):
        """Validate email configuration"""
        if not all([self.smtp_server, self.username, self.password, self.from_email]):
            raise BadRequestException(
                "Email configuration is incomplete. Please set MAIL_SERVER, "
                "MAIL_USERNAME, MAIL_PASSWORD, and MAIL_FROM in environment variables."
            )

    def _render_template(self, template_name: str, context: Dict) -> str:
        """Render email template with context"""
        template_path = Path(__file__).parent.parent / "templates" / template_name

        if not template_path.exists():
            raise BadRequestException(f"Email template '{template_name}' not found")

        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        template = Template(template_content)
        return template.render(**context)

    def send_task_reminder_email(
        self,
        to_email: str,
        task_data: Dict
    ) -> bool:
        """
        Send task reminder email

        Args:
            to_email: Recipient email address
            task_data: Dictionary containing task information

        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            self._validate_config()

            # Prepare template context
            context = {
                "assignee_name": task_data.get("tsk_assignee_name", "User"),
                "task_code": task_data.get("tsk_code", "N/A"),
                "task_title": task_data.get("tsk_title", "Untitled Task"),
                "description": task_data.get("tsk_description", "No description provided"),
                "project_name": task_data.get("tsk_project_name", "No Project"),
                "project_code": task_data.get("tsk_project_code", "N/A"),
                "status_name": task_data.get("tsk_status_name", "Unknown"),
                "priority_name": task_data.get("tsk_priority_name", "Normal"),
                "priority_class": self._get_priority_class(task_data.get("tsk_priority_name", "")),
                "task_type": task_data.get("tsk_type_name", "Task"),
                "reporter_name": task_data.get("tsk_reporter_name", "Unknown"),
                "start_date": self._format_date(task_data.get("tsk_start_date")),
                "year": datetime.now().year
            }

            # Render HTML template
            html_content = self._render_template("email.html", context)

            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = f"Task Reminder: {context['task_code']} - {context['task_title']}"
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email

            # Attach HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)

            # Send email
            if self.use_ssl:
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                    server.login(self.username, self.password)
                    server.send_message(message)
            else:
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    if self.use_tls:
                        server.starttls()
                    server.login(self.username, self.password)
                    server.send_message(message)

            return True

        except Exception as e:
            print(f"Failed to send email to {to_email}: {str(e)}")
            return False

    def _get_priority_class(self, priority_name: str) -> str:
        """Map priority name to CSS class"""
        priority_map = {
            "high": "high",
            "urgent": "high",
            "critical": "high",
            "medium": "medium",
            "normal": "medium",
            "low": "low"
        }
        return priority_map.get(priority_name.lower(), "medium")

    def _format_date(self, date_value) -> Optional[str]:
        """Format datetime to readable string"""
        if not date_value:
            return None

        if isinstance(date_value, str):
            try:
                date_value = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
            except:
                return date_value

        if isinstance(date_value, datetime):
            return date_value.strftime("%B %d, %Y at %I:%M %p")

        return str(date_value)

    def send_test_email(self, to_email: str) -> bool:
        """Send a test email to verify configuration"""
        try:
            self._validate_config()

            message = MIMEText("This is a test email from Atask notification system.")
            message["Subject"] = "Test Email - Atask Notification"
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email

            if self.use_ssl:
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                    server.login(self.username, self.password)
                    server.send_message(message)
            else:
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    if self.use_tls:
                        server.starttls()
                    server.login(self.username, self.password)
                    server.send_message(message)

            return True

        except Exception as e:
            print(f"Test email failed: {str(e)}")
            return False
