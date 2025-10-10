"""
Task History Model
"""
from sqlalchemy import Column, Integer, String, DateTime, BigInteger, ForeignKey, Text
from sqlalchemy.sql import func
from atams.db import Base


class TaskHistory(Base):
    """Task History model for atask schema - Table: atask.task_history"""
    __tablename__ = "task_history"
    __table_args__ = {"schema": "atask"}

    th_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    th_tsk_id = Column(Integer, ForeignKey("atask.task.tsk_id", ondelete="CASCADE"), nullable=False)
    th_field_name = Column(String(100), nullable=False)
    th_old_value = Column(Text, nullable=True)
    th_new_value = Column(Text, nullable=True)
    th_u_id = Column(BigInteger, nullable=False)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_by = Column(String(100), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
