"""
Task Attachment Service
Business logic layer with role-based permission validation
"""
from typing import List
from sqlalchemy.orm import Session

from app.repositories.task_attachment_repository import TaskAttachmentRepository
from app.schemas.task_attachment_schema import TaskAttachmentCreate, TaskAttachmentUpdate, TaskAttachment
from atams.exceptions import NotFoundException, ForbiddenException


class TaskAttachmentService:
    def __init__(self):
        self.repository = TaskAttachmentRepository()

    def get_task_attachment(
        self,
        db: Session,
        ta_id: int,
        current_user_role_level: int,
        current_user_id: int
    ) -> TaskAttachment:
        """Get single task attachment by ID"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to view task attachment")

        db_task_attachment = self.repository.get(db, ta_id)
        if not db_task_attachment:
            raise NotFoundException(f"Task attachment with ID {ta_id} not found")

        return TaskAttachment.model_validate(db_task_attachment)

    def get_task_attachments(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        current_user_role_level: int = 0
    ) -> List[TaskAttachment]:
        """Get list of task attachments with pagination"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to list task attachments")

        db_task_attachments = self.repository.get_multi(db, skip=skip, limit=limit)
        return [TaskAttachment.model_validate(ta) for ta in db_task_attachments]

    def create_task_attachment(
        self,
        db: Session,
        task_attachment: TaskAttachmentCreate,
        current_user_role_level: int,
        current_user_id: int
    ) -> TaskAttachment:
        """Create new task attachment"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to create task attachment")

        # Add created_by
        data = task_attachment.model_dump()
        data["created_by"] = str(current_user_id)

        db_task_attachment = self.repository.create(db, data)
        return TaskAttachment.model_validate(db_task_attachment)

    def update_task_attachment(
        self,
        db: Session,
        ta_id: int,
        task_attachment: TaskAttachmentUpdate,
        current_user_role_level: int,
        current_user_id: int
    ) -> TaskAttachment:
        """Update existing task attachment"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to update task attachment")

        db_task_attachment = self.repository.get(db, ta_id)
        if not db_task_attachment:
            raise NotFoundException(f"Task attachment with ID {ta_id} not found")

        update_data = task_attachment.model_dump(exclude_unset=True)
        update_data["updated_by"] = str(current_user_id)

        db_task_attachment = self.repository.update(db, db_task_attachment, update_data)
        return TaskAttachment.model_validate(db_task_attachment)

    def delete_task_attachment(
        self,
        db: Session,
        ta_id: int,
        current_user_role_level: int
    ) -> None:
        """Delete task attachment"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to delete task attachment")

        deleted = self.repository.delete(db, ta_id)
        if not deleted:
            raise NotFoundException(f"Task attachment with ID {ta_id} not found")

    def get_total_task_attachments(self, db: Session) -> int:
        """Get total count of task attachments"""
        return self.repository.count(db)
