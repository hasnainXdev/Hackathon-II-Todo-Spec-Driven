from typing import Dict, Any, Optional
from datetime import datetime
import re


def validate_task_data(task_data: Dict[str, Any]) -> Dict[str, list]:
    """
    Validates task data parsed from AI and returns any errors found
    """
    errors = {}

    # Validate title - required field
    if 'title' not in task_data or not task_data['title']:
        errors['title'] = ["Title is required"]
    else:
        title_errors = _validate_title(task_data['title'])
        if title_errors:
            errors['title'] = title_errors
    
    # Validate description
    if 'description' in task_data:
        desc_errors = _validate_description(task_data['description'])
        if desc_errors:
            errors['description'] = desc_errors
    
    # Validate due date
    if 'due_date' in task_data:
        date_errors = _validate_due_date(task_data['due_date'])
        if date_errors:
            errors['due_date'] = date_errors
    
    # Validate priority
    if 'priority' in task_data:
        priority_errors = _validate_priority(task_data['priority'])
        if priority_errors:
            errors['priority'] = priority_errors
    
    # Validate completion status
    if 'completed' in task_data:
        completion_errors = _validate_completion(task_data['completed'])
        if completion_errors:
            errors['completed'] = completion_errors
    
    return errors


def _validate_title(title: str) -> list:
    """
    Validates task title
    """
    errors = []
    
    if not title or not title.strip():
        errors.append("Title is required")
    elif len(title.strip()) > 200:
        errors.append("Title must be less than 200 characters")
    elif len(title.strip()) < 1:
        errors.append("Title must be at least 1 character")
    
    return errors


def _validate_description(description: str) -> list:
    """
    Validates task description
    """
    errors = []
    
    if description and len(description) > 1000:
        errors.append("Description must be less than 1000 characters")
    
    return errors


def _validate_due_date(due_date: str) -> list:
    """
    Validates task due date
    """
    errors = []
    
    if due_date:
        try:
            # Try to parse the date
            parsed_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            # Check if date is in the past (optional validation)
            # if parsed_date < datetime.now(parsed_date.tzinfo):
            #     errors.append("Due date cannot be in the past")
        except ValueError:
            errors.append("Invalid date format. Please use ISO format (YYYY-MM-DDTHH:MM:SS)")
    
    return errors


def _validate_priority(priority: str) -> list:
    """
    Validates task priority
    """
    errors = []
    
    valid_priorities = ['low', 'medium', 'high']
    
    if priority and priority not in valid_priorities:
        errors.append(f"Priority must be one of: {', '.join(valid_priorities)}")
    
    return errors


def _validate_completion(completed: bool) -> list:
    """
    Validates task completion status
    """
    errors = []
    
    if completed is not None and not isinstance(completed, bool):
        errors.append("Completion status must be a boolean value")
    
    return errors


def sanitize_task_data(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitizes task data by cleaning and normalizing values
    """
    sanitized = task_data.copy()
    
    # Sanitize title
    if 'title' in sanitized:
        sanitized['title'] = sanitized['title'].strip().capitalize()
    
    # Sanitize description
    if 'description' in sanitized and sanitized['description']:
        sanitized['description'] = sanitized['description'].strip()
    
    # Sanitize priority
    if 'priority' in sanitized and sanitized['priority']:
        sanitized['priority'] = sanitized['priority'].lower()
    
    return sanitized


def validate_and_sanitize_task_data(task_data: Dict[str, Any]) -> tuple:
    """
    Validates and sanitizes task data, returning both errors and sanitized data
    """
    errors = validate_task_data(task_data)
    sanitized_data = sanitize_task_data(task_data)
    
    return errors, sanitized_data