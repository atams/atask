"""
Master Status Model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from atams.db import Base


class MasterStatus(Base):
    """Master Status model for atask schema - Table: atask.master_status"""
    __tablename__ = "master_status"
    __table_args__ = {"schema": "atask"}

    ms_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ms_code = Column(String(50), nullable=False, unique=True)
    ms_name = Column(String(100), nullable=False)
    ms_description = Column(Text, nullable=True)
    ms_is_active = Column(Boolean, default=True, nullable=False)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
