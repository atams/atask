"""
Task History Repository
"""
from atams.db import BaseRepository
from app.models.task_history import TaskHistory


class TaskHistoryRepository(BaseRepository[TaskHistory]):
    def __init__(self):
        super().__init__(TaskHistory)
