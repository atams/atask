"""
Label Service
Business logic layer with role-based permission validation
"""
from typing import List
from sqlalchemy.orm import Session

from app.repositories.label_repository import LabelRepository
from app.schemas.label_schema import LabelCreate, LabelUpdate, Label
from atams.exceptions import NotFoundException, ForbiddenException


class LabelService:
    def __init__(self):
        self.repository = LabelRepository()

    def get_label(
        self,
        db: Session,
        lbl_id: int,
        current_user_role_level: int,
        current_user_id: int
    ) -> Label:
        """Get single label by ID"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to view label")

        db_label = self.repository.get(db, lbl_id)
        if not db_label:
            raise NotFoundException(f"Label with ID {lbl_id} not found")

        return Label.model_validate(db_label)

    def get_labels(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        current_user_role_level: int = 0
    ) -> List[Label]:
        """Get list of labels with pagination"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to list labels")

        db_labels = self.repository.get_multi(db, skip=skip, limit=limit)
        return [Label.model_validate(lbl) for lbl in db_labels]

    def create_label(
        self,
        db: Session,
        label: LabelCreate,
        current_user_role_level: int,
        current_user_id: int
    ) -> Label:
        """Create new label"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to create label")

        # Add created_by
        data = label.model_dump()
        data["created_by"] = str(current_user_id)

        db_label = self.repository.create(db, data)
        return Label.model_validate(db_label)

    def update_label(
        self,
        db: Session,
        lbl_id: int,
        label: LabelUpdate,
        current_user_role_level: int,
        current_user_id: int
    ) -> Label:
        """Update existing label"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to update label")

        db_label = self.repository.get(db, lbl_id)
        if not db_label:
            raise NotFoundException(f"Label with ID {lbl_id} not found")

        update_data = label.model_dump(exclude_unset=True)
        update_data["updated_by"] = str(current_user_id)

        db_label = self.repository.update(db, db_label, update_data)
        return Label.model_validate(db_label)

    def delete_label(
        self,
        db: Session,
        lbl_id: int,
        current_user_role_level: int
    ) -> None:
        """Delete label"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to delete label")

        deleted = self.repository.delete(db, lbl_id)
        if not deleted:
            raise NotFoundException(f"Label with ID {lbl_id} not found")

    def get_total_labels(self, db: Session) -> int:
        """Get total count of labels"""
        return self.repository.count(db)
