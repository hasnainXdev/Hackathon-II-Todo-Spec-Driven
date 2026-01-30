import re
from typing import Optional, Dict, Any
from .nlp_parser import Priority


def parse_task_update(text: str) -> Optional[Dict[str, Any]]:
    """
    Parses natural language input to extract task update parameters
    """
    # Normalize the input text
    normalized_text = text.lower().strip()
    
    # Define patterns for task updates
    update_patterns = [
        r"update (?:the )?(.+?)(?: task)? (?:to|with|by) (.+)",
        r"change (?:the )?(.+?)(?: task)? (?:to|with|by) (.+)",
        r"modify (?:the )?(.+?)(?: task)? (?:to|with|by) (.+)",
        r"edit (?:the )?(.+?)(?: task)? (?:to|with|by) (.+)",
        r"update (?:the )?(.+?)(?: task)? and (.+)",
        r"change (?:the )?(.+?)(?: task)? and (.+)",
        r"update (?:the )?(.+?)(?: task)?(?=\.|!|\?|$)"  # For cases like "update the meeting task" without additional details
    ]
    
    # Try to match any of the update patterns
    matched = False
    task_identifier = ''
    update_details = ''
    
    for pattern in update_patterns:
        match = re.search(pattern, normalized_text)
        if match:
            matched = True
            task_identifier = match.group(1)
            # Check if there's a second group (update details)
            if len(match.groups()) > 1:
                update_details = match.group(2)
            else:
                # If there's no second group, treat the task identifier as the target
                # and return a minimal update request
                update_details = ""
            break
    
    if not matched:
        return None

    # If update_details is empty, this might not be a real update request
    # Only proceed if there are actual update details to process
    if not update_details.strip():
        # For cases like "update the meeting task" without details,
        # we might want to return a minimal update request or None
        # Let's return a minimal update request with just the task identifier
        return {
            "task_identifier": task_identifier.strip()
        }

    # Extract what needs to be updated
    title_update = extract_title_update(update_details)
    description_update = extract_description_update(update_details)
    due_date_update = extract_due_date_update(update_details)
    priority_update = extract_priority_update(update_details)
    completion_update = extract_completion_update(update_details)

    # Create the update data dictionary
    update_data = {
        "task_identifier": task_identifier.strip(),
        "title": title_update,
        "description": description_update,
        "due_date": due_date_update,
        "priority": priority_update,
        "completed": completion_update
    }

    # Remove None values
    update_data = {k: v for k, v in update_data.items() if v is not None}

    # If only task_identifier remains, return it
    if len(update_data) == 1 and "task_identifier" in update_data:
        return update_data

    return update_data


def extract_title_update(text: str) -> Optional[str]:
    """
    Extracts title update from natural language text
    """
    # Look for patterns indicating a title change
    title_patterns = [
        r"(?:change|update|modify|set) title (?:to|as) (.+)",
        r"(?:rename|retitle) (?:to|as) (.+)",
        r"title (?:is|should be|now) (.+)"
    ]
    
    for pattern in title_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip().capitalize()
    
    # If the entire text seems to be a new title
    if not any(keyword in text for keyword in ["description", "due", "date", "priority", "complete", "mark"]):
        return text.strip().capitalize()
    
    return None


def extract_description_update(text: str) -> Optional[str]:
    """
    Extracts description update from natural language text
    """
    # Look for patterns indicating a description change
    desc_patterns = [
        r"(?:change|update|modify|set) description (?:to|as) (.+)",
        r"(?:add|include|append) (?:description|details?) (?:of|as) (.+)",
        r"description (?:is|should be|now) (.+)"
    ]
    
    for pattern in desc_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return None


def extract_due_date_update(text: str) -> Optional[str]:
    """
    Extracts due date update from natural language text
    """
    # Import from nlp_parser
    from .nlp_parser import extract_due_date
    return extract_due_date(text)


def extract_priority_update(text: str) -> Optional[str]:
    """
    Extracts priority update from natural language text
    """
    # Look for patterns indicating a priority change
    if re.search(r"\b(make|set|change|update) (?:it )?to (?:the )?(highest|high|medium|low) priority\b", text):
        match = re.search(r"\b(?:make|set|change|update) (?:it )?to (?:the )?(highest|high|medium|low) priority\b", text)
        if match:
            priority_word = match.group(1).lower()
            if priority_word in ["highest", "high"]:
                return Priority.HIGH.value
            elif priority_word == "low":
                return Priority.LOW.value
            else:
                return Priority.MEDIUM.value
    
    # Look for priority keywords without explicit "priority" term
    if re.search(r"\b(highest|high|urgent|asap|important)\b", text):
        return Priority.HIGH.value
    
    if re.search(r"\b(low|least important)\b", text):
        return Priority.LOW.value
    
    return None


def extract_completion_update(text: str) -> Optional[bool]:
    """
    Extracts completion status update from natural language text
    """
    # Look for patterns indicating completion status change
    if re.search(r"\b(mark|set|make|toggle) (?:it )?(?:as )?(completed|done|finished|complete)\b", text):
        return True
    
    if re.search(r"\b(mark|set|make|toggle) (?:it )?(?:as )?(incomplete|not done|not finished|not complete|open)\b", text):
        return False
    
    # Direct statements about completion
    if re.search(r"\b(is|should be|now) (completed|done|finished|complete)\b", text):
        return True
    
    if re.search(r"\b(is|should be|now) (incomplete|not done|not finished|not complete|open)\b", text):
        return False
    
    return None