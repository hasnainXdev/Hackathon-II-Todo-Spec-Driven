from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from core.security import get_current_user
from database.session import get_db
from models.user_preference import UserPreference, UserPreferenceCreate, UserPreferenceRead, UserPreferenceUpdate
from services.user_preference_service import UserPreferenceService
from utils.exceptions import TaskException

router = APIRouter()


@router.get("/", response_model=list[UserPreferenceRead])
async def get_preferences(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all preferences for the current user"""
    service = UserPreferenceService(db)
    try:
        preferences = service.get_all_preferences(current_user["id"])
        return preferences
    except TaskException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get("/{key}", response_model=UserPreferenceRead)
async def get_preference(
    key: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific preference for the current user"""
    service = UserPreferenceService(db)
    try:
        preference = service.get_preference(current_user["id"], key)
        if not preference:
            raise TaskException(f"Preference '{key}' not found for user {current_user['id']}")
        return preference
    except TaskException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.put("/{key}", response_model=UserPreferenceRead)
async def update_preference(
    key: str,
    preference_data: UserPreferenceUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a specific preference for the current user"""
    service = UserPreferenceService(db)
    try:
        # If preference doesn't exist, create it
        existing_pref = service.get_preference(current_user["id"], key)
        if not existing_pref:
            # Create a new preference
            new_pref_data = UserPreferenceCreate(
                preference_key=key,
                preference_value=preference_data.preference_value
            )
            preference = service.create_preference(new_pref_data, current_user["id"])
        else:
            # Update the existing preference
            preference = service.update_preference(current_user["id"], key, preference_data)

        return preference
    except TaskException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.delete("/{key}")
async def delete_preference(
    key: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific preference for the current user"""
    service = UserPreferenceService(db)
    try:
        success = service.delete_preference(current_user["id"], key)
        return {"message": "Preference deleted successfully"}
    except TaskException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)