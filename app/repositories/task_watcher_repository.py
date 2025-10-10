"""
Task Watcher Repository
"""
from typing import Optional
from sqlalchemy.orm import Session

from atams.db import BaseRepository
from app.models.task_watcher import TaskWatcher


class TaskWatcherRepository(BaseRepository[TaskWatcher]):
    def __init__(self):
        super().__init__(TaskWatcher)

    def get_watched_tasks_by_user(
        self,
        db: Session,
        u_id: int,
        skip: int = 0,
        limit: int = 100,
        status_id: Optional[int] = None
    ):
        """Get tasks watched by specific user with JOIN"""
        query = """
            SELECT t.*, tw.created_at as watched_at,
                   ms.ms_name as status_name,
                   mp.mp_name as priority_name,
                   p.prj_name as project_name,
                   mtt.mtt_name as type_name
            FROM atask.task_watcher tw
            JOIN atask.task t ON tw.tw_tsk_id = t.tsk_id
            LEFT JOIN atask.master_status ms ON t.tsk_ms_id = ms.ms_id
            LEFT JOIN atask.master_priority mp ON t.tsk_mp_id = mp.mp_id
            LEFT JOIN atask.project p ON t.tsk_prj_id = p.prj_id
            LEFT JOIN atask.master_task_type mtt ON t.tsk_mtt_id = mtt.mtt_id
            WHERE tw.tw_u_id = :u_id
        """

        params = {"u_id": u_id, "skip": skip, "limit": limit}

        if status_id:
            query += " AND t.tsk_ms_id = :status_id"
            params["status_id"] = status_id

        query += " ORDER BY tw.created_at DESC LIMIT :limit OFFSET :skip"

        return self.execute_raw_sql_dict(db, query, params)

    def count_watched_tasks_by_user(
        self,
        db: Session,
        u_id: int,
        status_id: Optional[int] = None
    ) -> int:
        """Count watched tasks by user"""
        query = """
            SELECT COUNT(*) as count
            FROM atask.task_watcher tw
            JOIN atask.task t ON tw.tw_tsk_id = t.tsk_id
            WHERE tw.tw_u_id = :u_id
        """

        params = {"u_id": u_id}

        if status_id:
            query += " AND t.tsk_ms_id = :status_id"
            params["status_id"] = status_id

        result = self.execute_raw_sql_dict(db, query, params)
        return result[0]["count"] if result else 0
