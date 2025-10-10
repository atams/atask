from fastapi import APIRouter
from app.api.v1.endpoints import (
    master_status,
    master_priority,
    master_task_type,
    project,
    task,
    task_comment,
    task_attachment,
    task_history,
    label,
    task_label,
    task_watcher,
    users
)

api_router = APIRouter()

# Master Data Endpoints
api_router.include_router(
    master_status.router,
    prefix="/master-statuses",
    tags=["Master Statuses"]
)
api_router.include_router(
    master_priority.router,
    prefix="/master-priorities",
    tags=["Master Priorities"]
)
api_router.include_router(
    master_task_type.router,
    prefix="/master-task-types",
    tags=["Master Task Types"]
)

# Core Endpoints
api_router.include_router(
    project.router,
    prefix="/projects",
    tags=["Projects"]
)
api_router.include_router(
    task.router,
    prefix="/tasks",
    tags=["Tasks"]
)

# Task Related Endpoints
api_router.include_router(
    task_comment.router,
    prefix="/comments",
    tags=["Task Comments"]
)
api_router.include_router(
    task_attachment.router,
    prefix="/attachments",
    tags=["Task Attachments"]
)
api_router.include_router(
    task_history.router,
    prefix="/history",
    tags=["Task History"]
)

# Label Endpoints
api_router.include_router(
    label.router,
    prefix="/labels",
    tags=["Labels"]
)
api_router.include_router(
    task_label.router,
    prefix="/task-labels",
    tags=["Task Labels"]
)

# Watcher Endpoints
api_router.include_router(
    task_watcher.router,
    prefix="/watchers",
    tags=["Task Watchers"]
)

# User Endpoints
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)
