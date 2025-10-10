"""
Project Schema
"""
from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict, field_validator


class ProjectBase(BaseModel):
    prj_code: str
    prj_name: str
    prj_description: Optional[str] = None
    prj_start_date: Optional[date] = None
    prj_end_date: Optional[date] = None
    prj_u_id: int
    prj_is_active: bool = True


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    prj_code: Optional[str] = None
    prj_name: Optional[str] = None
    prj_description: Optional[str] = None
    prj_start_date: Optional[date] = None
    prj_end_date: Optional[date] = None
    prj_u_id: Optional[int] = None
    prj_is_active: Optional[bool] = None


class ProjectInDB(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    prj_id: int
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


class Project(ProjectInDB):
    pass
