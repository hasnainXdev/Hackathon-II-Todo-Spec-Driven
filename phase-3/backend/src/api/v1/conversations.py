from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select
from typing import List
from uuid import UUID
from datetime import datetime

from ..models.conversation import Conversation, Message, ConversationBase, MessageBase
from ..database import get_session
from ..services.ai_service import AIService

router = APIRouter(prefix="/conversations", tags=["conversations"])

@router.get("/", response_model=List[Conversation])
def get_conversations(
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Get all conversations for the current user
    """
    statement = select(Conversation).where(Conversation.user_id == current_user_id)
    conversations = session.exec(statement).all()
    return conversations


@router.post("/", response_model=Conversation)
def create_conversation(
    conversation: ConversationBase,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Create a new conversation
    """
    db_conversation = Conversation(
        **conversation.dict(),
        user_id=current_user_id
    )
    session.add(db_conversation)
    session.commit()
    session.refresh(db_conversation)
    return db_conversation


@router.get("/{conversation_id}/messages", response_model=List[Message])
def get_messages(
    conversation_id: str,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Get all messages in a specific conversation
    """
    # Verify that the conversation belongs to the current user
    conversation_statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user_id
    )
    conversation = session.exec(conversation_statement).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    statement = select(Message).where(Message.conversation_id == conversation_id)
    messages = session.exec(statement).all()
    return messages


# Placeholder for the get_current_user_id dependency
# This would typically come from your auth system
def get_current_user_id():
    # This is a placeholder - implement with your actual auth system
    # For example, using better-auth or extracting from token
    pass