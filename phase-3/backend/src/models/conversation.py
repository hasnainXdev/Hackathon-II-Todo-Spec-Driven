from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from uuid import uuid4
import sqlalchemy as sa
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from enum import Enum
from utils.types import GUID

if TYPE_CHECKING:
    from .user import User  # Import User model only for type checking
    from models.task import Task  # Import Task model from the models directory only for type checking


class MessageType(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationBase(SQLModel):
    title: str = Field(default="New Conversation", max_length=255)


class Conversation(ConversationBase, table=True):
    __tablename__ = "conversation"

    id: str = Field(
        sa_column=sa.Column(sa.String, primary_key=True, default=lambda: str(uuid4())),
        default_factory=lambda: str(uuid4())
    )
    user_id: str = Field(sa_column=sa.Column(sa.String, sa.ForeignKey("users.id"), nullable=False))
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column("created_at", DateTime(timezone=True), nullable=False)
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column("updated_at", DateTime(timezone=True), nullable=False)
    )

    # Relationships
    user: "User" = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")


class MessageBase(SQLModel):
    role: MessageType = Field(sa_column=Column("role", String, nullable=False))  # Using enum
    content: str = Field(sa_column=Column("content", Text, nullable=False))
    # Note: Using created_at instead of timestamp to match database schema


class Message(MessageBase, table=True):
    __tablename__ = "message"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(sa_column=sa.Column(sa.String, sa.ForeignKey("users.id"), nullable=False))
    conversation_id: str = Field(sa_column=sa.Column(sa.String, sa.ForeignKey("conversation.id"), nullable=False))
    task_id: Optional[str] = Field(sa_column=sa.Column(GUID(), sa.ForeignKey("tasks.id"), nullable=True))
    # Use timestamp field that maps to the created_at column in the database
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column("created_at", DateTime(timezone=True), nullable=False)
    )

    # Add alias for backward compatibility
    @property
    def created_at(self):
        return self.timestamp

    # Relationships
    user: "User" = Relationship(back_populates="messages")
    conversation: "Conversation" = Relationship(back_populates="messages")
    task: Optional["models.task.Task"] = Relationship(back_populates="messages")


# Pydantic models for API requests/responses
class MessageCreate(MessageBase):
    pass


class MessageRead(MessageBase):
    id: str
    user_id: str
    conversation_id: str
    timestamp: datetime


class ConversationCreate(ConversationBase):
    pass


class ConversationRead(ConversationBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime


# Forward references need to be set after all classes are defined
Conversation.model_rebuild()
Message.model_rebuild()