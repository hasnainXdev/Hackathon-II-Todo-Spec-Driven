from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from src.models.conversation import Message, Conversation, MessageCreate, ConversationCreate
from src.models.user import User


class ChatHistoryService:
    """
    Service class to handle chat history operations
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_conversation(self, user_id: str, title: Optional[str] = None) -> Conversation:
        """
        Create a new conversation
        """
        if not title:
            title = f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        conversation = Conversation(
            title=title,
            user_id=user_id
        )
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        return conversation
    
    def get_user_conversations(self, user_id: str) -> List[Conversation]:
        """
        Get all conversations for a user
        """
        conversations = self.session.exec(
            select(Conversation).where(Conversation.user_id == user_id)
        ).all()
        return conversations
    
    def get_conversation_by_id(self, conversation_id: str, user_id: str) -> Optional[Conversation]:
        """
        Get a specific conversation by ID for a user
        """
        conversation = self.session.get(Conversation, conversation_id)
        if conversation and conversation.user_id == user_id:
            return conversation
        return None
    
    def add_message_to_conversation(
        self, 
        conversation_id: str, 
        user_id: str, 
        role: str, 
        content: str
    ) -> Message:
        """
        Add a message to a conversation
        """
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content
        )
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)
        return message
    
    def get_conversation_messages(self, conversation_id: str, user_id: str) -> List[Message]:
        """
        Get all messages in a conversation
        """
        # First verify the conversation belongs to the user
        conversation = self.session.get(Conversation, conversation_id)
        if not conversation or conversation.user_id != user_id:
            return []
        
        messages = self.session.exec(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.timestamp)
        ).all()
        return messages
    
    def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """
        Delete a conversation and all its messages
        """
        conversation = self.session.get(Conversation, conversation_id)
        if not conversation or conversation.user_id != user_id:
            return False
        
        # Delete all messages in the conversation first
        messages = self.session.exec(
            select(Message).where(Message.conversation_id == conversation_id)
        ).all()
        for message in messages:
            self.session.delete(message)
        
        # Then delete the conversation
        self.session.delete(conversation)
        self.session.commit()
        return True


def get_chat_history_service(session: Session) -> ChatHistoryService:
    """
    Dependency to get chat history service
    """
    return ChatHistoryService(session)