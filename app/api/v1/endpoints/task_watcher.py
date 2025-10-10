"""
Task Watcher Endpoints
Complete CRUD operations with Atlas SSO authentication
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.task_watcher_service import TaskWatcherService
from app.schemas.task_watcher_schema import TaskWatcher, TaskWatcherCreate, TaskWatcherUpdate
from app.schemas.common import DataResponse, PaginationResponse
from app.api.deps import require_auth, require_min_role_level
from atams.encryption import encrypt_response_data
from app.core.config import settings

router = APIRouter()
task_watcher_service = TaskWatcherService()


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def get_task_watchers(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Get list of task watchers with pagination"""
    task_watchers = task_watcher_service.get_task_watchers(
        db,
        skip=skip,
        limit=limit,
        current_user_role_level=current_user["role_level"]
    )
    total = task_watcher_service.get_total_task_watchers(db)

    response = PaginationResponse(
        success=True,
        message="Task watchers retrieved successfully",
        data=task_watchers,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

    return encrypt_response_data(response, settings)


@router.get(
    "/{tw_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def get_task_watcher(
    tw_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Get single task watcher by ID"""
    task_watcher = task_watcher_service.get_task_watcher(
        db,
        tw_id,
        current_user_role_level=current_user["role_level"],
        current_user_id=current_user["user_id"]
    )

    response = DataResponse(
        success=True,
        message="Task watcher retrieved successfully",
        data=task_watcher
    )

    return encrypt_response_data(response, settings)


@router.post(
    "/",
    response_model=DataResponse[TaskWatcher],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_min_role_level(10))]
)
async def create_task_watcher(
    task_watcher: TaskWatcherCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Create new task watcher"""
    new_task_watcher = task_watcher_service.create_task_watcher(
        db,
        task_watcher,
        current_user_role_level=current_user["role_level"],
        current_user_id=current_user["user_id"]
    )

    return DataResponse(
        success=True,
        message="Task watcher created successfully",
        data=new_task_watcher
    )


@router.put(
    "/{tw_id}",
    response_model=DataResponse[TaskWatcher],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def update_task_watcher(
    tw_id: int,
    task_watcher: TaskWatcherUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Update existing task watcher"""
    updated_task_watcher = task_watcher_service.update_task_watcher(
        db,
        tw_id,
        task_watcher,
        current_user_role_level=current_user["role_level"],
        current_user_id=current_user["user_id"]
    )

    return DataResponse(
        success=True,
        message="Task watcher updated successfully",
        data=updated_task_watcher
    )


@router.delete(
    "/{tw_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_min_role_level(10))]
)
async def delete_task_watcher(
    tw_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Delete task watcher"""
    task_watcher_service.delete_task_watcher(
        db,
        tw_id,
        current_user_role_level=current_user["role_level"]
    )

    return None
