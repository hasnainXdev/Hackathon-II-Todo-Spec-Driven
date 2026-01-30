from typing import Dict, Any
from sqlmodel import Session, select
from ..models.user_preferences import UserPreferences  # Assuming this model exists


class SuggestionsOptOutManager:
    """
    Manages the opt-out mechanism for AI suggestions
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def is_user_opted_out(self, user_id: str) -> bool:
        """
        Check if a user has opted out of AI suggestions
        """
        statement = select(UserPreferences).where(UserPreferences.user_id == user_id)
        user_prefs = self.session.exec(statement).first()
        
        if not user_prefs:
            # If no preferences exist, default to opted in
            return False
        
        return not user_prefs.ai_suggestions_enabled
    
    def opt_user_in(self, user_id: str) -> bool:
        """
        Opt a user back into AI suggestions
        """
        statement = select(UserPreferences).where(UserPreferences.user_id == user_id)
        user_prefs = self.session.exec(statement).first()
        
        if not user_prefs:
            # Create preferences record if it doesn't exist
            user_prefs = UserPreferences(
                user_id=user_id,
                ai_suggestions_enabled=True
            )
            self.session.add(user_prefs)
        else:
            # Update existing preferences
            user_prefs.ai_suggestions_enabled = True
        
        self.session.commit()
        return True
    
    def opt_user_out(self, user_id: str) -> bool:
        """
        Opt a user out of AI suggestions
        """
        statement = select(UserPreferences).where(UserPreferences.user_id == user_id)
        user_prefs = self.session.exec(statement).first()
        
        if not user_prefs:
            # Create preferences record if it doesn't exist
            user_prefs = UserPreferences(
                user_id=user_id,
                ai_suggestions_enabled=False
            )
            self.session.add(user_prefs)
        else:
            # Update existing preferences
            user_prefs.ai_suggestions_enabled = False
        
        self.session.commit()
        return True
    
    def toggle_suggestions_preference(self, user_id: str) -> bool:
        """
        Toggle the user's AI suggestions preference
        """
        statement = select(UserPreferences).where(UserPreferences.user_id == user_id)
        user_prefs = self.session.exec(statement).first()
        
        if not user_prefs:
            # If no preferences exist, default to opting out
            user_prefs = UserPreferences(
                user_id=user_id,
                ai_suggestions_enabled=False
            )
            self.session.add(user_prefs)
        else:
            # Toggle the current setting
            user_prefs.ai_suggestions_enabled = not user_prefs.ai_suggestions_enabled
        
        self.session.commit()
        return user_prefs.ai_suggestions_enabled
    
    def get_user_preference(self, user_id: str) -> Dict[str, Any]:
        """
        Get the user's current preference regarding AI suggestions
        """
        statement = select(UserPreferences).where(UserPreferences.user_id == user_id)
        user_prefs = self.session.exec(statement).first()
        
        if not user_prefs:
            # Default to opted in if no preferences exist
            return {
                "user_id": user_id,
                "ai_suggestions_enabled": True,
                "opted_out": False
            }
        
        return {
            "user_id": user_id,
            "ai_suggestions_enabled": user_prefs.ai_suggestions_enabled,
            "opted_out": not user_prefs.ai_suggestions_enabled
        }
    
    def process_opt_out_request(self, user_message: str, user_id: str) -> Dict[str, Any]:
        """
        Process a user's request to opt out of or opt back into AI suggestions
        """
        user_message_lower = user_message.lower()
        
        # Check if the message contains opt-out related keywords
        opt_out_indicators = [
            "opt out", "unsubscribe", "stop suggestions", 
            "disable ai", "turn off suggestions", "no more suggestions"
        ]
        
        opt_in_indicators = [
            "opt in", "resubscribe", "enable suggestions",
            "turn on ai", "want suggestions", "restart suggestions"
        ]
        
        toggled = False
        action_taken = ""
        
        if any(indicator in user_message_lower for indicator in opt_out_indicators):
            if self.opt_user_out(user_id):
                toggled = True
                action_taken = "opt_out"
        elif any(indicator in user_message_lower for indicator in opt_in_indicators):
            if self.opt_user_in(user_id):
                toggled = True
                action_taken = "opt_in"
        elif "toggle" in user_message_lower and ("suggestions" in user_message_lower or "ai" in user_message_lower):
            enabled = self.toggle_suggestions_preference(user_id)
            toggled = True
            action_taken = "toggle_on" if enabled else "toggle_off"
        
        return {
            "request_processed": toggled,
            "action_taken": action_taken,
            "preferences": self.get_user_preference(user_id)
        }


# Example UserPreferences model (if it doesn't exist yet)
"""
class UserPreferences(SQLModel, table=True):
    user_id: str = Field(foreign_key="user.id", primary_key=True)
    ai_suggestions_enabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: "User" = Relationship(back_populates="preferences")
"""