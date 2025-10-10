"""
Task History Service
Business logic layer with role-based permission validation
"""
from typing import List
from sqlalchemy.orm import Session

from app.repositories.task_history_repository import TaskHistoryRepository
from app.schemas.task_history_schema import TaskHistoryCreate, TaskHistoryUpdate, TaskHistory
from atams.exceptions import NotFoundException, ForbiddenException


class TaskHistoryService:
    def __init__(self):
        self.repository = TaskHistoryRepository()

    def get_task_history(
        self,
        db: Session,
        th_id: int,
        current_user_role_level: int,
        current_user_id: int
    ) -> TaskHistory:
        """Get single task history by ID"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to view task history")

        db_task_history = self.repository.get(db, th_id)
        if not db_task_history:
            raise NotFoundException(f"Task history with ID {th_id} not found")

        return TaskHistory.model_validate(db_task_history)

    def get_task_histories(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        current_user_role_level: int = 0
    ) -> List[TaskHistory]:
        """Get list of task histories with pagination"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to list task histories")

        db_task_histories = self.repository.get_multi(db, skip=skip, limit=limit)
        return [TaskHistory.model_validate(th) for th in db_task_histories]

    def create_task_history(
        self,
        db: Session,
        task_history: TaskHistoryCreate,
        current_user_role_level: int,
        current_user_id: int
    ) -> TaskHistory:
        """Create new task history"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to create task history")

        # Add created_by
        data = task_history.model_dump()
        data["created_by"] = str(current_user_id)

        db_task_history = self.repository.create(db, data)
        return TaskHistory.model_validate(db_task_history)

    def update_task_history(
        self,
        db: Session,
        th_id: int,
        task_history: TaskHistoryUpdate,
        current_user_role_level: int,
        current_user_id: int
    ) -> TaskHistory:
        """Update existing task history"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to update task history")

        db_task_history = self.repository.get(db, th_id)
        if not db_task_history:
            raise NotFoundException(f"Task history with ID {th_id} not found")

        update_data = task_history.model_dump(exclude_unset=True)
        update_data["updated_by"] = str(current_user_id)

        db_task_history = self.repository.update(db, db_task_history, update_data)
        return TaskHistory.model_validate(db_task_history)

    def delete_task_history(
        self,
        db: Session,
        th_id: int,
        current_user_role_level: int
    ) -> None:
        """Delete task history"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to delete task history")

        deleted = self.repository.delete(db, th_id)
        if not deleted:
            raise NotFoundException(f"Task history with ID {th_id} not found")

    def get_total_task_histories(self, db: Session) -> int:
        """Get total count of task histories"""
        return self.repository.count(db)
