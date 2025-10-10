"""
Task Label Service
Business logic layer with role-based permission validation
"""
from typing import List
from sqlalchemy.orm import Session

from app.repositories.task_label_repository import TaskLabelRepository
from app.schemas.task_label_schema import TaskLabelCreate, TaskLabelUpdate, TaskLabel
from atams.exceptions import NotFoundException, ForbiddenException


class TaskLabelService:
    def __init__(self):
        self.repository = TaskLabelRepository()

    def get_task_label(
        self,
        db: Session,
        tl_id: int,
        current_user_role_level: int,
        current_user_id: int
    ) -> TaskLabel:
        """Get single task label by ID"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to view task label")

        db_task_label = self.repository.get(db, tl_id)
        if not db_task_label:
            raise NotFoundException(f"Task label with ID {tl_id} not found")

        return TaskLabel.model_validate(db_task_label)

    def get_task_labels(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        current_user_role_level: int = 0
    ) -> List[TaskLabel]:
        """Get list of task labels with pagination"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to list task labels")

        db_task_labels = self.repository.get_multi(db, skip=skip, limit=limit)
        return [TaskLabel.model_validate(tl) for tl in db_task_labels]

    def create_task_label(
        self,
        db: Session,
        task_label: TaskLabelCreate,
        current_user_role_level: int,
        current_user_id: int
    ) -> TaskLabel:
        """Create new task label"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to create task label")

        # Add created_by
        data = task_label.model_dump()
        data["created_by"] = str(current_user_id)

        db_task_label = self.repository.create(db, data)
        return TaskLabel.model_validate(db_task_label)

    def update_task_label(
        self,
        db: Session,
        tl_id: int,
        task_label: TaskLabelUpdate,
        current_user_role_level: int,
        current_user_id: int
    ) -> TaskLabel:
        """Update existing task label"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to update task label")

        db_task_label = self.repository.get(db, tl_id)
        if not db_task_label:
            raise NotFoundException(f"Task label with ID {tl_id} not found")

        update_data = task_label.model_dump(exclude_unset=True)
        update_data["updated_by"] = str(current_user_id)

        db_task_label = self.repository.update(db, db_task_label, update_data)
        return TaskLabel.model_validate(db_task_label)

    def delete_task_label(
        self,
        db: Session,
        tl_id: int,
        current_user_role_level: int
    ) -> None:
        """Delete task label"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to delete task label")

        deleted = self.repository.delete(db, tl_id)
        if not deleted:
            raise NotFoundException(f"Task label with ID {tl_id} not found")

    def get_total_task_labels(self, db: Session) -> int:
        """Get total count of task labels"""
        return self.repository.count(db)
