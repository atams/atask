"""
Task Comment Repository
"""
from atams.db import BaseRepository
from app.models.task_comment import TaskComment


class TaskCommentRepository(BaseRepository[TaskComment]):
    def __init__(self):
        super().__init__(TaskComment)
