from datetime import datetime
from typing import List, Optional
import uuid
from sqlmodel import Field, SQLModel, Relationship
from pydantic import field_validator
from typing import TYPE_CHECKING
import sqlalchemy as sa
from sqlalchemy.types import String
from utils.types import GUID
import json
from sqlalchemy.types import TypeDecorator


# Custom type to handle JSON arrays in the database
class JSONArray(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if value is not None:
            if isinstance(value, list):
                return json.dumps(value)
            else:
                # If it's a string representation of a list, return as is
                return value
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except (ValueError, TypeError):
                    # If it's not valid JSON, return as is
                    return value
            elif isinstance(value, list):
                return value
        return []


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
    tags: Optional[List[str]] = Field(default=[], sa_column=sa.Column(JSONArray))  # Tags for categorization


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
    tags: Optional[List[str]] = []  # Initialize with empty list

    @field_validator('priority', mode='before')
    @classmethod
    def validate_priority(cls, v):
        """Validate priority is one of the allowed values"""
        if v is None:
            return "medium"  # Default value
        if isinstance(v, str) and v.lower() in ['low', 'medium', 'high']:
            return v.lower()
        raise ValueError(f"Priority must be one of 'low', 'medium', 'high', got '{v}'")

    @field_validator('tags', mode='before')
    @classmethod
    def validate_tags(cls, v):
        """Validate tags according to requirements"""
        if v is None:
            return []
        
        if not isinstance(v, list):
            v = [v] if v else []
        
        # Validate each tag
        for tag in v:
            if not isinstance(tag, str):
                raise ValueError(f"All tags must be strings, got {type(tag)}")
            
            if len(tag) < 2 or len(tag) > 20:
                raise ValueError(f"Each tag must be 2-20 characters, got '{tag}' with length {len(tag)}")
        
        # Limit to 10 tags
        if len(v) > 10:
            raise ValueError(f"Maximum 10 tags allowed, got {len(v)} tags")
        
        # Convert to lowercase and remove duplicates
        v = [tag.strip().lower() for tag in v]
        v = list(dict.fromkeys(v))  # Remove duplicates while preserving order
        
        return v


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

    @field_validator('priority', mode='before')
    @classmethod
    def validate_priority(cls, v):
        """Validate priority is one of the allowed values"""
        if v is None:
            return "medium"
        if isinstance(v, str) and v.lower() in ['low', 'medium', 'high']:
            return v.lower()
        raise ValueError(f"Priority must be one of 'low', 'medium', 'high', got '{v}'")

    @field_validator('tags', mode='before')
    @classmethod
    def validate_tags(cls, v):
        """Validate tags according to requirements"""
        if v is None:
            return []
        
        if not isinstance(v, list):
            v = [v] if v else []
        
        # Validate each tag
        for tag in v:
            if not isinstance(tag, str):
                raise ValueError(f"All tags must be strings, got {type(tag)}")
            
            if len(tag) < 2 or len(tag) > 20:
                raise ValueError(f"Each tag must be 2-20 characters, got '{tag}' with length {len(tag)}")
        
        # Limit to 10 tags
        if len(v) > 10:
            raise ValueError(f"Maximum 10 tags allowed, got {len(v)} tags")
        
        # Convert to lowercase and remove duplicates
        v = [tag.strip().lower() for tag in v]
        v = list(dict.fromkeys(v))  # Remove duplicates while preserving order
        
        return v


class TaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completion_status: Optional[bool] = None
    due_date: Optional[datetime] = Field(default=None)  # Optional due date for the task
    priority: Optional[str] = Field(default=None, max_length=20)  # Task priority: low, medium, high
    tags: Optional[List[str]] = None  # Tags for categorization
    version: Optional[int] = None  # For optimistic locking

    @field_validator('priority', mode='before')
    @classmethod
    def validate_priority(cls, v):
        """Validate priority is one of the allowed values"""
        if v is None:
            return v  # Allow None to pass through for optional updates
        if isinstance(v, str) and v.lower() in ['low', 'medium', 'high']:
            return v.lower()
        raise ValueError(f"Priority must be one of 'low', 'medium', 'high', got '{v}'")

    @field_validator('tags', mode='before')
    @classmethod
    def validate_tags(cls, v):
        """Validate tags according to requirements"""
        if v is None:
            return v  # Allow None to pass through for optional updates
        
        if not isinstance(v, list):
            v = [v] if v else []
        
        # Validate each tag
        for tag in v:
            if not isinstance(tag, str):
                raise ValueError(f"All tags must be strings, got {type(tag)}")
            
            if len(tag) < 2 or len(tag) > 20:
                raise ValueError(f"Each tag must be 2-20 characters, got '{tag}' with length {len(tag)}")
        
        # Limit to 10 tags
        if len(v) > 10:
            raise ValueError(f"Maximum 10 tags allowed, got {len(v)} tags")
        
        # Convert to lowercase and remove duplicates
        v = [tag.strip().lower() for tag in v]
        v = list(dict.fromkeys(v))  # Remove duplicates while preserving order
        
        return v