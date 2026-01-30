from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlmodel import Session, select
from .models.conversation import Message
from .models.task import Task  # Assuming task model exists from phase-2


class ContextManager:
    """
    Manages conversation context to enable awareness for follow-up commands
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_recent_context(self, conversation_id: str, user_id: str, limit: int = 5) -> Dict[str, Any]:
        """
        Retrieves recent conversation context for follow-up understanding
        """
        # Get recent messages in the conversation
        statement = select(Message).where(
            Message.conversation_id == conversation_id,
            Message.user_id == user_id
        ).order_by(Message.created_at.desc()).limit(limit)
        
        recent_messages = self.session.exec(statement).all()
        
        # Get user's tasks
        task_statement = select(Task).where(Task.user_id == user_id)
        user_tasks = self.session.exec(task_statement).all()
        
        context = {
            "recent_messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.created_at.isoformat()
                } 
                for msg in reversed(recent_messages)  # Reverse to get chronological order
            ],
            "user_tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": getattr(task, 'description', ''),
                    "completed": getattr(task, 'completed', False),
                    "due_date": getattr(task, 'due_date', None)
                }
                for task in user_tasks
            ],
            "last_task_action": self._get_last_task_action(recent_messages)
        }
        
        return context
    
    def _get_last_task_action(self, messages: List[Message]) -> Optional[Dict[str, Any]]:
        """
        Gets the last task-related action from the conversation history
        """
        for message in reversed(messages):  # Go backwards to find the most recent
            if message.role == "assistant":
                # Simple heuristic to detect if the message relates to a task action
                content = message.content.lower()
                if any(action in content for action in ["task", "added", "created", "updated", "completed", "deleted"]):
                    return {
                        "content": message.content,
                        "timestamp": message.created_at.isoformat()
                    }
        
        return None
    
    def infer_task_reference(self, user_input: str, context: Dict[str, Any]) -> Optional[str]:
        """
        Infers which task the user is referring to based on context
        """
        # If user mentions a specific task ID or title, return that
        for task in context.get("user_tasks", []):
            if task["title"].lower() in user_input.lower():
                return task["id"]
        
        # If user says "it" or "that", infer from the last task action
        if any(pronoun in user_input.lower() for pronoun in ["it", "that", "the task"]):
            last_action = context.get("last_task_action")
            if last_action:
                # Try to find the task referenced in the last action
                for task in context.get("user_tasks", []):
                    if task["title"].lower() in last_action["content"].lower():
                        return task["id"]
        
        # If user refers to position ("first", "second", etc.), map to tasks
        position_map = {
            "first": 0, "second": 1, "third": 2, "fourth": 3, "fifth": 4,
            "1st": 0, "2nd": 1, "3rd": 2, "4th": 3, "5th": 4
        }
        
        for word, idx in position_map.items():
            if word in user_input.lower() and idx < len(context.get("user_tasks", [])):
                return context["user_tasks"][idx]["id"]
        
        # If user refers to a numbered task ("task 1", "task 2", etc.)
        import re
        number_match = re.search(r"task\s+(\d+)", user_input.lower())
        if number_match:
            task_num = int(number_match.group(1)) - 1  # Convert to 0-indexed
            if 0 <= task_num < len(context.get("user_tasks", [])):
                return context["user_tasks"][task_num]["id"]
        
        return None
    
    def update_context_for_followup(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates context to handle follow-up commands
        """
        # Infer task reference if applicable
        task_id = self.infer_task_reference(user_input, context)
        
        if task_id:
            context["inferred_task_id"] = task_id
            
            # Find the task details
            for task in context.get("user_tasks", []):
                if task["id"] == task_id:
                    context["inferred_task_details"] = task
                    break
        
        return context