"""
Task Model
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, BigInteger, ForeignKey, Numeric
from sqlalchemy.sql import func
from atams.db import Base


class Task(Base):
    """Task model for atask schema - Table: atask.task"""
    __tablename__ = "task"
    __table_args__ = {"schema": "atask"}

    tsk_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tsk_code = Column(String(50), nullable=False, unique=True)
    tsk_title = Column(String(255), nullable=False)
    tsk_description = Column(Text, nullable=True)
    tsk_prj_id = Column(Integer, ForeignKey("atask.project.prj_id"), nullable=True)
    tsk_ms_id = Column(Integer, ForeignKey("atask.master_status.ms_id"), nullable=False)
    tsk_mp_id = Column(Integer, ForeignKey("atask.master_priority.mp_id"), nullable=False)
    tsk_mtt_id = Column(Integer, ForeignKey("atask.master_task_type.mtt_id"), nullable=False)
    tsk_assignee_u_id = Column(BigInteger, nullable=True)
    tsk_reporter_u_id = Column(BigInteger, nullable=False)
    tsk_start_date = Column(DateTime(timezone=True), nullable=True)
    tsk_due_date = Column(DateTime(timezone=True), nullable=True)
    tsk_duration = Column(Numeric(10, 2), nullable=True)
    tsk_parent_tsk_id = Column(Integer, ForeignKey("atask.task.tsk_id"), nullable=True)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_by = Column(String(100), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
