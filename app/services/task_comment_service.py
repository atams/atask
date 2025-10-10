"""
Task Comment Service
Business logic layer with role-based permission validation
"""
from typing import List
from sqlalchemy.orm import Session

from app.repositories.task_comment_repository import TaskCommentRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.schemas.task_comment_schema import TaskCommentCreate, TaskCommentUpdate, TaskComment
from atams.exceptions import NotFoundException, ForbiddenException


class TaskCommentService:
    def __init__(self):
        self.repository = TaskCommentRepository()
        self.task_repository = TaskRepository()
        self.user_repository = UserRepository()

    def _populate_comment_joins(self, db: Session, db_comment) -> dict:
        """Populate task comment with joined data from related tables"""
        comment_dict = TaskComment.model_validate(db_comment).model_dump()

        # Get task title
        if db_comment.tc_tsk_id:
            task = self.task_repository.get(db, db_comment.tc_tsk_id)
            if task:
                comment_dict["tc_task_title"] = task.tsk_title

        # Get user name and email
        if db_comment.tc_u_id:
            user = self.user_repository.get_user_by_id(db, db_comment.tc_u_id)
            if user:
                comment_dict["tc_user_name"] = user.get("u_full_name")
                comment_dict["tc_user_email"] = user.get("u_email")

        return comment_dict

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

        # Populate joined data
        comment_dict = self._populate_comment_joins(db, db_task_comment)
        return TaskComment.model_validate(comment_dict)

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

        # Populate joined data for each task comment
        comments = []
        for db_comment in db_task_comments:
            comment_dict = self._populate_comment_joins(db, db_comment)
            comments.append(TaskComment.model_validate(comment_dict))

        return comments

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

        # Populate joined data
        comment_dict = self._populate_comment_joins(db, db_task_comment)
        return TaskComment.model_validate(comment_dict)

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
