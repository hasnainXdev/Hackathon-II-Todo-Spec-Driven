from typing import Dict, Any, List
from .task_validator import validate_task_data


def format_validation_errors(errors: Dict[str, List[str]]) -> str:
    """
    Formats validation errors into a user-friendly message
    """
    if not errors:
        return ""
    
    error_messages = []
    for field, field_errors in errors.items():
        field_name = field.replace('_', ' ').title()
        for error in field_errors:
            error_messages.append(f"{field_name}: {error}")
    
    return "Validation errors: " + "; ".join(error_messages)


def create_nlp_error_response(original_message: str, error_type: str = "processing", details: str = "") -> str:
    """
    Creates a user-friendly error response for NLP processing failures
    """
    error_responses = {
        "parsing": f"I had trouble understanding your request: '{original_message}'. Could you rephrase it? For example, you can say 'Add a task to buy groceries' or 'Show me my tasks'.",
        "validation": f"The task information you provided has some issues. {details} Please try again with corrected information.",
        "extraction": f"I couldn't extract the necessary information from your request: '{original_message}'. Try being more specific. For example, say 'Create a task to call mom tomorrow' instead of just 'call mom'.",
        "intent_recognition": f"I'm not sure what you'd like me to do with your request: '{original_message}'. You can ask me to create, update, complete, or list your tasks.",
        "processing": f"Sorry, I encountered an issue processing your request: '{original_message}'. {details} Please try again or rephrase your request."
    }
    
    return error_responses.get(error_type, error_responses["processing"])


def create_task_operation_error(operation: str, task_details: str = "", error_details: str = "") -> str:
    """
    Creates a user-friendly error response for task operation failures
    """
    error_messages = {
        "create": f"Sorry, I couldn't create the task '{task_details}'. {error_details} Please try again.",
        "update": f"Sorry, I couldn't update the task '{task_details}'. {error_details} Please try again with different information.",
        "delete": f"Sorry, I couldn't delete the task '{task_details}'. {error_details} It might not exist or you might not have permission to delete it.",
        "complete": f"Sorry, I couldn't mark the task '{task_details}' as complete. {error_details} Please try again.",
        "retrieve": f"Sorry, I couldn't retrieve your tasks. {error_details} Please try again."
    }
    
    return error_messages.get(operation, f"Sorry, I couldn't perform the requested operation on the task '{task_details}'. {error_details}")


def create_unsupported_feature_response(feature_request: str) -> str:
    """
    Creates a response for unsupported features
    """
    return f"I understand you're asking about '{feature_request}', but this feature isn't available yet. I can help you with creating, updating, completing, and listing tasks. Is there something else I can help you with?"


def create_ambiguous_request_response(original_message: str, suggestions: List[str] = None) -> str:
    """
    Creates a response for ambiguous requests with suggestions
    """
    response = f"I'm not entirely sure what you mean by: '{original_message}'. Could you clarify?"
    
    if suggestions:
        response += " Perhaps you meant one of these:"
        for i, suggestion in enumerate(suggestions, 1):
            response += f" {i}) {suggestion}"
    
    return response