"""
Task Watcher Model
"""
from sqlalchemy import Column, Integer, String, DateTime, BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from atams.db import Base


class TaskWatcher(Base):
    """Task Watcher model for atask schema - Table: atask.task_watcher"""
    __tablename__ = "task_watcher"
    __table_args__ = (
        UniqueConstraint('tw_tsk_id', 'tw_u_id', name='uq_task_watcher'),
        {"schema": "atask"}
    )

    tw_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tw_tsk_id = Column(Integer, ForeignKey("atask.task.tsk_id", ondelete="CASCADE"), nullable=False)
    tw_u_id = Column(BigInteger, nullable=False)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_by = Column(String(100), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
