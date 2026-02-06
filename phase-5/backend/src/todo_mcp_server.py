from mcp.server.fastmcp import FastMCP, Icon
from typing import Dict, Any
import json
import sys
from pathlib import Path
from sqlmodel import create_engine, Session
from core.config import settings
import urllib.parse

# Add the project root to the path to import database models and services
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from models.task import TaskCreate, TaskUpdate
from services.task_service import TaskService
from database.session import get_session, engine


# Initialize the MCP server for todo operations
mcp = FastMCP(
    "Todo Service",
    website_url="https://todo-service.example.com",
    icons=[Icon(src="https://todo-service.example.com/icon.png", mimeType="image/png")]
)


def get_db_session():
    """Helper to get database session"""
    return Session(engine)


def get_authenticated_user_id() -> str:
    """
    Placeholder function to get the authenticated user ID.
    In a real implementation, this would extract the user ID from the authentication context.
    For now, returning a placeholder that should be replaced with actual authentication.
    """
    # This is a temporary placeholder - in a real implementation,
    # this would extract the user ID from the authentication context
    import os
    # For now, we'll use an environment variable or return a default
    # In production, this should be replaced with proper authentication
    user_id = os.getenv("AUTHENTICATED_USER_ID", "default_user")
    return user_id


@mcp.tool()
def create_todo(title: str, description: str = "", priority: str = "medium", category: str = "") -> str:
    """
    Creates a new todo item with the given parameters.
    """
    try:
        with get_db_session() as session:
            # Get the authenticated user ID
            user_id = get_authenticated_user_id()

            # Create task data - don't set user_id in TaskCreate as it will be set by the service
            task_data = TaskCreate(
                title=title,
                description=description,
                priority=priority,
            )

            # Create task service and create the task
            task_service = TaskService(session)
            created_task = task_service.create_task(task_data, user_id)

            # Return the created task as JSON
            task_dict = {
                "id": created_task.id,
                "title": created_task.title,
                "description": created_task.description,
                "priority": created_task.priority,
                "completed": created_task.completion_status,
                "created_at": created_task.created_at.isoformat(),
                "updated_at": created_task.updated_at.isoformat(),
                "user_id": created_task.user_id
            }

            return json.dumps(task_dict)
    except Exception as e:
        error_result = {
            "error": str(e),
            "message": "Failed to create todo"
        }
        return json.dumps(error_result)


@mcp.tool()
def get_todos(filter_by: str = "all", category: str = "", priority: str = "", search: str = "") -> str:
    """
    Retrieves a list of todo items based on optional filters.
    """
    try:
        with get_db_session() as session:
            # Get the authenticated user ID
            user_id = get_authenticated_user_id()

            # Create task service and get tasks
            task_service = TaskService(session)
            tasks = task_service.get_tasks_by_user(user_id)

            # Apply filters if provided
            filtered_tasks = []
            for task in tasks:
                # Apply status filter
                if filter_by == "completed" and not task.completion_status:
                    continue
                elif filter_by == "pending" and task.completion_status:
                    continue

                # Apply category filter (currently tasks don't have categories in the model)
                # This is kept for compatibility but won't filter anything in current model
                if category and category.lower() not in (task.title + (task.description or "")).lower():
                    continue

                # Apply priority filter
                if priority and task.priority.lower() != priority.lower():
                    continue

                # Apply search filter (search in title and description)
                if search and search.lower() not in (task.title + (task.description or "")).lower():
                    continue

                filtered_tasks.append({
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "priority": task.priority,
                    "completed": task.completion_status,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat(),
                    "user_id": task.user_id
                })

            return json.dumps(filtered_tasks)
    except Exception as e:
        error_result = {
            "error": str(e),
            "message": "Failed to retrieve todos"
        }
        return json.dumps(error_result)


