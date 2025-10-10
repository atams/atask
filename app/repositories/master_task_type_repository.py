"""
Master Task Type Repository
"""
from atams.db import BaseRepository
from app.models.master_task_type import MasterTaskType


class MasterTaskTypeRepository(BaseRepository[MasterTaskType]):
    def __init__(self):
        super().__init__(MasterTaskType)
