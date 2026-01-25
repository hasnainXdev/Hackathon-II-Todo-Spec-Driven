import pytest
from src.utils.nlp_parser import parse_task_creation
from src.utils.nlp_task_updates import parse_task_update
from src.utils.nlp_task_deletion import parse_task_deletion
from src.utils.nlp_task_completion import parse_task_completion
from src.utils.intent_recognizer import recognize_intent, IntentType


@pytest.mark.parametrize("input_text,expected_title", [
    ("Add a task to buy groceries", "Buy groceries"),
    ("Create a task to finish the report", "Finish the report"),
    ("New task: walk the dog", "Walk the dog"),
    ("Please add clean the house", "Clean the house"),
    ("I need to call mom", "Call mom"),
    ("Remind me to schedule appointment", "Schedule appointment"),
    ("Don't forget to pay bills", "Pay bills"),
    ("Task: prepare presentation", "Prepare presentation"),
])
def test_various_task_creation_inputs(input_text, expected_title):
    """Test various ways users might request to create a task"""
    result = parse_task_creation(input_text)
    
    assert result is not None, f"Failed to parse: {input_text}"
    assert result["title"] == expected_title


@pytest.mark.parametrize("input_text,expected_elements", [
    ("Add a high priority task to buy groceries", {"priority": "high"}),
    ("Create a task to finish report by tomorrow", {"due_date": True}),  # due_date will be present
    ("New task: call mom today with high importance", {"priority": "high"}),
    ("Add a task to schedule appointment for next week", {"due_date": True}),
    ("Create urgent task to finish project", {"priority": "high"}),
])
def test_task_creation_with_attributes(input_text, expected_elements):
    """Test task creation with additional attributes like priority and due date"""
    result = parse_task_creation(input_text)
    
    assert result is not None, f"Failed to parse: {input_text}"
    
    for attr, expected_value in expected_elements.items():
        if attr == "due_date":
            if expected_value:  # Expecting due_date to be present
                assert "due_date" in result, f"Expected due_date in result for: {input_text}"
            else:  # Expecting due_date to be absent
                assert "due_date" not in result, f"Did not expect due_date in result for: {input_text}"
        else:
            assert result[attr] == expected_value, f"Expected {attr}={expected_value}, got {result.get(attr)} for: {input_text}"


@pytest.mark.parametrize("input_text", [
    "Update the buy groceries task to include organic items",
    "Change the meeting task to include zoom link",
    "Modify the workout task to be in the morning",
    "Edit the report task to add deadline",
    "Update the buy groceries task and make it high priority",
    "Change the meeting task and move it to tomorrow",
])
def test_various_task_update_inputs(input_text):
    """Test various ways users might request to update a task"""
    result = parse_task_update(input_text)
    
    assert result is not None, f"Failed to parse: {input_text}"
    assert "task_identifier" in result


@pytest.mark.parametrize("input_text", [
    "Delete the meeting with john task",
    "Remove the grocery shopping task",
    "Get rid of the appointment task",
    "Erase the reminder task",
    "Eliminate the chore task",
    "Cancel the event task",
    "Drop the activity task",
    "Kill the assignment task",
])
def test_various_task_deletion_inputs(input_text):
    """Test various ways users might request to delete a task"""
    result = parse_task_deletion(input_text)
    
    assert result is not None, f"Failed to parse: {input_text}"
    assert "task_identifier" in result


@pytest.mark.parametrize("input_text", [
    "Mark the laundry task as complete",
    "Complete the dishes task",
    "Finish the vacuuming task",
    "Check off the shopping task",
    "Tick off the exercise task",
    "Cross off the reading task",
    "Get done the cooking task",
    "Get finished the gardening task",
])
def test_various_task_completion_inputs(input_text):
    """Test various ways users might request to complete a task"""
    result = parse_task_completion(input_text)
    
    assert result is not None, f"Failed to parse: {input_text}"
    assert "task_identifier" in result
    assert result["completed"] is True


@pytest.mark.parametrize("input_text", [
    "Mark the laundry task as incomplete",
    "Reopen the dishes task",
    "Uncomplete the vacuuming task",
    "Mark the shopping task back to incomplete",
])
def test_various_task_incompletion_inputs(input_text):
    """Test various ways users might request to mark a task as incomplete"""
    result = parse_task_completion(input_text)
    
    assert result is not None, f"Failed to parse: {input_text}"
    assert "task_identifier" in result
    assert result["completed"] is False


@pytest.mark.parametrize("input_text,expected_intent", [
    ("Add a task to buy groceries", IntentType.CREATE_TASK),
    ("Show me my tasks", IntentType.GET_TASKS),
    ("List all my tasks", IntentType.GET_TASKS),
    ("What are my current tasks?", IntentType.GET_TASKS),
    ("Update the meeting task", IntentType.UPDATE_TASK),
    ("Delete the old task", IntentType.DELETE_TASK),
    ("Mark the task as complete", IntentType.COMPLETE_TASK),
    ("How's the weather?", IntentType.UNKNOWN),
    ("Tell me a joke", IntentType.UNKNOWN),
])
def test_various_intent_recognition_inputs(input_text, expected_intent):
    """Test intent recognition for various inputs"""
    intent, params = recognize_intent(input_text)
    
    assert intent == expected_intent


def test_complex_task_creation_phrases():
    """Test complex phrases for task creation"""
    complex_phrases = [
        "I really need to add a high priority task to finish the quarterly report by tomorrow",
        "Can you create an urgent task for me to call the client today?",
        "Add a task with low priority to clean out the garage next weekend",
        "I've got to remember to schedule the team meeting for next week",
    ]
    
    for phrase in complex_phrases:
        result = parse_task_creation(phrase)
        assert result is not None, f"Failed to parse complex phrase: {phrase}"
        assert "title" in result


def test_negation_in_task_operations():
    """Test phrases with negation"""
    negation_phrases = [
        "Don't forget to add a task to call mom",
        "Please don't remove the important task",
        "I didn't mean to mark that task as complete",
    ]
    
    # Test the first one for task creation
    result = parse_task_creation(negation_phrases[0])
    assert result is not None
    assert "title" in result
    
    # The other phrases might not match specific patterns, which is okay
    # as this tests the robustness of the NLP system


if __name__ == "__main__":
    pytest.main([__file__])