"""
Task Comment Endpoints
Complete CRUD operations with Atlas SSO authentication
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.task_comment_service import TaskCommentService
from app.schemas.task_comment_schema import TaskComment, TaskCommentCreate, TaskCommentUpdate
from app.schemas.common import DataResponse, PaginationResponse
from app.api.deps import require_auth, require_min_role_level
from atams.encryption import encrypt_response_data
from app.core.config import settings

router = APIRouter()
task_comment_service = TaskCommentService()


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def get_task_comments(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Get list of task comments with pagination"""
    task_comments = task_comment_service.get_task_comments(
        db,
        skip=skip,
        limit=limit,
        current_user_role_level=current_user["role_level"]
    )
    total = task_comment_service.get_total_task_comments(db)

    response = PaginationResponse(
        success=True,
        message="Task comments retrieved successfully",
        data=task_comments,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

    return encrypt_response_data(response, settings)


@router.get(
    "/{tc_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def get_task_comment(
    tc_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Get single task comment by ID"""
    task_comment = task_comment_service.get_task_comment(
        db,
        tc_id,
        current_user_role_level=current_user["role_level"],
        current_user_id=current_user["user_id"]
    )

    response = DataResponse(
        success=True,
        message="Task comment retrieved successfully",
        data=task_comment
    )

    return encrypt_response_data(response, settings)


@router.post(
    "/",
    response_model=DataResponse[TaskComment],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_min_role_level(10))]
)
async def create_task_comment(
    task_comment: TaskCommentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Create new task comment"""
    new_task_comment = task_comment_service.create_task_comment(
        db,
        task_comment,
        current_user_role_level=current_user["role_level"],
        current_user_id=current_user["user_id"]
    )

    return DataResponse(
        success=True,
        message="Task comment created successfully",
        data=new_task_comment
    )


@router.put(
    "/{tc_id}",
    response_model=DataResponse[TaskComment],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def update_task_comment(
    tc_id: int,
    task_comment: TaskCommentUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Update existing task comment"""
    updated_task_comment = task_comment_service.update_task_comment(
        db,
        tc_id,
        task_comment,
        current_user_role_level=current_user["role_level"],
        current_user_id=current_user["user_id"]
    )

    return DataResponse(
        success=True,
        message="Task comment updated successfully",
        data=updated_task_comment
    )


@router.delete(
    "/{tc_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_min_role_level(10))]
)
async def delete_task_comment(
    tc_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Delete task comment"""
    task_comment_service.delete_task_comment(
        db,
        tc_id,
        current_user_role_level=current_user["role_level"]
    )

    return None
