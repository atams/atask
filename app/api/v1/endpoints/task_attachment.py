"""
Task Attachment Endpoints
Complete CRUD operations with Cloudinary integration and Atlas SSO authentication
"""
from fastapi import APIRouter, Depends, Query, status, File, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import httpx

from app.db.session import get_db
from app.services.task_attachment_service import TaskAttachmentService
from app.schemas.task_attachment_schema import TaskAttachment, TaskAttachmentUpdate
from app.schemas.common import DataResponse, PaginationResponse
from app.api.deps import require_auth, require_min_role_level
from atams.encryption import encrypt_response_data
from app.core.config import settings

router = APIRouter()
task_attachment_service = TaskAttachmentService()


@router.get(
    "/",
    response_model=PaginationResponse[TaskAttachment],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def get_task_attachments(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """
    Get list of all task attachments with pagination

    **Required role level:** 10 (User)
    """
    attachments = task_attachment_service.get_task_attachments(
        db,
        skip=skip,
        limit=limit,
        current_user_role_level=current_user["role_level"]
    )
    total = task_attachment_service.get_total_task_attachments(db)

    response = PaginationResponse(
        success=True,
        message="Task attachments retrieved successfully",
        data=attachments,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

    if settings.ENCRYPTION_ENABLED:
        return encrypt_response_data(response.model_dump())

    return response


@router.post(
    "/",
    response_model=DataResponse[TaskAttachment],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_min_role_level(10))]
)
async def create_task_attachment(
    task_id: int = Query(..., description="Task ID to attach file to"),
    file: UploadFile = File(..., description="File to upload"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """
    Upload and create new task attachment

    **Required role level:** 10 (User)

    **Parameters:**
    - task_id: ID of the task to attach file to (query parameter)
    - file: File to upload (multipart/form-data)

    **File Validation:**
    - Allowed types: PDF documents (.pdf) and Images (.png, .jpg, .jpeg)
    - Maximum size: 5MB for images, 10MB for PDF documents
    - Content-Type validation is enforced

    **Example:**
    ```
    POST /api/v1/attachments/?task_id=123
    Content-Type: multipart/form-data

    file: [binary file]
    ```
    """
    attachment = await task_attachment_service.upload_attachment(
        db,
        file=file,
        task_id=task_id,
        current_user_role_level=current_user["role_level"],
        current_user_id=current_user["user_id"]
    )

    response = DataResponse(
        success=True,
        message="Task attachment uploaded successfully",
        data=attachment
    )

    if settings.ENCRYPTION_ENABLED:
        return encrypt_response_data(response.model_dump())

    return response


@router.get(
    "/{ta_id}",
    response_model=DataResponse[TaskAttachment],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def get_task_attachment(
    ta_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """
    Get single task attachment by ID

    **Required role level:** 10 (User)
    """
    attachment = task_attachment_service.get_task_attachment(
        db,
        ta_id,
        current_user_role_level=current_user["role_level"],
        current_user_id=current_user["user_id"]
    )

    response = DataResponse(
        success=True,
        message="Task attachment retrieved successfully",
        data=attachment
    )

    if settings.ENCRYPTION_ENABLED:
        return encrypt_response_data(response.model_dump())

    return response


@router.put(
    "/{ta_id}",
    response_model=DataResponse[TaskAttachment],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def update_task_attachment(
    ta_id: int,
    task_attachment: TaskAttachmentUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """
    Update existing task attachment metadata (file name only)

    **Required role level:** 10 (User)

    **Note:** To replace the file, delete and upload a new one
    """
    updated_attachment = task_attachment_service.update_task_attachment(
        db,
        ta_id,
        task_attachment,
        current_user_role_level=current_user["role_level"],
        current_user_id=current_user["user_id"]
    )

    response = DataResponse(
        success=True,
        message="Task attachment updated successfully",
        data=updated_attachment
    )

    if settings.ENCRYPTION_ENABLED:
        return encrypt_response_data(response.model_dump())

    return response


@router.delete(
    "/{ta_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]
)
async def delete_task_attachment(
    ta_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """
    Delete task attachment (removes from both database and Cloudinary)

    **Required role level:** 10 (User)
    """
    task_attachment_service.delete_task_attachment(
        db,
        ta_id,
        current_user_role_level=current_user["role_level"]
    )

    response = DataResponse(
        success=True,
        message="Task attachment deleted successfully",
        data=None
    )

    if settings.ENCRYPTION_ENABLED:
        return encrypt_response_data(response.model_dump())

    return response


@router.get(
    "/{ta_id}/download",
    dependencies=[Depends(require_min_role_level(10))]
)
async def download_task_attachment(
    ta_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """
    Download task attachment file (forces download instead of display)

    **Required role level:** 10 (User)

    **Note:** This endpoint streams the file from Cloudinary with Content-Disposition header
    to force download in browser
    """
    attachment, cloudinary_url = task_attachment_service.get_download_url(
        db,
        ta_id,
        current_user_role_level=current_user["role_level"]
    )

    # Fetch file from Cloudinary and stream it with proper headers
    async with httpx.AsyncClient() as client:
        response = await client.get(cloudinary_url)

        # Set headers to force download
        headers = {
            "Content-Disposition": f'attachment; filename="{attachment.ta_file_name}"',
            "Content-Type": attachment.ta_file_type or "application/octet-stream"
        }

        return StreamingResponse(
            iter([response.content]),
            headers=headers,
            media_type=attachment.ta_file_type or "application/octet-stream"
        )
