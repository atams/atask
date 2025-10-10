"""
Task Label Schema
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator


class TaskLabelBase(BaseModel):
    tl_tsk_id: int
    tl_lbl_id: int


class TaskLabelCreate(TaskLabelBase):
    pass


class TaskLabelUpdate(BaseModel):
    tl_tsk_id: Optional[int] = None
    tl_lbl_id: Optional[int] = None


class TaskLabelInDB(TaskLabelBase):
    model_config = ConfigDict(from_attributes=True)

    tl_id: int
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


class TaskLabel(TaskLabelInDB):
    pass
