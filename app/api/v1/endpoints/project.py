"""
Project Endpoints
Complete CRUD operations with Atlas SSO authentication
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.services.project_service import ProjectService
from app.schemas.project_schema import Project, ProjectCreate, ProjectUpdate
from app.schemas.common import DataResponse, PaginationResponse
from app.api.deps import require_auth, require_min_role_level
from atams.encryption import encrypt_response_data
from app.core.config import settings

router = APIRouter()
project_service = ProjectService()


@router.get(
    "/",
    response_model=PaginationResponse[Project],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def get_projects(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Get list of projects with pagination"""
    projects = project_service.get_projects(
        db,
        skip=skip,
        limit=limit,
        current_user_role_level=current_user["role_level"]
    )
    total = project_service.get_total_projects(db)

    response = PaginationResponse(
        success=True,
        message="Projects retrieved successfully",
        data=projects,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

    return encrypt_response_data(response, settings)


@router.get(
    "/{prj_id}",
    response_model=DataResponse[Project],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def get_project(
    prj_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Get single project by ID"""
    project = project_service.get_project(
        db,
        prj_id,
        current_user_role_level=current_user["role_level"],
        current_user_id=current_user["user_id"]
    )

    response = DataResponse(
        success=True,
        message="Project retrieved successfully",
        data=project
    )

    return encrypt_response_data(response, settings)


@router.post(
    "/",
    response_model=DataResponse[Project],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_min_role_level(10))]
)
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Create new project"""
    new_project = project_service.create_project(
        db,
        project,
        current_user_role_level=current_user["role_level"],
        current_user_id=current_user["user_id"]
    )

    return DataResponse(
        success=True,
        message="Project created successfully",
        data=new_project
    )


@router.put(
    "/{prj_id}",
    response_model=DataResponse[Project],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def update_project(
    prj_id: int,
    project: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Update existing project"""
    updated_project = project_service.update_project(
        db,
        prj_id,
        project,
        current_user_role_level=current_user["role_level"],
        current_user_id=current_user["user_id"]
    )

    return DataResponse(
        success=True,
        message="Project updated successfully",
        data=updated_project
    )


@router.delete(
    "/{prj_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_min_role_level(10))]
)
async def delete_project(
    prj_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Delete project"""
    project_service.delete_project(
        db,
        prj_id,
        current_user_role_level=current_user["role_level"],
        current_user_id=current_user["user_id"]
    )

    return None


# ==================== PROJECT STATISTICS ENDPOINTS ====================

class StatusCounts(BaseModel):
    TODO: int
    IN_PROGRESS: int
    IN_REVIEW: int
    DONE: int
    CANCELLED: int

class PriorityCounts(BaseModel):
    LOW: int
    MEDIUM: int
    HIGH: int
    CRITICAL: int

class TypeCounts(BaseModel):
    TASK: int
    BUG: int
    FEATURE: int
    IMPROVEMENT: int
    RESEARCH: int

class ProjectStatistics(BaseModel):
    prj_id: int
    prj_name: str
    total_tasks: int
    by_status: StatusCounts
    by_priority: PriorityCounts
    by_type: TypeCounts
    overdue_tasks: int
    completion_rate: float
    average_completion_time: Optional[float] = None


@router.get(
    "/{prj_id}/statistics",
    response_model=DataResponse[ProjectStatistics],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def get_project_statistics(
    prj_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Get project statistics"""
    statistics = project_service.get_project_statistics(
        db,
        prj_id,
        current_user_role_level=current_user["role_level"]
    )

    response = DataResponse(
        success=True,
        message="Project statistics retrieved successfully",
        data=statistics
    )

    return encrypt_response_data(response, settings)
