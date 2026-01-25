from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from fastapi import WebSocket, WebSocketException
import json

from core.security import get_current_user
from database.session import get_db
from models.task import Task, TaskCreate, TaskRead, TaskUpdate
from services.task_service import TaskService
from utils.exceptions import TaskNotFoundException, TaskUpdateConflictException
from .ws_manager import manager

router = APIRouter()


@router.get("/", response_model=list[TaskRead])
async def get_tasks(
    current_user: dict = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get all tasks for the current user"""
    # Validate that the user ID exists
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user token: user ID not found",
        )

    service = TaskService(db)
    tasks = service.get_tasks_by_user(user_id, skip=skip, limit=limit)
    return tasks


@router.post("/", response_model=TaskRead)
async def create_task(
    task_data: TaskCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new task for the current user"""
    # Validate that the user ID exists
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user token: user ID not found",
        )

    service = TaskService(db)
    task = service.create_task(task_data, user_id)

    # Broadcast the creation to all connected clients for this user
    event_data = {
        "type": "TASK_CREATED",
        "payload": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "completion_status": task.completion_status,
            "user_id": task.user_id,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat()
        }
    }
    await manager.broadcast_to_user(json.dumps(event_data), user_id)

    return task


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific task by ID"""
    # Validate that the user ID exists
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user token: user ID not found",
        )

    service = TaskService(db)
    try:
        task = service.get_task_by_id(task_id, user_id)
        if not task:
            raise TaskNotFoundException(task_id)
        return task
    except TaskNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )


@router.put("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a specific task"""
    # Validate that the user ID exists
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user token: user ID not found",
        )

    service = TaskService(db)
    try:
        task = service.update_task(task_id, task_data, user_id)

        # Broadcast the update to all connected clients for this user
        event_data = {
            "type": "TASK_UPDATED",
            "payload": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completion_status": task.completion_status,
                "user_id": task.user_id,
                "updated_at": task.updated_at.isoformat()
            }
        }
        await manager.broadcast_to_user(json.dumps(event_data), user_id)

        return task
    except TaskNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    except TaskUpdateConflictException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Task with id {task_id} was modified by another user. Please refresh and try again.",
        )


@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a specific task"""
    # Validate that the user ID exists
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user token: user ID not found",
        )

    service = TaskService(db)
    try:
        success = service.delete_task(task_id, user_id)

        # Broadcast the deletion to all connected clients for this user
        event_data = {
            "type": "TASK_DELETED",
            "payload": {
                "id": task_id
            }
        }
        await manager.broadcast_to_user(json.dumps(event_data), user_id)

        return {"message": "Task deleted successfully"}
    except TaskNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )


@router.patch("/{task_id}/complete")
async def toggle_task_completion(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Toggle the completion status of a task"""
    # Validate that the user ID exists
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user token: user ID not found",
        )

    service = TaskService(db)
    try:
        task = service.toggle_completion(task_id, user_id)

        # Broadcast the update to all connected clients for this user
        event_data = {
            "type": "TASK_UPDATED",
            "payload": {
                "id": task.id,
                "completion_status": task.completion_status,
                "updated_at": task.updated_at.isoformat()
            }
        }
        await manager.broadcast_to_user(json.dumps(event_data), user_id)

        return {"id": task.id, "completion_status": task.completion_status}
    except TaskNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )


from jose import JWTError, jwt
from core.config import settings


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time task updates"""
    await manager.connect(websocket, user_id)

    try:
        while True:
            # Listen for messages from the client
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle authentication message
            if message.get("type") == "AUTH":
                token = message.get("token")

                try:
                    # Decode and validate the JWT token
                    # Use the same secret as the token generation (BETTER_AUTH_SECRET)
                    secret_to_use = settings.BETTER_AUTH_SECRET or settings.SECRET_KEY
                    payload = jwt.decode(token, secret_to_use, algorithms=[settings.ALGORITHM])
                    token_user_id = payload.get("sub")

                    # Verify that the token's user ID matches the URL parameter
                    if token_user_id != user_id:
                        await manager.send_personal_message(
                            json.dumps({"type": "AUTH_ERROR", "message": "Unauthorized"}),
                            websocket
                        )
                        continue

                    # Token is valid and user IDs match
                    await manager.send_personal_message(
                        json.dumps({"type": "AUTH_SUCCESS", "message": "Authenticated"}),
                        websocket
                    )

                except JWTError:
                    # Invalid token
                    await manager.send_personal_message(
                        json.dumps({"type": "AUTH_ERROR", "message": "Invalid token"}),
                        websocket
                    )
                    continue

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
