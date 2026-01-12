from datetime import datetime
from typing import Optional
import uuid
from sqlmodel import Field, SQLModel


class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completion_status: bool = Field(default=False)
    user_id: str  # UUID of the user from Better Auth


class Task(TaskBase, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = Field(default=1)  # For optimistic locking


class TaskCreate(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completion_status: bool = Field(default=False)


class TaskRead(TaskBase):
    id: str
    created_at: datetime
    updated_at: datetime
    version: int


class TaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completion_status: Optional[bool] = None
    version: Optional[int] = None  # For optimistic locking