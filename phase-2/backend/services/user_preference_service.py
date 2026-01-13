from typing import List, Optional
from sqlmodel import Session, select
from models.user_preference import UserPreference, UserPreferenceCreate, UserPreferenceUpdate
from utils.exceptions import TaskException, UserNotAuthorizedException
from core.logging_config import logger


class UserPreferenceService:
    def __init__(self, session: Session):
        self.session = session

    def create_preference(self, preference_data: UserPreferenceCreate, user_id: str) -> UserPreference:
        """Create a new preference for a user"""
        try:
            # Check if preference already exists
            existing_pref = self.get_preference(user_id, preference_data.preference_key)
            if existing_pref:
                # Update the existing preference
                return self.update_preference(user_id, preference_data.preference_key,
                                            UserPreferenceUpdate(
                                                preference_value=preference_data.preference_value
                                            ))

            preference = UserPreference(
                user_id=user_id,
                preference_key=preference_data.preference_key,
                preference_value=preference_data.preference_value
            )
            self.session.add(preference)
            self.session.commit()
            self.session.refresh(preference)
            logger.info(f"Created preference {preference_data.preference_key} for user {user_id}")
            return preference
        except Exception as e:
            logger.error(f"Error creating preference: {e}")
            raise

    def get_preference(self, user_id: str, preference_key: str) -> Optional[UserPreference]:
        """Get a specific preference for a user"""
        try:
            preference = self.session.exec(
                select(UserPreference).where(
                    UserPreference.user_id == user_id,
                    UserPreference.preference_key == preference_key
                )
            ).first()
            return preference
        except Exception as e:
            logger.error(f"Error getting preference {preference_key} for user {user_id}: {e}")
            raise

    def get_all_preferences(self, user_id: str) -> List[UserPreference]:
        """Get all preferences for a user"""
        try:
            preferences = self.session.exec(
                select(UserPreference).where(UserPreference.user_id == user_id)
            ).all()
            logger.info(f"Retrieved {len(preferences)} preferences for user {user_id}")
            return preferences
        except Exception as e:
            logger.error(f"Error getting all preferences for user {user_id}: {e}")
            raise

    def update_preference(self, user_id: str, preference_key: str,
                         preference_data: UserPreferenceUpdate) -> Optional[UserPreference]:
        """Update a specific preference for a user"""
        try:
            preference = self.get_preference(user_id, preference_key)
            if not preference:
                raise TaskException(f"Preference '{preference_key}' not found for user {user_id}")

            update_data = preference_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if value is not None:
                    setattr(preference, field, value)

            self.session.add(preference)
            self.session.commit()
            self.session.refresh(preference)
            logger.info(f"Updated preference {preference_key} for user {user_id}")
            return preference
        except Exception as e:
            logger.error(f"Error updating preference {preference_key} for user {user_id}: {e}")
            raise

    def delete_preference(self, user_id: str, preference_key: str) -> bool:
        """Delete a specific preference for a user"""
        try:
            preference = self.get_preference(user_id, preference_key)
            if not preference:
                raise TaskException(f"Preference '{preference_key}' not found for user {user_id}")

            self.session.delete(preference)
            self.session.commit()
            logger.info(f"Deleted preference {preference_key} for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting preference {preference_key} for user {user_id}: {e}")
            raise