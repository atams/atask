"""
Label Schema
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator


class LabelBase(BaseModel):
    lbl_name: str
    lbl_color: Optional[str] = None
    lbl_description: Optional[str] = None


class LabelCreate(LabelBase):
    pass


class LabelUpdate(BaseModel):
    lbl_name: Optional[str] = None
    lbl_color: Optional[str] = None
    lbl_description: Optional[str] = None


class LabelInDB(LabelBase):
    model_config = ConfigDict(from_attributes=True)

    lbl_id: int
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


class Label(LabelInDB):
    pass
