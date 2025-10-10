"""
Task Watcher Schema
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator


class TaskWatcherBase(BaseModel):
    tw_tsk_id: int
    tw_u_id: int


class TaskWatcherCreate(TaskWatcherBase):
    pass


class TaskWatcherUpdate(BaseModel):
    tw_tsk_id: Optional[int] = None
    tw_u_id: Optional[int] = None


class TaskWatcherInDB(TaskWatcherBase):
    model_config = ConfigDict(from_attributes=True)

    tw_id: int
    created_by: str
    created_at: datetime
    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None

    @field_validator('created_at', 'updated_at', mode='before')
    @classmethod
    def fix_datetime_timezone(cls, v):
        if v == '' or v is None:
            return None
        if isinstance(v, str):
            import re
            pattern = r'([+-]\d{2})$'
            match = re.search(pattern, v)
            if match:
                v = v + ':00'
        return v


class TaskWatcher(TaskWatcherInDB):
    pass
