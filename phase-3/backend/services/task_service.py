from datetime import datetime
from typing import List, Optional
from sqlmodel import Session, select, func
from models.task import Task, TaskCreate, TaskUpdate
from sqlalchemy.exc import NoResultFound
from sqlalchemy import text, and_
from utils.exceptions import TaskNotFoundException, TaskUpdateConflictException
from utils.tag_utils import sanitize_and_validate_tags
import json


class TaskService:
    def __init__(self, session: Session):
        self.session = session

    def create_task(self, task_data: TaskCreate, user_id: str) -> Task:
        """Create a new task for a user"""
        # Sanitize and validate tags
        tags = task_data.tags if task_data.tags is not None else []
        sanitized_tags = sanitize_and_validate_tags(tags)
        
        # Create the task with the user_id from the authenticated user
        task = Task(
            title=task_data.title,
            description=task_data.description,
            completion_status=task_data.completion_status,
            user_id=user_id,  # Use the user_id from the authenticated user
            due_date=task_data.due_date,
            priority=task_data.priority,
            tags=sanitized_tags,
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
        self, 
        user_id: str, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None,
        priority: Optional[str] = None,
        tag: Optional[str] = None,
        completed: Optional[bool] = None,
        sort: Optional[str] = None,
        order: Optional[str] = None
    ) -> List[Task]:
        """
        Get all tasks for a specific user with optional search, filter, and sort
        """
        # Start with the base query
        query = select(Task).where(Task.user_id == user_id)
        
        # Apply search if provided
        if search:
            search_lower = search.lower()
            # Search in title and description
            query = query.where(
                (Task.title.ilike(f"%{search}%")) |
                (Task.description.ilike(f"%{search}%"))
            )
            # For tag search, we'll need to handle it differently since tags are stored as JSON
            # We'll filter the results after fetching if search term might match a tag
        
        # Apply filters
        if priority:
            query = query.where(Task.priority == priority.lower())
        
        if completed is not None:
            query = query.where(Task.completion_status == completed)
        
        # Apply sorting
        if sort:
            sort_attr = getattr(Task, sort, None)
            if sort_attr:
                if order and order.lower() == 'asc':
                    query = query.order_by(sort_attr.asc())
                else:
                    query = query.order_by(sort_attr.desc())
            else:
                # Fallback to default sorting if invalid sort field
                query = query.order_by(Task.created_at.desc())
        else:
            # Default sorting
            query = query.order_by(Task.created_at.desc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        tasks = self.session.execute(query).scalars().all()
        
        # Apply tag filter and search in tags after fetching (since tags are JSON)
        if tag:
            tasks = [task for task in tasks if tag in task.tags]
        
        if search and not tag:  # Only apply tag search if not already filtering by specific tag
            search_lower = search.lower()
            tasks = [task for task in tasks if 
                     search_lower in task.title.lower() or 
                     (task.description and search_lower in task.description.lower()) or
                     search_lower in [t.lower() for t in task.tags]]
        
        if search and tag:  # If both search and tag are specified
            search_lower = search.lower()
            tasks = [task for task in tasks if 
                     tag in task.tags and
                     (search_lower in task.title.lower() or 
                      (task.description and search_lower in task.description.lower()) or
                      search_lower in [t.lower() for t in task.tags])]
        
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
        
        # Handle tags separately to sanitize and validate them
        if 'tags' in update_data and update_data['tags'] is not None:
            update_data['tags'] = sanitize_and_validate_tags(update_data['tags'])
        
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
