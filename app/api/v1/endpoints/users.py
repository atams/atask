"""
Users Endpoints
Access users from pt_atams_indonesia schema and user-specific data
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from app.repositories.task_watcher_repository import TaskWatcherRepository
from app.services.task_service import TaskService
from app.schemas.common import DataResponse, PaginationResponse
from app.api.deps import require_auth, require_min_role_level
from atams.encryption import encrypt_response_data
from app.core.config import settings

router = APIRouter()
user_repository = UserRepository()
task_watcher_repository = TaskWatcherRepository()
task_service = TaskService()


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def get_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    search: Optional[str] = Query(None, description="Search by username, email, or full name"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Get list of users from pt_atams_indonesia.users table"""
    users = user_repository.get_users_from_atlas(
        db,
        skip=skip,
        limit=limit,
        search=search
    )
    total = user_repository.count_users_from_atlas(db, search=search)

    response = PaginationResponse(
        success=True,
        message="Users retrieved successfully",
        data=users,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

    return encrypt_response_data(response, settings)


@router.get(
    "/{u_id}/dashboard",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def get_user_dashboard(
    u_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Get user task dashboard with statistics"""
    dashboard_data = task_service.get_user_dashboard(
        db,
        u_id,
        current_user_role_level=current_user["role_level"]
    )

    response = DataResponse(
        success=True,
        message="User dashboard retrieved successfully",
        data=dashboard_data
    )

    return encrypt_response_data(response, settings)


@router.get(
    "/{u_id}/watched-tasks",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def get_watched_tasks(
    u_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    status_id: Optional[int] = Query(None, description="Filter by status ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Get all tasks watched by user"""
    watched_tasks = task_watcher_repository.get_watched_tasks_by_user(
        db,
        u_id=u_id,
        skip=skip,
        limit=limit,
        status_id=status_id
    )

    count_result = task_watcher_repository.count_watched_tasks_by_user(
        db,
        u_id=u_id,
        status_id=status_id
    )

    response = PaginationResponse(
        success=True,
        message="Watched tasks retrieved successfully",
        data=watched_tasks,
        total=count_result,
        page=skip // limit + 1,
        size=limit,
        pages=(count_result + limit - 1) // limit
    )

    return encrypt_response_data(response, settings)
