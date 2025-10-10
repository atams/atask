"""
Project Repository
"""
from typing import Dict, Any
from sqlalchemy.orm import Session

from atams.db import BaseRepository
from app.models.project import Project


class ProjectRepository(BaseRepository[Project]):
    def __init__(self):
        super().__init__(Project)

    def get_project_statistics(self, db: Session, prj_id: int) -> Dict[str, Any]:
        """
        Get project statistics including task counts by status, priority, and type
        """
        query = """
            SELECT
                p.prj_id,
                p.prj_name,
                COUNT(t.tsk_id) as total_tasks,
                SUM(CASE WHEN ms.ms_code = 'TODO' THEN 1 ELSE 0 END) as todo_count,
                SUM(CASE WHEN ms.ms_code = 'IN_PROGRESS' THEN 1 ELSE 0 END) as in_progress_count,
                SUM(CASE WHEN ms.ms_code = 'IN_REVIEW' THEN 1 ELSE 0 END) as in_review_count,
                SUM(CASE WHEN ms.ms_code = 'DONE' THEN 1 ELSE 0 END) as done_count,
                SUM(CASE WHEN ms.ms_code = 'CANCELLED' THEN 1 ELSE 0 END) as cancelled_count,
                SUM(CASE WHEN mp.mp_code = 'LOW' THEN 1 ELSE 0 END) as low_priority_count,
                SUM(CASE WHEN mp.mp_code = 'MEDIUM' THEN 1 ELSE 0 END) as medium_priority_count,
                SUM(CASE WHEN mp.mp_code = 'HIGH' THEN 1 ELSE 0 END) as high_priority_count,
                SUM(CASE WHEN mp.mp_code = 'CRITICAL' THEN 1 ELSE 0 END) as critical_priority_count,
                SUM(CASE WHEN mtt.mtt_code = 'TASK' THEN 1 ELSE 0 END) as task_type_count,
                SUM(CASE WHEN mtt.mtt_code = 'BUG' THEN 1 ELSE 0 END) as bug_type_count,
                SUM(CASE WHEN mtt.mtt_code = 'FEATURE' THEN 1 ELSE 0 END) as feature_type_count,
                SUM(CASE WHEN mtt.mtt_code = 'IMPROVEMENT' THEN 1 ELSE 0 END) as improvement_type_count,
                SUM(CASE WHEN mtt.mtt_code = 'RESEARCH' THEN 1 ELSE 0 END) as research_type_count,
                SUM(CASE WHEN t.tsk_due_date < NOW() AND ms.ms_code NOT IN ('DONE', 'CANCELLED') THEN 1 ELSE 0 END) as overdue_tasks
            FROM project p
            LEFT JOIN task t ON p.prj_id = t.tsk_prj_id
            LEFT JOIN master_status ms ON t.tsk_ms_id = ms.ms_id
            LEFT JOIN master_priority mp ON t.tsk_mp_id = mp.mp_id
            LEFT JOIN master_task_type mtt ON t.tsk_mtt_id = mtt.mtt_id
            WHERE p.prj_id = :prj_id
            GROUP BY p.prj_id, p.prj_name
        """

        result = self.execute_raw_sql_dict(db, query, {"prj_id": prj_id})

        if not result:
            return None

        row = result[0]

        # Calculate completion rate
        total = row.get("total_tasks", 0) or 0
        done = row.get("done_count", 0) or 0
        completion_rate = (done / total * 100) if total > 0 else 0

        return {
            "prj_id": row.get("prj_id"),
            "prj_name": row.get("prj_name"),
            "total_tasks": total,
            "by_status": {
                "TODO": row.get("todo_count", 0) or 0,
                "IN_PROGRESS": row.get("in_progress_count", 0) or 0,
                "IN_REVIEW": row.get("in_review_count", 0) or 0,
                "DONE": done,
                "CANCELLED": row.get("cancelled_count", 0) or 0
            },
            "by_priority": {
                "LOW": row.get("low_priority_count", 0) or 0,
                "MEDIUM": row.get("medium_priority_count", 0) or 0,
                "HIGH": row.get("high_priority_count", 0) or 0,
                "CRITICAL": row.get("critical_priority_count", 0) or 0
            },
            "by_type": {
                "TASK": row.get("task_type_count", 0) or 0,
                "BUG": row.get("bug_type_count", 0) or 0,
                "FEATURE": row.get("feature_type_count", 0) or 0,
                "IMPROVEMENT": row.get("improvement_type_count", 0) or 0,
                "RESEARCH": row.get("research_type_count", 0) or 0
            },
            "overdue_tasks": row.get("overdue_tasks", 0) or 0,
            "completion_rate": round(completion_rate, 2),
            "average_completion_time": None  # This would require more complex calculation
        }
