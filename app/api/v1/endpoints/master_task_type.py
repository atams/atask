"""
Master Task Type Endpoints
Complete CRUD operations with Atlas SSO authentication
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.master_task_type_service import MasterTaskTypeService
from app.schemas.master_task_type_schema import MasterTaskType
from app.schemas.common import PaginationResponse
from app.api.deps import require_auth, require_min_role_level
from atams.encryption import encrypt_response_data
from app.core.config import settings

router = APIRouter()
master_task_type_service = MasterTaskTypeService()


@router.get(
    "/",
    response_model=PaginationResponse[MasterTaskType],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def get_master_task_types(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Get list of master task types with pagination"""
    master_task_types = master_task_type_service.get_master_task_types(
        db,
        skip=skip,
        limit=limit,
        current_user_role_level=current_user["role_level"]
    )
    total = master_task_type_service.get_total_master_task_types(db)

    response = PaginationResponse(
        success=True,
        message="Master task types retrieved successfully",
        data=master_task_types,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

    return encrypt_response_data(response, settings)


# @router.get(
#     "/{mtt_id}",
#     status_code=status.HTTP_200_OK,
#     dependencies=[Depends(require_min_role_level(10))]
# )
# async def get_master_task_type(
#     mtt_id: int,
#     db: Session = Depends(get_db),
#     current_user: dict = Depends(require_auth)
# ):
#     """Get single master task type by ID"""
#     master_task_type = master_task_type_service.get_master_task_type(
#         db,
#         mtt_id,
#         current_user_role_level=current_user["role_level"],
#         current_user_id=current_user["user_id"]
#     )

#     response = DataResponse(
#         success=True,
#         message="Master task type retrieved successfully",
#         data=master_task_type
#     )

#     return encrypt_response_data(response, settings)


# @router.post(
#     "/",
#     response_model=DataResponse[MasterTaskType],
#     status_code=status.HTTP_201_CREATED,
#     dependencies=[Depends(require_min_role_level(10))]
# )
# async def create_master_task_type(
#     master_task_type: MasterTaskTypeCreate,
#     db: Session = Depends(get_db),
#     current_user: dict = Depends(require_auth)
# ):
#     """Create new master task type"""
#     new_master_task_type = master_task_type_service.create_master_task_type(
#         db,
#         master_task_type,
#         current_user_role_level=current_user["role_level"],
#         current_user_id=current_user["user_id"]
#     )

#     return DataResponse(
#         success=True,
#         message="Master task type created successfully",
#         data=new_master_task_type
#     )


# @router.put(
#     "/{mtt_id}",
#     response_model=DataResponse[MasterTaskType],
#     status_code=status.HTTP_200_OK,
#     dependencies=[Depends(require_min_role_level(10))]
# )
# async def update_master_task_type(
#     mtt_id: int,
#     master_task_type: MasterTaskTypeUpdate,
#     db: Session = Depends(get_db),
#     current_user: dict = Depends(require_auth)
# ):
#     """Update existing master task type"""
#     updated_master_task_type = master_task_type_service.update_master_task_type(
#         db,
#         mtt_id,
#         master_task_type,
#         current_user_role_level=current_user["role_level"],
#         current_user_id=current_user["user_id"]
#     )

#     return DataResponse(
#         success=True,
#         message="Master task type updated successfully",
#         data=updated_master_task_type
#     )


# @router.delete(
#     "/{mtt_id}",
#     status_code=status.HTTP_204_NO_CONTENT,
#     dependencies=[Depends(require_min_role_level(10))]
# )
# async def delete_master_task_type(
#     mtt_id: int,
#     db: Session = Depends(get_db),
#     current_user: dict = Depends(require_auth)
# ):
#     """Delete master task type"""
#     master_task_type_service.delete_master_task_type(
#         db,
#         mtt_id,
#         current_user_role_level=current_user["role_level"]
#     )

#     return None
