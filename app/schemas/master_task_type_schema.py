"""
Master Task Type Schema
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator


class MasterTaskTypeBase(BaseModel):
    mtt_code: str
    mtt_name: str
    mtt_description: Optional[str] = None
    mtt_is_active: bool = True


class MasterTaskTypeCreate(MasterTaskTypeBase):
    pass


class MasterTaskTypeUpdate(BaseModel):
    mtt_code: Optional[str] = None
    mtt_name: Optional[str] = None
    mtt_description: Optional[str] = None
    mtt_is_active: Optional[bool] = None


class MasterTaskTypeInDB(MasterTaskTypeBase):
    model_config = ConfigDict(from_attributes=True)

    mtt_id: int
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


class MasterTaskType(MasterTaskTypeInDB):
    pass
