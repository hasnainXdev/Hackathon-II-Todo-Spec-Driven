"""
Task service for managing tasks in memory.
"""

from typing import Dict, List, Optional
from todo_app.models.task import Task
from todo_app.services.persistent_storage import PersistentTaskStorage


class TaskService:
    """
    Provides business logic for task management with persistent in-memory storage.
    """

    def __init__(self, use_test_storage=False):
        """
        Initializes the TaskService with persistent task storage.
        """
        self._storage = PersistentTaskStorage(use_test_storage=use_test_storage)

    def add_task(self, title: str, description: str = "") -> Task:
        """
        Adds a new task with the given title and description.

        Args:
            title: The title of the task
            description: The description of the task (optional)

        Returns:
            The newly created Task object
        """
        next_id = self._storage.get_next_id()
        task = Task(
            id=next_id, title=title, description=description, completed=False
        )
        return self._storage.add_task(task)

    def get_all_tasks(self) -> List[Task]:
        """
        Returns all tasks in the system.

        Returns:
            A list of all Task objects
        """
        return self._storage.get_all_tasks()

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """
        Returns the task with the given ID, or None if not found.

        Args:
            task_id: The ID of the task to retrieve

        Returns:
            The Task object if found, None otherwise
        """
        return self._storage.get_task_by_id(task_id)

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[Task]:
        """
        Updates the task with the given ID.

        Args:
            task_id: The ID of the task to update
            title: The new title (optional)
            description: The new description (optional)

        Returns:
            The updated Task object if successful, None if task not found
        """
        return self._storage.update_task(task_id, title, description)

    def delete_task(self, task_id: int) -> bool:
        """
        Deletes the task with the given ID.

        Args:
            task_id: The ID of the task to delete

        Returns:
            True if the task was deleted, False if not found
        """
        return self._storage.delete_task(task_id)

    def mark_complete(self, task_id: int) -> bool:
        """
        Marks the task with the given ID as complete.

        Args:
            task_id: The ID of the task to mark complete

        Returns:
            True if the task was marked complete, False if not found
        """
        return self._storage.mark_complete(task_id)

    def mark_incomplete(self, task_id: int) -> bool:
        """
        Marks the task with the given ID as incomplete.

        Args:
            task_id: The ID of the task to mark incomplete

        Returns:
            True if the task was marked incomplete, False if not found
        """
        return self._storage.mark_incomplete(task_id)
