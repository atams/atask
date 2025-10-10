"""
Task Service
Business logic layer with role-based permission validation
"""
from typing import List
from sqlalchemy.orm import Session

from app.repositories.task_repository import TaskRepository
from app.repositories.master_task_type_repository import MasterTaskTypeRepository
from app.repositories.task_history_repository import TaskHistoryRepository
from app.schemas.task_schema import TaskCreate, TaskUpdate, Task
from atams.exceptions import NotFoundException, ForbiddenException, BadRequestException


class TaskService:
    def __init__(self):
        self.repository = TaskRepository()
        self.master_task_type_repository = MasterTaskTypeRepository()
        self.history_repository = TaskHistoryRepository()

    def _track_changes(self, db: Session, task_id: int, old_task, new_data: dict, user_id: int):
        """Track changes to task fields and create history records"""
        # Fields to track for changes
        tracked_fields = {
            "tsk_title": "title",
            "tsk_description": "description",
            "tsk_ms_id": "status",
            "tsk_mp_id": "priority",
            "tsk_assignee_u_id": "assignee",
            "tsk_due_date": "due_date",
            "tsk_start_date": "start_date"
        }

        for field_key, field_name in tracked_fields.items():
            if field_key in new_data:
                old_value = getattr(old_task, field_key, None)
                new_value = new_data[field_key]

                # Convert to string for comparison
                old_str = str(old_value) if old_value is not None else None
                new_str = str(new_value) if new_value is not None else None

                # Only create history if value actually changed
                if old_str != new_str:
                    history_data = {
                        "th_tsk_id": task_id,
                        "th_field_name": field_name,
                        "th_old_value": old_str,
                        "th_new_value": new_str,
                        "th_u_id": user_id,
                        "created_by": str(user_id)
                    }
                    self.history_repository.create(db, history_data)

    def get_task(
        self,
        db: Session,
        tsk_id: int,
        current_user_role_level: int,
        current_user_id: int
    ) -> Task:
        """Get single task by ID"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to view task")

        db_task = self.repository.get(db, tsk_id)
        if not db_task:
            raise NotFoundException(f"Task with ID {tsk_id} not found")

        return Task.model_validate(db_task)

    def get_tasks(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        current_user_role_level: int = 0
    ) -> List[Task]:
        """Get list of tasks with pagination"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to list tasks")

        db_tasks = self.repository.get_multi(db, skip=skip, limit=limit)
        return [Task.model_validate(tsk) for tsk in db_tasks]

    def create_task(
        self,
        db: Session,
        task: TaskCreate,
        current_user_role_level: int,
        current_user_id: int
    ) -> Task:
        """Create new task with auto-generated tsk_code"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to create task")

        # Get the task type to retrieve its code
        db_task_type = self.master_task_type_repository.get(db, task.tsk_mtt_id)
        if not db_task_type:
            raise NotFoundException(f"Master task type with ID {task.tsk_mtt_id} not found")

        # Validate project exists if provided
        if task.tsk_prj_id is None:
            raise BadRequestException("Project ID is required to create a task")

        # Auto-generate task code
        task_type_code = db_task_type.mtt_code
        auto_generated_code = self.repository.get_next_task_number_for_project(
            db, task.tsk_prj_id, task_type_code
        )

        # Add created_by and override tsk_code
        data = task.model_dump()
        data["tsk_code"] = auto_generated_code  # Override any user-provided code
        data["created_by"] = str(current_user_id)

        db_task = self.repository.create(db, data)
        return Task.model_validate(db_task)

    def update_task(
        self,
        db: Session,
        tsk_id: int,
        task: TaskUpdate,
        current_user_role_level: int,
        current_user_id: int
    ) -> Task:
        """Update existing task with automatic history tracking"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to update task")

        db_task = self.repository.get(db, tsk_id)
        if not db_task:
            raise NotFoundException(f"Task with ID {tsk_id} not found")

        update_data = task.model_dump(exclude_unset=True)
        update_data["updated_by"] = str(current_user_id)

        # Track changes before updating
        self._track_changes(db, tsk_id, db_task, update_data, current_user_id)

        db_task = self.repository.update(db, db_task, update_data)
        return Task.model_validate(db_task)

    def delete_task(
        self,
        db: Session,
        tsk_id: int,
        current_user_role_level: int
    ) -> None:
        """Delete task"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission to delete task")

        deleted = self.repository.delete(db, tsk_id)
        if not deleted:
            raise NotFoundException(f"Task with ID {tsk_id} not found")

    def get_total_tasks(self, db: Session) -> int:
        """Get total count of tasks"""
        return self.repository.count(db)

    def get_user_dashboard(self, db: Session, u_id: int, current_user_role_level: int):
        """Get user dashboard with task statistics"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission")

        # Use native SQL to get dashboard data
        query = """
            SELECT
                COUNT(*) FILTER (WHERE tsk_assignee_u_id = :u_id) as assigned_total,
                COUNT(*) FILTER (WHERE tsk_assignee_u_id = :u_id AND ms.ms_code = 'TODO') as assigned_todo,
                COUNT(*) FILTER (WHERE tsk_assignee_u_id = :u_id AND ms.ms_code = 'IN_PROGRESS') as assigned_in_progress,
                COUNT(*) FILTER (WHERE tsk_assignee_u_id = :u_id AND ms.ms_code = 'IN_REVIEW') as assigned_in_review,
                COUNT(*) FILTER (WHERE tsk_assignee_u_id = :u_id AND ms.ms_code = 'DONE') as assigned_done,
                COUNT(*) FILTER (WHERE tsk_assignee_u_id = :u_id AND tsk_due_date < NOW() AND ms.ms_code NOT IN ('DONE', 'CANCELLED')) as assigned_overdue,
                COUNT(*) FILTER (WHERE tsk_reporter_u_id = :u_id) as reported_total,
                COUNT(*) FILTER (WHERE tsk_reporter_u_id = :u_id AND ms.ms_code NOT IN ('DONE', 'CANCELLED')) as reported_pending,
                COUNT(*) FILTER (WHERE tsk_reporter_u_id = :u_id AND ms.ms_code IN ('DONE', 'CANCELLED')) as reported_completed
            FROM atask.task t
            LEFT JOIN atask.master_status ms ON t.tsk_ms_id = ms.ms_id
        """

        result = self.repository.execute_raw_sql_dict(db, query, {"u_id": u_id})
        return result[0] if result else {}

    def bulk_update_status(self, db: Session, task_ids: List[int], ms_id: int, current_user_role_level: int, current_user_id: int):
        """Bulk update task status"""
        if current_user_role_level < 10:
            raise ForbiddenException("Insufficient permission")

        # Get all tasks by IDs
        tasks = []
        for task_id in task_ids:
            task = self.repository.get(db, task_id)
            if task:
                tasks.append(task)

        # Update status for all tasks
        updated_tasks = []
        for task in tasks:
            task.tsk_ms_id = ms_id
            task.updated_by = str(current_user_id)
            updated_tasks.append(task)

        # Bulk update
        self.repository.bulk_update(db, updated_tasks)

        return {
            "updated_count": len(updated_tasks),
            "task_ids": task_ids
        }
