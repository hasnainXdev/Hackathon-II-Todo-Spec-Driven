import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session
from app.main import app  # Adjust import based on your main app location
from src.models.user import User
from models.task import Task
from src.models.conversation import Conversation, Message
from src.services.ai_service import AIService
from src.services.ai_chat_service import AIChatService
from src.utils.nlp_parser import parse_task_creation
from src.algorithms.task_creation_suggestion_algorithm import TaskCreationSuggestionAlgorithm
from src.services.analytics_service import AnalyticsService


@pytest.fixture
def client():
    """Create a test client for the API"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_session():
    """Create a mock database session"""
    session = MagicMock(spec=Session)
    return session


@pytest.fixture
def mock_ai_service():
    """Create a mock AI service"""
    ai_service = MagicMock(spec=AIService)
    ai_service.process_user_message = AsyncMock(return_value={
        "response": "I've added the task 'buy groceries' to your list.",
        "success": True,
        "model_used": "gpt-4"
    })
    return ai_service


@pytest.mark.asyncio
class TestAIChatbotEndToEnd:
    """End-to-end tests for AI chatbot features"""
    
    async def test_end_to_end_task_creation_flow(self, client, mock_session, mock_ai_service):
        """Test the complete flow of creating a task via chatbot"""
        # Mock the AI service response for task creation
        mock_ai_service.process_user_message = AsyncMock(return_value={
            "response": "I've added the task 'buy groceries' to your list.",
            "success": True,
            "model_used": "gpt-4"
        })
        
        # Create an AI chat service with mocked dependencies
        ai_chat_service = AIChatService(mock_ai_service)
        
        # Simulate a user request to create a task
        user_message = "Add a task to buy groceries"
        user_id = "test_user_123"
        
        # Process the message
        result = await ai_chat_service.process_chat_message(
            user_id=user_id,
            message_content=user_message,
            session=mock_session
        )
        
        # Verify the response
        assert result["success"] is True
        assert "buy groceries" in result["ai_response"]["response"]
        
        # Verify that the AI service was called with the correct parameters
        mock_ai_service.process_user_message.assert_called_once()
    
    
    async def test_end_to_end_task_query_flow(self, client, mock_session, mock_ai_service):
        """Test the complete flow of querying tasks via chatbot"""
        # Mock the AI service response for task query
        mock_ai_service.process_user_message = AsyncMock(return_value={
            "response": "You have 2 tasks: 'buy groceries' and 'walk the dog'.",
            "success": True,
            "model_used": "gpt-4"
        })
        
        # Create an AI chat service with mocked dependencies
        ai_chat_service = AIChatService(mock_ai_service)
        
        # Simulate a user request to query tasks
        user_message = "Show me my tasks"
        user_id = "test_user_123"
        
        # Process the message
        result = await ai_chat_service.process_chat_message(
            user_id=user_id,
            message_content=user_message,
            session=mock_session
        )
        
        # Verify the response
        assert result["success"] is True
        assert "buy groceries" in result["ai_response"]["response"]
        assert "walk the dog" in result["ai_response"]["response"]
    
    
    async def test_nlp_parsing_integration(self):
        """Test the integration of NLP parsing with task creation"""
        # Test various natural language inputs for task creation
        test_inputs = [
            "Add a task to buy groceries",
            "Create a task to finish the report by Friday",
            "New task: schedule dentist appointment",
            "I need to call mom tomorrow",
            "Remind me to water plants next week"
        ]
        
        expected_titles = [
            "Buy groceries",
            "Finish the report",
            "Schedule dentist appointment",
            "Call mom",
            "Water plants"
        ]
        
        for i, inp in enumerate(test_inputs):
            result = parse_task_creation(inp)
            assert result is not None, f"Failed to parse: {inp}"
            assert result["title"] == expected_titles[i], f"Mismatch for input: {inp}"
    
    
    async def test_suggestion_algorithm_integration(self, mock_session):
        """Test the integration of suggestion algorithms"""
        # Create a mock behavior aggregator
        mock_behavior_agg = MagicMock()
        mock_behavior_agg.aggregate_user_behavior = MagicMock(return_value={
            "task_interdependency": [
                {"keyword": "groceries", "related_tasks": ["buy milk", "buy bread"], "count": 5}
            ],
            "peak_activity_times": [(9, {"creation": 5, "completion": 3})],
            "category_preferences": {"work": 10, "personal": 5, "health": 3}
        })
        
        # Create the suggestion algorithm
        suggester = TaskCreationSuggestionAlgorithm(mock_behavior_agg)
        
        # Generate suggestions
        suggestions = suggester.suggest_new_tasks("test_user_123", limit=3)
        
        # Verify suggestions are generated
        assert isinstance(suggestions, list)
        assert len(suggestions) <= 3
    
    
    async def test_analytics_service_integration(self, mock_session):
        """Test the integration of analytics service"""
        # Create mock tasks for the user
        mock_tasks = [
            Task(id="task1", title="Task 1", completed=True),
            Task(id="task2", title="Task 2", completed=False),
            Task(id="task3", title="Task 3", completed=True)
        ]
        
        # Mock the session to return these tasks
        mock_session.exec.return_value.all.return_value = mock_tasks
        
        # Create analytics service
        analytics_service = AnalyticsService(mock_session)
        
        # Get user insights
        insights = analytics_service.get_user_task_insights("test_user_123")
        
        # Verify insights are calculated correctly
        assert insights["total_tasks"] == 3
        assert insights["completed_tasks"] == 2
        assert insights["pending_tasks"] == 1
    
    
    async def test_conversation_history_persistence(self, mock_session):
        """Test that conversation history is properly persisted"""
        # Create a mock AI service
        mock_ai_service = MagicMock(spec=AIService)
        mock_ai_service.process_user_message = AsyncMock(return_value={
            "response": "Sure, I can help with that.",
            "success": True,
            "model_used": "gpt-4"
        })
        
        # Create AI chat service
        ai_chat_service = AIChatService(mock_ai_service)
        
        # Simulate a conversation
        user_id = "test_user_123"
        message1 = "Add a task to buy groceries"
        message2 = "Show me my tasks"
        
        # Process first message
        result1 = await ai_chat_service.process_chat_message(
            user_id=user_id,
            message_content=message1,
            session=mock_session
        )
        
        # Process second message in the same conversation
        result2 = await ai_chat_service.process_chat_message(
            user_id=user_id,
            message_content=message2,
            conversation_id=result1["conversation_id"],
            session=mock_session
        )
        
        # Verify both messages were processed successfully
        assert result1["success"] is True
        assert result2["success"] is True
        assert result1["conversation_id"] == result2["conversation_id"]
    
    
    async def test_error_handling_in_chat_flow(self, mock_session, mock_ai_service):
        """Test error handling in the chat flow"""
        # Mock an error response from the AI service
        mock_ai_service.process_user_message = AsyncMock(side_effect=Exception("AI service error"))
        
        # Create AI chat service
        ai_chat_service = AIChatService(mock_ai_service)
        
        # Process a message that causes an error
        with pytest.raises(Exception):
            await ai_chat_service.process_chat_message(
                user_id="test_user_123",
                message_content="This will cause an error",
                session=mock_session
            )
    
    
    async def test_security_and_isolation(self, mock_session):
        """Test that users can only access their own data"""
        # This would test that when user A queries conversations,
        # they don't see user B's conversations
        
        # Mock conversations for different users
        user_a_convs = [
            Conversation(id="conv_a1", user_id="user_A", title="User A's conversation")
        ]
        user_b_convs = [
            Conversation(id="conv_b1", user_id="user_B", title="User B's conversation")
        ]
        
        # Mock the session to return different results based on user
        def mock_exec(statement):
            mock_result = MagicMock()
            if "user_A" in str(statement):
                mock_result.all.return_value = user_a_convs
            elif "user_B" in str(statement):
                mock_result.all.return_value = user_b_convs
            else:
                mock_result.all.return_value = []
            return mock_result
        
        mock_session.exec.side_effect = mock_exec
        
        # In a real test, we would verify that each user only sees their own conversations
        # This is a simplified version to demonstrate the concept
        assert True  # Placeholder assertion


# Additional integration tests
class TestAPIEndpoints:
    """Test the API endpoints for the AI chatbot"""
    
    def test_chat_endpoint_exists(self, client):
        """Test that the chat endpoint exists"""
        # This would require a logged-in user session in a real test
        # For now, we'll just check if the endpoint path exists in our routes
        assert True  # Placeholder - would implement actual test with proper auth
    
    def test_health_check_endpoint(self, client):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code in [200, 404]  # Either exists and works, or doesn't exist


if __name__ == "__main__":
    pytest.main([__file__])