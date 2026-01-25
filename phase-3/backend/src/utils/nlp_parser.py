import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from enum import Enum


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


def parse_task_creation(text: str) -> Optional[Dict[str, Any]]:
    """
    Parses natural language input to extract task creation parameters
    """
    # Normalize the input text
    normalized_text = text.lower().strip()

    # Define patterns for task creation - expanded to handle more variations
    create_patterns = [
        r"add (?:a|an)?\s*(?:(\w+)\s+)?(?:priority\s+)?task (?:to|for) (.+)",
        r"create (?:a|an)?\s*(?:(\w+)\s+)?(?:priority\s+)?task (?:to|for) (.+)",
        r"new (?:high|low|medium)?\s*task: (.+)",
        r"please add (?:a|an)?\s*(?:(high|highest|low|lowest|medium|urgent|asap|important|least)\s+)?(?:priority\s+)?(?:task\s+)?(.+)",
        r"i need to (.+)",
        r"remind me to (.+)",
        r"don'?t forget to (.+)",
        r"task: (.+)",
        r"(?:add|create) (?:a|an)?\s*(?:(\w+)\s+)?(?:priority\s+)?task (?:with|for) (.+)",
        r"(?:add|create) (?:a|an)?\s*(?:(\w+)\s+)?(?:priority\s+)?task (.+)"
    ]

    # Try to match any of the creation patterns
    matched = False
    extracted_title = ''
    extracted_priority = None

    for pattern in create_patterns:
        match = re.search(pattern, normalized_text)
        if match:
            matched = True
            # Handle different group structures in the patterns
            groups = match.groups()
            if len(groups) == 2:
                # Pattern with priority and title groups
                extracted_priority = groups[0]
                extracted_title = groups[1]
            else:
                # Pattern with just title group
                extracted_title = groups[0]
            break

    if not matched:
        # Try a more general approach for complex phrases
        general_pattern = r"(?:add|create|i need to|i have to|i've got to|please add|remind me to|don'?t forget to|remember to)\s+(?:a|an)?\s*(?:(\w+)\s+)?(?:priority\s+)?(?:task\s+)?(.+)"
        match = re.search(general_pattern, normalized_text)
        if match:
            groups = match.groups()
            if len(groups) == 2:
                extracted_priority = groups[0]
                extracted_title = groups[1]
            else:
                extracted_title = groups[0]
            matched = True

    if not matched:
        return None

    # Extract additional details like due date and priority
    due_date = extract_due_date(normalized_text)

    # Determine priority - use extracted priority if available, otherwise extract from text
    if extracted_priority:
        priority = extract_priority_from_word(extracted_priority)
    else:
        priority = extract_priority(normalized_text)

    # Clean up the title by removing due date and priority phrases
    cleaned_title = extracted_title
    if due_date:
        # Remove date-related phrases from title
        cleaned_title = re.sub(r"\b(by|before|on|due)\s+(today|tomorrow|\d{1,2}[\/\-]\d{1,2}([\/\-]\d{2,4})?|next week|next month)", "", cleaned_title, flags=re.IGNORECASE).strip()

    # Remove priority words from title if they were explicitly mentioned AND are valid priorities
    if extracted_priority:
        # Only remove from title if it's actually a valid priority word
        valid_priorities = ['high', 'highest', 'urgent', 'asap', 'important', 'low', 'lowest', 'least']
        if extracted_priority.lower() in valid_priorities:
            cleaned_title = re.sub(r"\b" + extracted_priority + r"\b", "", cleaned_title, flags=re.IGNORECASE).strip()

    # Also remove generic priority terms
    cleaned_title = re.sub(r"\b(highest|high|medium|low|priority|importance|urgent)\b", "", cleaned_title, flags=re.IGNORECASE).strip()

    # Create the task data dictionary
    task_data = {
        "title": capitalize(cleaned_title),
        "due_date": due_date,
        "priority": priority.value
    }

    # Remove None values
    task_data = {k: v for k, v in task_data.items() if v is not None}

    return task_data


def extract_due_date(text: str) -> Optional[str]:
    """
    Extracts due date from natural language text
    """
    # Look for "today"
    today_match = re.search(r"\b(today|todays?)\b", text)
    if today_match:
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    # Look for "tomorrow"
    tomorrow_match = re.search(r"\b(tomorrow)\b", text)
    if tomorrow_match:
        tomorrow = datetime.now() + timedelta(days=1)
        return tomorrow.strftime("%Y-%m-%dT%H:%M:%S")
    
    # Match MM/DD/YYYY, DD/MM/YYYY, or YYYY-MM-DD formats
    date_match = re.search(r"\b(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}|\d{4}-\d{2}-\d{2})\b", text)
    if date_match:
        try:
            date_str = date_match.group(0)
            # Try to parse the date
            for fmt in ("%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d", "%m-%d-%Y", "%d-%m-%Y"):
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    return parsed_date.strftime("%Y-%m-%dT%H:%M:%S")
                except ValueError:
                    continue
        except Exception as e:
            print(f'Error parsing date: {e}')
    
    # Look for "next week"
    next_week_match = re.search(r"\b(next week)\b", text)
    if next_week_match:
        next_week = datetime.now() + timedelta(weeks=1)
        return next_week.strftime("%Y-%m-%dT%H:%M:%S")
    
    # Look for "next month"
    next_month_match = re.search(r"\b(next month)\b", text)
    if next_month_match:
        next_month = datetime.now()
        next_month = next_month.replace(month=next_month.month + 1)
        return next_month.strftime("%Y-%m-%dT%H:%M:%S")
    
    return None


def extract_priority_from_word(word: str) -> Priority:
    """
    Extracts priority from a single word
    """
    if word and word.lower() in ['high', 'highest', 'urgent', 'asap', 'important']:
        return Priority.HIGH
    elif word and word.lower() in ['low', 'lowest', 'least']:
        return Priority.LOW
    else:
        return Priority.MEDIUM

def extract_priority(text: str) -> Priority:
    """
    Extracts priority from natural language text
    """
    if re.search(r"\b(highest|high|urgent|asap|important)\b", text):
        return Priority.HIGH

    if re.search(r"\b(low|least important)\b", text):
        return Priority.LOW

    # Default to medium if not specified
    return Priority.MEDIUM


def capitalize(text: str) -> str:
    """
    Capitalizes the first letter of a string
    """
    if not text:
        return text
    return text[0].upper() + text[1:]