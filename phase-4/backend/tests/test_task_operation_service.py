import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from sqlmodel import Session
from src.services.task_operation_service import TaskOperationService
from src.utils.intent_recognizer import IntentType
from models.task import Task


class TestTaskOperationService:
    """Tests for the TaskOperationService"""

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session"""
        session = MagicMock(spec=Session)
        return session

    @pytest.fixture
    def task_op_service(self, mock_session):
        """Create a TaskOperationService instance with mocked dependencies"""
        return TaskOperationService(mock_session)

    @pytest.mark.asyncio
    async def test_execute_task_operation_create_task(self, task_op_service):
        """Test executing a task creation operation"""
        # Mock the task service
        task_op_service.task_service = MagicMock()
        task_op_service.task_service.create_task = MagicMock(return_value=Task(
            id="task123",
            title="Buy groceries",
            description="",
            completion_status=False,
            user_id="user123"
        ))

        # Test data
        user_id = "user123"
        message = "Add a task to buy groceries"
        params = {
            "title": "Buy groceries",
            "description": "",
            "completion_status": False
        }

        # Execute the operation
        result = await task_op_service._execute_create_task(user_id, params)

        # Verify the result
        assert result["success"] is True
        assert "buy groceries" in result["response"].lower()
        assert result["action_performed"] == "create_task"

    @pytest.mark.asyncio
    async def test_execute_task_operation_get_tasks(self, task_op_service):
        """Test executing a get tasks operation"""
        # Mock the task service
        task_op_service.task_service = MagicMock()
        task_op_service.task_service.get_tasks_by_user = MagicMock(return_value=[
            Task(id="task1", title="Task 1", completion_status=False, user_id="user123"),
            Task(id="task2", title="Task 2", completion_status=True, user_id="user123")
        ])

        # Test data
        user_id = "user123"

        # Execute the operation
        result = await task_op_service._execute_get_tasks(user_id)

        # Verify the result
        assert result["success"] is True
        assert result["action_performed"] == "get_tasks"
        assert len(result["task_details"]) == 2

    @pytest.mark.asyncio
    async def test_execute_task_operation_unknown_intent(self, task_op_service):
        """Test executing an unknown intent"""
        # Test data
        user_id = "user123"
        message = "This is an unknown request"

        # Execute the operation
        result = await task_op_service.execute_task_operation(user_id, message)

        # Verify the result
        assert result["success"] is False
        assert result["action_performed"] == "unknown_intent"

    @pytest.mark.asyncio
    async def test_execute_task_operation_exception_handling(self, task_op_service):
        """Test exception handling in task operations"""
        # Mock the task service to raise an exception
        task_op_service.task_service = MagicMock()
        task_op_service.task_service.create_task.side_effect = Exception("Database error")

        # Test data
        user_id = "user123"
        params = {
            "title": "Test task",
            "description": "",
            "completion_status": False
        }

        # Execute the operation
        result = await task_op_service._execute_create_task(user_id, params)

        # Verify the result
        assert result["success"] is False
        assert result["action_performed"] == "create_task_failed"

    @pytest.mark.asyncio
    async def test_execute_task_operation_update_task(self, task_op_service):
        """Test executing a task update operation"""
        # Mock the task service
        task_op_service.task_service = MagicMock()
        task_op_service.task_service.get_tasks_by_user = MagicMock(return_value=[
            Task(id="task1", title="Old task", completion_status=False, user_id="user123")
        ])
        task_op_service.task_service.update_task = MagicMock(return_value=Task(
            id="task1",
            title="Updated task",
            completion_status=False,
            user_id="user123"
        ))

        # Test data
        user_id = "user123"
        params = {
            "task_identifier": "old task",
            "title": "Updated task"
        }

        # Execute the operation
        result = await task_op_service._execute_update_task(user_id, params)

        # Verify the result
        assert result["success"] is True
        assert result["action_performed"] == "update_task"

    @pytest.mark.asyncio
    async def test_execute_task_operation_delete_task(self, task_op_service):
        """Test executing a task deletion operation"""
        # Mock the task service
        task_op_service.task_service = MagicMock()
        task_op_service.task_service.get_tasks_by_user = MagicMock(return_value=[
            Task(id="task1", title="Task to delete", completion_status=False, user_id="user123")
        ])
        task_op_service.task_service.delete_task = MagicMock(return_value=True)

        # Test data
        user_id = "user123"
        params = {
            "task_identifier": "task to delete"
        }

        # Execute the operation
        result = await task_op_service._execute_delete_task(user_id, params)

        # Verify the result
        assert result["success"] is True
        assert result["action_performed"] == "delete_task"

    @pytest.mark.asyncio
    async def test_execute_task_operation_complete_task(self, task_op_service):
        """Test executing a task completion operation"""
        # Mock the task service
        task_op_service.task_service = MagicMock()
        task_op_service.task_service.get_tasks_by_user = MagicMock(return_value=[
            Task(id="task1", title="Task to complete", completion_status=False, user_id="user123")
        ])
        task_op_service.task_service.toggle_completion = MagicMock(return_value=Task(
            id="task1",
            title="Task to complete",
            completion_status=True,
            user_id="user123"
        ))

        # Test data
        user_id = "user123"
        params = {
            "task_identifier": "task to complete",
            "completed": True
        }

        # Execute the operation
        result = await task_op_service._execute_complete_task(user_id, params)

        # Verify the result
        assert result["success"] is True
        assert result["action_performed"] == "complete_task"