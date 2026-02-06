from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import json

from ..models.task import Task, PriorityEnum, Event
from ..services.task_service import TaskService
from ..services.task_history_service import TaskHistoryService

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])
task_service = TaskService()
task_history_service = TaskHistoryService()


@router.post("/", response_model=Task, status_code=201)
async def create_task(
    title: str,
    description: Optional[str] = None,
    priority: Optional[PriorityEnum] = PriorityEnum.MEDIUM,
    tags: Optional[List[str]] = [],
    due_date: Optional[datetime] = None,
    recurrence_rule: Optional[str] = None,
    user_id: UUID = None  # In a real implementation, this would come from auth
):
    """
    Create a new task.
    """
    if not title.strip():
        raise HTTPException(status_code=400, detail="Title is required and cannot be empty")
    
    # In a real implementation, user_id would come from authentication
    if not user_id:
        user_id = UUID(int=1)  # Placeholder
    
    try:
        task = task_service.create_task(
            title=title,
            description=description,
            priority=priority,
            tags=tags,
            due_date=due_date,
            recurrence_rule=recurrence_rule,
            user_id=user_id
        )
        return task
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")


@router.get("/{task_id}", response_model=Task)
async def get_task(task_id: UUID, user_id: UUID = None):
    """
    Get a specific task by ID.
    """
    # In a real implementation, user_id would come from authentication
    if not user_id:
        user_id = UUID(int=1)  # Placeholder
    
    task = task_service.get_task_by_id(task_id, user_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_id: UUID,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[PriorityEnum] = None,
    tags: Optional[List[str]] = None,
    due_date: Optional[datetime] = None,
    completed: Optional[bool] = None,
    user_id: UUID = None
):
    """
    Update an existing task.
    """
    # In a real implementation, user_id would come from authentication
    if not user_id:
        user_id = UUID(int=1)  # Placeholder
    
    updated_task = task_service.update_task(
        task_id=task_id,
        user_id=user_id,
        title=title,
        description=description,
        priority=priority,
        tags=tags,
        due_date=due_date,
        completed=completed
    )
    
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return updated_task


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: UUID, user_id: UUID = None):
    """
    Delete a task.
    """
    # In a real implementation, user_id would come from authentication
    if not user_id:
        user_id = UUID(int=1)  # Placeholder
    
    success = task_service.delete_task(task_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return


@router.post("/{task_id}/complete", response_model=Task)
async def complete_task(task_id: UUID, user_id: UUID = None):
    """
    Mark a task as complete.
    """
    # In a real implementation, user_id would come from authentication
    if not user_id:
        user_id = UUID(int=1)  # Placeholder
    
    task = task_service.complete_task(task_id, user_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task


@router.get("/", response_model=dict)
async def list_tasks(
    priority: Optional[PriorityEnum] = Query(None, description="Filter by priority level"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    sort_by: Optional[str] = Query("created_at", description="Field to sort by"),
    order: Optional[str] = Query("asc", description="Sort order"),
    search: Optional[str] = Query(None, description="Search term for title or description"),
    user_id: UUID = None
):
    """
    List tasks with optional filtering, sorting, and search.
    """
    # In a real implementation, user_id would come from authentication
    if not user_id:
        user_id = UUID(int=1)  # Placeholder
    
    if search:
        # Use search functionality if search term is provided
        tasks = task_service.search_tasks(
            user_id=user_id,
            search_term=search,
            priority=priority,
            completed=completed,
            tag=tag
        )
    else:
        # Use regular filtering if no search term
        tasks = task_service.get_tasks_by_user(
            user_id=user_id,
            priority=priority,
            completed=completed,
            tag=tag,
            sort_by=sort_by,
            order=order
        )
    
    return {"tasks": tasks, "total_count": len(tasks)}


@router.get("/{task_id}/history", response_model=List[dict])
async def get_task_history(task_id: UUID, user_id: UUID = None):
    """
    Get the history of events for a specific task.
    """
    # In a real implementation, user_id would come from authentication
    if not user_id:
        user_id = UUID(int=1)  # Placeholder
    
    # Verify that the user has access to this task
    task = task_service.get_task_by_id(task_id, user_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get the task history from the audit service
    history = await task_history_service.get_task_history(str(task_id))
    
    # Convert events to a serializable format
    history_dicts = [
        {
            "event_id": str(event.event_id),
            "event_type": event.event_type,
            "timestamp": event.timestamp.isoformat() if event.timestamp else None,
            "payload": event.payload
        }
        for event in history
    ]
    
    return history_dicts