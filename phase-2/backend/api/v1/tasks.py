from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from core.security import get_current_user
from database.session import get_db
from models.task import Task, TaskCreate, TaskRead, TaskUpdate
from services.task_service import TaskService
from utils.exceptions import TaskNotFoundException, TaskUpdateConflictException

router = APIRouter()


@router.get("/", response_model=list[TaskRead])
async def get_tasks(
    current_user: dict = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all tasks for the current user"""
    service = TaskService(db)
    tasks = service.get_tasks_by_user(current_user["id"], skip=skip, limit=limit)
    return tasks


@router.post("/", response_model=TaskRead)
async def create_task(
    task_data: TaskCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new task for the current user"""
    service = TaskService(db)
    task = service.create_task(task_data, current_user["id"])
    return task


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific task by ID"""
    service = TaskService(db)
    try:
        task = service.get_task_by_id(task_id, current_user["id"])
        if not task:
            raise TaskNotFoundException(task_id)
        return task
    except TaskNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )


@router.put("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a specific task"""
    service = TaskService(db)
    try:
        task = service.update_task(task_id, task_data, current_user["id"])
        return task
    except TaskNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    except TaskUpdateConflictException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Task with id {task_id} was modified by another user. Please refresh and try again."
        )


@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific task"""
    service = TaskService(db)
    try:
        success = service.delete_task(task_id, current_user["id"])
        return {"message": "Task deleted successfully"}
    except TaskNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )


@router.patch("/{task_id}/complete")
async def toggle_task_completion(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle the completion status of a task"""
    service = TaskService(db)
    try:
        task = service.toggle_completion(task_id, current_user["id"])
        return {"id": task.id, "completion_status": task.completion_status}
    except TaskNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )