import json
from typing import Dict, Any, List
from datetime import datetime
from sqlmodel import Session, select
from ..models.user import User
from ..models.user_preferences import UserPreferences  # Assuming this model exists
from ..services.ai_service import AIService
from ..core.i18n_manager import get_localized_response


class AIChatbotOnboardingManager:
    """
    Manager for onboarding users to AI chatbot features
    """
    
    def __init__(self, session: Session, ai_service: AIService):
        self.session = session
        self.ai_service = ai_service
        self.onboarding_steps = [
            {
                "id": "welcome",
                "title": "Welcome to AI Todo Assistant!",
                "description": "Learn how to use the AI-powered chatbot to manage your tasks",
                "content": [
                    "The AI Todo Assistant helps you manage tasks using natural language.",
                    "Simply type what you want to do, and the AI will create, update, or manage your tasks."
                ],
                "actions": ["next"]
            },
            {
                "id": "basics",
                "title": "Getting Started",
                "description": "Basic commands to interact with the AI",
                "content": [
                    "Create tasks: 'Add a task to buy groceries'",
                    "Update tasks: 'Change the meeting task to include Zoom link'",
                    "Complete tasks: 'Mark the laundry task as complete'",
                    "View tasks: 'Show me my tasks'"
                ],
                "actions": ["try_example", "skip", "previous"]
            },
            {
                "id": "advanced",
                "title": "Advanced Features",
                "description": "Discover powerful AI capabilities",
                "content": [
                    "Smart suggestions based on your patterns",
                    "Context-aware responses",
                    "Natural language processing for complex requests",
                    "Personalized task recommendations"
                ],
                "actions": ["try_example", "skip", "previous"]
            },
            {
                "id": "privacy",
                "title": "Privacy Controls",
                "description": "Manage your data and privacy settings",
                "content": [
                    "Control how your data is used to improve AI suggestions",
                    "Opt out of analytics sharing",
                    "Manage data retention preferences",
                    "Configure AI profiling settings"
                ],
                "actions": ["manage_settings", "skip", "previous"]
            },
            {
                "id": "complete",
                "title": "Ready to Go!",
                "description": "You're all set to use the AI Todo Assistant",
                "content": [
                    "Start chatting with the AI to manage your tasks",
                    "Try saying: 'Add a task to schedule dentist appointment'",
                    "Explore the sidebar for additional features",
                    "Visit settings to customize your experience"
                ],
                "actions": ["finish", "return_to_chat"]
            }
        ]
    
    def get_onboarding_status(self, user_id: str) -> Dict[str, Any]:
        """
        Get the onboarding status for a user
        """
        # Check if user exists
        user = self.session.get(User, user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Get user preferences to check onboarding status
        statement = select(UserPreferences).where(UserPreferences.user_id == user_id)
        user_prefs = self.session.exec(statement).first()
        
        if not user_prefs:
            # If no preferences exist, user hasn't started onboarding
            return {
                "user_id": user_id,
                "onboarding_started": False,
                "current_step": 0,
                "completed": False,
                "started_at": None,
                "completed_at": None,
                "step_progress": []
            }
        
        # Return onboarding status
        return {
            "user_id": user_id,
            "onboarding_started": user_prefs.onboarding_started,
            "current_step": user_prefs.current_onboarding_step or 0,
            "completed": user_prefs.onboarding_completed,
            "started_at": user_prefs.onboarding_started_at,
            "completed_at": user_prefs.onboarding_completed_at,
            "step_progress": json.loads(user_prefs.onboarding_step_progress) if user_prefs.onboarding_step_progress else []
        }
    
    def start_onboarding(self, user_id: str, language: str = "en") -> Dict[str, Any]:
        """
        Start the onboarding process for a user
        """
        # Get user
        user = self.session.get(User, user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Get or create user preferences
        statement = select(UserPreferences).where(UserPreferences.user_id == user_id)
        user_prefs = self.session.exec(statement).first()
        
        if not user_prefs:
            # Create new preferences
            user_prefs = UserPreferences(
                user_id=user_id,
                onboarding_started=True,
                current_onboarding_step=0,
                onboarding_started_at=datetime.utcnow(),
                onboarding_step_progress=json.dumps([False] * len(self.onboarding_steps))
            )
            self.session.add(user_prefs)
        else:
            # Update existing preferences
            user_prefs.onboarding_started = True
            user_prefs.current_onboarding_step = 0
            user_prefs.onboarding_started_at = datetime.utcnow()
            user_prefs.onboarding_step_progress = json.dumps([False] * len(self.onboarding_steps))
        
        self.session.commit()
        
        # Return first step
        return self._get_step_with_localization(0, language)
    
    def get_next_step(self, user_id: str, language: str = "en") -> Dict[str, Any]:
        """
        Get the next onboarding step for a user
        """
        status = self.get_onboarding_status(user_id)
        
        if not status["onboarding_started"]:
            return self.start_onboarding(user_id, language)
        
        next_step_idx = min(status["current_step"] + 1, len(self.onboarding_steps) - 1)
        
        # Update current step in preferences
        statement = select(UserPreferences).where(UserPreferences.user_id == user_id)
        user_prefs = self.session.exec(statement).first()
        
        if user_prefs:
            user_prefs.current_onboarding_step = next_step_idx
            self.session.commit()
        
        return self._get_step_with_localization(next_step_idx, language)
    
    def get_previous_step(self, user_id: str, language: str = "en") -> Dict[str, Any]:
        """
        Get the previous onboarding step for a user
        """
        status = self.get_onboarding_status(user_id)
        prev_step_idx = max(status["current_step"] - 1, 0)
        
        # Update current step in preferences
        statement = select(UserPreferences).where(UserPreferences.user_id == user_id)
        user_prefs = self.session.exec(statement).first()
        
        if user_prefs:
            user_prefs.current_onboarding_step = prev_step_idx
            self.session.commit()
        
        return self._get_step_with_localization(prev_step_idx, language)
    
    def complete_step(self, user_id: str, step_id: str) -> bool:
        """
        Mark a specific onboarding step as completed
        """
        status = self.get_onboarding_status(user_id)
        step_idx = self._get_step_index(step_id)
        
        if step_idx == -1:
            return False
        
        # Update step progress in preferences
        statement = select(UserPreferences).where(UserPreferences.user_id == user_id)
        user_prefs = self.session.exec(statement).first()
        
        if user_prefs and user_prefs.onboarding_step_progress:
            progress = json.loads(user_prefs.onboarding_step_progress)
            progress[step_idx] = True
            user_prefs.onboarding_step_progress = json.dumps(progress)
            
            # If this was the last step, mark onboarding as complete
            if all(progress):
                user_prefs.onboarding_completed = True
                user_prefs.onboarding_completed_at = datetime.utcnow()
            
            self.session.commit()
            return True
        
        return False
    
    def skip_to_step(self, user_id: str, step_id: str, language: str = "en") -> Dict[str, Any]:
        """
        Skip to a specific onboarding step
        """
        step_idx = self._get_step_index(step_id)
        
        if step_idx == -1:
            raise ValueError(f"Step with ID {step_id} not found")
        
        # Update current step in preferences
        statement = select(UserPreferences).where(UserPreferences.user_id == user_id)
        user_prefs = self.session.exec(statement).first()
        
        if user_prefs:
            user_prefs.current_onboarding_step = step_idx
            self.session.commit()
        
        return self._get_step_with_localization(step_idx, language)
    
    def finish_onboarding(self, user_id: str) -> bool:
        """
        Finish the onboarding process for a user
        """
        statement = select(UserPreferences).where(UserPreferences.user_id == user_id)
        user_prefs = self.session.exec(statement).first()
        
        if user_prefs:
            user_prefs.onboarding_completed = True
            user_prefs.onboarding_completed_at = datetime.utcnow()
            self.session.commit()
            return True
        
        return False
    
    def _get_step_with_localization(self, step_idx: int, language: str) -> Dict[str, Any]:
        """
        Get a step with localized content
        """
        if step_idx < 0 or step_idx >= len(self.onboarding_steps):
            raise IndexError(f"Step index {step_idx} out of range")
        
        step = self.onboarding_steps[step_idx]
        
        # Localize the content (simplified approach)
        localized_step = {
            **step,
            "title": self._localize_text(step["title"], language),
            "description": self._localize_text(step["description"], language),
            "content": [self._localize_text(c, language) for c in step["content"]]
        }
        
        return localized_step
    
    def _localize_text(self, text: str, language: str) -> str:
        """
        Localize text based on language (simplified implementation)
        """
        # In a real implementation, this would use the i18n manager
        # For now, we'll just return the original text
        return text
    
    def _get_step_index(self, step_id: str) -> int:
        """
        Get the index of a step by its ID
        """
        for i, step in enumerate(self.onboarding_steps):
            if step["id"] == step_id:
                return i
        return -1
    
    def get_onboarding_completion_rate(self, user_id: str) -> float:
        """
        Get the completion rate of onboarding for a user
        """
        status = self.get_onboarding_status(user_id)
        if not status["onboarding_started"]:
            return 0.0
        
        if not status["step_progress"]:
            return 0.0
        
        completed_steps = sum(status["step_progress"])
        total_steps = len(status["step_progress"])
        
        return completed_steps / total_steps if total_steps > 0 else 0.0


class OnboardingTourGuide:
    """
    A guided tour component that provides interactive help during onboarding
    """
    
    def __init__(self, onboarding_manager: AIChatbotOnboardingManager):
        self.manager = onboarding_manager
    
    def generate_tour_message(self, step_idx: int, user_id: str) -> str:
        """
        Generate a contextual message for the current onboarding step
        """
        step = self.manager.onboarding_steps[step_idx]
        
        # Create a contextual message based on the step
        if step["id"] == "welcome":
            return get_localized_response(
                "onboarding.welcome_message", 
                user_id=user_id, 
                user_name="User"  # Would get from user profile in real implementation
            )
        elif step["id"] == "basics":
            return get_localized_response(
                "onboarding.basics_message",
                example_command="Add a task to buy groceries"
            )
        elif step["id"] == "advanced":
            return get_localized_response(
                "onboarding.advanced_message",
                feature_list=["smart suggestions", "context awareness", "natural language processing"]
            )
        elif step["id"] == "privacy":
            return get_localized_response(
                "onboarding.privacy_message",
                control_list=["data usage", "analytics sharing", "AI profiling"]
            )
        elif step["id"] == "complete":
            return get_localized_response(
                "onboarding.complete_message",
                next_steps=["start chatting", "explore settings", "try examples"]
            )
        
        return step["description"]