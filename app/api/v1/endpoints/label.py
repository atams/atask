"""
Label Endpoints
Complete CRUD operations with Atlas SSO authentication
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.label_service import LabelService
from app.schemas.label_schema import Label, LabelCreate, LabelUpdate
from app.schemas.common import DataResponse, PaginationResponse
from app.api.deps import require_auth, require_min_role_level
from atams.encryption import encrypt_response_data
from app.core.config import settings

router = APIRouter()
label_service = LabelService()


@router.get(
    "/",
    response_model=PaginationResponse[Label],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def get_labels(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Get list of labels with pagination"""
    labels = label_service.get_labels(
        db,
        skip=skip,
        limit=limit,
        current_user_role_level=current_user["role_level"]
    )
    total = label_service.get_total_labels(db)

    response = PaginationResponse(
        success=True,
        message="Labels retrieved successfully",
        data=labels,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

    return encrypt_response_data(response, settings)


@router.get(
    "/{lbl_id}",
    response_model=DataResponse[Label],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def get_label(
    lbl_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Get single label by ID"""
    label = label_service.get_label(
        db,
        lbl_id,
        current_user_role_level=current_user["role_level"],
        current_user_id=current_user["user_id"]
    )

    response = DataResponse(
        success=True,
        message="Label retrieved successfully",
        data=label
    )

    return encrypt_response_data(response, settings)


@router.post(
    "/",
    response_model=DataResponse[Label],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_min_role_level(10))]
)
async def create_label(
    label: LabelCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Create new label"""
    new_label = label_service.create_label(
        db,
        label,
        current_user_role_level=current_user["role_level"],
        current_user_id=current_user["user_id"]
    )

    return DataResponse(
        success=True,
        message="Label created successfully",
        data=new_label
    )


@router.put(
    "/{lbl_id}",
    response_model=DataResponse[Label],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def update_label(
    lbl_id: int,
    label: LabelUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Update existing label"""
    updated_label = label_service.update_label(
        db,
        lbl_id,
        label,
        current_user_role_level=current_user["role_level"],
        current_user_id=current_user["user_id"]
    )

    return DataResponse(
        success=True,
        message="Label updated successfully",
        data=updated_label
    )


@router.delete(
    "/{lbl_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_min_role_level(10))]
)
async def delete_label(
    lbl_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Delete label"""
    label_service.delete_label(
        db,
        lbl_id,
        current_user_role_level=current_user["role_level"]
    )

    return None
