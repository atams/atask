"""
Task Label Endpoints
Complete CRUD operations with Atlas SSO authentication
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.task_label_service import TaskLabelService
from app.schemas.task_label_schema import TaskLabel, TaskLabelCreate, TaskLabelUpdate
from app.schemas.common import DataResponse, PaginationResponse
from app.api.deps import require_auth, require_min_role_level
from atams.encryption import encrypt_response_data
from app.core.config import settings

router = APIRouter()
task_label_service = TaskLabelService()


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def get_task_labels(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Get list of task labels with pagination"""
    task_labels = task_label_service.get_task_labels(
        db,
        skip=skip,
        limit=limit,
        current_user_role_level=current_user["role_level"]
    )
    total = task_label_service.get_total_task_labels(db)

    response = PaginationResponse(
        success=True,
        message="Task labels retrieved successfully",
        data=task_labels,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

    return encrypt_response_data(response, settings)


@router.get(
    "/{tl_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def get_task_label(
    tl_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Get single task label by ID"""
    task_label = task_label_service.get_task_label(
        db,
        tl_id,
        current_user_role_level=current_user["role_level"],
        current_user_id=current_user["user_id"]
    )

    response = DataResponse(
        success=True,
        message="Task label retrieved successfully",
        data=task_label
    )

    return encrypt_response_data(response, settings)


@router.post(
    "/",
    response_model=DataResponse[TaskLabel],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_min_role_level(10))]
)
async def create_task_label(
    task_label: TaskLabelCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Create new task label"""
    new_task_label = task_label_service.create_task_label(
        db,
        task_label,
        current_user_role_level=current_user["role_level"],
        current_user_id=current_user["user_id"]
    )

    return DataResponse(
        success=True,
        message="Task label created successfully",
        data=new_task_label
    )


@router.put(
    "/{tl_id}",
    response_model=DataResponse[TaskLabel],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def update_task_label(
    tl_id: int,
    task_label: TaskLabelUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Update existing task label"""
    updated_task_label = task_label_service.update_task_label(
        db,
        tl_id,
        task_label,
        current_user_role_level=current_user["role_level"],
        current_user_id=current_user["user_id"]
    )

    return DataResponse(
        success=True,
        message="Task label updated successfully",
        data=updated_task_label
    )


@router.delete(
    "/{tl_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_min_role_level(10))]
)
async def delete_task_label(
    tl_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Delete task label"""
    task_label_service.delete_task_label(
        db,
        tl_id,
        current_user_role_level=current_user["role_level"]
    )

    return None
