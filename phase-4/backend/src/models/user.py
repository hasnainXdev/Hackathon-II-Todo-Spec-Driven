from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from datetime import datetime
from uuid import uuid4
import sqlalchemy as sa
from sqlalchemy import Column, String, DateTime
from utils.types import GUID


class UserBase(SQLModel):
    email: str = Field(sa_column=sa.Column("email", String, unique=True, index=True, nullable=False))
    name: str = Field(sa_column=sa.Column("name", String, nullable=False))


class User(UserBase, table=True):
    __tablename__ = "users"

    id: str = Field(
        sa_column=sa.Column(sa.String, primary_key=True, default=lambda: str(uuid4())),
        default_factory=lambda: str(uuid4())
    )
    password_hash: Optional[str] = Field(default=None, sa_column=sa.Column("password_hash", String))
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=sa.Column("created_at", DateTime(timezone=True), nullable=False)
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=sa.Column("updated_at", DateTime(timezone=True), nullable=False)
    )

    # Relationships - using string references to avoid circular imports
    # Note: Better Auth handles user authentication, but we still need to define relationships
    tasks: List["models.task.Task"] = Relationship(back_populates="user")
    conversations: List["src.models.conversation.Conversation"] = Relationship(back_populates="user")
    messages: List["src.models.conversation.Message"] = Relationship(back_populates="user")


# Forward reference for rebuild after all classes are defined
User.model_rebuild()