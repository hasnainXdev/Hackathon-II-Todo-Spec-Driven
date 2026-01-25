import unittest
from unittest.mock import Mock, MagicMock
from src.algorithms.task_creation_suggestion_algorithm import TaskCreationSuggestionAlgorithm
from src.algorithms.task_prioritization_suggestion_algorithm import TaskPrioritizationSuggestionAlgorithm
from src.algorithms.task_completion_suggestion_algorithm import TaskCompletionSuggestionAlgorithm
from src.utils.task_behavior_aggregator import TaskBehaviorAggregator
from src.services.analytics_service import AnalyticsService
from src.ai_models.personalized_suggestions_model import PersonalizedSuggestionsAIModel


class TestAISuggestionsEffectiveness(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create mock objects for dependencies
        self.mock_behavior_aggregator = Mock(spec=TaskBehaviorAggregator)
        self.mock_analytics_service = Mock(spec=AnalyticsService)
        self.mock_session = Mock()
        
        # Create instances of the algorithms to test
        self.creation_suggester = TaskCreationSuggestionAlgorithm(self.mock_behavior_aggregator)
        self.prioritization_suggester = TaskPrioritizationSuggestionAlgorithm(self.mock_session)
        self.completion_suggester = TaskCompletionSuggestionAlgorithm(self.mock_session)
        self.ai_model = PersonalizedSuggestionsAIModel()
    
    def test_creation_suggester_output_format(self):
        """Test that creation suggestions are in the expected format."""
        # Mock behavior data
        mock_behavior_data = {
            "task_interdependency": [
                {"keyword": "groceries", "related_tasks": ["buy milk", "buy bread"], "count": 5},
                {"keyword": "work", "related_tasks": ["attend meeting", "review report"], "count": 3}
            ],
            "peak_activity_times": [(9, {"creation": 5, "completion": 3}), (14, {"creation": 4, "completion": 6})],
            "category_preferences": {"work": 10, "personal": 5, "health": 3}
        }
        
        self.mock_behavior_aggregator.aggregate_user_behavior.return_value = mock_behavior_data
        
        # Test the method
        suggestions = self.creation_suggester.suggest_new_tasks("user123", limit=3)
        
        # Assertions
        self.assertIsInstance(suggestions, list)
        self.assertLessEqual(len(suggestions), 3)
        
        if suggestions:
            suggestion = suggestions[0]
            self.assertIn("title", suggestion)
            self.assertIn("description", suggestion)
            self.assertIn("priority", suggestion)
            self.assertIn("category", suggestion)
            self.assertIn("confidence", suggestion)
    
    def test_prioritization_suggester_accuracy(self):
        """Test that prioritization suggestions are reasonable."""
        # Mock task data
        mock_task = Mock()
        mock_task.id = "task1"
        mock_task.title = "Complete project report"
        mock_task.description = "Finish the quarterly report"
        mock_task.due_date = None
        mock_task.priority = "medium"
        
        # Mock the session to return tasks
        mock_session = Mock()
        mock_statement = Mock()
        mock_exec_result = Mock()
        mock_exec_result.all.return_value = [mock_task]
        mock_session.exec.return_value = mock_exec_result
        
        # Create suggester with mocked session
        suggester = TaskPrioritizationSuggestionAlgorithm(mock_session)
        
        # Test the method
        suggestions = suggester.suggest_task_priorities("user123")
        
        # Assertions
        self.assertIsInstance(suggestions, list)
        if suggestions:
            suggestion = suggestions[0]
            self.assertEqual(suggestion["task_id"], "task1")
            self.assertIn("suggested_priority", suggestion)
            self.assertIn(suggestion["suggested_priority"], ["low", "medium", "high"])
            self.assertIn("confidence", suggestion)
            self.assertGreaterEqual(suggestion["confidence"], 0.0)
            self.assertLessEqual(suggestion["confidence"], 1.0)
    
    def test_completion_suggester_logic(self):
        """Test that completion suggestions follow logical rules."""
        # Mock task data
        mock_task = Mock()
        mock_task.id = "task1"
        mock_task.title = "Submit assignment"
        mock_task.completed = False
        mock_task.due_date = None
        
        # Mock the session to return tasks
        mock_session = Mock()
        mock_statement = Mock()
        mock_exec_result = Mock()
        mock_exec_result.all.return_value = [mock_task]
        mock_session.exec.return_value = mock_exec_result
        
        # Create suggester with mocked session
        suggester = TaskCompletionSuggestionAlgorithm(mock_session)
        
        # Test the method
        suggestions = suggester.suggest_tasks_for_completion("user123")
        
        # Assertions
        self.assertIsInstance(suggestions, list)
        
        # If there are suggestions, verify their structure
        if suggestions:
            suggestion = suggestions[0]
            self.assertIn("task_id", suggestion)
            self.assertIn("task_title", suggestion)
            self.assertIn("suggestion_reason", suggestion)
            self.assertIn("confidence", suggestion)
            self.assertIn("urgency", suggestion)
    
    def test_ai_model_training_and_prediction(self):
        """Test that the AI model can be trained and make predictions."""
        # Sample training data
        sample_tasks = [
            {
                "title": "Complete project proposal",
                "description": "Finish the Q4 project proposal document",
                "priority": "high"
            },
            {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread, fruits",
                "priority": "medium"
            },
            {
                "title": "Schedule dentist appointment",
                "description": "Regular checkup",
                "priority": "low"
            }
        ]
        
        sample_behavior = {
            "category_preferences": {"work": 5, "personal": 3, "health": 2}
        }
        
        # Train the model
        self.ai_model.train(sample_tasks, sample_behavior)
        
        # Test prediction
        priority, confidence = self.ai_model.predict_task_priority(
            "Prepare presentation slides"
        )
        
        # Assertions
        self.assertIn(priority, ["low", "medium", "high"])
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_recommendation_generation(self):
        """Test that the AI model generates meaningful recommendations."""
        # Sample training data
        sample_tasks = [
            {
                "title": "Complete project proposal",
                "description": "Finish the Q4 project proposal document",
                "priority": "high"
            },
            {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread, fruits",
                "priority": "medium"
            }
        ]
        
        sample_behavior = {
            "category_preferences": {"work": 5, "personal": 3, "health": 2}
        }
        
        # Train the model
        self.ai_model.train(sample_tasks, sample_behavior)
        
        # Generate recommendations
        recommendations = self.ai_model.recommend_new_tasks(sample_behavior, num_suggestions=3)
        
        # Assertions
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 3)
        
        for rec in recommendations:
            self.assertIn("title", rec)
            self.assertIn("category", rec)
            self.assertIn("predicted_priority", rec)
            self.assertIn("confidence", rec)
            self.assertIn("reason", rec)
    
    def test_suggestion_integration_logic(self):
        """Test the logic for integrating suggestions into responses."""
        # This tests the filtering logic in the SuggestionIntegrator
        from backend.src.services.suggestion_integrator import SuggestionIntegrator
        
        # Create a mock integrator
        mock_ai_service = Mock()
        mock_creation_suggester = Mock()
        mock_prioritization_suggester = Mock()
        mock_completion_suggester = Mock()
        mock_behavior_aggregator = Mock()
        mock_ai_model = Mock()
        
        integrator = SuggestionIntegrator(
            ai_service=mock_ai_service,
            analytics_service=self.mock_analytics_service,
            creation_suggester=mock_creation_suggester,
            prioritization_suggester=mock_prioritization_suggester,
            completion_suggester=mock_completion_suggester,
            behavior_aggregator=mock_behavior_aggregator,
            ai_model=mock_ai_model,
            session=self.mock_session
        )
        
        # Test the filtering logic
        test_suggestions = {
            "creation": [{"title": "Suggested task", "confidence": 0.8}],
            "prioritization": [{"task_title": "Existing task", "suggested_priority": "high"}],
            "completion": [{"task_title": "Pending task", "suggestion_reason": "Overdue"}],
            "ai_recommendations": [{"title": "AI suggested task", "confidence": 0.9}]
        }
        
        # Test with a message that should trigger creation suggestions
        filtered = integrator._filter_relevant_suggestions(test_suggestions, "What should I do today?")
        self.assertIn("creation", filtered)
        
        # Test with a message that should trigger prioritization suggestions
        filtered = integrator._filter_relevant_suggestions(test_suggestions, "What should I prioritize?")
        self.assertIn("prioritization", filtered)
        
        # Test with a message that should trigger completion suggestions
        filtered = integrator._filter_relevant_suggestions(test_suggestions, "What tasks do I have?")
        self.assertIn("completion", filtered)


if __name__ == '__main__':
    unittest.main()