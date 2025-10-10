"""
Master Status Schema
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator


class MasterStatusBase(BaseModel):
    ms_code: str
    ms_name: str
    ms_description: Optional[str] = None
    ms_is_active: bool = True


class MasterStatusCreate(MasterStatusBase):
    pass


class MasterStatusUpdate(BaseModel):
    ms_code: Optional[str] = None
    ms_name: Optional[str] = None
    ms_description: Optional[str] = None
    ms_is_active: Optional[bool] = None


class MasterStatusInDB(MasterStatusBase):
    model_config = ConfigDict(from_attributes=True)

    ms_id: int
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


class MasterStatus(MasterStatusInDB):
    pass
