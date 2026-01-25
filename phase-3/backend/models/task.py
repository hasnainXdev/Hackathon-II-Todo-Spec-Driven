from datetime import datetime
from typing import List, Optional
import uuid
from sqlmodel import Field, SQLModel, Relationship
from pydantic import field_validator
from typing import TYPE_CHECKING
import sqlalchemy as sa
from sqlalchemy.types import String
from utils.types import GUID


if TYPE_CHECKING:
    from .user import User  # Import User for type checking
    from src.models.conversation import Message  # Import Message from src for type checking only


class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completion_status: bool = Field(default=False)
    user_id: str = Field(sa_column=sa.Column(sa.String, sa.ForeignKey("users.id"), nullable=False))
    due_date: Optional[datetime] = Field(default=None)  # Optional due date for the task
    priority: str = Field(default="medium", max_length=20)  # Task priority: low, medium, high


class Task(TaskBase, table=True):
    __tablename__ = "tasks"

    id: str = Field(
        sa_column=sa.Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4())),
        default_factory=lambda: str(uuid.uuid4())
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = Field(default=1)  # For optimistic locking

    # Relationships
    user: "User" = Relationship(back_populates="tasks")
    messages: List["src.models.conversation.Message"] = Relationship(back_populates="task")


class TaskCreate(TaskBase):
    user_id: Optional[str] = None  # Will be set from authenticated user, not from request


class TaskRead(TaskBase):
    id: str
    created_at: datetime
    updated_at: datetime
    version: int

    @field_validator('id', mode='before')
    @classmethod
    def validate_id(cls, v):
        """Ensure ID is always a string"""
        if isinstance(v, str):
            return v
        elif hasattr(v, '__str__'):
            return str(v)
        else:
            return v


class TaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completion_status: Optional[bool] = None
    due_date: Optional[datetime] = Field(default=None)  # Optional due date for the task
    priority: Optional[str] = Field(default=None, max_length=20)  # Task priority: low, medium, high
    version: Optional[int] = None  # For optimistic locking