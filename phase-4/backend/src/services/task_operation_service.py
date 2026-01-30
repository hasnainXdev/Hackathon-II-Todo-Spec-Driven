from typing import Dict, Any, Optional, List
from sqlmodel import Session
from datetime import datetime
from ..utils.intent_recognizer import recognize_intent, IntentType
from ..utils.nlp_parser import parse_task_creation
from ..utils.nlp_task_updates import parse_task_update
from ..utils.nlp_task_deletion import parse_task_deletion
from ..utils.nlp_task_completion import parse_task_completion
from ..utils.error_formatter import create_task_operation_error
from ..core.ai_logging import AIServiceLogger, AILogLevel

# Handle the imports that might be in different locations depending on how the module is run
try:
    # When running as part of the package structure
    from ...services.task_service import TaskService
    from ...models.task import TaskCreate, TaskUpdate
except (ImportError, ValueError):
    # Fallback for when the module is run directly
    import sys
    import os
    from pathlib import Path
    # Add the project root to the path
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

    from services.task_service import TaskService
    from models.task import TaskCreate, TaskUpdate


class TaskOperationService:
    """
    Service class for executing task operations based on NLP-parsed intents
    """
    
    def __init__(self, session: Session):
        self.session = session
        self.task_service = TaskService(session)
        self.logger = AIServiceLogger(__name__)

    async def execute_task_operation(
        self, 
        user_id: str, 
        message: str, 
        user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Execute a task operation based on the user's message
        """
        try:
            # Recognize the intent from the message
            intent_type, params = recognize_intent(message)
            
            self.logger.log_event(AILogLevel.INFO, f"Recognized intent: {intent_type.value} for user {user_id}")
            
            # Execute the appropriate operation based on the intent
            if intent_type == IntentType.CREATE_TASK:
                return await self._execute_create_task(user_id, params)
            elif intent_type == IntentType.UPDATE_TASK:
                return await self._execute_update_task(user_id, params)
            elif intent_type == IntentType.DELETE_TASK:
                return await self._execute_delete_task(user_id, params)
            elif intent_type == IntentType.COMPLETE_TASK:
                return await self._execute_complete_task(user_id, params)
            elif intent_type == IntentType.GET_TASKS:
                return await self._execute_get_tasks(user_id)
            else:
                # For unknown intents, return a response indicating the intent wasn't recognized
                return {
                    "success": False,
                    "response": "I didn't understand that request. You can ask me to create, update, delete, or view your tasks.",
                    "action_performed": "unknown_intent"
                }
                
        except Exception as e:
            self.logger.log_event(AILogLevel.ERROR, f"Error executing task operation for user {user_id}: {str(e)}")
            return {
                "success": False,
                "response": f"An error occurred while processing your request: {str(e)}",
                "action_performed": "error"
            }

    async def _execute_create_task(self, user_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute task creation based on parsed parameters
        """
        try:
            # Create a TaskCreate object from the parsed parameters
            task_create_data = TaskCreate(
                title=params.get("title", ""),
                description=params.get("description", ""),
                completion_status=params.get("completion_status", False),
                due_date=params.get("due_date"),
                priority=params.get("priority", "medium"),
                user_id=user_id  # Add the user_id to the task
            )
            
            # Create the task using the task service
            created_task = self.task_service.create_task(task_create_data, user_id)
            
            self.logger.log_event(AILogLevel.INFO, f"Created task {created_task.id} for user {user_id}")
            
            return {
                "success": True,
                "response": f"I've created the task '{created_task.title}' for you.",
                "action_performed": "create_task",
                "task_details": {
                    "id": created_task.id,
                    "title": created_task.title,
                    "description": created_task.description,
                    "due_date": created_task.due_date,
                    "priority": created_task.priority
                }
            }
        except Exception as e:
            self.logger.log_event(AILogLevel.ERROR, f"Error creating task for user {user_id}: {str(e)}")
            error_msg = create_task_operation_error("create", params.get("title", ""), str(e))
            return {
                "success": False,
                "response": error_msg,
                "action_performed": "create_task_failed"
            }

    async def _execute_update_task(self, user_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute task update based on parsed parameters
        """
        try:
            # Find the task to update (this is a simplified approach)
            # In a real implementation, we'd have more sophisticated task identification
            task_identifier = params.get("task_identifier", "")
            
            # For now, we'll just get all tasks and try to match based on title
            user_tasks = self.task_service.get_tasks_by_user(user_id)
            target_task = None
            
            for task in user_tasks:
                if task_identifier.lower() in task.title.lower() or task_identifier.lower() in (task.description or "").lower():
                    target_task = task
                    break
            
            if not target_task:
                return {
                    "success": False,
                    "response": f"I couldn't find a task matching '{task_identifier}'. Could you be more specific?",
                    "action_performed": "update_task_failed_no_match"
                }
            
            # Prepare update data
            update_data = {}
            if "title" in params:
                update_data["title"] = params["title"]
            if "description" in params:
                update_data["description"] = params["description"]
            if "due_date" in params:
                update_data["due_date"] = params["due_date"]
            if "priority" in params:
                update_data["priority"] = params["priority"]
            
            # Create TaskUpdate object
            task_update_data = TaskUpdate(**update_data)
            
            # Update the task
            updated_task = self.task_service.update_task(target_task.id, task_update_data, user_id)
            
            self.logger.log_event(AILogLevel.INFO, f"Updated task {updated_task.id} for user {user_id}")
            
            return {
                "success": True,
                "response": f"I've updated the task '{updated_task.title}' for you.",
                "action_performed": "update_task",
                "task_details": {
                    "id": updated_task.id,
                    "title": updated_task.title,
                    "description": updated_task.description,
                    "due_date": updated_task.due_date,
                    "priority": updated_task.priority
                }
            }
        except Exception as e:
            self.logger.log_event(AILogLevel.ERROR, f"Error updating task for user {user_id}: {str(e)}")
            error_msg = create_task_operation_error("update", params.get("task_identifier", ""), str(e))
            return {
                "success": False,
                "response": error_msg,
                "action_performed": "update_task_failed"
            }

    async def _execute_delete_task(self, user_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute task deletion based on parsed parameters
        """
        try:
            # Find the task to delete
            task_identifier = params.get("task_identifier", "")
            
            # For now, we'll just get all tasks and try to match based on title
            user_tasks = self.task_service.get_tasks_by_user(user_id)
            target_task = None
            
            for task in user_tasks:
                if task_identifier.lower() in task.title.lower() or task_identifier.lower() in (task.description or "").lower():
                    target_task = task
                    break
            
            if not target_task:
                return {
                    "success": False,
                    "response": f"I couldn't find a task matching '{task_identifier}'. Could you be more specific?",
                    "action_performed": "delete_task_failed_no_match"
                }
            
            # Delete the task
            success = self.task_service.delete_task(target_task.id, user_id)
            
            if success:
                self.logger.log_event(AILogLevel.INFO, f"Deleted task {target_task.id} for user {user_id}")
                
                return {
                    "success": True,
                    "response": f"I've deleted the task '{target_task.title}' for you.",
                    "action_performed": "delete_task",
                    "task_details": {
                        "id": target_task.id,
                        "title": target_task.title
                    }
                }
            else:
                return {
                    "success": False,
                    "response": f"Failed to delete the task '{target_task.title}'.",
                    "action_performed": "delete_task_failed"
                }
        except Exception as e:
            self.logger.log_event(AILogLevel.ERROR, f"Error deleting task for user {user_id}: {str(e)}")
            error_msg = create_task_operation_error("delete", params.get("task_identifier", ""), str(e))
            return {
                "success": False,
                "response": error_msg,
                "action_performed": "delete_task_failed"
            }

    async def _execute_complete_task(self, user_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute task completion based on parsed parameters
        """
        try:
            # Find the task to complete/incomplete
            task_identifier = params.get("task_identifier", "")
            completed_status = params.get("completed", True)  # Default to marking as complete
            
            # For now, we'll just get all tasks and try to match based on title
            user_tasks = self.task_service.get_tasks_by_user(user_id)
            target_task = None
            
            for task in user_tasks:
                if task_identifier.lower() in task.title.lower() or task_identifier.lower() in (task.description or "").lower():
                    target_task = task
                    break
            
            if not target_task:
                return {
                    "success": False,
                    "response": f"I couldn't find a task matching '{task_identifier}'. Could you be more specific?",
                    "action_performed": "complete_task_failed_no_match"
                }
            
            # Toggle the completion status
            updated_task = self.task_service.toggle_completion(target_task.id, user_id)
            
            status_text = "completed" if updated_task.completion_status else "marked as incomplete"
            self.logger.log_event(AILogLevel.INFO, f"Marked task {updated_task.id} as {status_text} for user {user_id}")
            
            return {
                "success": True,
                "response": f"I've {status_text} the task '{updated_task.title}' for you.",
                "action_performed": "complete_task" if completed_status else "incomplete_task",
                "task_details": {
                    "id": updated_task.id,
                    "title": updated_task.title,
                    "completed": updated_task.completion_status
                }
            }
        except Exception as e:
            self.logger.log_event(AILogLevel.ERROR, f"Error completing task for user {user_id}: {str(e)}")
            error_msg = create_task_operation_error("complete", params.get("task_identifier", ""), str(e))
            return {
                "success": False,
                "response": error_msg,
                "action_performed": "complete_task_failed"
            }

    async def _execute_get_tasks(self, user_id: str) -> Dict[str, Any]:
        """
        Execute getting tasks
        """
        try:
            # Get all tasks for the user
            user_tasks = self.task_service.get_tasks_by_user(user_id)
            
            if not user_tasks:
                return {
                    "success": True,
                    "response": "You don't have any tasks yet. You can add tasks by telling me what you need to do!",
                    "action_performed": "get_tasks_empty"
                }
            
            # Format the response
            task_list = []
            for task in user_tasks:
                status = "completed" if task.completion_status else "pending"
                task_list.append(f"- {task.title} ({status})")
            
            task_list_str = "\n".join(task_list)
            response = f"Here are your tasks:\n{task_list_str}"
            
            return {
                "success": True,
                "response": response,
                "action_performed": "get_tasks",
                "task_details": [{"id": task.id, "title": task.title, "completed": task.completion_status} for task in user_tasks]
            }
        except Exception as e:
            self.logger.log_event(AILogLevel.ERROR, f"Error getting tasks for user {user_id}: {str(e)}")
            error_msg = create_task_operation_error("retrieve", "", str(e))
            return {
                "success": False,
                "response": error_msg,
                "action_performed": "get_tasks_failed"
            }