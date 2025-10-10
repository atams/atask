"""
Task Attachment Repository
"""
from typing import List
from sqlalchemy.orm import Session
from atams.db import BaseRepository
from app.models.task_attachment import TaskAttachment


class TaskAttachmentRepository(BaseRepository[TaskAttachment]):
    def __init__(self):
        super().__init__(TaskAttachment)

    def get_by_task_id(self, db: Session, task_id: int) -> List[TaskAttachment]:
        """Get all attachments for a specific task"""
        return db.query(TaskAttachment).filter(
            TaskAttachment.ta_tsk_id == task_id
        ).all()

    def count_by_task_id(self, db: Session, task_id: int) -> int:
        """Count attachments for a specific task"""
        return db.query(TaskAttachment).filter(
            TaskAttachment.ta_tsk_id == task_id
        ).count()
