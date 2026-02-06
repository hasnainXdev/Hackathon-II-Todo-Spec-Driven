import re
from typing import Optional, Dict, Any


def parse_task_deletion(text: str) -> Optional[Dict[str, Any]]:
    """
    Parses natural language input to extract task deletion parameters
    """
    # Normalize the input text
    normalized_text = text.lower().strip()
    
    # Define patterns for task deletion
    delete_patterns = [
        r"delete (?:the )?(.+?)(?: task)?(?=\.|!|\?|$)",
        r"remove (?:the )?(.+?)(?: task)?(?=\.|!|\?|$)",
        r"get rid of (?:the )?(.+?)(?: task)?(?=\.|!|\?|$)",
        r"erase (?:the )?(.+?)(?: task)?(?=\.|!|\?|$)",
        r"eliminate (?:the )?(.+?)(?: task)?(?=\.|!|\?|$)",
        r"cancel (?:the )?(.+?)(?: task)?(?=\.|!|\?|$)",
        r"drop (?:the )?(.+?)(?: task)?(?=\.|!|\?|$)",
        r"kill (?:the )?(.+?)(?: task)?(?=\.|!|\?|$)"
    ]
    
    # Try to match any of the deletion patterns
    matched = False
    task_identifier = ''
    
    for pattern in delete_patterns:
        match = re.search(pattern, normalized_text)
        if match:
            matched = True
            task_identifier = match.group(1)
            # Ensure we capture the full task identifier, not just the first character
            task_identifier = task_identifier.strip()
            break
    
    if not matched:
        return None
    
    # Clean up the task identifier
    task_identifier = task_identifier.strip()
    
    # Create the deletion data dictionary
    deletion_data = {
        "task_identifier": task_identifier
    }
    
    return deletion_data


def identify_task_by_reference(text: str, available_tasks: list) -> Optional[str]:
    """
    Identifies a specific task from a list of available tasks based on the reference in the text
    """
    # Normalize the input text
    normalized_text = text.lower().strip()
    
    # Look for ordinal references (first, second, third, etc.)
    ordinal_patterns = [
        (r"\b(first|1st)\b", 0),
        (r"\b(second|2nd)\b", 1),
        (r"\b(third|3rd)\b", 2),
        (r"\b(fourth|4th)\b", 3),
        (r"\b(fifth|5th)\b", 4),
        (r"\b(sixth|6th)\b", 5),
        (r"\b(seventh|7th)\b", 6),
        (r"\b(eighth|8th)\b", 7),
        (r"\b(ninth|9th)\b", 8),
        (r"\b(tenth|10th)\b", 9)
    ]
    
    for pattern, index in ordinal_patterns:
        if re.search(pattern, normalized_text) and index < len(available_tasks):
            return available_tasks[index].get('id')  # Assuming tasks have an 'id' field
    
    # Look for numbered references (task 1, task 2, etc.)
    number_match = re.search(r"\btask (\d+)\b", normalized_text)
    if number_match:
        task_num = int(number_match.group(1)) - 1  # Convert to 0-indexed
        if 0 <= task_num < len(available_tasks):
            return available_tasks[task_num].get('id')
    
    # Look for keyword matching in task titles/descriptions
    for task in available_tasks:
        title = task.get('title', '').lower()
        description = task.get('description', '').lower()
        
        # Check if the task identifier matches the title or description
        if task_identifier := extract_task_identifier(normalized_text):
            if task_identifier in title or task_identifier in description:
                return task.get('id')
    
    # If no specific task is identified, return None
    return None


def extract_task_identifier(text: str) -> Optional[str]:
    """
    Extracts the task identifier from the deletion command
    """
    # This function would extract the specific task identifier from the command
    # For now, we'll just return the whole text as a placeholder
    # In a real implementation, this would use more sophisticated NLP
    return text