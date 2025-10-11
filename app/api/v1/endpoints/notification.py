"""
Notification Endpoints
Handles daily task reminder notifications
"""
from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.task_notification_service import TaskNotificationService
from app.schemas.common import DataResponse
from app.core.config import settings
from atams.exceptions import ForbiddenException, BadRequestException

router = APIRouter()
notification_service = TaskNotificationService()


def verify_cron_api_key(x_api_key: str = Header(None)):
    """Verify CRON_API_KEY for scheduled endpoints"""
    if not settings.CRON_API_KEY:
        raise BadRequestException(
            "CRON_API_KEY is not configured. Please set it in environment variables."
        )

    if not x_api_key or x_api_key != settings.CRON_API_KEY:
        raise ForbiddenException(
            "Invalid or missing API key. Access denied."
        )
    return True


@router.post(
    "/send-daily-reminders",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_cron_api_key)]
)
async def send_daily_reminders(
    db: Session = Depends(get_db)
):
    """
    Send daily task reminder emails to assignees

    **Security:** Requires valid CRON_API_KEY in X-Api-Key header

    **Schedule:** This endpoint should be triggered daily at 9:00 AM via GitHub Actions

    **Logic:**
    - Finds all tasks where tsk_start_date = today
    - Has tsk_assignee_u_id (assigned user)
    - Sends email reminder to assignee

    **Returns:**
    - Summary of email sending operation
    - Total tasks processed
    - Success/failure counts
    - Failed task details
    """
    summary = notification_service.send_daily_reminders(db)

    return DataResponse(
        success=True,
        message=f"Daily reminders processed: {summary.emails_sent} sent, {summary.emails_failed} failed",
        data=summary.to_dict()
    )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK
)
async def notification_health_check():
    """
    Health check endpoint for notification service

    **No authentication required** - Used for monitoring

    **Returns:**
    - Service status
    - Email configuration status
    """
    email_configured = all([
        settings.MAIL_SERVER,
        settings.MAIL_USERNAME,
        settings.MAIL_PASSWORD,
        settings.MAIL_FROM
    ])

    cron_configured = bool(settings.CRON_API_KEY)

    return {
        "status": "ok",
        "email_configured": email_configured,
        "cron_api_key_configured": cron_configured
    }
