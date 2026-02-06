# Import all models here so they're registered with SQLModel
from .task import Task, TaskBase, TaskCreate, TaskRead, TaskUpdate

# Import models from src to ensure they're registered with SQLModel
# Use only the src models to avoid duplication
from src.models.user import User, UserBase
from src.models.conversation import Conversation, Message, ConversationBase, MessageBase, ConversationCreate, ConversationRead, MessageCreate, MessageRead

__all__ = [
    "User",
    "UserBase",
    "Task",
    "TaskBase",
    "TaskCreate",
    "TaskRead",
    "TaskUpdate",
    "Conversation",
    "Message",
    "ConversationBase",
    "MessageBase",
    "ConversationCreate",
    "ConversationRead",
    "MessageCreate",
    "MessageRead"
]