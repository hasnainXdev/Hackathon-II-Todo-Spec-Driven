from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserPreferenceBase(BaseModel):
    user_id: str
    preference_key: str
    preference_value: str


class UserPreferenceCreate(UserPreferenceBase):
    preference_key: str
    preference_value: str


class UserPreferenceUpdate(BaseModel):
    preference_key: Optional[str] = None
    preference_value: Optional[str] = None


class UserPreferenceRead(UserPreferenceBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True