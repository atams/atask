"""
Task Comment Schema
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator


class TaskCommentBase(BaseModel):
    tc_tsk_id: int
    tc_u_id: int
    tc_comment: str
    tc_parent_tc_id: Optional[int] = None


class TaskCommentCreate(TaskCommentBase):
    pass


class TaskCommentUpdate(BaseModel):
    tc_tsk_id: Optional[int] = None
    tc_u_id: Optional[int] = None
    tc_comment: Optional[str] = None
    tc_parent_tc_id: Optional[int] = None


class TaskCommentInDB(TaskCommentBase):
    model_config = ConfigDict(from_attributes=True)

    tc_id: int
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


class TaskComment(TaskCommentInDB):
    pass
