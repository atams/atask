"""
Master Priority Schema
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator


class MasterPriorityBase(BaseModel):
    mp_code: str
    mp_name: str
    mp_level: int
    mp_color: Optional[str] = None
    mp_is_active: bool = True


class MasterPriorityCreate(MasterPriorityBase):
    pass


class MasterPriorityUpdate(BaseModel):
    mp_code: Optional[str] = None
    mp_name: Optional[str] = None
    mp_level: Optional[int] = None
    mp_color: Optional[str] = None
    mp_is_active: Optional[bool] = None


class MasterPriorityInDB(MasterPriorityBase):
    model_config = ConfigDict(from_attributes=True)

    mp_id: int
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


class MasterPriority(MasterPriorityInDB):
    pass
