"""
Task Attachment Service
Business logic layer with role-based permission validation and Cloudinary integration
"""
from typing import List
from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.repositories.task_attachment_repository import TaskAttachmentRepository
from app.schemas.task_attachment_schema import TaskAttachmentCreate, TaskAttachmentUpdate, TaskAttachment
from app.services.cloudinary_service import CloudinaryService
from atams.exceptions import NotFoundException, ForbiddenException, BadRequestException


class TaskAttachmentService:
    def __init__(self):
        self.repository = TaskAttachmentRepository()
        self.cloudinary_service = CloudinaryService()

    def get_task_attachment(
        self,
        db: Session,
        ta_id: int,
        current_user_role_level: int,
        current_user_id: int
    ) -> TaskAttachment:
        """Get single task attachment by ID"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to view task attachment")

        db_task_attachment = self.repository.get(db, ta_id)
        if not db_task_attachment:
            raise NotFoundException(f"Task attachment with ID {ta_id} not found")

        return TaskAttachment.model_validate(db_task_attachment)

    def get_task_attachments(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        current_user_role_level: int = 0
    ) -> List[TaskAttachment]:
        """Get list of task attachments with pagination"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to list task attachments")

        db_task_attachments = self.repository.get_multi(db, skip=skip, limit=limit)
        return [TaskAttachment.model_validate(ta) for ta in db_task_attachments]

    def get_attachments_by_task_id(
        self,
        db: Session,
        task_id: int,
        current_user_role_level: int
    ) -> List[TaskAttachment]:
        """Get all attachments for a specific task"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to view task attachments")

        db_attachments = self.repository.get_by_task_id(db, task_id)
        return [TaskAttachment.model_validate(ta) for ta in db_attachments]

    async def upload_attachment(
        self,
        db: Session,
        file: UploadFile,
        task_id: int,
        current_user_role_level: int,
        current_user_id: int
    ) -> TaskAttachment:
        """
        Upload file to Cloudinary and create attachment record

        Validation rules:
        - Only PDF documents and images (PNG, JPG, JPEG) are allowed
        - Maximum file size: 5MB for images, 10MB for PDFs
        - File type is validated by both extension and content-type

        Args:
            db: Database session
            file: Uploaded file
            task_id: Task ID to attach file to
            current_user_role_level: Current user's role level
            current_user_id: Current user's ID

        Returns:
            Created TaskAttachment

        Raises:
            ForbiddenException: If user lacks permission
            BadRequestException: If file validation fails
        """
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to upload attachment")

        # Upload to Cloudinary with folder structure: atask/task-{task_id}/
        # Validation is done inside cloudinary_service.upload_file()
        folder = f"atask/task-{task_id}"

        upload_result = await self.cloudinary_service.upload_file(
            file=file,
            folder=folder,
            resource_type="auto"  # Will be validated and determined by cloudinary_service
        )

        # Create attachment record in database
        # Note: We don't store cloudinary_public_id in DB, we extract it from URL when needed
        attachment_data = TaskAttachmentCreate(
            ta_tsk_id=task_id,
            ta_file_name=file.filename,
            ta_file_path=upload_result["secure_url"],
            ta_file_size=upload_result.get("bytes"),
            ta_file_type=file.content_type
        )

        data = attachment_data.model_dump()
        data["created_by"] = str(current_user_id)

        db_task_attachment = self.repository.create(db, data)
        return TaskAttachment.model_validate(db_task_attachment)

    def update_task_attachment(
        self,
        db: Session,
        ta_id: int,
        task_attachment: TaskAttachmentUpdate,
        current_user_role_level: int,
        current_user_id: int
    ) -> TaskAttachment:
        """Update existing task attachment metadata (file name only)"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to update task attachment")

        db_task_attachment = self.repository.get(db, ta_id)
        if not db_task_attachment:
            raise NotFoundException(f"Task attachment with ID {ta_id} not found")

        update_data = task_attachment.model_dump(exclude_unset=True)
        update_data["updated_by"] = str(current_user_id)

        db_task_attachment = self.repository.update(db, db_task_attachment, update_data)
        return TaskAttachment.model_validate(db_task_attachment)

    def delete_task_attachment(
        self,
        db: Session,
        ta_id: int,
        current_user_role_level: int
    ) -> None:
        """Delete task attachment from database and Cloudinary"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to delete task attachment")

        # Get attachment first to extract public_id
        db_attachment = self.repository.get(db, ta_id)
        if not db_attachment:
            raise NotFoundException(f"Task attachment with ID {ta_id} not found")

        # Extract public_id from URL
        public_id = self.cloudinary_service.extract_public_id_from_url(db_attachment.ta_file_path)

        if public_id:
            # Determine resource type from file type
            resource_type = "raw"  # Default
            if db_attachment.ta_file_type:
                file_type = db_attachment.ta_file_type.lower()
                if any(img in file_type for img in ["image", "jpg", "jpeg", "png", "gif"]):
                    resource_type = "image"
                elif any(vid in file_type for vid in ["video", "mp4", "avi", "mov"]):
                    resource_type = "video"

            # Delete from Cloudinary
            try:
                self.cloudinary_service.delete_file(public_id, resource_type)
            except Exception as e:
                # Log error but continue with database deletion
                print(f"Warning: Failed to delete file from Cloudinary: {str(e)}")

        # Delete from database
        deleted = self.repository.delete(db, ta_id)
        if not deleted:
            raise NotFoundException(f"Task attachment with ID {ta_id} not found")

    def get_total_task_attachments(self, db: Session) -> int:
        """Get total count of task attachments"""
        return self.repository.count(db)

    def get_download_url(
        self,
        db: Session,
        ta_id: int,
        current_user_role_level: int
    ) -> tuple[TaskAttachment, str]:
        """
        Get attachment and Cloudinary URL for download

        Returns:
            tuple: (TaskAttachment, cloudinary_url)
        """
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to download attachment")

        db_attachment = self.repository.get(db, ta_id)
        if not db_attachment:
            raise NotFoundException(f"Task attachment with ID {ta_id} not found")

        # Return attachment object and original Cloudinary URL
        # The endpoint will handle adding Content-Disposition header
        attachment = TaskAttachment.model_validate(db_attachment)
        return attachment, db_attachment.ta_file_path
