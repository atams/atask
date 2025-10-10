"""
Master Priority Service
Business logic layer with role-based permission validation
"""
from typing import List
from sqlalchemy.orm import Session

from app.repositories.master_priority_repository import MasterPriorityRepository
from app.schemas.master_priority_schema import MasterPriorityCreate, MasterPriorityUpdate, MasterPriority
from atams.exceptions import NotFoundException, ForbiddenException


class MasterPriorityService:
    def __init__(self):
        self.repository = MasterPriorityRepository()

    def get_master_priority(
        self,
        db: Session,
        mp_id: int,
        current_user_role_level: int,
        current_user_id: int
    ) -> MasterPriority:
        """Get single master priority by ID"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to view master priority")

        db_master_priority = self.repository.get(db, mp_id)
        if not db_master_priority:
            raise NotFoundException(f"Master priority with ID {mp_id} not found")

        return MasterPriority.model_validate(db_master_priority)

    def get_master_priorities(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        current_user_role_level: int = 0
    ) -> List[MasterPriority]:
        """Get list of master priorities with pagination"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to list master priorities")

        db_master_priorities = self.repository.get_multi(db, skip=skip, limit=limit)
        return [MasterPriority.model_validate(mp) for mp in db_master_priorities]

    def create_master_priority(
        self,
        db: Session,
        master_priority: MasterPriorityCreate,
        current_user_role_level: int,
        current_user_id: int
    ) -> MasterPriority:
        """Create new master priority"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to create master priority")

        # Add created_by
        data = master_priority.model_dump()
        data["created_by"] = str(current_user_id)

        db_master_priority = self.repository.create(db, data)
        return MasterPriority.model_validate(db_master_priority)

    def update_master_priority(
        self,
        db: Session,
        mp_id: int,
        master_priority: MasterPriorityUpdate,
        current_user_role_level: int,
        current_user_id: int
    ) -> MasterPriority:
        """Update existing master priority"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to update master priority")

        db_master_priority = self.repository.get(db, mp_id)
        if not db_master_priority:
            raise NotFoundException(f"Master priority with ID {mp_id} not found")

        update_data = master_priority.model_dump(exclude_unset=True)

        db_master_priority = self.repository.update(db, db_master_priority, update_data)
        return MasterPriority.model_validate(db_master_priority)

    def delete_master_priority(
        self,
        db: Session,
        mp_id: int,
        current_user_role_level: int
    ) -> None:
        """Delete master priority"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to delete master priority")

        deleted = self.repository.delete(db, mp_id)
        if not deleted:
            raise NotFoundException(f"Master priority with ID {mp_id} not found")

    def get_total_master_priorities(self, db: Session) -> int:
        """Get total count of master priorities"""
        return self.repository.count(db)
