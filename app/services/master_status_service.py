"""
Master Status Service
Business logic layer with role-based permission validation
"""
from typing import List
from sqlalchemy.orm import Session

from app.repositories.master_status_repository import MasterStatusRepository
from app.schemas.master_status_schema import MasterStatusCreate, MasterStatusUpdate, MasterStatus
from atams.exceptions import NotFoundException, ForbiddenException


class MasterStatusService:
    def __init__(self):
        self.repository = MasterStatusRepository()

    def get_master_status(
        self,
        db: Session,
        ms_id: int,
        current_user_role_level: int,
        current_user_id: int
    ) -> MasterStatus:
        """Get single master status by ID"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to view master status")

        db_master_status = self.repository.get(db, ms_id)
        if not db_master_status:
            raise NotFoundException(f"Master status with ID {ms_id} not found")

        return MasterStatus.model_validate(db_master_status)

    def get_master_statuses(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        current_user_role_level: int = 0
    ) -> List[MasterStatus]:
        """Get list of master statuses with pagination"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to list master statuses")

        db_master_statuses = self.repository.get_multi(db, skip=skip, limit=limit)
        return [MasterStatus.model_validate(ms) for ms in db_master_statuses]

    def create_master_status(
        self,
        db: Session,
        master_status: MasterStatusCreate,
        current_user_role_level: int,
        current_user_id: int
    ) -> MasterStatus:
        """Create new master status"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to create master status")

        # Add created_by
        data = master_status.model_dump()
        data["created_by"] = str(current_user_id)

        db_master_status = self.repository.create(db, data)
        return MasterStatus.model_validate(db_master_status)

    def update_master_status(
        self,
        db: Session,
        ms_id: int,
        master_status: MasterStatusUpdate,
        current_user_role_level: int,
        current_user_id: int
    ) -> MasterStatus:
        """Update existing master status"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to update master status")

        db_master_status = self.repository.get(db, ms_id)
        if not db_master_status:
            raise NotFoundException(f"Master status with ID {ms_id} not found")

        update_data = master_status.model_dump(exclude_unset=True)

        db_master_status = self.repository.update(db, db_master_status, update_data)
        return MasterStatus.model_validate(db_master_status)

    def delete_master_status(
        self,
        db: Session,
        ms_id: int,
        current_user_role_level: int
    ) -> None:
        """Delete master status"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to delete master status")

        deleted = self.repository.delete(db, ms_id)
        if not deleted:
            raise NotFoundException(f"Master status with ID {ms_id} not found")

    def get_total_master_statuses(self, db: Session) -> int:
        """Get total count of master statuses"""
        return self.repository.count(db)
