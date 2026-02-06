from typing import List, Optional, Dict, Any
from sqlmodel import Session, select
from uuid import UUID
from datetime import datetime
import logging
from ..models.task import Task, TaskStatusEnum, PriorityEnum
from ..database.init import get_db_session
from ..kafka.publishers import EventPublisher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskService:
    def __init__(self):
        self.event_publisher = EventPublisher()
    
    def create_task(self, 
                   title: str, 
                   description: Optional[str], 
                   priority: PriorityEnum, 
                   tags: Optional[List[str]], 
                   due_date: Optional[datetime], 
                   recurrence_rule: Optional[str], 
                   user_id: UUID) -> Task:
        """Create a new task and publish TASK_CREATED event."""
        with get_db_session() as session:
            task = Task(
                title=title,
                description=description,
                priority=priority,
                tags=tags or [],
                due_date=due_date,
                recurrence_rule=recurrence_rule,
                user_id=user_id
            )
            
            session.add(task)
            session.commit()
            session.refresh(task)
            
            # Publish event to Kafka
            import asyncio
            asyncio.create_task(self.event_publisher.publish_task_created(task, str(user_id)))
            
            logger.info(f"Task created with ID: {task.id}")
            return task
    
    def get_task_by_id(self, task_id: UUID, user_id: UUID) -> Optional[Task]:
        """Retrieve a task by its ID for a specific user."""
        with get_db_session() as session:
            statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
            task = session.exec(statement).first()
            return task
    
    def get_tasks_by_user(self, 
                         user_id: UUID, 
                         priority: Optional[PriorityEnum] = None, 
                         completed: Optional[bool] = None, 
                         tag: Optional[str] = None,
                         sort_by: Optional[str] = 'created_at',
                         order: Optional[str] = 'asc') -> List[Task]:
        """Retrieve all tasks for a specific user with optional filters."""
        with get_db_session() as session:
            statement = select(Task).where(Task.user_id == user_id)
            
            if priority:
                statement = statement.where(Task.priority == priority)
            if completed is not None:
                statement = statement.where(Task.completed == completed)
            if tag:
                # Using a raw SQL expression to check if the tag exists in the tags array
                statement = statement.where(f"'{tag}' = ANY(tags)")
            
            # Add sorting
            if sort_by == 'created_at':
                if order == 'desc':
                    statement = statement.order_by(Task.created_at.desc())
                else:
                    statement = statement.order_by(Task.created_at.asc())
            elif sort_by == 'due_date':
                if order == 'desc':
                    statement = statement.order_by(Task.due_date.desc())
                else:
                    statement = statement.order_by(Task.due_date.asc())
            elif sort_by == 'priority':
                if order == 'desc':
                    statement = statement.order_by(Task.priority.desc())
                else:
                    statement = statement.order_by(Task.priority.asc())
            
            tasks = session.exec(statement).all()
            return tasks
    
    def update_task(self, 
                   task_id: UUID, 
                   user_id: UUID, 
                   title: Optional[str] = None, 
                   description: Optional[str] = None, 
                   priority: Optional[PriorityEnum] = None, 
                   tags: Optional[List[str]] = None, 
                   due_date: Optional[datetime] = None, 
                   completed: Optional[bool] = None) -> Optional[Task]:
        """Update an existing task and publish TASK_UPDATED event."""
        with get_db_session() as session:
            statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
            task = session.exec(statement).first()
            
            if not task:
                return None
            
            # Track which fields are being updated
            updated_fields = []
            
            if title is not None:
                task.title = title
                updated_fields.append('title')
            if description is not None:
                task.description = description
                updated_fields.append('description')
            if priority is not None:
                task.priority = priority
                updated_fields.append('priority')
            if tags is not None:
                task.tags = tags
                updated_fields.append('tags')
            if due_date is not None:
                task.due_date = due_date
                updated_fields.append('due_date')
            if completed is not None:
                task.completed = completed
                task.completed_at = datetime.utcnow() if completed else None
                updated_fields.append('completed')
            
            # Update the version for optimistic locking
            task.version += 1
            
            session.add(task)
            session.commit()
            session.refresh(task)
            
            # Publish event to Kafka
            import asyncio
            asyncio.create_task(self.event_publisher.publish_task_updated(task, str(user_id), updated_fields))
            
            logger.info(f"Task updated with ID: {task.id}")
            return task
    
    def complete_task(self, task_id: UUID, user_id: UUID) -> Optional[Task]:
        """Mark a task as completed and publish TASK_COMPLETED event."""
        with get_db_session() as session:
            statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
            task = session.exec(statement).first()
            
            if not task:
                return None
            
            task.completed = True
            task.completed_at = datetime.utcnow()
            task.version += 1
            
            session.add(task)
            session.commit()
            session.refresh(task)
            
            # Publish event to Kafka
            import asyncio
            asyncio.create_task(self.event_publisher.publish_task_completed(task, str(user_id)))
            
            logger.info(f"Task completed with ID: {task.id}")
            return task
    
    def delete_task(self, task_id: UUID, user_id: UUID) -> bool:
        """Delete a task and publish TASK_DELETED event."""
        with get_db_session() as session:
            statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
            task = session.exec(statement).first()
            
            if not task:
                return False
            
            session.delete(task)
            session.commit()
            
            # Publish event to Kafka
            import asyncio
            asyncio.create_task(self.event_publisher.publish_task_deleted(str(task_id), str(user_id)))
            
            logger.info(f"Task deleted with ID: {task.id}")
            return True
    
    def search_tasks(self,
                   user_id: UUID,
                   search_term: str,
                   priority: Optional[PriorityEnum] = None,
                   completed: Optional[bool] = None,
                   tag: Optional[str] = None) -> List[Task]:
        """Search tasks by content with optional filters."""
        with get_db_session() as session:
            statement = select(Task).where(
                Task.user_id == user_id,
                (Task.title.contains(search_term)) | (Task.description.contains(search_term))
            )

            if priority:
                statement = statement.where(Task.priority == priority)
            if completed is not None:
                statement = statement.where(Task.completed == completed)
            if tag:
                # For searching tags, we need to use a different approach since JSON arrays
                # in PostgreSQL require special handling
                # Using a raw SQL expression to check if the tag exists in the tags array
                statement = statement.where(f"'{tag}' = ANY(tags)")

            tasks = session.exec(statement).all()
            return tasks