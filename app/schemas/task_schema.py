"""
Task Schema
"""
from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, field_validator


class TaskBase(BaseModel):
    tsk_code: str
    tsk_title: str
    tsk_description: Optional[str] = None
    tsk_prj_id: Optional[int] = None
    tsk_ms_id: int
    tsk_mp_id: int
    tsk_mtt_id: int
    tsk_assignee_u_id: Optional[int] = None
    tsk_reporter_u_id: int
    tsk_start_date: Optional[datetime] = None
    tsk_due_date: Optional[datetime] = None
    tsk_duration: Optional[Decimal] = None  # Duration in hours (auto-calculated, read-only)
    tsk_parent_tsk_id: Optional[int] = None
    tsk_thumbnail: Optional[str] = None


class TaskCreate(BaseModel):
    """Schema for creating a new task. tsk_code is auto-generated."""
    tsk_title: str
    tsk_description: Optional[str] = None
    tsk_prj_id: Optional[int] = None
    tsk_ms_id: int
    tsk_mp_id: int
    tsk_mtt_id: int
    tsk_assignee_u_id: Optional[int] = None
    tsk_reporter_u_id: int
    tsk_start_date: Optional[datetime] = None
    # tsk_due_date removed - only assignee can set this
    # tsk_duration removed - auto-calculated from dates
    tsk_parent_tsk_id: Optional[int] = None


class TaskUpdate(BaseModel):
    """Schema for updating a task. tsk_code cannot be updated as it's auto-generated."""
    tsk_title: Optional[str] = None
    tsk_description: Optional[str] = None
    tsk_prj_id: Optional[int] = None
    tsk_ms_id: Optional[int] = None
    tsk_mp_id: Optional[int] = None
    tsk_mtt_id: Optional[int] = None
    tsk_assignee_u_id: Optional[int] = None
    tsk_reporter_u_id: Optional[int] = None
    tsk_start_date: Optional[datetime] = None
    tsk_due_date: Optional[datetime] = None  # Only assignee can update this field
    # tsk_duration removed - auto-calculated and read-only
    tsk_parent_tsk_id: Optional[int] = None


class TaskInDB(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    tsk_id: int
    created_by: str
    created_at: datetime
    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None

    @field_validator('tsk_start_date', 'tsk_due_date', 'created_at', 'updated_at', mode='before')
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


class Task(TaskInDB):
    # Additional fields from joins
    tsk_project_name: Optional[str] = None
    tsk_status_name: Optional[str] = None
    tsk_priority_name: Optional[str] = None
    tsk_priority_color: Optional[str] = None
    tsk_type_name: Optional[str] = None
    tsk_assignee_name: Optional[str] = None
    tsk_reporter_name: Optional[str] = None
    tsk_thumbnail_url: Optional[str] = None