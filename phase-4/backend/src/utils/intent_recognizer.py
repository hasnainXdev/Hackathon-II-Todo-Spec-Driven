import re
from enum import Enum
from typing import Tuple, Optional
from .nlp_parser import parse_task_creation
from .nlp_task_updates import parse_task_update
from .nlp_task_deletion import parse_task_deletion
from .nlp_task_completion import parse_task_completion


class IntentType(Enum):
    CREATE_TASK = "create_task"
    UPDATE_TASK = "update_task"
    DELETE_TASK = "delete_task"
    COMPLETE_TASK = "complete_task"
    GET_TASKS = "get_tasks"
    UNKNOWN = "unknown"


def recognize_intent(text: str) -> Tuple[IntentType, Optional[dict]]:
    """
    Recognizes the intent behind a user's message and extracts relevant parameters
    """
    # Normalize the input text
    normalized_text = text.lower().strip()

    # Check for get tasks intent first
    if _is_get_tasks_intent(normalized_text):
        return IntentType.GET_TASKS, {}

    # Check for task creation
    creation_params = parse_task_creation(text)
    if creation_params:
        return IntentType.CREATE_TASK, creation_params

    # Check for task completion first (before deletion since some completion phrases might match deletion patterns)
    completion_params = parse_task_completion(text)
    if completion_params:
        return IntentType.COMPLETE_TASK, completion_params

    # Check for task deletion
    deletion_params = parse_task_deletion(text)
    if deletion_params:
        return IntentType.DELETE_TASK, deletion_params

    # Check for task update (this should come after other operations since update is more general)
    update_params = parse_task_update(text)
    if update_params:
        return IntentType.UPDATE_TASK, update_params

    # If no specific intent is recognized, return unknown
    return IntentType.UNKNOWN, {}


def _is_get_tasks_intent(text: str) -> bool:
    """
    Checks if the text indicates a request to get tasks
    """
    get_patterns = [
        r"\b(list|show|display|get|see|view)\b.*\b(tasks|my tasks|to-do|todo|things to do)\b",
        r"\b(what|whats)\b.*\b(mine|my tasks|to-do|todo|things to do)\b",
        r"\b(my|current|existing)\b.*\b(tasks|to-do|todo)\b",
        r"\b(tasks|to-do|todo)\b.*\b(list|show|display|get|see|view)\b",
        r"\b(check|review)\b.*\b(tasks|my tasks|to-do|todo)\b",
        r"\b(all|everything)\b.*\b(tasks|to-do|todo)\b"
    ]
    
    for pattern in get_patterns:
        if re.search(pattern, text):
            return True
    
    return False