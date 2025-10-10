"""
Task Label Repository
"""
from atams.db import BaseRepository
from app.models.task_label import TaskLabel


class TaskLabelRepository(BaseRepository[TaskLabel]):
    def __init__(self):
        super().__init__(TaskLabel)
