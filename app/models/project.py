"""
Project Model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Text, BigInteger
from sqlalchemy.sql import func
from atams.db import Base


class Project(Base):
    """Project model for atask schema - Table: atask.project"""
    __tablename__ = "project"
    __table_args__ = {"schema": "atask"}

    prj_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    prj_code = Column(String(50), nullable=False, unique=True)
    prj_name = Column(String(255), nullable=False)
    prj_description = Column(Text, nullable=True)
    prj_start_date = Column(Date, nullable=True)
    prj_end_date = Column(Date, nullable=True)
    prj_u_id = Column(BigInteger, nullable=False)
    prj_is_active = Column(Boolean, default=True, nullable=False)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_by = Column(String(100), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
