import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlmodel import Session, select
from uuid import uuid4

from src.models.conversation import Conversation, Message
from models.task import Task  # Assuming task model exists from phase-2
from .ai_service import AIService
from database.session import get_db


class AIChatService:
    """
    Service class for handling AI chat functionality
    """
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
    
    async def process_chat_message(
        self, 
        user_id: str, 
        message_content: str, 
        conversation_id: Optional[str] = None,
        session: Session = None
    ) -> Dict[str, Any]:
        """
        Process a chat message from a user and return AI response
        """
        # Get or create conversation
        if conversation_id:
            conversation = await self._get_conversation(conversation_id, user_id, session)
        else:
            conversation = await self._create_new_conversation(user_id, session)
        
        # Save user message
        user_message = await self._save_message(
            user_id=user_id,
            conversation_id=conversation.id,
            role="user",
            content=message_content,
            session=session
        )
        
        # Get user's tasks for context
        user_tasks = await self._get_user_tasks(user_id, session)
        context = {
            "tasks": [task.dict() for task in user_tasks],
            "conversation_history": await self._get_recent_messages(conversation.id, session)
        }
        
        # Process with AI service - use task operation method which executes actual task operations
        ai_response = await self.ai_service.process_task_operation(
            message=message_content,
            user_id=user_id,
            session=session
        )
        
        # Save AI response
        ai_message = await self._save_message(
            user_id=user_id,  # System message attributed to user for consistency
            conversation_id=conversation.id,
            role="assistant",
            content=ai_response.get("response", ""),
            session=session
        )
        
        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)
        session.commit()
        
        return {
            "conversation_id": conversation.id,
            "user_message": user_message,
            "ai_response": ai_response,
            "success": True
        }
    
    async def _get_conversation(self, conversation_id: str, user_id: str, session: Session) -> Conversation:
        """
        Get an existing conversation for the user
        """
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        conversation = session.exec(statement).first()
        
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found for user {user_id}")
        
        return conversation
    
    async def _create_new_conversation(self, user_id: str, session: Session) -> Conversation:
        """
        Create a new conversation for the user
        """
        conversation = Conversation(
            user_id=user_id,
            title=f"Conversation {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        return conversation
    
    async def _save_message(
        self, 
        user_id: str, 
        conversation_id: str, 
        role: str, 
        content: str, 
        session: Session
    ) -> Message:
        """
        Save a message to the database
        """
        message = Message(
            user_id=user_id,
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        session.add(message)
        session.commit()
        session.refresh(message)
        return message
    
    async def _get_user_tasks(self, user_id: str, session: Session) -> List[Task]:
        """
        Get all tasks for the user
        """
        statement = select(Task).where(Task.user_id == user_id)
        tasks = session.exec(statement).all()
        return tasks
    
    async def _get_recent_messages(self, conversation_id: str, session: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent messages from a conversation
        """
        from sqlalchemy import desc
        statement = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(desc(Message.timestamp)).limit(limit)
        
        messages = session.exec(statement).all()
        return [{"role": msg.role, "content": msg.content} for msg in reversed(messages)]