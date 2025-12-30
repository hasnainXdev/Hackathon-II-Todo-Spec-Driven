"""
Utility functions for the Todo Console Application.
"""
import logging


def setup_logging():
    """
    Sets up basic logging configuration.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def validate_task_id(task_id: str) -> int:
    """
    Validates and converts a task ID string to an integer.
    
    Args:
        task_id: The task ID as a string
        
    Returns:
        The task ID as an integer
        
    Raises:
        ValueError: If the task ID is not a valid positive integer
    """
    try:
        task_id_int = int(task_id)
        if task_id_int <= 0:
            raise ValueError("Task ID must be a positive integer")
        return task_id_int
    except ValueError:
        raise ValueError(f"Invalid task ID: {task_id}. Task ID must be a positive integer")


def format_task(task):
    """
    Formats a task for display.
    
    Args:
        task: The task object to format
        
    Returns:
        A formatted string representation of the task
    """
    status = "✓" if task.completed else "○"
    return f"[{status}] ID: {task.id} | Title: {task.title} | Description: {task.description}"