"""
Project Service
Business logic layer with role-based permission validation
"""
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository
from app.schemas.project_schema import ProjectCreate, ProjectUpdate, Project
from atams.exceptions import NotFoundException, ForbiddenException, ConflictException


class ProjectService:
    def __init__(self):
        self.repository = ProjectRepository()
        self.user_repository = UserRepository()

    def get_project(
        self,
        db: Session,
        prj_id: int,
        current_user_role_level: int,
        current_user_id: int
    ) -> Project:
        """Get single project by ID"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to view project")

        db_project = self.repository.get(db, prj_id)
        if not db_project:
            raise NotFoundException(f"Project with ID {prj_id} not found")

        # Get owner name from users table
        project_dict = Project.model_validate(db_project).model_dump()
        if db_project.prj_u_id:
            owner = self.user_repository.get_user_by_id(db, db_project.prj_u_id)
            if owner:
                project_dict["prj_owner_name"] = owner.get("u_full_name")

        return Project.model_validate(project_dict)

    def get_projects(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        current_user_role_level: int = 0
    ) -> List[Project]:
        """Get list of projects with pagination"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to list projects")

        db_projects = self.repository.get_multi(db, skip=skip, limit=limit)

        # Get all unique owner IDs
        owner_ids = list(set([prj.prj_u_id for prj in db_projects if prj.prj_u_id]))

        # Fetch all owners in one query (batch)
        owner_map = {}
        for owner_id in owner_ids:
            owner = self.user_repository.get_user_by_id(db, owner_id)
            if owner:
                owner_map[owner_id] = owner.get("u_full_name")

        # Build project list with owner names
        projects = []
        for prj in db_projects:
            project_dict = Project.model_validate(prj).model_dump()
            if prj.prj_u_id and prj.prj_u_id in owner_map:
                project_dict["prj_owner_name"] = owner_map[prj.prj_u_id]
            projects.append(Project.model_validate(project_dict))

        return projects

    def create_project(
        self,
        db: Session,
        project: ProjectCreate,
        current_user_role_level: int,
        current_user_id: int
    ) -> Project:
        """Create new project"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to create project")

        # Check if project code already exists
        existing_project = self.repository.get_by_code(db, project.prj_code)
        if existing_project:
            raise ConflictException(
                f"Project with code '{project.prj_code}' already exists",
                details={"field": "prj_code", "value": project.prj_code}
            )

        # Add created_by
        data = project.model_dump()
        data["created_by"] = str(current_user_id)

        db_project = self.repository.create(db, data)

        # Get owner name from users table
        project_dict = Project.model_validate(db_project).model_dump()
        if db_project.prj_u_id:
            owner = self.user_repository.get_user_by_id(db, db_project.prj_u_id)
            if owner:
                project_dict["prj_owner_name"] = owner.get("u_full_name")

        return Project.model_validate(project_dict)

    def update_project(
        self,
        db: Session,
        prj_id: int,
        project: ProjectUpdate,
        current_user_role_level: int,
        current_user_id: int
    ) -> Project:
        """Update existing project"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to update project")

        db_project = self.repository.get(db, prj_id)
        if not db_project:
            raise NotFoundException(f"Project with ID {prj_id} not found")

        # If updating prj_code, check if new code already exists
        if hasattr(project, 'prj_code') and project.prj_code:
            existing_project = self.repository.get_by_code(db, project.prj_code)
            if existing_project and existing_project.prj_id != prj_id:
                raise ConflictException(
                    f"Project with code '{project.prj_code}' already exists",
                    details={"field": "prj_code", "value": project.prj_code}
                )

        update_data = project.model_dump(exclude_unset=True)
        update_data["updated_by"] = str(current_user_id)

        db_project = self.repository.update(db, db_project, update_data)

        # Get owner name from users table
        project_dict = Project.model_validate(db_project).model_dump()
        if db_project.prj_u_id:
            owner = self.user_repository.get_user_by_id(db, db_project.prj_u_id)
            if owner:
                project_dict["prj_owner_name"] = owner.get("u_full_name")

        return Project.model_validate(project_dict)

    def delete_project(
        self,
        db: Session,
        prj_id: int,
        current_user_role_level: int,
        current_user_id: int
    ) -> None:
        """Delete project"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to delete project")

        db_project = self.repository.get(db, prj_id)
        if not db_project:
            raise NotFoundException(f"Project with ID {prj_id} not found")

        # Only creator can delete project
        if db_project.created_by != str(current_user_id):
            raise ForbiddenException("Only the creator can delete this project")

        deleted = self.repository.delete(db, prj_id)
        if not deleted:
            raise NotFoundException(f"Project with ID {prj_id} not found")

    def get_total_projects(self, db: Session) -> int:
        """Get total count of projects"""
        return self.repository.count(db)

    def get_project_statistics(
        self,
        db: Session,
        prj_id: int,
        current_user_role_level: int
    ) -> Dict[str, Any]:
        """Get project statistics"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to view project statistics")

        # Verify project exists
        db_project = self.repository.get(db, prj_id)
        if not db_project:
            raise NotFoundException(f"Project with ID {prj_id} not found")

        statistics = self.repository.get_project_statistics(db, prj_id)
        if not statistics:
            raise NotFoundException(f"Statistics for project {prj_id} not found")

        return statistics
