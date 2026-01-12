from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    completion_status: bool = False


class TaskCreate(TaskBase):
    title: str  # Required field


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completion_status: Optional[bool] = None
    version: Optional[int] = None  # For optimistic locking


class TaskRead(TaskBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    version: int

    class Config:
        from_attributes = True