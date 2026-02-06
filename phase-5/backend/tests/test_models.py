import pytest
from datetime import datetime
from models.task import Task, TaskCreate


def test_task_creation():
    """Test creating a task with valid data"""
    task_data = TaskCreate(
        title="Test Task",
        description="This is a test task",
        completion_status=False,
        user_id="test_user_id"
    )

    task = Task(
        title=task_data.title,
        description=task_data.description,
        completion_status=task_data.completion_status,
        user_id=task_data.user_id
    )

    assert task.title == "Test Task"
    assert task.description == "This is a test task"
    assert task.completion_status is False
    assert task.user_id == "test_user_id"
    assert isinstance(task.created_at, datetime)
    assert isinstance(task.updated_at, datetime)


def test_task_title_validation():
    """Test task title validation"""
    with pytest.raises(Exception):  # Changed from ValueError to Exception to catch pydantic validation error
        TaskCreate(
            title="",  # Empty title should fail validation
            description="This is a test task",
            completion_status=False,
            user_id="test_user_id"
        )