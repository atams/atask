"""
User Repository
Access users from pt_atams_indonesia.users table
"""
from typing import Optional
from sqlalchemy.orm import Session

from atams.db import BaseRepository
from app.models.task import Task  # Using Task model as base since we don't have a User model


class UserRepository(BaseRepository[Task]):
    def __init__(self):
        super().__init__(Task)

    def get_users_from_atlas(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None
    ):
        """Get users from pt_atams_indonesia.users table"""
        query = """
            SELECT u_id, u_username, u_email, u_full_name
            FROM pt_atams_indonesia.users
            WHERE 1=1
        """
        params = {"skip": skip, "limit": limit}

        if search:
            query += " AND (u_username ILIKE :search OR u_email ILIKE :search OR u_full_name ILIKE :search)"
            params["search"] = f"%{search}%"

        query += " ORDER BY u_id LIMIT :limit OFFSET :skip"

        return self.execute_raw_sql_dict(db, query, params)

    def count_users_from_atlas(self, db: Session, search: Optional[str] = None):
        """Count users from pt_atams_indonesia.users"""
        query = "SELECT COUNT(*) as count FROM pt_atams_indonesia.users WHERE 1=1"
        params = {}

        if search:
            query += " AND (u_username ILIKE :search OR u_email ILIKE :search OR u_full_name ILIKE :search)"
            params["search"] = f"%{search}%"

        result = self.execute_raw_sql_dict(db, query, params)
        return result[0]["count"] if result else 0

    def get_user_by_id(self, db: Session, u_id: int):
        """Get user by ID from pt_atams_indonesia.users table"""
        query = """
            SELECT u_id, u_username, u_email, u_full_name
            FROM pt_atams_indonesia.users
            WHERE u_id = :u_id
        """
        result = self.execute_raw_sql_dict(db, query, {"u_id": u_id})
        return result[0] if result else None
