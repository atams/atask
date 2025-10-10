"""
Task Endpoints
Complete CRUD operations with Atlas SSO authentication
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status, File, UploadFile
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date

from app.db.session import get_db
from app.services.task_service import TaskService
from app.services.task_comment_service import TaskCommentService
from app.services.task_attachment_service import TaskAttachmentService
from app.services.task_history_service import TaskHistoryService
from app.services.task_label_service import TaskLabelService
from app.services.task_watcher_service import TaskWatcherService
from app.schemas.task_schema import Task, TaskCreate, TaskUpdate
from app.schemas.task_comment_schema import TaskComment, TaskCommentCreate
from app.schemas.task_attachment_schema import TaskAttachment, TaskAttachmentCreate
from app.schemas.task_history_schema import TaskHistory
from app.schemas.task_label_schema import TaskLabel, TaskLabelCreate
from app.schemas.task_watcher_schema import TaskWatcher, TaskWatcherCreate
from app.schemas.common import DataResponse, PaginationResponse
from app.api.deps import require_auth, require_min_role_level
from atams.encryption import encrypt_response_data
from app.core.config import settings

router = APIRouter()
task_service = TaskService()
task_comment_service = TaskCommentService()
task_attachment_service = TaskAttachmentService()
task_history_service = TaskHistoryService()
task_label_service = TaskLabelService()
task_watcher_service = TaskWatcherService()


# Request schemas for nested endpoints
class CommentCreateRequest(BaseModel):
    tc_comment: str
    tc_parent_tc_id: Optional[int] = None


class LabelAssignRequest(BaseModel):
    lbl_id: int


class WatcherAddRequest(BaseModel):
    u_id: int


class BulkUpdateStatusRequest(BaseModel):
    task_ids: List[int]
    ms_id: int


class AdvancedSearchRequest(BaseModel):
    keyword: Optional[str] = None
    project_ids: Optional[List[int]] = None
    status_ids: Optional[List[int]] = None
    priority_ids: Optional[List[int]] = None
    assignee_ids: Optional[List[int]] = None
    reporter_ids: Optional[List[int]] = None
    type_ids: Optional[List[int]] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    skip: int = 0
    limit: int = 100


@router.get(
    "/",
    response_model=PaginationResponse[Task],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def get_tasks(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Get list of tasks with pagination"""
    tasks = task_service.get_tasks(
        db,
        skip=skip,
        limit=limit,
        current_user_role_level=current_user["role_level"]
    )
    total = task_service.get_total_tasks(db)

    response = PaginationResponse(
        success=True,
        message="Tasks retrieved successfully",
        data=tasks,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

    return encrypt_response_data(response, settings)


@router.get(
    "/{tsk_id}",
    response_model=DataResponse[Task],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def get_task(
    tsk_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Get single task by ID"""
    task = task_service.get_task(
        db,
        tsk_id,
        current_user_role_level=current_user["role_level"],
        current_user_id=current_user["user_id"]
    )

    response = DataResponse(
        success=True,
        message="Task retrieved successfully",
        data=task
    )

    return encrypt_response_data(response, settings)


@router.post(
    "/",
    response_model=DataResponse[Task],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_min_role_level(10))]
)
async def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Create new task"""
    new_task = task_service.create_task(
        db,
        task,
        current_user_role_level=current_user["role_level"],
        current_user_id=current_user["user_id"]
    )

    return DataResponse(
        success=True,
        message="Task created successfully",
        data=new_task
    )


@router.put(
    "/{tsk_id}",
    response_model=DataResponse[Task],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def update_task(
    tsk_id: int,
    task: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Update existing task"""
    updated_task = task_service.update_task(
        db,
        tsk_id,
        task,
        current_user_role_level=current_user["role_level"],
        current_user_id=current_user["user_id"]
    )

    return DataResponse(
        success=True,
        message="Task updated successfully",
        data=updated_task
    )


@router.delete(
    "/{tsk_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_min_role_level(10))]
)
async def delete_task(
    tsk_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Delete task"""
    task_service.delete_task(
        db,
        tsk_id,
        current_user_role_level=current_user["role_level"]
    )

    return None


# ==================== TASK COMMENTS ENDPOINTS ====================

@router.post(
    "/{tsk_id}/comments",
    response_model=DataResponse[TaskComment],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_min_role_level(10))]
)
async def create_task_comment(
    tsk_id: int,
    comment: CommentCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Create comment on task"""
    # Build comment data with task ID and user ID
    comment_data = TaskCommentCreate(
        tc_tsk_id=tsk_id,
        tc_u_id=current_user["user_id"],
        tc_comment=comment.tc_comment,
        tc_parent_tc_id=comment.tc_parent_tc_id
    )

    new_comment = task_comment_service.create_task_comment(
        db,
        comment_data,
        current_user_role_level=current_user["role_level"],
        current_user_id=current_user["user_id"]
    )

    return DataResponse(
        success=True,
        message="Comment created successfully",
        data=new_comment
    )


@router.get(
    "/{tsk_id}/comments",
    response_model=PaginationResponse[TaskComment],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def get_task_comments(
    tsk_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Get all comments for task"""
    # Use repository filter method to get comments by task ID
    comments = task_comment_service.repository.filter(
        db,
        filters={"tc_tsk_id": tsk_id},
        skip=skip,
        limit=limit,
        order_by="-created_at"
    )
    total = task_comment_service.repository.count_filtered(db, {"tc_tsk_id": tsk_id})

    response = PaginationResponse(
        success=True,
        message="Comments retrieved successfully",
        data=[TaskComment.model_validate(c) for c in comments],
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

    return encrypt_response_data(response, settings)


# ==================== TASK ATTACHMENTS ENDPOINTS ====================
# TODO: Attachment functionality is under development

@router.post(
    "/{tsk_id}/attachments",
    response_model=DataResponse[TaskAttachment],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_min_role_level(10))]
)
async def upload_task_attachment(
    tsk_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Upload attachment to task"""
    # TODO: Implement file upload handling
    # TODO: Add file validation (size, type)
    # TODO: Store file to local/cloud storage
    # TODO: Create attachment database record
    return DataResponse(
        success=False,
        message="Attachment feature is currently under development",
        data=None
    )


class TaskAttachmentsResponse(BaseModel):
    attachments: List[TaskAttachment]
    total_size: int


@router.get(
    "/{tsk_id}/attachments",
    response_model=DataResponse[TaskAttachmentsResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def get_task_attachments(
    tsk_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Get all attachments for task"""
    # TODO: Implement attachment retrieval for specific task
    return DataResponse(
        success=False,
        message="Attachment feature is currently under development",
        data=None
    )


# ==================== TASK HISTORY ENDPOINTS ====================

@router.get(
    "/{tsk_id}/history",
    response_model=PaginationResponse[TaskHistory],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def get_task_history(
    tsk_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    field_name: Optional[str] = Query(None, description="Filter by field name"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Get task history"""
    # Build filters
    filters = {"th_tsk_id": tsk_id}
    if field_name:
        filters["th_field_name"] = field_name

    history = task_history_service.repository.filter(
        db,
        filters=filters,
        skip=skip,
        limit=limit,
        order_by="-created_at"
    )
    total = task_history_service.repository.count_filtered(db, filters)

    response = PaginationResponse(
        success=True,
        message="Task history retrieved successfully",
        data=[TaskHistory.model_validate(h) for h in history],
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

    return encrypt_response_data(response, settings)


# ==================== TASK LABELS ENDPOINTS ====================

@router.post(
    "/{tsk_id}/labels",
    response_model=DataResponse[TaskLabel],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_min_role_level(10))]
)
async def assign_label_to_task(
    tsk_id: int,
    label: LabelAssignRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Assign label to task"""
    label_data = TaskLabelCreate(
        tl_tsk_id=tsk_id,
        tl_lbl_id=label.lbl_id
    )

    new_label = task_label_service.create_task_label(
        db,
        label_data,
        current_user_role_level=current_user["role_level"],
        current_user_id=current_user["user_id"]
    )

    return DataResponse(
        success=True,
        message="Label assigned to task successfully",
        data=new_label
    )


class TaskLabelsResponse(BaseModel):
    labels: List[TaskLabel]


@router.get(
    "/{tsk_id}/labels",
    response_model=DataResponse[TaskLabelsResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def get_task_labels(
    tsk_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Get all labels for task"""
    labels = task_label_service.repository.filter(
        db,
        filters={"tl_tsk_id": tsk_id},
        order_by="-created_at"
    )

    response_data = {
        "labels": [TaskLabel.model_validate(lbl) for lbl in labels]
    }

    response = DataResponse(
        success=True,
        message="Task labels retrieved successfully",
        data=response_data
    )

    return encrypt_response_data(response, settings)


@router.delete(
    "/{tsk_id}/labels/{lbl_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_min_role_level(10))]
)
async def remove_label_from_task(
    tsk_id: int,
    lbl_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Remove label from task"""
    # Find the task_label record
    task_label = task_label_service.repository.first(
        db,
        filters={"tl_tsk_id": tsk_id, "tl_lbl_id": lbl_id}
    )

    if task_label:
        task_label_service.delete_task_label(
            db,
            task_label.tl_id,
            current_user_role_level=current_user["role_level"]
        )

    return None


# ==================== TASK WATCHERS ENDPOINTS ====================

@router.post(
    "/{tsk_id}/watchers",
    response_model=DataResponse[TaskWatcher],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_min_role_level(10))]
)
async def add_watcher_to_task(
    tsk_id: int,
    watcher: WatcherAddRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Add watcher to task"""
    watcher_data = TaskWatcherCreate(
        tw_tsk_id=tsk_id,
        tw_u_id=watcher.u_id
    )

    new_watcher = task_watcher_service.create_task_watcher(
        db,
        watcher_data,
        current_user_role_level=current_user["role_level"],
        current_user_id=current_user["user_id"]
    )

    return DataResponse(
        success=True,
        message="Watcher added to task successfully",
        data=new_watcher
    )


class TaskWatchersResponse(BaseModel):
    watchers: List[TaskWatcher]


@router.get(
    "/{tsk_id}/watchers",
    response_model=DataResponse[TaskWatchersResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def get_task_watchers(
    tsk_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Get all watchers for task"""
    watchers = task_watcher_service.repository.filter(
        db,
        filters={"tw_tsk_id": tsk_id},
        order_by="-created_at"
    )

    response_data = {
        "watchers": [TaskWatcher.model_validate(w) for w in watchers]
    }

    response = DataResponse(
        success=True,
        message="Watchers retrieved successfully",
        data=response_data
    )

    return encrypt_response_data(response, settings)


@router.delete(
    "/{tsk_id}/watchers/{u_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_min_role_level(10))]
)
async def remove_watcher_from_task(
    tsk_id: int,
    u_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Remove watcher from task"""
    # Find the task_watcher record
    task_watcher = task_watcher_service.repository.first(
        db,
        filters={"tw_tsk_id": tsk_id, "tw_u_id": u_id}
    )

    if task_watcher:
        task_watcher_service.delete_task_watcher(
            db,
            task_watcher.tw_id,
            current_user_role_level=current_user["role_level"]
        )

    return None


# ==================== BULK OPERATIONS ====================

@router.patch(
    "/bulk-update-status",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def bulk_update_task_status(
    request: BulkUpdateStatusRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Bulk update task status for multiple tasks"""
    result = task_service.bulk_update_status(
        db,
        task_ids=request.task_ids,
        ms_id=request.ms_id,
        current_user_role_level=current_user["role_level"],
        current_user_id=current_user["user_id"]
    )

    return DataResponse(
        success=True,
        message="Task statuses updated successfully",
        data=result
    )


# ==================== ADVANCED SEARCH ====================

@router.post(
    "/search",
    response_model=PaginationResponse[Task],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def advanced_task_search(
    request: AdvancedSearchRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Advanced task search with multiple filters"""
    # Build filters dictionary from request
    filters = {}
    if request.keyword:
        filters["keyword"] = request.keyword
    if request.project_ids:
        filters["project_ids"] = request.project_ids
    if request.status_ids:
        filters["status_ids"] = request.status_ids
    if request.priority_ids:
        filters["priority_ids"] = request.priority_ids
    if request.assignee_ids:
        filters["assignee_ids"] = request.assignee_ids
    if request.reporter_ids:
        filters["reporter_ids"] = request.reporter_ids
    if request.type_ids:
        filters["type_ids"] = request.type_ids
    if request.date_from:
        filters["date_from"] = request.date_from
    if request.date_to:
        filters["date_to"] = request.date_to

    # Execute advanced search
    tasks = task_service.repository.advanced_search(
        db,
        filters=filters,
        skip=request.skip,
        limit=request.limit
    )

    total = task_service.repository.count_advanced_search(db, filters=filters)

    response = PaginationResponse(
        success=True,
        message="Tasks retrieved successfully",
        data=tasks,
        total=total,
        page=request.skip // request.limit + 1,
        size=request.limit,
        pages=(total + request.limit - 1) // request.limit
    )

    return encrypt_response_data(response, settings)
