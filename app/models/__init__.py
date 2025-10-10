"""
Models package
Import all models here for Alembic autogenerate
"""
from app.models.master_status import MasterStatus
from app.models.master_priority import MasterPriority
from app.models.master_task_type import MasterTaskType
from app.models.project import Project
from app.models.task import Task
from app.models.task_comment import TaskComment
from app.models.task_attachment import TaskAttachment
from app.models.task_history import TaskHistory
from app.models.label import Label
from app.models.task_label import TaskLabel
from app.models.task_watcher import TaskWatcher

__all__ = [
    "MasterStatus",
    "MasterPriority",
    "MasterTaskType",
    "Project",
    "Task",
    "TaskComment",
    "TaskAttachment",
    "TaskHistory",
    "Label",
    "TaskLabel",
    "TaskWatcher"
]
