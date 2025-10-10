"""
Task Attachment Repository
"""
from atams.db import BaseRepository
from app.models.task_attachment import TaskAttachment


class TaskAttachmentRepository(BaseRepository[TaskAttachment]):
    def __init__(self):
        super().__init__(TaskAttachment)
