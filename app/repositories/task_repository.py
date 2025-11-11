"""
Task Repository
"""
from typing import Dict, Any
from sqlalchemy.orm import Session

from atams.db import BaseRepository
from app.models.task import Task


class TaskRepository(BaseRepository[Task]):
    def __init__(self):
        super().__init__(Task)

    def get_tasks_with_joins(self, db: Session, skip: int = 0, limit: int = 100):
        """
        Get tasks with all related data in single query (optimized for performance)
        This eliminates N+1 query problem by using JOINs
        """
        query = """
            SELECT
                t.tsk_id, t.tsk_code, t.tsk_title, t.tsk_description,
                t.tsk_prj_id, t.tsk_ms_id, t.tsk_mp_id, t.tsk_mtt_id,
                t.tsk_assignee_u_id, t.tsk_reporter_u_id,
                t.tsk_start_date, t.tsk_due_date, t.tsk_duration,
                t.tsk_parent_tsk_id, t.tsk_thumbnail,
                t.created_by, t.created_at, t.updated_by, t.updated_at,
                -- Joined data
                p.prj_name as tsk_project_name,
                ms.ms_name as tsk_status_name,
                mp.mp_name as tsk_priority_name,
                mp.mp_color as tsk_priority_color,
                mtt.mtt_name as tsk_type_name,
                u_assignee.u_full_name as tsk_assignee_name,
                u_reporter.u_full_name as tsk_reporter_name
            FROM atask.task t
            LEFT JOIN atask.project p ON t.tsk_prj_id = p.prj_id
            LEFT JOIN atask.master_status ms ON t.tsk_ms_id = ms.ms_id
            LEFT JOIN atask.master_priority mp ON t.tsk_mp_id = mp.mp_id
            LEFT JOIN atask.master_task_type mtt ON t.tsk_mtt_id = mtt.mtt_id
            LEFT JOIN pt_atams_indonesia.users u_assignee ON t.tsk_assignee_u_id = u_assignee.u_id
            LEFT JOIN pt_atams_indonesia.users u_reporter ON t.tsk_reporter_u_id = u_reporter.u_id
            ORDER BY t.created_at DESC
            LIMIT :limit OFFSET :skip
        """

        params = {"skip": skip, "limit": limit}
        return self.execute_raw_sql_dict(db, query, params)

    def get_next_task_number_for_project(self, db: Session, project_id: int, task_type_code: str) -> str:
        """
        Generate next task code for a project
        Format: <PRJ_ID_3DIGIT>/<MTT_CODE_3CHAR>/<COUNT_3DIGIT>
        """
        # Get the count of existing tasks in this project
        query = """
            SELECT COUNT(*) as count
            FROM atask.task
            WHERE tsk_prj_id = :project_id
        """
        result = self.execute_raw_sql_dict(db, query, {"project_id": project_id})
        count = result[0]["count"] if result else 0

        # Generate task code
        prj_id_str = str(project_id).zfill(3)
        type_code = task_type_code[:3].upper()
        count_str = str(count + 1).zfill(3)

        return f"{prj_id_str}/{type_code}/{count_str}"

    def advanced_search(self, db: Session, filters: Dict[str, Any], skip: int = 0, limit: int = 100):
        """Advanced task search with multiple filters and JOINs"""
        query = """
            SELECT t.*,
                   p.prj_name as project_name,
                   ms.ms_name as status_name,
                   mp.mp_name as priority_name,
                   mtt.mtt_name as type_name
            FROM atask.task t
            LEFT JOIN atask.project p ON t.tsk_prj_id = p.prj_id
            LEFT JOIN atask.master_status ms ON t.tsk_ms_id = ms.ms_id
            LEFT JOIN atask.master_priority mp ON t.tsk_mp_id = mp.mp_id
            LEFT JOIN atask.master_task_type mtt ON t.tsk_mtt_id = mtt.mtt_id
            WHERE 1=1
        """

        params = {"skip": skip, "limit": limit}

        # Keyword search in title and description
        if filters.get("keyword"):
            query += " AND (t.tsk_title ILIKE :keyword OR t.tsk_description ILIKE :keyword)"
            params["keyword"] = f"%{filters['keyword']}%"

        # Filter by project IDs
        if filters.get("project_ids"):
            query += " AND t.tsk_prj_id = ANY(:project_ids)"
            params["project_ids"] = filters["project_ids"]

        # Filter by status IDs
        if filters.get("status_ids"):
            query += " AND t.tsk_ms_id = ANY(:status_ids)"
            params["status_ids"] = filters["status_ids"]

        # Filter by priority IDs
        if filters.get("priority_ids"):
            query += " AND t.tsk_mp_id = ANY(:priority_ids)"
            params["priority_ids"] = filters["priority_ids"]

        # Filter by assignee IDs
        if filters.get("assignee_ids"):
            query += " AND t.tsk_assignee_u_id = ANY(:assignee_ids)"
            params["assignee_ids"] = filters["assignee_ids"]

        # Filter by reporter IDs
        if filters.get("reporter_ids"):
            query += " AND t.tsk_reporter_u_id = ANY(:reporter_ids)"
            params["reporter_ids"] = filters["reporter_ids"]

        # Filter by task type IDs
        if filters.get("type_ids"):
            query += " AND t.tsk_mtt_id = ANY(:type_ids)"
            params["type_ids"] = filters["type_ids"]

        # Filter by date range (created_at)
        if filters.get("date_from"):
            query += " AND t.created_at >= :date_from"
            params["date_from"] = filters["date_from"]

        if filters.get("date_to"):
            query += " AND t.created_at <= :date_to"
            params["date_to"] = filters["date_to"]

        # Order by created_at descending
        query += " ORDER BY t.created_at DESC LIMIT :limit OFFSET :skip"

        return self.execute_raw_sql_dict(db, query, params)

    def count_advanced_search(self, db: Session, filters: Dict[str, Any]) -> int:
        """Count results for advanced search"""
        query = """
            SELECT COUNT(*) as count
            FROM atask.task t
            WHERE 1=1
        """

        params = {}

        # Apply same filters as advanced_search
        if filters.get("keyword"):
            query += " AND (t.tsk_title ILIKE :keyword OR t.tsk_description ILIKE :keyword)"
            params["keyword"] = f"%{filters['keyword']}%"

        if filters.get("project_ids"):
            query += " AND t.tsk_prj_id = ANY(:project_ids)"
            params["project_ids"] = filters["project_ids"]

        if filters.get("status_ids"):
            query += " AND t.tsk_ms_id = ANY(:status_ids)"
            params["status_ids"] = filters["status_ids"]

        if filters.get("priority_ids"):
            query += " AND t.tsk_mp_id = ANY(:priority_ids)"
            params["priority_ids"] = filters["priority_ids"]

        if filters.get("assignee_ids"):
            query += " AND t.tsk_assignee_u_id = ANY(:assignee_ids)"
            params["assignee_ids"] = filters["assignee_ids"]

        if filters.get("reporter_ids"):
            query += " AND t.tsk_reporter_u_id = ANY(:reporter_ids)"
            params["reporter_ids"] = filters["reporter_ids"]

        if filters.get("type_ids"):
            query += " AND t.tsk_mtt_id = ANY(:type_ids)"
            params["type_ids"] = filters["type_ids"]

        if filters.get("date_from"):
            query += " AND t.created_at >= :date_from"
            params["date_from"] = filters["date_from"]

        if filters.get("date_to"):
            query += " AND t.created_at <= :date_to"
            params["date_to"] = filters["date_to"]

        result = self.execute_raw_sql_dict(db, query, params)
        return result[0]["count"] if result else 0
