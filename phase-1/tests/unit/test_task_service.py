"""
Unit tests for the TaskService.
"""
import pytest
from src.todo_app.services.task_service import TaskService
from src.todo_app.models.task import Task


def test_add_task():
    """Test adding a new task."""
    service = TaskService(use_test_storage=True)
    task = service.add_task("Test Task", "Test Description")

    assert task.id == 1
    assert task.title == "Test Task"
    assert task.description == "Test Description"
    assert task.completed is False
    assert len(service.get_all_tasks()) == 1


def test_add_task_defaults():
    """Test adding a task with default description."""
    service = TaskService(use_test_storage=True)
    task = service.add_task("Test Task")

    assert task.id == 1
    assert task.title == "Test Task"
    assert task.description == ""
    assert task.completed is False


def test_get_all_tasks():
    """Test getting all tasks."""
    service = TaskService(use_test_storage=True)
    service.add_task("Task 1", "Description 1")
    service.add_task("Task 2", "Description 2")

    tasks = service.get_all_tasks()
    assert len(tasks) == 2
    assert tasks[0].title == "Task 1"
    assert tasks[1].title == "Task 2"


def test_get_task_by_id():
    """Test getting a task by ID."""
    service = TaskService(use_test_storage=True)
    task = service.add_task("Test Task", "Test Description")

    retrieved_task = service.get_task_by_id(task.id)
    assert retrieved_task is not None
    assert retrieved_task.id == task.id
    assert retrieved_task.title == task.title
    assert retrieved_task.description == task.description
    assert retrieved_task.completed == task.completed

    # Test getting a non-existent task
    assert service.get_task_by_id(999) is None


def test_update_task():
    """Test updating a task."""
    service = TaskService(use_test_storage=True)
    task = service.add_task("Original Title", "Original Description")

    updated_task = service.update_task(task.id, "New Title", "New Description")

    assert updated_task is not None
    assert updated_task.id == task.id
    assert updated_task.title == "New Title"
    assert updated_task.description == "New Description"
    assert updated_task.completed == task.completed  # Should remain unchanged

    # Test partial updates
    partial_updated = service.update_task(task.id, title="Partial Update")
    assert partial_updated.title == "Partial Update"
    assert partial_updated.description == "New Description"  # Should remain unchanged

    # Test updating non-existent task
    assert service.update_task(999, "New Title") is None


def test_delete_task():
    """Test deleting a task."""
    service = TaskService(use_test_storage=True)
    task = service.add_task("Test Task", "Test Description")

    result = service.delete_task(task.id)
    assert result is True
    assert len(service.get_all_tasks()) == 0

    # Test deleting non-existent task
    result = service.delete_task(999)
    assert result is False


def test_mark_complete():
    """Test marking a task as complete."""
    service = TaskService(use_test_storage=True)
    task = service.add_task("Test Task", "Test Description")

    # Initially should be incomplete
    assert task.completed is False

    result = service.mark_complete(task.id)
    assert result is True

    # After marking complete, should be complete
    updated_task = service.get_task_by_id(task.id)
    assert updated_task.completed is True

    # Test marking non-existent task as complete
    result = service.mark_complete(999)
    assert result is False


def test_mark_incomplete():
    """Test marking a task as incomplete."""
    service = TaskService(use_test_storage=True)
    task = service.add_task("Test Task", "Test Description")

    # Mark as complete first
    service.mark_complete(task.id)
    assert service.get_task_by_id(task.id).completed is True

    # Now mark as incomplete
    result = service.mark_incomplete(task.id)
    assert result is True

    # After marking incomplete, should be incomplete
    updated_task = service.get_task_by_id(task.id)
    assert updated_task.completed is False

    # Test marking non-existent task as incomplete
    result = service.mark_incomplete(999)
    assert result is False