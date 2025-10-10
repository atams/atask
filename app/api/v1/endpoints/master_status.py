"""
Master Status Endpoints
Complete CRUD operations with Atlas SSO authentication
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.master_status_service import MasterStatusService
from app.schemas.master_status_schema import MasterStatus
from app.schemas.common import PaginationResponse
from app.api.deps import require_auth, require_min_role_level
from atams.encryption import encrypt_response_data
from app.core.config import settings

router = APIRouter()
master_status_service = MasterStatusService()


@router.get(
    "/",
    response_model=PaginationResponse[MasterStatus],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def get_master_statuses(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Get list of master statuses with pagination"""
    master_statuses = master_status_service.get_master_statuses(
        db,
        skip=skip,
        limit=limit,
        current_user_role_level=current_user["role_level"]
    )
    total = master_status_service.get_total_master_statuses(db)

    response = PaginationResponse(
        success=True,
        message="Master statuses retrieved successfully",
        data=master_statuses,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

    return encrypt_response_data(response, settings)


# @router.get(
#     "/{ms_id}",
#     status_code=status.HTTP_200_OK,
#     dependencies=[Depends(require_min_role_level(10))]
# )
# async def get_master_status(
#     ms_id: int,
#     db: Session = Depends(get_db),
#     current_user: dict = Depends(require_auth)
# ):
#     """Get single master status by ID"""
#     master_status = master_status_service.get_master_status(
#         db,
#         ms_id,
#         current_user_role_level=current_user["role_level"],
#         current_user_id=current_user["user_id"]
#     )

#     response = DataResponse(
#         success=True,
#         message="Master status retrieved successfully",
#         data=master_status
#     )

#     return encrypt_response_data(response, settings)


# @router.post(
#     "/",
#     response_model=DataResponse[MasterStatus],
#     status_code=status.HTTP_201_CREATED,
#     dependencies=[Depends(require_min_role_level(10))]
# )
# async def create_master_status(
#     master_status: MasterStatusCreate,
#     db: Session = Depends(get_db),
#     current_user: dict = Depends(require_auth)
# ):
#     """Create new master status"""
#     new_master_status = master_status_service.create_master_status(
#         db,
#         master_status,
#         current_user_role_level=current_user["role_level"],
#         current_user_id=current_user["user_id"]
#     )

#     return DataResponse(
#         success=True,
#         message="Master status created successfully",
#         data=new_master_status
#     )


# @router.put(
#     "/{ms_id}",
#     response_model=DataResponse[MasterStatus],
#     status_code=status.HTTP_200_OK,
#     dependencies=[Depends(require_min_role_level(10))]
# )
# async def update_master_status(
#     ms_id: int,
#     master_status: MasterStatusUpdate,
#     db: Session = Depends(get_db),
#     current_user: dict = Depends(require_auth)
# ):
#     """Update existing master status"""
#     updated_master_status = master_status_service.update_master_status(
#         db,
#         ms_id,
#         master_status,
#         current_user_role_level=current_user["role_level"],
#         current_user_id=current_user["user_id"]
#     )

#     return DataResponse(
#         success=True,
#         message="Master status updated successfully",
#         data=updated_master_status
#     )


# @router.delete(
#     "/{ms_id}",
#     status_code=status.HTTP_204_NO_CONTENT,
#     dependencies=[Depends(require_min_role_level(10))]
# )
# async def delete_master_status(
#     ms_id: int,
#     db: Session = Depends(get_db),
#     current_user: dict = Depends(require_auth)
# ):
#     """Delete master status"""
#     master_status_service.delete_master_status(
#         db,
#         ms_id,
#         current_user_role_level=current_user["role_level"]
#     )

#     return None
