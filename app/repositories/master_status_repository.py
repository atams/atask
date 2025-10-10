"""
Master Status Repository
"""
from atams.db import BaseRepository
from app.models.master_status import MasterStatus


class MasterStatusRepository(BaseRepository[MasterStatus]):
    def __init__(self):
        super().__init__(MasterStatus)
