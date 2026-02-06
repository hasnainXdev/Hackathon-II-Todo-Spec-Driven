import os
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv
from sqlmodel import Session

load_dotenv()

class AIService:
    """
    AI Service abstraction layer for handling interactions with OpenAI API
    """

    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

    async def process_user_message(self, message: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process a user message and return an AI-generated response
        """
        try:
            # Prepare the conversation history for context
            system_prompt = self._get_system_prompt()

            messages = [
                {"role": "system", "content": system_prompt},
            ]

            # Add user context if provided
            if user_context:
                messages.append({
                    "role": "system",
                    "content": f"User context: {str(user_context)}"
                })

            messages.append({"role": "user", "content": message})

            # Call the OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )

            return {
                "response": response.choices[0].message.content,
                "success": True,
                "model_used": self.model
            }

        except Exception as e:
            return {
                "response": f"Sorry, I encountered an error processing your request: {str(e)}",
                "success": False,
                "error": str(e)
            }

    def _get_system_prompt(self) -> str:
        """
        Get the system prompt that guides the AI's behavior
        """
        return """
        You are an AI assistant integrated with a todo management system.
        Your role is to help users manage their tasks through natural language.
        You can create, read, update, delete, and mark tasks as complete.
        Always respond in a helpful and friendly manner.
        If you're unsure about a request, ask for clarification.
        """

    async def process_task_operation(self, message: str, user_id: str, session: Session) -> Dict[str, Any]:
        """
        Process a user message and execute the corresponding task operation
        """
        try:
            # Create the task operation service
            from .task_operation_service import TaskOperationService
            task_op_service = TaskOperationService(session)

            # Execute the task operation
            result = await task_op_service.execute_task_operation(user_id, message)

            return result
        except Exception as e:
            return {
                "success": False,
                "response": f"Sorry, I encountered an error processing your request: {str(e)}",
                "action_performed": "error"
            }