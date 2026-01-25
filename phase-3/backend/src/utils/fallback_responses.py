from typing import Dict, List
from enum import Enum


class IntentType(Enum):
    CREATE_TASK = "create_task"
    UPDATE_TASK = "update_task"
    DELETE_TASK = "delete_task"
    COMPLETE_TASK = "complete_task"
    GET_TASKS = "get_tasks"
    UNKNOWN = "unknown"


def get_fallback_response(user_message: str = "") -> str:
    """
    Generates a fallback response for unrecognized commands
    """
    fallback_responses = [
        "I'm sorry, I didn't understand that. Could you rephrase your request?",
        "I'm not sure how to help with that. Try asking me to create, update, or check your tasks.",
        "Could you clarify what you'd like me to do? You can ask me to add, update, or view your tasks.",
        "I'm not quite sure what you mean. You can say things like 'Add a task to buy groceries' or 'Show me my tasks'.",
        "I didn't catch that. Try using simple commands like 'Create a task to...', 'Update the task...', or 'Show my tasks'."
    ]
    
    # For more specific responses based on partial matches
    if _contains_task_related_words(user_message):
        return "I'm having trouble understanding your specific request about tasks. Could you try rephrasing? For example: 'Add a task to [your task]', 'Show me my tasks', or 'Mark task as complete'."
    
    import random
    return random.choice(fallback_responses)


def _contains_task_related_words(message: str) -> bool:
    """
    Checks if the message contains task-related keywords
    """
    task_keywords = [
        'task', 'todo', 'to-do', 'do ', 'complete', 'finish', 'done', 
        'add', 'create', 'update', 'change', 'modify', 'delete', 'remove',
        'list', 'show', 'view', 'see', 'my ', 'work', 'job', 'chore'
    ]
    
    lower_msg = message.lower()
    return any(keyword in lower_msg for keyword in task_keywords)


def get_suggested_commands() -> List[str]:
    """
    Returns a list of suggested commands the user can try
    """
    return [
        "Add a task to [your task description]",
        "Create a task to [your task description]", 
        "Show me my tasks",
        "List my tasks",
        "Update the [task name] task to [new details]",
        "Mark the [task name] task as complete",
        "Complete the [task name] task",
        "Delete the [task name] task"
    ]


def get_help_response() -> str:
    """
    Generates a help response with available commands
    """
    suggestions = get_suggested_commands()
    help_text = "I can help you manage your tasks. Here are some things you can ask me:\n\n"
    for suggestion in suggestions:
        help_text += f"• {suggestion}\n"
    
    help_text += "\nJust let me know what you'd like to do with your tasks!"
    return help_text