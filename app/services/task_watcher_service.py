"""
Task Watcher Service
Business logic layer with role-based permission validation
"""
from typing import List
from sqlalchemy.orm import Session

from app.repositories.task_watcher_repository import TaskWatcherRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.schemas.task_watcher_schema import TaskWatcherCreate, TaskWatcherUpdate, TaskWatcher
from atams.exceptions import NotFoundException, ForbiddenException, BadRequestException


class TaskWatcherService:
    def __init__(self):
        self.repository = TaskWatcherRepository()
        self.task_repository = TaskRepository()
        self.user_repository = UserRepository()

    def _populate_watcher_joins(self, db: Session, db_watcher) -> dict:
        """Populate task watcher with joined data from related tables"""
        watcher_dict = TaskWatcher.model_validate(db_watcher).model_dump()

        # Get task title
        if db_watcher.tw_tsk_id:
            task = self.task_repository.get(db, db_watcher.tw_tsk_id)
            if task:
                watcher_dict["tw_task_title"] = task.tsk_title

        # Get user name and email
        if db_watcher.tw_u_id:
            user = self.user_repository.get_user_by_id(db, db_watcher.tw_u_id)
            if user:
                watcher_dict["tw_user_name"] = user.get("u_full_name")
                watcher_dict["tw_user_email"] = user.get("u_email")

        return watcher_dict

    def get_task_watcher(
        self,
        db: Session,
        tw_id: int,
        current_user_role_level: int,
        current_user_id: int
    ) -> TaskWatcher:
        """Get single task watcher by ID"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to view task watcher")

        db_task_watcher = self.repository.get(db, tw_id)
        if not db_task_watcher:
            raise NotFoundException(f"Task watcher with ID {tw_id} not found")

        return TaskWatcher.model_validate(db_task_watcher)

    def get_task_watchers(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        current_user_role_level: int = 0
    ) -> List[TaskWatcher]:
        """Get list of task watchers with pagination"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to list task watchers")

        db_task_watchers = self.repository.get_multi(db, skip=skip, limit=limit)
        return [TaskWatcher.model_validate(tw) for tw in db_task_watchers]

    def create_task_watcher(
        self,
        db: Session,
        task_watcher: TaskWatcherCreate,
        current_user_role_level: int,
        current_user_id: int
    ) -> TaskWatcher:
        """Create new task watcher"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to create task watcher")

        # Add created_by
        data = task_watcher.model_dump()
        data["created_by"] = str(current_user_id)

        db_task_watcher = self.repository.create(db, data)
        return TaskWatcher.model_validate(db_task_watcher)

    def update_task_watcher(
        self,
        db: Session,
        tw_id: int,
        task_watcher: TaskWatcherUpdate,
        current_user_role_level: int,
        current_user_id: int
    ) -> TaskWatcher:
        """Update existing task watcher"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to update task watcher")

        db_task_watcher = self.repository.get(db, tw_id)
        if not db_task_watcher:
            raise NotFoundException(f"Task watcher with ID {tw_id} not found")

        update_data = task_watcher.model_dump(exclude_unset=True)
        update_data["updated_by"] = str(current_user_id)

        db_task_watcher = self.repository.update(db, db_task_watcher, update_data)
        return TaskWatcher.model_validate(db_task_watcher)

    def delete_task_watcher(
        self,
        db: Session,
        tw_id: int,
        current_user_role_level: int
    ) -> None:
        """Delete task watcher"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to delete task watcher")

        deleted = self.repository.delete(db, tw_id)
        if not deleted:
            raise NotFoundException(f"Task watcher with ID {tw_id} not found")

    def get_total_task_watchers(self, db: Session) -> int:
        """Get total count of task watchers"""
        return self.repository.count(db)
