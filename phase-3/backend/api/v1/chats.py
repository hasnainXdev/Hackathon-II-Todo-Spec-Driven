from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlmodel import Session, select
from typing import List
from datetime import datetime

from core.security import get_current_user
from database.session import get_session
from src.models.conversation import (
    Message,
    Conversation,
    MessageCreate,
    ConversationCreate,
    MessageRead,
    ConversationRead,
)
from services.ai_service import get_ai_service
from services.chat_history_service import ChatHistoryService
from core.config import settings
from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()


@router.post("/chats/conversations", response_model=ConversationRead)
def create_conversation(
    conversation_data: ConversationCreate,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Create a new conversation
    """
    # Temporarily create the service inside the function
    from services.chat_history_service import ChatHistoryService

    chat_service = ChatHistoryService(session)
    conversation = chat_service.create_conversation(
        user_id=current_user["id"], title=conversation_data.title
    )
    return conversation


@router.get("/chats/conversations", response_model=List[ConversationRead])
def get_user_conversations(
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get all conversations for the current user
    """
    chat_service = ChatHistoryService(session)
    conversations = chat_service.get_user_conversations(user_id=current_user["id"])
    return conversations


@router.get("/chats/conversations/{conversation_id}", response_model=ConversationRead)
def get_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get a specific conversation by ID
    """
    chat_service = ChatHistoryService(session)
    conversation = chat_service.get_conversation_by_id(
        conversation_id=conversation_id, user_id=current_user["id"]
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.post(
    "/chats/conversations/{conversation_id}/messages", response_model=MessageRead
)
async def send_message(
    conversation_id: str,
    message_data: MessageCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Send a message in a conversation and get AI response
    """
    # Create the chat service
    chat_service = ChatHistoryService(session)

    # Verify conversation exists and belongs to user
    conversation = chat_service.get_conversation_by_id(
        conversation_id=conversation_id, user_id=current_user["id"]
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Add user message to conversation
    user_message = chat_service.add_message_to_conversation(
        conversation_id=conversation_id,
        user_id=current_user["id"],
        role=message_data.role,
        content=message_data.content,
    )

    # Process with AI service in background
    if settings.OPEN_ROUTER_KEY:
        ai_service = get_ai_service(settings.OPEN_ROUTER_KEY)

        # Process the message with AI
        async def process_with_ai():
            # Process the task operation which will execute actual task operations
            ai_response = await ai_service.process_task_operation(
                message=message_data.content,
                user_id=current_user["id"],
                session=session,
            )

            # Add AI response message to conversation
            chat_service.add_message_to_conversation(
                conversation_id=conversation_id,
                user_id=current_user["id"],
                role="assistant",
                content=ai_response.get("response"),
            )

        # Run the async function in the background
        import asyncio

        background_tasks.add_task(process_with_ai)

    return user_message


@router.get(
    "/chats/conversations/{conversation_id}/messages", response_model=List[MessageRead]
)
def get_conversation_messages(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get all messages in a conversation
    """
    chat_service = ChatHistoryService(session)
    messages = chat_service.get_conversation_messages(
        conversation_id=conversation_id, user_id=current_user["id"]
    )
    if not messages:
        # Check if conversation exists and belongs to user
        conversation = chat_service.get_conversation_by_id(
            conversation_id=conversation_id, user_id=current_user["id"]
        )
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

    return messages