@mcp.tool()
def update_todo(todo_id: str = None, title: str = None, description: str = None,
                priority: str = None, category: str = None, completed: bool = None) -> str:
    """
    Updates an existing todo item with the provided parameters.
    If todo_id is not provided, attempts to find the task by title.
    """
    try:
        with get_db_session() as session:
            # Get the authenticated user ID
            user_id = get_authenticated_user_id()

            task_service = TaskService(session)

            # If no ID provided, try to find by title
            if not todo_id and title:
                # Get all tasks for the user
                all_tasks = task_service.get_tasks_by_user(user_id)

                # Find the task with matching title (case-insensitive)
                matching_task = None
                for task in all_tasks:
                    if title.lower() in task.title.lower():
                        matching_task = task
                        break

                if not matching_task:
                    error_result = {
                        "error": f"No task found with title containing '{title}' for user {user_id}",
                        "message": "Task not found"
                    }
                    return json.dumps(error_result)

                todo_id = matching_task.id
            elif not todo_id:
                error_result = {
                    "error": "Either todo_id or title must be provided to update a task",
                    "message": "Missing identifier"
                }
                return json.dumps(error_result)

            # Get the existing task to check if it exists and belongs to the user
            existing_task = task_service.get_task_by_id(todo_id, user_id)

            if not existing_task:
                error_result = {
                    "error": f"Task with id {todo_id} not found for user {user_id}",
                    "message": "Task not found"
                }
                return json.dumps(error_result)

            # Prepare update data
            update_data = {}
            if title is not None:
                update_data["title"] = title
            if description is not None:
                update_data["description"] = description
            if priority is not None:
                update_data["priority"] = priority
            if completed is not None:
                update_data["completion_status"] = completed
            # Note: category is not part of the current Task model

            # Create TaskUpdate object with the provided updates
            task_update_data = TaskUpdate(**{k: v for k, v in update_data.items()})

            # Update the task
            updated_task = task_service.update_task(todo_id, task_update_data, user_id)

            # Return the updated task as JSON
            task_dict = {
                "id": updated_task.id,
                "title": updated_task.title,
                "description": updated_task.description,
                "priority": updated_task.priority,
                "completed": updated_task.completion_status,
                "created_at": updated_task.created_at.isoformat(),
                "updated_at": updated_task.updated_at.isoformat(),
                "user_id": updated_task.user_id
            }

            return json.dumps(task_dict)
    except Exception as e:
        error_result = {
            "error": str(e),
            "message": "Failed to update todo"
        }
        return json.dumps(error_result)


@mcp.tool()
def delete_todo(todo_id: str = None, title: str = None) -> str:
    """
    Deletes a todo item by its ID or title.
    """
    try:
        with get_db_session() as session:
            # Get the authenticated user ID
            user_id = get_authenticated_user_id()

            task_service = TaskService(session)

            # If no ID provided, try to find by title
            if not todo_id and title:
                # Get all tasks for the user
                all_tasks = task_service.get_tasks_by_user(user_id)

                # Find the task with matching title (case-insensitive)
                matching_task = None
                for task in all_tasks:
                    if title.lower() in task.title.lower():
                        matching_task = task
                        break

                if not matching_task:
                    error_result = {
                        "error": f"No task found with title containing '{title}' for user {user_id}",
                        "message": "Task not found"
                    }
                    return json.dumps(error_result)

                todo_id = matching_task.id
            elif not todo_id:
                error_result = {
                    "error": "Either todo_id or title must be provided to delete a task",
                    "message": "Missing identifier"
                }
                return json.dumps(error_result)

            # Create task service and delete the task
            success = task_service.delete_task(todo_id, user_id)

            if success:
                result = {
                    "success": True,
                    "deleted_id": todo_id,
                    "message": f"Todo item {todo_id} has been deleted successfully"
                }
            else:
                result = {
                    "success": False,
                    "deleted_id": todo_id,
                    "message": f"Failed to delete todo item {todo_id}"
                }

            return json.dumps(result)
    except Exception as e:
        error_result = {
            "error": str(e),
            "message": "Failed to delete todo"
        }
        return json.dumps(error_result)


@mcp.resource("todos://list")
def get_todo_list() -> str:
    """
    Exposes the current list of todos as a resource.
    """
    try:
        with get_db_session() as session:
            # Get the authenticated user ID
            user_id = get_authenticated_user_id()

            # Create task service and get tasks
            task_service = TaskService(session)
            tasks = task_service.get_tasks_by_user(user_id)

            # Calculate statistics
            total_count = len(tasks)
            completed_count = sum(1 for task in tasks if task.completion_status)
            pending_count = total_count - completed_count

            # Extract unique priorities
            priorities = list(set(task.priority for task in tasks))

            # This is a simplified version - in a real implementation, categories would be part of the model
            categories = []  # Categories are not currently part of the model

            data = {
                "total_count": total_count,
                "completed_count": completed_count,
                "pending_count": pending_count,
                "categories": categories,
                "priorities": priorities
            }

            return json.dumps(data)
    except Exception as e:
        error_result = {
            "error": str(e),
            "message": "Failed to retrieve todo list"
        }
        return json.dumps(error_result)


@mcp.prompt()
def generate_productivity_tip(category: str = "general") -> str:
    """
    Generates a productivity tip based on the specified category.
    """
    tips = {
        "work": "Break large work tasks into smaller, manageable chunks to improve focus and reduce overwhelm.",
        "personal": "Schedule personal tasks during your most energetic hours of the day for maximum efficiency.",
        "health": "Include health-related todos in your list to maintain a balanced lifestyle.",
        "general": "Prioritize your todos by importance and deadline to stay organized and productive."
    }

    tip = tips.get(category, tips["general"])
    return f"Productivity Tip: {tip}"


# Run the server
if __name__ == "__main__":
    mcp.run()