"""
Project Service
Business logic layer with role-based permission validation
"""
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.repositories.project_repository import ProjectRepository
from app.schemas.project_schema import ProjectCreate, ProjectUpdate, Project
from atams.exceptions import NotFoundException, ForbiddenException


class ProjectService:
    def __init__(self):
        self.repository = ProjectRepository()

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

        return Project.model_validate(db_project)

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
        return [Project.model_validate(prj) for prj in db_projects]

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

        # Add created_by
        data = project.model_dump()
        data["created_by"] = str(current_user_id)

        db_project = self.repository.create(db, data)
        return Project.model_validate(db_project)

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

        update_data = project.model_dump(exclude_unset=True)
        update_data["updated_by"] = str(current_user_id)

        db_project = self.repository.update(db, db_project, update_data)
        return Project.model_validate(db_project)

    def delete_project(
        self,
        db: Session,
        prj_id: int,
        current_user_role_level: int
    ) -> None:
        """Delete project"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to delete project")

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
