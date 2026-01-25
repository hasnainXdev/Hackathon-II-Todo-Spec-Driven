from datetime import datetime
from typing import List, Optional
from sqlmodel import Session, select
from models.task import Task, TaskCreate, TaskUpdate
from sqlalchemy.exc import NoResultFound
from utils.exceptions import TaskNotFoundException, TaskUpdateConflictException


class TaskService:
    def __init__(self, session: Session):
        self.session = session

    def create_task(self, task_data: TaskCreate, user_id: str) -> Task:
        """Create a new task for a user"""
        # Create the task with the user_id from the authenticated user
        task = Task(
            title=task_data.title,
            description=task_data.description,
            completion_status=task_data.completion_status,
            user_id=user_id,  # Use the user_id from the authenticated user
            due_date=task_data.due_date,
            priority=task_data.priority,
        )
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def get_task_by_id(self, task_id: str, user_id: str) -> Optional[Task]:
        """Get a specific task by ID for a user"""
        task = self.session.execute(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).scalar_one_or_none()
        return task

    def get_tasks_by_user(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[Task]:
        """Get all tasks for a specific user"""
        tasks = (
            self.session.execute(
                select(Task).where(Task.user_id == user_id).offset(skip).limit(limit)
            )
            .scalars()
            .all()
        )
        return tasks

    def update_task(
        self, task_id: str, task_data: TaskUpdate, user_id: str
    ) -> Optional[Task]:
        """Update a specific task for a user with optimistic locking"""
        # Get the current version of the task
        current_task = self.get_task_by_id(task_id, user_id)
        if not current_task:
            raise TaskNotFoundException(task_id)

        # Check if the version matches (optimistic locking)
        if task_data.version is not None and current_task.version != task_data.version:
            raise TaskUpdateConflictException(task_id)

        # Update the task
        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field != "version":  # Don't update the version field directly
                setattr(current_task, field, value)

        # Increment the version
        current_task.version += 1
        current_task.updated_at = datetime.utcnow()

        self.session.add(current_task)
        self.session.commit()
        self.session.refresh(current_task)
        return current_task

    def delete_task(self, task_id: str, user_id: str) -> bool:
        """Delete a specific task for a user"""
        from sqlmodel import select
        from models.task import Task
        from src.models.conversation import Message
        from sqlalchemy import text

        # Get the task without triggering relationship loading
        task = self.session.execute(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).scalar_one_or_none()

        if not task:
            raise TaskNotFoundException(task_id)

        # Delete related messages first to avoid foreign key constraint issues
        # Use raw SQL with explicit text casting to ensure UUID/string compatibility
        # Since both task_id and message.task_id are stored as strings, direct comparison should work
        self.session.execute(
            text("DELETE FROM message WHERE task_id = :task_id"),
            {"task_id": task_id}
        )

        # Now delete the task
        self.session.delete(task)
        self.session.commit()
        return True

    def toggle_completion(self, task_id: str, user_id: str) -> Optional[Task]:
        """Toggle the completion status of a task"""
        task = self.get_task_by_id(task_id, user_id)
        if not task:
            raise TaskNotFoundException(task_id)

        task.completion_status = not task.completion_status
        task.version += 1  # Increment version for optimistic locking
        task.updated_at = datetime.utcnow()

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task
