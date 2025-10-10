"""
Task Label Model
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from atams.db import Base


class TaskLabel(Base):
    """Task Label model for atask schema - Table: atask.task_label"""
    __tablename__ = "task_label"
    __table_args__ = (
        UniqueConstraint('tl_tsk_id', 'tl_lbl_id', name='uq_task_label'),
        {"schema": "atask"}
    )

    tl_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tl_tsk_id = Column(Integer, ForeignKey("atask.task.tsk_id", ondelete="CASCADE"), nullable=False)
    tl_lbl_id = Column(Integer, ForeignKey("atask.label.lbl_id", ondelete="CASCADE"), nullable=False)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_by = Column(String(100), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
