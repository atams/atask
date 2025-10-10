"""
Task History Schema
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator


class TaskHistoryBase(BaseModel):
    th_tsk_id: int
    th_field_name: str
    th_old_value: Optional[str] = None
    th_new_value: Optional[str] = None
    th_u_id: int


class TaskHistoryCreate(TaskHistoryBase):
    pass


class TaskHistoryUpdate(BaseModel):
    th_tsk_id: Optional[int] = None
    th_field_name: Optional[str] = None
    th_old_value: Optional[str] = None
    th_new_value: Optional[str] = None
    th_u_id: Optional[int] = None


class TaskHistoryInDB(TaskHistoryBase):
    model_config = ConfigDict(from_attributes=True)

    th_id: int
    created_by: str
    created_at: datetime

    @field_validator('created_at', mode='before')
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


class TaskHistory(TaskHistoryInDB):
    # Additional fields from joins
    th_task_title: Optional[str] = None
    th_user_name: Optional[str] = None
