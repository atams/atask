"""
Master Priority Repository
"""
from atams.db import BaseRepository
from app.models.master_priority import MasterPriority


class MasterPriorityRepository(BaseRepository[MasterPriority]):
    def __init__(self):
        super().__init__(MasterPriority)
