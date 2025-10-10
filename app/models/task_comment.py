"""
Task Comment Model
"""
from sqlalchemy import Column, Integer, Text, DateTime, BigInteger, ForeignKey, String
from sqlalchemy.sql import func
from atams.db import Base


class TaskComment(Base):
    """Task Comment model for atask schema - Table: atask.task_comment"""
    __tablename__ = "task_comment"
    __table_args__ = {"schema": "atask"}

    tc_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tc_tsk_id = Column(Integer, ForeignKey("atask.task.tsk_id", ondelete="CASCADE"), nullable=False)
    tc_u_id = Column(BigInteger, nullable=False)
    tc_comment = Column(Text, nullable=False)
    tc_parent_tc_id = Column(Integer, ForeignKey("atask.task_comment.tc_id"), nullable=True)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_by = Column(String(100), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
