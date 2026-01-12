from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class UserPreferenceBase(SQLModel):
    user_id: str  # UUID of the user from Better Auth
    preference_key: str = Field(min_length=1, max_length=100)
    preference_value: str = Field(min_length=1, max_length=500)


class UserPreference(UserPreferenceBase, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserPreferenceCreate(UserPreferenceBase):
    pass


class UserPreferenceRead(UserPreferenceBase):
    id: str
    created_at: datetime
    updated_at: datetime


class UserPreferenceUpdate(SQLModel):
    preference_key: Optional[str] = Field(default=None, min_length=1, max_length=100)
    preference_value: Optional[str] = Field(default=None, min_length=1, max_length=500)