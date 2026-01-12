from . import task, user_preference

# Import all models here so they're registered with SQLModel
from .task import Task, TaskBase, TaskCreate, TaskRead, TaskUpdate
from .user_preference import UserPreference, UserPreferenceBase, UserPreferenceCreate, UserPreferenceRead, UserPreferenceUpdate

__all__ = [
    "Task",
    "TaskBase", 
    "TaskCreate",
    "TaskRead",
    "TaskUpdate",
    "UserPreference",
    "UserPreferenceBase",
    "UserPreferenceCreate",
    "UserPreferenceRead", 
    "UserPreferenceUpdate"
]