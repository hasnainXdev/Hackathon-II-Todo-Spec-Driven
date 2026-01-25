from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import openai
from sqlmodel import Session, select
from src.models.conversation import Message, Conversation
from models.task import Task, TaskCreate, TaskUpdate
from database.session import get_session
from core.config import settings
from datetime import datetime
import uuid
from core.logging_config import logger
import sys
from pathlib import Path

# Add the project root to the path to import the TodoAgent
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.todo_agent import TodoAgent


class AIResponse(BaseModel):
    content: str
    intent: str
    entities: Dict[str, Any]


class AIService(ABC):
    @abstractmethod
    async def process_message(self, user_input: str, user_id: str) -> AIResponse:
        pass

    @abstractmethod
    async def process_user_message(
        self, message: str, user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        pass


class OpenAIService(AIService):
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Initialize the TodoAgent for handling todo operations
        self.todo_agent = TodoAgent()

    async def process_message(self, user_input: str, user_id: str) -> AIResponse:
        """
        Process user input using OpenAI and return structured response
        """
        try:
            logger.info(
                f"Processing AI request for user {user_id}: {user_input[:50]}..."
            )

            # Use the TodoAgent to process the request with user context
            content = await self.todo_agent.process_request(user_input, user_id)

            # Extract intent and entities (simplified for now)
            intent = self._extract_intent(user_input)
            entities = self._extract_entities(user_input)

            logger.info(f"AI processed request for user {user_id}, intent: {intent}")

            return AIResponse(content=content, intent=intent, entities=entities)
        except Exception as e:
            logger.error(
                f"Error processing message with AI for user {user_id}: {str(e)}",
                exc_info=True,
            )
            raise Exception(f"Error processing message with AI: {str(e)}")

    def _extract_intent(self, user_input: str) -> str:
        """
        Simple intent extraction - in a real implementation, this would be more sophisticated
        """
        logger.debug(f"Extracting intent from: {user_input}")

        user_input_lower = user_input.lower()

        if any(word in user_input_lower for word in ["create", "add", "new", "make"]):
            return "create_task"
        elif any(
            word in user_input_lower for word in ["update", "change", "modify", "edit"]
        ):
            return "update_task"
        elif any(word in user_input_lower for word in ["delete", "remove", "cancel"]):
            return "delete_task"
        elif any(
            word in user_input_lower for word in ["complete", "done", "finish", "mark"]
        ):
            return "complete_task"
        elif any(
            word in user_input_lower
            for word in ["show", "view", "list", "see", "get", "display"]
        ):
            return "view_tasks"
        else:
            return "unknown"

    def _extract_entities(self, user_input: str) -> Dict[str, Any]:
        """
        Simple entity extraction - in a real implementation, this would be more sophisticated
        """
        logger.debug(f"Extracting entities from: {user_input}")

        # This is a simplified version - in reality, you'd use NLP techniques
        return {
            "task_title": self._extract_task_title(user_input),
            "due_date": self._extract_due_date(user_input),
            "priority": self._extract_priority(user_input),
        }

    def _extract_task_title(self, user_input: str) -> Optional[str]:
        # Look for common patterns to extract task title
        # This is a simplified version
        if "add" in user_input.lower():
            parts = user_input.split("add", 1)
            if len(parts) > 1:
                return parts[1].strip().split("to")[0].strip()
        return None

    def _extract_due_date(self, user_input: str) -> Optional[str]:
        # Simplified date extraction
        # In a real implementation, use dateutil or similar
        return None

    def _extract_priority(self, user_input: str) -> Optional[str]:
        # Simplified priority extraction
        if "urgent" in user_input.lower() or "high" in user_input.lower():
            return "high"
        elif "low" in user_input.lower():
            return "low"
        return "medium"

    async def process_user_message(
        self, message: str, user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and return an AI-generated response
        """
        try:
            logger.info(f"Processing user message for AI: {message[:50]}...")

            # Extract user_id from user_context if available
            user_id = user_context.get("user_id") if user_context else None

            # Use the TodoAgent to process the request with user context
            content = await self.todo_agent.process_request(message, user_id)

            logger.info(f"AI processed user message successfully")

            return {"response": content, "success": True}

        except Exception as e:
            logger.error(
                f"Error processing user message with AI: {str(e)}", exc_info=True
            )
            return {
                "response": f"Sorry, I encountered an error processing your request: {str(e)}",
                "success": False,
                "error": str(e),
            }

    async def process_task_operation(
        self, message: str, user_id: str, session: Session
    ) -> Dict[str, Any]:
        """
        Process a user message and execute the corresponding task operation
        """
        try:
            logger.info(
                f"Processing task operation for user {user_id}: {message[:50]}..."
            )

            # Set the authenticated user ID in the environment for the MCP tools
            import os
            os.environ["AUTHENTICATED_USER_ID"] = user_id

            # Use the TodoAgent to process the request which will utilize MCP tools
            content = await self.todo_agent.process_request(message, user_id)

            logger.info(
                f"Task operation completed for user {user_id}"
            )

            return {
                "success": True,
                "response": content,
                "action_performed": "processed_by_agent"
            }
        except Exception as e:
            logger.error(
                f"Error processing task operation for user {user_id}: {str(e)}",
                exc_info=True,
            )
            return {
                "success": False,
                "response": f"Sorry, I encountered an error processing your request: {str(e)}",
                "action_performed": "error",
            }


# Singleton instance
ai_service: Optional[AIService] = None


def get_ai_service(api_key: str) -> AIService:
    global ai_service
    if ai_service is None:
        ai_service = OpenAIService(api_key)
    return ai_service
