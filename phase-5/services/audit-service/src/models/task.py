from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, create_engine, Session
from sqlalchemy import JSON
from uuid import UUID, uuid4
import enum


class PriorityEnum(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TaskStatusEnum(str, enum.Enum):
    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    RECURRING_CREATED_NEXT = "RECURRING_CREATED_NEXT"
    ARCHIVED = "ARCHIVED"


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None)
    priority: PriorityEnum = Field(default=PriorityEnum.MEDIUM)
    tags: Optional[List[str]] = Field(default=None, sa_column_kwargs={"type_": JSON})
    due_date: Optional[datetime] = Field(default=None)
    completed: bool = Field(default=False)
    completed_at: Optional[datetime] = Field(default=None)
    recurrence_rule: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: UUID
    last_event_id: Optional[UUID] = Field(default=None)
    version: int = Field(default=1)  # For optimistic locking

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure updated_at is set to current time when initialized
        if not self.updated_at or self.updated_at == self.created_at:
            self.updated_at = datetime.utcnow()


class Event(SQLModel, table=True):
    __tablename__ = "events"

    event_id: UUID = Field(default_factory=uuid4, primary_key=True)
    event_type: str = Field(sa_column_kwargs={"comment": "TASK_CREATED, TASK_UPDATED, TASK_COMPLETED, TASK_DELETED, RECURRING_TRIGGERED, REMINDER_DUE, TASK_ASSIGNED, TASK_PRIORITY_CHANGED"})
    aggregate_id: UUID = Field(description="ID of the entity the event relates to (usually Task.id)")
    aggregate_type: str = Field(description="Type of aggregate (e.g., 'Task', 'User')")
    payload: dict = Field(sa_column_kwargs={"comment": "Data associated with the event, varies by event_type"})
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_context: dict = Field(sa_column_kwargs={"comment": "Information about the user who initiated the action"})
    correlation_id: Optional[UUID] = Field(default=None, description="Links related events together (from the same user command)")
    causation_id: Optional[UUID] = Field(default=None, description="References the event that caused this event")
    version: int = Field(default=1, description="Version of the event schema")
    source_service: str = Field(description="Name of the service that generated the event")


class User(SQLModel, table=True):
    __tablename__ = "users"

    user_id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(max_length=50, unique=True)
    email: str = Field(unique=True)
    preferences: dict = Field(default={})
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: Optional[datetime] = Field(default=None)
    timezone: str = Field(default="UTC")