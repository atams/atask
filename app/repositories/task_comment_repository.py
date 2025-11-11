"""
Task Comment Repository
"""
from sqlalchemy.orm import Session
from atams.db import BaseRepository
from app.models.task_comment import TaskComment


class TaskCommentRepository(BaseRepository[TaskComment]):
    def __init__(self):
        super().__init__(TaskComment)

    def get_comments_with_joins(self, db: Session, skip: int = 0, limit: int = 100):
        """
        Get comments with all related data in single query (optimized for performance)
        This eliminates N+1 query problem by using JOINs
        """
        query = """
            SELECT
                tc.tc_id, tc.tc_tsk_id, tc.tc_u_id, tc.tc_comment, tc.tc_parent_tc_id,
                tc.created_by, tc.created_at, tc.updated_by, tc.updated_at,
                -- Joined data
                t.tsk_title as tc_task_title,
                u.u_full_name as tc_user_name,
                u.u_email as tc_user_email
            FROM atask.task_comment tc
            LEFT JOIN atask.task t ON tc.tc_tsk_id = t.tsk_id
            LEFT JOIN pt_atams_indonesia.users u ON tc.tc_u_id = u.u_id
            ORDER BY tc.created_at DESC
            LIMIT :limit OFFSET :skip
        """

        params = {"skip": skip, "limit": limit}
        return self.execute_raw_sql_dict(db, query, params)
