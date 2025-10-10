"""
Master Priority Endpoints
Complete CRUD operations with Atlas SSO authentication
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.master_priority_service import MasterPriorityService
from app.schemas.master_priority_schema import MasterPriority, MasterPriorityCreate, MasterPriorityUpdate
from app.schemas.common import DataResponse, PaginationResponse
from app.api.deps import require_auth, require_min_role_level
from atams.encryption import encrypt_response_data
from app.core.config import settings

router = APIRouter()
master_priority_service = MasterPriorityService()


@router.get(
    "/",
    response_model=PaginationResponse[MasterPriority],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def get_master_priorities(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Get list of master priorities with pagination"""
    master_priorities = master_priority_service.get_master_priorities(
        db,
        skip=skip,
        limit=limit,
        current_user_role_level=current_user["role_level"]
    )
    total = master_priority_service.get_total_master_priorities(db)

    response = PaginationResponse(
        success=True,
        message="Master priorities retrieved successfully",
        data=master_priorities,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

    return encrypt_response_data(response, settings)


# @router.get(
#     "/{mp_id}",
#     status_code=status.HTTP_200_OK,
#     dependencies=[Depends(require_min_role_level(10))]
# )
# async def get_master_priority(
#     mp_id: int,
#     db: Session = Depends(get_db),
#     current_user: dict = Depends(require_auth)
# ):
#     """Get single master priority by ID"""
#     master_priority = master_priority_service.get_master_priority(
#         db,
#         mp_id,
#         current_user_role_level=current_user["role_level"],
#         current_user_id=current_user["user_id"]
#     )

#     response = DataResponse(
#         success=True,
#         message="Master priority retrieved successfully",
#         data=master_priority
#     )

#     return encrypt_response_data(response, settings)


# @router.post(
#     "/",
#     response_model=DataResponse[MasterPriority],
#     status_code=status.HTTP_201_CREATED,
#     dependencies=[Depends(require_min_role_level(10))]
# )
# async def create_master_priority(
#     master_priority: MasterPriorityCreate,
#     db: Session = Depends(get_db),
#     current_user: dict = Depends(require_auth)
# ):
#     """Create new master priority"""
#     new_master_priority = master_priority_service.create_master_priority(
#         db,
#         master_priority,
#         current_user_role_level=current_user["role_level"],
#         current_user_id=current_user["user_id"]
#     )

#     return DataResponse(
#         success=True,
#         message="Master priority created successfully",
#         data=new_master_priority
#     )


# @router.put(
#     "/{mp_id}",
#     response_model=DataResponse[MasterPriority],
#     status_code=status.HTTP_200_OK,
#     dependencies=[Depends(require_min_role_level(10))]
# )
# async def update_master_priority(
#     mp_id: int,
#     master_priority: MasterPriorityUpdate,
#     db: Session = Depends(get_db),
#     current_user: dict = Depends(require_auth)
# ):
#     """Update existing master priority"""
#     updated_master_priority = master_priority_service.update_master_priority(
#         db,
#         mp_id,
#         master_priority,
#         current_user_role_level=current_user["role_level"],
#         current_user_id=current_user["user_id"]
#     )

#     return DataResponse(
#         success=True,
#         message="Master priority updated successfully",
#         data=updated_master_priority
#     )


# @router.delete(
#     "/{mp_id}",
#     status_code=status.HTTP_204_NO_CONTENT,
#     dependencies=[Depends(require_min_role_level(10))]
# )
# async def delete_master_priority(
#     mp_id: int,
#     db: Session = Depends(get_db),
#     current_user: dict = Depends(require_auth)
# ):
#     """Delete master priority"""
#     master_priority_service.delete_master_priority(
#         db,
#         mp_id,
#         current_user_role_level=current_user["role_level"]
#     )

#     return None
