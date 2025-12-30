"""
Unit tests for the Task model.
"""
import pytest
from src.todo_app.models.task import Task


def test_task_creation():
    """Test creating a valid task."""
    task = Task(id=1, title="Test Task", description="Test Description", completed=False)
    assert task.id == 1
    assert task.title == "Test Task"
    assert task.description == "Test Description"
    assert task.completed is False


def test_task_creation_defaults():
    """Test creating a task with default values."""
    task = Task(id=1, title="Test Task")
    assert task.id == 1
    assert task.title == "Test Task"
    assert task.description == ""
    assert task.completed is False


def test_task_id_validation():
    """Test that task ID must be a positive integer."""
    with pytest.raises(ValueError):
        Task(id=0, title="Test Task")
    
    with pytest.raises(ValueError):
        Task(id=-1, title="Test Task")
    
    with pytest.raises(ValueError):
        Task(id="invalid", title="Test Task")


def test_task_title_validation():
    """Test that task title must be a non-empty string."""
    with pytest.raises(ValueError):
        Task(id=1, title="")
    
    with pytest.raises(ValueError):
        Task(id=1, title="   ")
    
    with pytest.raises(ValueError):
        Task(id=1, title=123)


def test_task_description_validation():
    """Test that task description must be a string."""
    with pytest.raises(ValueError):
        Task(id=1, title="Test Task", description=123)


def test_task_completed_validation():
    """Test that task completed status must be a boolean."""
    with pytest.raises(ValueError):
        Task(id=1, title="Test Task", completed="true")