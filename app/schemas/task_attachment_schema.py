"""
Task Attachment Schema
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator


class TaskAttachmentBase(BaseModel):
    ta_tsk_id: int
    ta_file_name: str
    ta_file_path: str
    ta_file_size: Optional[int] = None
    ta_file_type: Optional[str] = None


class TaskAttachmentCreate(TaskAttachmentBase):
    pass


class TaskAttachmentUpdate(BaseModel):
    ta_tsk_id: Optional[int] = None
    ta_file_name: Optional[str] = None
    ta_file_path: Optional[str] = None
    ta_file_size: Optional[int] = None
    ta_file_type: Optional[str] = None


class TaskAttachmentInDB(TaskAttachmentBase):
    model_config = ConfigDict(from_attributes=True)

    ta_id: int
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


class TaskAttachment(TaskAttachmentInDB):
    pass
