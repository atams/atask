"""
Task Comment Service
Business logic layer with role-based permission validation
"""
from typing import List
from sqlalchemy.orm import Session

from app.repositories.task_comment_repository import TaskCommentRepository
from app.schemas.task_comment_schema import TaskCommentCreate, TaskCommentUpdate, TaskComment
from atams.exceptions import NotFoundException, ForbiddenException


class TaskCommentService:
    def __init__(self):
        self.repository = TaskCommentRepository()

    def get_task_comment(
        self,
        db: Session,
        tc_id: int,
        current_user_role_level: int,
        current_user_id: int
    ) -> TaskComment:
        """Get single task comment by ID"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to view task comment")

        db_task_comment = self.repository.get(db, tc_id)
        if not db_task_comment:
            raise NotFoundException(f"Task comment with ID {tc_id} not found")

        return TaskComment.model_validate(db_task_comment)

    def get_task_comments(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        current_user_role_level: int = 0
    ) -> List[TaskComment]:
        """Get list of task comments with pagination"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to list task comments")

        db_task_comments = self.repository.get_multi(db, skip=skip, limit=limit)
        return [TaskComment.model_validate(tc) for tc in db_task_comments]

    def create_task_comment(
        self,
        db: Session,
        task_comment: TaskCommentCreate,
        current_user_role_level: int,
        current_user_id: int
    ) -> TaskComment:
        """Create new task comment"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to create task comment")

        # Add created_by
        data = task_comment.model_dump()
        data["created_by"] = str(current_user_id)

        db_task_comment = self.repository.create(db, data)
        return TaskComment.model_validate(db_task_comment)

    def update_task_comment(
        self,
        db: Session,
        tc_id: int,
        task_comment: TaskCommentUpdate,
        current_user_role_level: int,
        current_user_id: int
    ) -> TaskComment:
        """Update existing task comment"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to update task comment")

        db_task_comment = self.repository.get(db, tc_id)
        if not db_task_comment:
            raise NotFoundException(f"Task comment with ID {tc_id} not found")

        update_data = task_comment.model_dump(exclude_unset=True)
        update_data["updated_by"] = str(current_user_id)

        db_task_comment = self.repository.update(db, db_task_comment, update_data)
        return TaskComment.model_validate(db_task_comment)

    def delete_task_comment(
        self,
        db: Session,
        tc_id: int,
        current_user_role_level: int
    ) -> None:
        """Delete task comment"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to delete task comment")

        deleted = self.repository.delete(db, tc_id)
        if not deleted:
            raise NotFoundException(f"Task comment with ID {tc_id} not found")

    def get_total_task_comments(self, db: Session) -> int:
        """Get total count of task comments"""
        return self.repository.count(db)
