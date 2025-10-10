"""
Cloudinary Service
Handles file upload, deletion, and URL generation for Cloudinary storage
"""
import cloudinary
import cloudinary.uploader
import cloudinary.api
from typing import Dict, Optional
from fastapi import UploadFile
import os

from app.core.config import settings
from atams.exceptions import BadRequestException


# File upload constraints
ALLOWED_IMAGE_TYPES = ["image/png", "image/jpg", "image/jpeg"]
ALLOWED_DOCUMENT_TYPES = ["application/pdf"]
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB in bytes
MAX_DOCUMENT_SIZE = 10 * 1024 * 1024  # 10 MB in bytes

# Allowed extensions
ALLOWED_IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg"]
ALLOWED_DOCUMENT_EXTENSIONS = [".pdf"]


class CloudinaryService:
    """Service for handling Cloudinary operations"""

    def __init__(self):
        """Initialize Cloudinary configuration"""
        if not all([
            settings.CLOUDINARY_CLOUD_NAME,
            settings.CLOUDINARY_API_KEY,
            settings.CLOUDINARY_API_SECRET
        ]):
            raise ValueError(
                "Cloudinary credentials are not configured. "
                "Please set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET in .env"
            )

        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True
        )

    def validate_file(self, file: UploadFile) -> tuple[str, str]:
        """
        Validate file type and size

        Args:
            file: FastAPI UploadFile object

        Returns:
            tuple: (resource_type, file_category) where file_category is 'image' or 'document'

        Raises:
            BadRequestException: If file is invalid
        """
        if not file.filename:
            raise BadRequestException("No file provided")

        # Get file extension
        file_extension = os.path.splitext(file.filename)[1].lower()

        # Determine file category and validate extension
        is_image = file_extension in ALLOWED_IMAGE_EXTENSIONS
        is_document = file_extension in ALLOWED_DOCUMENT_EXTENSIONS

        if not is_image and not is_document:
            raise BadRequestException(
                f"File type not allowed. Only images (png, jpg, jpeg) and PDF documents are supported. "
                f"Received: {file_extension}"
            )

        # Validate content type
        content_type = file.content_type or ""

        if is_image:
            if content_type not in ALLOWED_IMAGE_TYPES:
                raise BadRequestException(
                    f"Invalid image content type. Only PNG and JPEG images are allowed. "
                    f"Received: {content_type}"
                )
            file_category = "image"
            resource_type = "image"
        else:  # is_document
            if content_type not in ALLOWED_DOCUMENT_TYPES:
                raise BadRequestException(
                    f"Invalid document content type. Only PDF documents are allowed. "
                    f"Received: {content_type}"
                )
            file_category = "document"
            resource_type = "raw"  # PDF is stored as 'raw' in Cloudinary

        return resource_type, file_category

    async def validate_file_size(self, file: UploadFile, file_category: str) -> int:
        """
        Validate file size

        Args:
            file: FastAPI UploadFile object
            file_category: 'image' or 'document'

        Returns:
            int: File size in bytes

        Raises:
            BadRequestException: If file size exceeds limit
        """
        # Read file content to check size
        file_content = await file.read()
        file_size = len(file_content)

        # Reset file position for later reading
        await file.seek(0)

        # Check size limits
        if file_category == "image":
            max_size = MAX_IMAGE_SIZE
            max_size_mb = MAX_IMAGE_SIZE / (1024 * 1024)
        else:  # document
            max_size = MAX_DOCUMENT_SIZE
            max_size_mb = MAX_DOCUMENT_SIZE / (1024 * 1024)

        if file_size > max_size:
            current_size_mb = file_size / (1024 * 1024)
            raise BadRequestException(
                f"File size exceeds limit. Maximum allowed: {max_size_mb:.0f}MB, "
                f"Current file size: {current_size_mb:.2f}MB"
            )

        return file_size

    async def upload_file(
        self,
        file: UploadFile,
        folder: Optional[str] = None,
        public_id: Optional[str] = None,
        resource_type: str = "auto"
    ) -> Dict:
        """
        Upload file to Cloudinary with validation

        Args:
            file: FastAPI UploadFile object
            folder: Folder path in Cloudinary (default: settings.CLOUDINARY_FOLDER)
            public_id: Custom public ID (optional)
            resource_type: Type of file (image, video, raw, auto)

        Returns:
            Dict containing upload result with keys:
                - public_id: Cloudinary public ID
                - secure_url: HTTPS URL to access the file
                - resource_type: Type of uploaded resource
                - format: File format
                - bytes: File size in bytes
                - url: HTTP URL (deprecated, use secure_url)
        """
        try:
            # Validate file type and size
            validated_resource_type, file_category = self.validate_file(file)
            file_size = await self.validate_file_size(file, file_category)

            # Use validated resource type if auto
            if resource_type == "auto":
                resource_type = validated_resource_type

            # Determine folder
            upload_folder = folder or settings.CLOUDINARY_FOLDER

            # Read file content
            file_content = await file.read()

            # Prepare upload options
            upload_options = {
                "folder": upload_folder,
                "resource_type": resource_type,
                "use_filename": True,
                "unique_filename": True,
            }

            if public_id:
                upload_options["public_id"] = public_id

            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                file_content,
                **upload_options
            )

            return {
                "public_id": result.get("public_id"),
                "secure_url": result.get("secure_url"),
                "resource_type": result.get("resource_type"),
                "format": result.get("format"),
                "bytes": result.get("bytes"),
                "url": result.get("url"),
                "original_filename": file.filename,
                "width": result.get("width"),
                "height": result.get("height"),
            }

        except BadRequestException:
            # Re-raise validation errors
            raise
        except Exception as e:
            raise BadRequestException(f"Failed to upload file to Cloudinary: {str(e)}")

    def delete_file(self, public_id: str, resource_type: str = "image") -> Dict:
        """
        Delete file from Cloudinary

        Args:
            public_id: Cloudinary public ID of the file
            resource_type: Type of file (image, video, raw)

        Returns:
            Dict containing deletion result
        """
        try:
            result = cloudinary.uploader.destroy(
                public_id,
                resource_type=resource_type
            )
            return result
        except Exception as e:
            raise BadRequestException(f"Failed to delete file from Cloudinary: {str(e)}")

    def get_file_url(
        self,
        public_id: str,
        transformation: Optional[Dict] = None,
        resource_type: str = "image"
    ) -> str:
        """
        Get URL for a file in Cloudinary with optional transformation

        Args:
            public_id: Cloudinary public ID
            transformation: Transformation options (width, height, crop, etc.)
            resource_type: Type of file (image, video, raw)

        Returns:
            Secure URL to the file
        """
        try:
            if resource_type == "raw":
                # For raw files (documents, etc), use raw delivery
                url = cloudinary.CloudinaryResource(
                    public_id,
                    resource_type="raw"
                ).url
            else:
                # For images/videos, apply transformation if provided
                url = cloudinary.CloudinaryImage(public_id).build_url(
                    transformation=transformation,
                    secure=True
                )

            return url
        except Exception as e:
            raise BadRequestException(f"Failed to generate file URL: {str(e)}")

    def extract_public_id_from_url(self, url: str) -> Optional[str]:
        """
        Extract public_id from Cloudinary URL

        Args:
            url: Cloudinary URL

        Returns:
            Public ID or None if extraction fails
        """
        try:
            # Cloudinary URL format:
            # https://res.cloudinary.com/{cloud_name}/{resource_type}/upload/v{version}/{public_id}.{format}
            # or with transformations:
            # https://res.cloudinary.com/{cloud_name}/{resource_type}/upload/{transformations}/v{version}/{public_id}.{format}

            parts = url.split("/upload/")
            if len(parts) < 2:
                return None

            # Get the part after /upload/
            after_upload = parts[1]

            # Remove version (v1234567890/)
            if after_upload.startswith("v"):
                after_upload = "/".join(after_upload.split("/")[1:])

            # Extract public_id (remove file extension)
            public_id_with_ext = after_upload
            public_id = os.path.splitext(public_id_with_ext)[0]

            return public_id
        except Exception:
            return None

    def get_resource_info(self, public_id: str, resource_type: str = "image") -> Dict:
        """
        Get detailed information about a resource

        Args:
            public_id: Cloudinary public ID
            resource_type: Type of file (image, video, raw)

        Returns:
            Dict containing resource information
        """
        try:
            result = cloudinary.api.resource(
                public_id,
                resource_type=resource_type
            )
            return result
        except Exception as e:
            raise BadRequestException(f"Failed to get resource info: {str(e)}")
