from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from core.security import get_current_user
from database.session import get_db
from schemas.user import UserRead

router = APIRouter()


@router.get("/me", response_model=UserRead)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's information
    """
    # In a real implementation, we would fetch user details from the database
    # For now, we return the user info from the JWT token
    return UserRead(
        id=current_user["id"],
        email=current_user.get("email", ""),
        created_at=current_user.get("created_at", ""),
        updated_at=current_user.get("updated_at", "")
    )


@router.post("/logout")
async def logout():
    """
    Logout endpoint
    """
    # In a real implementation, we would invalidate the JWT token
    # For now, we just return a success message
    return {"message": "Successfully logged out"}