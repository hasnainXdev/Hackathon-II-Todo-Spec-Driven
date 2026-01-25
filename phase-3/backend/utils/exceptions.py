from typing import Optional
from fastapi import HTTPException, status


class TaskException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class TaskNotFoundException(TaskException):
    def __init__(self, task_id: str):
        super().__init__(
            detail=f"Task with id {task_id} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )


class TaskUpdateConflictException(TaskException):
    def __init__(self, task_id: str):
        super().__init__(
            detail=f"Task with id {task_id} was modified by another user. Please refresh and try again.",
            status_code=status.HTTP_409_CONFLICT
        )


class UserNotAuthorizedException(TaskException):
    def __init__(self):
        super().__init__(
            detail="User not authorized to perform this action",
            status_code=status.HTTP_403_FORBIDDEN
        )