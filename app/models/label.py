"""
Label Model
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from atams.db import Base


class Label(Base):
    """Label model for atask schema - Table: atask.label"""
    __tablename__ = "label"
    __table_args__ = {"schema": "atask"}

    lbl_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    lbl_name = Column(String(100), nullable=False, unique=True)
    lbl_color = Column(String(20), nullable=True)
    lbl_description = Column(Text, nullable=True)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_by = Column(String(100), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
