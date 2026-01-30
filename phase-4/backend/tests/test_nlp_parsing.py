import unittest
from src.utils.nlp_parser import parse_task_creation, extract_due_date, extract_priority
from src.utils.nlp_task_updates import parse_task_update
from src.utils.nlp_task_deletion import parse_task_deletion
from src.utils.nlp_task_completion import parse_task_completion
from src.utils.intent_recognizer import recognize_intent, IntentType
from src.utils.task_validator import validate_task_data, validate_and_sanitize_task_data


class TestNLPParsing(unittest.TestCase):
    
    def test_parse_task_creation_basic(self):
        """Test basic task creation parsing"""
        text = "Add a task to buy groceries"
        result = parse_task_creation(text)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "Buy groceries")
        self.assertNotIn("due_date", result)  # No due date specified
        self.assertIn("priority", result)  # Priority should default to medium
    
    def test_parse_task_creation_with_priority(self):
        """Test task creation with priority"""
        text = "Create a high priority task to finish the report"
        result = parse_task_creation(text)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "Finish the report")
        self.assertEqual(result["priority"], "high")
    
    def test_parse_task_creation_with_due_date(self):
        """Test task creation with due date"""
        text = "Add a task to call mom by tomorrow"
        result = parse_task_creation(text)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "Call mom")
        self.assertIn("due_date", result)
    
    def test_parse_task_update(self):
        """Test task update parsing"""
        text = "Update the buy groceries task to include organic items"
        result = parse_task_update(text)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["task_identifier"], "buy groceries")
        self.assertIn("title", result)  # Title update
        # Note: This would need more sophisticated parsing to extract the specific update
    
    def test_parse_task_deletion(self):
        """Test task deletion parsing"""
        text = "Delete the meeting with john task"
        result = parse_task_deletion(text)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["task_identifier"], "meeting with john")
    
    def test_parse_task_completion(self):
        """Test task completion parsing"""
        text = "Mark the laundry task as complete"
        result = parse_task_completion(text)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["task_identifier"], "laundry")
        self.assertTrue(result["completed"])
    
    def test_parse_task_completion_negative(self):
        """Test task completion parsing for marking incomplete"""
        text = "Mark the project task as incomplete"
        result = parse_task_completion(text)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["task_identifier"], "project")
        self.assertFalse(result["completed"])
    
    def test_intent_recognition_create(self):
        """Test intent recognition for task creation"""
        text = "Add a task to schedule dentist appointment"
        intent, params = recognize_intent(text)
        
        self.assertEqual(intent, IntentType.CREATE_TASK)
        self.assertIsNotNone(params)
    
    def test_intent_recognition_get_tasks(self):
        """Test intent recognition for getting tasks"""
        text = "Show me my tasks"
        intent, params = recognize_intent(text)
        
        self.assertEqual(intent, IntentType.GET_TASKS)
        self.assertEqual(params, {})
    
    def test_intent_recognition_unknown(self):
        """Test intent recognition for unknown intent"""
        text = "What's the weather like today?"
        intent, params = recognize_intent(text)
        
        self.assertEqual(intent, IntentType.UNKNOWN)
        self.assertEqual(params, {})


class TestTaskValidation(unittest.TestCase):
    
    def test_validate_valid_task(self):
        """Test validation of a valid task"""
        task_data = {
            "title": "Valid task title",
            "description": "This is a valid task description",
            "priority": "medium"
        }
        
        errors = validate_task_data(task_data)
        self.assertEqual(errors, {})
    
    def test_validate_task_missing_title(self):
        """Test validation of a task with missing title"""
        task_data = {
            "description": "This task has no title",
            "priority": "high"
        }
        
        errors = validate_task_data(task_data)
        self.assertIn("title", errors)
        self.assertGreater(len(errors["title"]), 0)
    
    def test_validate_task_long_title(self):
        """Test validation of a task with too long title"""
        task_data = {
            "title": "A" * 201,  # Exceeds 200 character limit
            "priority": "low"
        }
        
        errors = validate_task_data(task_data)
        self.assertIn("title", errors)
        self.assertGreater(len(errors["title"]), 0)
    
    def test_validate_task_invalid_priority(self):
        """Test validation of a task with invalid priority"""
        task_data = {
            "title": "Task with invalid priority",
            "priority": "super_high"  # Invalid priority
        }
        
        errors = validate_task_data(task_data)
        self.assertIn("priority", errors)
        self.assertGreater(len(errors["priority"]), 0)


if __name__ == '__main__':
    unittest.main()