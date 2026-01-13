from fastapi import APIRouter, Depends

from api.v1 import auth, tasks
from core.security import get_current_user

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])

# Add logout endpoint at the root level
@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout endpoint
    """
    # In a real implementation, we would invalidate the JWT token
    # For now, we just return a success message
    return {"message": "Successfully logged out"}