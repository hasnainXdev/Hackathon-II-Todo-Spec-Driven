"""
Main application entry point for the Todo Console Application.
"""
from todo_app.services.task_service import TaskService


class TodoApp:
    """
    Main application class that manages the Todo Console Application.
    """
    
    def __init__(self):
        """
        Initializes the TodoApp with a TaskService instance.
        """
        self.task_service = TaskService()