"""
Master Task Type Model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from atams.db import Base


class MasterTaskType(Base):
    """Master Task Type model for atask schema - Table: atask.master_task_type"""
    __tablename__ = "master_task_type"
    __table_args__ = {"schema": "atask"}

    mtt_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    mtt_code = Column(String(50), nullable=False, unique=True)
    mtt_name = Column(String(100), nullable=False)
    mtt_description = Column(Text, nullable=True)
    mtt_is_active = Column(Boolean, default=True, nullable=False)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
