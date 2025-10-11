"""
Task Notification Service
Business logic for sending task notifications
"""
from typing import Dict, List
from datetime import date
from sqlalchemy.orm import Session

from app.services.email_service import EmailService
from atams.exceptions import BadRequestException


class NotificationSummary:
    """Summary of notification send operation"""
    def __init__(self, total_tasks: int, emails_sent: int, emails_failed: int, failed_tasks: list):
        self.total_tasks = total_tasks
        self.emails_sent = emails_sent
        self.emails_failed = emails_failed
        self.success_rate = (emails_sent / total_tasks * 100) if total_tasks > 0 else 0
        self.failed_tasks = failed_tasks

    def to_dict(self):
        return {
            "total_tasks": self.total_tasks,
            "emails_sent": self.emails_sent,
            "emails_failed": self.emails_failed,
            "success_rate": round(self.success_rate, 2),
            "failed_tasks": self.failed_tasks
        }


class TaskNotificationService:
    def __init__(self):
        self.email_service = EmailService()

    def get_tasks_for_daily_reminder(self, db: Session):
        """
        Get tasks that:
        1. Start today (tsk_start_date = today)
        2. Have an assignee (tsk_assignee_u_id is not null)
        """
        query = """
            SELECT DISTINCT
                t.tsk_id,
                t.tsk_code,
                t.tsk_title,
                t.tsk_description,
                t.tsk_assignee_u_id,
                t.tsk_reporter_u_id,
                t.tsk_start_date,
                p.prj_name as tsk_project_name,
                p.prj_code as tsk_project_code,
                ms.ms_name as tsk_status_name,
                mp.mp_name as tsk_priority_name,
                mtt.mtt_name as tsk_type_name,
                u_assignee.u_email as assignee_email,
                u_assignee.u_full_name as tsk_assignee_name,
                u_reporter.u_full_name as tsk_reporter_name
            FROM atask.task t
            LEFT JOIN atask.project p ON t.tsk_prj_id = p.prj_id
            LEFT JOIN atask.master_status ms ON t.tsk_ms_id = ms.ms_id
            LEFT JOIN atask.master_priority mp ON t.tsk_mp_id = mp.mp_id
            LEFT JOIN atask.master_task_type mtt ON t.tsk_mtt_id = mtt.mtt_id
            LEFT JOIN pt_atams_indonesia.users u_assignee ON t.tsk_assignee_u_id = u_assignee.u_id
            LEFT JOIN pt_atams_indonesia.users u_reporter ON t.tsk_reporter_u_id = u_reporter.u_id
            WHERE DATE(t.tsk_start_date) = :today
              AND t.tsk_assignee_u_id IS NOT NULL
              AND u_assignee.u_email IS NOT NULL
            ORDER BY t.tsk_id
        """
        today = date.today()
        result = db.execute(query, {"today": today})
        return [dict(row._mapping) for row in result]

    def send_daily_reminders(self, db: Session) -> NotificationSummary:
        """
        Send daily task reminder emails to assignees

        Returns:
            NotificationSummary with statistics about sent emails
        """
        # Get tasks that need reminder emails
        tasks = self.get_tasks_for_daily_reminder(db)

        total_tasks = len(tasks)
        emails_sent = 0
        emails_failed = 0
        failed_tasks = []

        for task in tasks:
            try:
                # Validate email address
                assignee_email = task.get("assignee_email")
                if not assignee_email:
                    raise BadRequestException("Assignee email not found")

                # Send email
                success = self.email_service.send_task_reminder_email(
                    to_email=assignee_email,
                    task_data=task
                )

                if success:
                    emails_sent += 1
                else:
                    emails_failed += 1
                    failed_tasks.append({
                        "task_id": task["tsk_id"],
                        "task_code": task["tsk_code"],
                        "assignee_email": assignee_email,
                        "error": "Failed to send email"
                    })

            except Exception as e:
                emails_failed += 1
                error_message = str(e)

                failed_tasks.append({
                    "task_id": task["tsk_id"],
                    "task_code": task["tsk_code"],
                    "assignee_email": task.get("assignee_email", "unknown"),
                    "error": error_message
                })

        return NotificationSummary(
            total_tasks=total_tasks,
            emails_sent=emails_sent,
            emails_failed=emails_failed,
            failed_tasks=failed_tasks
        )
