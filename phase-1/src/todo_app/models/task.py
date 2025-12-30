"""
Task model representing a single todo item.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Task:
    """
    Represents a single todo item with a unique ID, title, description, and completion status.
    """
    id: int
    title: str
    description: str = ""
    completed: bool = False

    def __post_init__(self):
        """
        Validates the Task instance after initialization.
        """
        if not isinstance(self.id, int) or self.id <= 0:
            raise ValueError("Task ID must be a positive integer")
        
        if not isinstance(self.title, str):
            raise ValueError("Task title must be a string")
        
        if not self.title.strip():
            raise ValueError("Task title cannot be empty")
        
        if not isinstance(self.description, str):
            raise ValueError("Task description must be a string")
        
        if not isinstance(self.completed, bool):
            raise ValueError("Task completion status must be a boolean")