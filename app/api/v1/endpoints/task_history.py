"""
Task History Endpoints
Complete CRUD operations with Atlas SSO authentication
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.task_history_service import TaskHistoryService
from app.schemas.task_history_schema import TaskHistory, TaskHistoryCreate, TaskHistoryUpdate
from app.schemas.common import DataResponse, PaginationResponse
from app.api.deps import require_auth, require_min_role_level
from atams.encryption import encrypt_response_data
from app.core.config import settings

router = APIRouter()
task_history_service = TaskHistoryService()


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def get_task_histories(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Get list of task histories with pagination"""
    task_histories = task_history_service.get_task_histories(
        db,
        skip=skip,
        limit=limit,
        current_user_role_level=current_user["role_level"]
    )
    total = task_history_service.get_total_task_histories(db)

    response = PaginationResponse(
        success=True,
        message="Task histories retrieved successfully",
        data=task_histories,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

    return encrypt_response_data(response, settings)


@router.get(
    "/{th_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def get_task_history(
    th_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Get single task history by ID"""
    task_history = task_history_service.get_task_history(
        db,
        th_id,
        current_user_role_level=current_user["role_level"],
        current_user_id=current_user["user_id"]
    )

    response = DataResponse(
        success=True,
        message="Task history retrieved successfully",
        data=task_history
    )

    return encrypt_response_data(response, settings)


@router.post(
    "/",
    response_model=DataResponse[TaskHistory],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_min_role_level(10))]
)
async def create_task_history(
    task_history: TaskHistoryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Create new task history"""
    new_task_history = task_history_service.create_task_history(
        db,
        task_history,
        current_user_role_level=current_user["role_level"],
        current_user_id=current_user["user_id"]
    )

    return DataResponse(
        success=True,
        message="Task history created successfully",
        data=new_task_history
    )


@router.put(
    "/{th_id}",
    response_model=DataResponse[TaskHistory],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def update_task_history(
    th_id: int,
    task_history: TaskHistoryUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Update existing task history"""
    updated_task_history = task_history_service.update_task_history(
        db,
        th_id,
        task_history,
        current_user_role_level=current_user["role_level"],
        current_user_id=current_user["user_id"]
    )

    return DataResponse(
        success=True,
        message="Task history updated successfully",
        data=updated_task_history
    )


@router.delete(
    "/{th_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_min_role_level(10))]
)
async def delete_task_history(
    th_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Delete task history"""
    task_history_service.delete_task_history(
        db,
        th_id,
        current_user_role_level=current_user["role_level"]
    )

    return None
