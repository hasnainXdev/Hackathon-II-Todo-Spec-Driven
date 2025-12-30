"""
Persistent in-memory storage for tasks using a temporary file.
This simulates in-memory storage but persists between CLI commands in the same session.
"""
import json
import os
import tempfile
from typing import Dict, List, Optional, Any
from pathlib import Path

from todo_app.models.task import Task


class PersistentTaskStorage:
    """
    A storage class that persists tasks to a temporary file to simulate
    in-memory storage that persists between CLI command calls.
    """

    def __init__(self, use_test_storage=False):
        # Use a different storage file for tests to avoid conflicts
        if use_test_storage:
            # For tests, use a truly in-memory approach (no file persistence)
            self.storage_file = None
            self._tasks: Dict[int, Task] = {}
            self._next_id: int = 1
        else:
            self.storage_file = Path(tempfile.gettempdir()) / "todo_app_storage.json"
            self._tasks: Dict[int, Task] = {}
            self._next_id: int = 1
            self._load_from_file()
    
    def _load_from_file(self):
        """Load tasks from the storage file if it exists."""
        if self.storage_file is None:
            # For test storage, just initialize empty
            self._tasks = {}
            self._next_id = 1
        elif self.storage_file.exists():
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    self._next_id = data.get('next_id', 1)
                    tasks_data = data.get('tasks', {})
                    # Convert dict back to Task objects
                    self._tasks = {}
                    for task_id, task_dict in tasks_data.items():
                        task_id = int(task_id)  # Ensure it's an int
                        task = Task(
                            id=task_dict['id'],
                            title=task_dict['title'],
                            description=task_dict['description'],
                            completed=task_dict['completed']
                        )
                        self._tasks[task_id] = task
                        # Update next_id if needed
                        if task_id >= self._next_id:
                            self._next_id = task_id + 1
            except (json.JSONDecodeError, KeyError, ValueError):
                # If there's an error loading, start fresh
                self._tasks = {}
                self._next_id = 1
        else:
            self._tasks = {}
            self._next_id = 1
    
    def _save_to_file(self):
        """Save tasks to the storage file."""
        if self.storage_file is None:
            # For test storage, don't save to file
            return

        data = {
            'next_id': self._next_id,
            'tasks': {str(task_id): {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'completed': task.completed
            } for task_id, task in self._tasks.items()}
        }
        with open(self.storage_file, 'w') as f:
            json.dump(data, f)
    
    def get_all_tasks(self) -> List[Task]:
        """Get all tasks."""
        return list(self._tasks.values())
    
    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Get a task by ID."""
        return self._tasks.get(task_id)
    
    def add_task(self, task: Task) -> Task:
        """Add a task."""
        self._tasks[task.id] = task
        if task.id >= self._next_id:
            self._next_id = task.id + 1
        self._save_to_file()
        return task
    
    def update_task(self, task_id: int, title: Optional[str] = None, description: Optional[str] = None) -> Optional[Task]:
        """Update a task."""
        if task_id not in self._tasks:
            return None
        
        task = self._tasks[task_id]
        
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        
        self._save_to_file()
        return task
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task."""
        if task_id in self._tasks:
            del self._tasks[task_id]
            self._save_to_file()
            return True
        return False
    
    def mark_complete(self, task_id: int) -> bool:
        """Mark a task as complete."""
        if task_id in self._tasks:
            self._tasks[task_id].completed = True
            self._save_to_file()
            return True
        return False
    
    def mark_incomplete(self, task_id: int) -> bool:
        """Mark a task as incomplete."""
        if task_id in self._tasks:
            self._tasks[task_id].completed = False
            self._save_to_file()
            return True
        return False
    
    def get_next_id(self) -> int:
        """Get the next available ID."""
        return self._next_id