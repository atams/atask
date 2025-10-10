"""
Master Priority Model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from atams.db import Base


class MasterPriority(Base):
    """Master Priority model for atask schema - Table: atask.master_priority"""
    __tablename__ = "master_priority"
    __table_args__ = {"schema": "atask"}

    mp_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    mp_code = Column(String(50), nullable=False, unique=True)
    mp_name = Column(String(100), nullable=False)
    mp_level = Column(Integer, nullable=False)
    mp_color = Column(String(20), nullable=True)
    mp_is_active = Column(Boolean, default=True, nullable=False)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
