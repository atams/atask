"""
Task Attachment Model
"""
from sqlalchemy import Column, Integer, String, DateTime, BigInteger, ForeignKey, Text
from sqlalchemy.sql import func
from atams.db import Base


class TaskAttachment(Base):
    """Task Attachment model for atask schema - Table: atask.task_attachment"""
    __tablename__ = "task_attachment"
    __table_args__ = {"schema": "atask"}

    ta_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ta_tsk_id = Column(Integer, ForeignKey("atask.task.tsk_id", ondelete="CASCADE"), nullable=False)
    ta_file_name = Column(String(255), nullable=False)
    ta_file_path = Column(Text, nullable=False)
    ta_file_size = Column(BigInteger, nullable=True)
    ta_file_type = Column(String(100), nullable=True)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_by = Column(String(100), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
