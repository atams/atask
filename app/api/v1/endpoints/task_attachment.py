"""
Task Attachment Endpoints
Note: Most endpoints have been moved to /api/v1/tasks/{tsk_id}/attachments
This file is kept for backwards compatibility but may be removed in future versions
"""
from fastapi import APIRouter

router = APIRouter()

# All attachment endpoints have been moved to:
# - POST /api/v1/tasks/{tsk_id}/attachments - Upload attachments (supports bulk)
# - GET /api/v1/tasks/{tsk_id}/attachments - Get all attachments for a task
# - DELETE /api/v1/tasks/{tsk_id}/attachments/{ta_id} - Delete specific attachment
