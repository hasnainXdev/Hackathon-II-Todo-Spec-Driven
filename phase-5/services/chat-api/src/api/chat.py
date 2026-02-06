from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from uuid import UUID
import re
from datetime import datetime
from datetime import timedelta

from ..models.task import PriorityEnum
from ..services.task_service import TaskService

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])
task_service = TaskService()


def parse_priority(text: str) -> PriorityEnum:
    """Extract priority from text."""
    text_lower = text.lower()
    if 'high' in text_lower or 'urgent' in text_lower or 'critical' in text_lower:
        return PriorityEnum.HIGH
    elif 'low' in text_lower:
        return PriorityEnum.LOW
    elif 'critical' in text_lower:
        return PriorityEnum.CRITICAL
    else:
        return PriorityEnum.MEDIUM


def parse_due_date(text: str) -> datetime:
    """Extract due date from text."""
    text_lower = text.lower()
    
    # Look for explicit dates (e.g., "tomorrow", "next week", specific dates)
    if 'today' in text_lower:
        return datetime.utcnow().replace(hour=23, minute=59, second=59)
    elif 'tomorrow' in text_lower:
        return (datetime.utcnow() + timedelta(days=1)).replace(hour=23, minute=59, second=59)
    elif 'next week' in text_lower:
        return (datetime.utcnow() + timedelta(weeks=1)).replace(hour=23, minute=59, second=59)
    elif 'next month' in text_lower:
        return (datetime.utcnow() + timedelta(days=30)).replace(hour=23, minute=59, second=59)
    else:
        # Simple regex to catch dates in format MM/DD/YYYY or DD/MM/YYYY
        date_pattern = r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b'
        match = re.search(date_pattern, text)
        if match:
            try:
                date_str = match.group(1)
                # Try US format first (MM/DD/YYYY)
                try:
                    parsed_date = datetime.strptime(date_str, '%m/%d/%Y')
                except ValueError:
                    # Try European format (DD/MM/YYYY)
                    parsed_date = datetime.strptime(date_str, '%d/%m/%Y')
                return parsed_date.replace(hour=23, minute=59, second=59)
            except ValueError:
                pass
    
    return None


def parse_tags(text: str) -> list:
    """Extract tags from text (words preceded by #)."""
    tag_pattern = r'#(\w+)'
    tags = re.findall(tag_pattern, text)
    return tags


def parse_recurrence(text: str) -> str:
    """Extract recurrence rule from text."""
    text_lower = text.lower()
    
    if 'daily' in text_lower:
        return 'daily'
    elif 'weekly' in text_lower:
        return 'weekly'
    elif 'monthly' in text_lower:
        return 'monthly'
    elif 'yearly' in text_lower:
        return 'yearly'
    
    return None


@router.post("/")
async def process_chat_command(command_data: Dict[str, Any]):
    """
    Process a chat command to perform task operations.
    Expected format: {"command": "string", "userId": "string"}
    """
    command = command_data.get("command", "").strip()
    user_id_str = command_data.get("userId", "")
    
    if not command:
        raise HTTPException(status_code=400, detail="Command is required")
    
    if not user_id_str:
        raise HTTPException(status_code=400, detail="User ID is required")
    
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    # Normalize the command for easier parsing
    normalized_cmd = command.lower().strip()
    
    # Handle different types of commands
    if any(word in normalized_cmd for word in ["add", "create", "new", "make"]):
        # Extract task title (everything after "add task:" or similar)
        title_match = re.search(r'(?:add|create|new|make)\s+(?:a\s+|an\s+|the\s+)?(?:task|todo|to-do|item)\s*[:\-]?\s*(.*)', command, re.IGNORECASE)
        if not title_match:
            # If no specific pattern matched, try to extract the main content
            title_match = re.search(r'(?:add|create|new|make)\s+(?:a\s+|an\s+|the\s+)?(?:task|todo|to-do|item)\s*(.*)', command, re.IGNORECASE)
        
        if title_match:
            title_text = title_match.group(1).strip()
            
            # Extract additional details
            priority = parse_priority(title_text)
            due_date = parse_due_date(title_text)
            tags = parse_tags(title_text)
            recurrence_rule = parse_recurrence(title_text)
            
            # Clean up title by removing extracted elements
            cleaned_title = re.sub(r'\b(high|low|medium|critical|urgent)\b', '', title_text, flags=re.IGNORECASE).strip()
            cleaned_title = re.sub(r'#\w+', '', cleaned_title).strip()
            cleaned_title = re.sub(r'\b(today|tomorrow|next week|next month)\b', '', cleaned_title, flags=re.IGNORECASE).strip()
            cleaned_title = re.sub(r'\b(daily|weekly|monthly|yearly)\b', '', cleaned_title, flags=re.IGNORECASE).strip()
            cleaned_title = re.sub(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', '', cleaned_title).strip()
            cleaned_title = re.sub(r'\s+', ' ', cleaned_title).strip()
            
            if not cleaned_title:
                cleaned_title = "Untitled Task"
            
            # Create the task
            task = task_service.create_task(
                title=cleaned_title,
                description=title_text,
                priority=priority,
                tags=tags,
                due_date=due_date,
                recurrence_rule=recurrence_rule,
                user_id=user_id
            )
            
            return {
                "success": True,
                "message": f"Task '{task.title}' created successfully!",
                "taskId": str(task.id),
                "eventType": "TASK_CREATED",
                "eventId": str(task.id)  # Simplified - in reality, this would be a separate event ID
            }
        else:
            raise HTTPException(status_code=400, detail="Could not extract task details from command")
    
    elif any(word in normalized_cmd for word in ["show", "list", "view", "see"]):
        # Get all tasks for the user
        tasks = task_service.get_tasks_by_user(user_id=user_id)
        
        if not tasks:
            return {
                "success": True,
                "message": "You have no tasks.",
                "tasks": []
            }
        else:
            return {
                "success": True,
                "message": f"You have {len(tasks)} task(s).",
                "tasks": [{"id": str(t.id), "title": t.title, "completed": t.completed} for t in tasks]
            }
    
    elif any(word in normalized_cmd for word in ["complete", "finish", "done", "mark"]):
        # Extract task ID or title to complete
        id_match = re.search(r'(\d+)', command)
        if id_match:
            # This is a simplified approach - in reality, you'd need to map user-friendly IDs to UUIDs
            # For now, we'll just return an error since we don't have a mapping
            return {
                "success": False,
                "message": "Task completion by ID not fully implemented in this demo."
            }
        else:
            # Try to find by title keywords
            # This is a simplified approach - in reality, you'd need more sophisticated NLP
            return {
                "success": False,
                "message": "Task completion by title not fully implemented in this demo."
            }
    
    else:
        # Unknown command
        return {
            "success": False,
            "message": f"I didn't understand the command: '{command}'. Try commands like 'Add a task: Buy groceries' or 'Show me my tasks'."
        }