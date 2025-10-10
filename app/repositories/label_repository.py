"""
Label Repository
"""
from atams.db import BaseRepository
from app.models.label import Label


class LabelRepository(BaseRepository[Label]):
    def __init__(self):
        super().__init__(Label)
