"""
Master Task Type Service
Business logic layer with role-based permission validation
"""
from typing import List
from sqlalchemy.orm import Session

from app.repositories.master_task_type_repository import MasterTaskTypeRepository
from app.schemas.master_task_type_schema import MasterTaskTypeCreate, MasterTaskTypeUpdate, MasterTaskType
from atams.exceptions import NotFoundException, ForbiddenException


class MasterTaskTypeService:
    def __init__(self):
        self.repository = MasterTaskTypeRepository()

    def get_master_task_type(
        self,
        db: Session,
        mtt_id: int,
        current_user_role_level: int,
        current_user_id: int
    ) -> MasterTaskType:
        """Get single master task type by ID"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to view master task type")

        db_master_task_type = self.repository.get(db, mtt_id)
        if not db_master_task_type:
            raise NotFoundException(f"Master task type with ID {mtt_id} not found")

        return MasterTaskType.model_validate(db_master_task_type)

    def get_master_task_types(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        current_user_role_level: int = 0
    ) -> List[MasterTaskType]:
        """Get list of master task types with pagination"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to list master task types")

        db_master_task_types = self.repository.get_multi(db, skip=skip, limit=limit)
        return [MasterTaskType.model_validate(mtt) for mtt in db_master_task_types]

    def create_master_task_type(
        self,
        db: Session,
        master_task_type: MasterTaskTypeCreate,
        current_user_role_level: int,
        current_user_id: int
    ) -> MasterTaskType:
        """Create new master task type"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to create master task type")

        # Add created_by
        data = master_task_type.model_dump()
        data["created_by"] = str(current_user_id)

        db_master_task_type = self.repository.create(db, data)
        return MasterTaskType.model_validate(db_master_task_type)

    def update_master_task_type(
        self,
        db: Session,
        mtt_id: int,
        master_task_type: MasterTaskTypeUpdate,
        current_user_role_level: int,
        current_user_id: int
    ) -> MasterTaskType:
        """Update existing master task type"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to update master task type")

        db_master_task_type = self.repository.get(db, mtt_id)
        if not db_master_task_type:
            raise NotFoundException(f"Master task type with ID {mtt_id} not found")

        update_data = master_task_type.model_dump(exclude_unset=True)

        db_master_task_type = self.repository.update(db, db_master_task_type, update_data)
        return MasterTaskType.model_validate(db_master_task_type)

    def delete_master_task_type(
        self,
        db: Session,
        mtt_id: int,
        current_user_role_level: int
    ) -> None:
        """Delete master task type"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to delete master task type")

        deleted = self.repository.delete(db, mtt_id)
        if not deleted:
            raise NotFoundException(f"Master task type with ID {mtt_id} not found")

    def get_total_master_task_types(self, db: Session) -> int:
        """Get total count of master task types"""
        return self.repository.count(db)
