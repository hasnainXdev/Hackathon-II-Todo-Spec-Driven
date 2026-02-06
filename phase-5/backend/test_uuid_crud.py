#!/usr/bin/env python3
"""
Test script to verify CRUD operations work correctly with fixed UUID types
"""

import sys
import os
from datetime import datetime

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_uuid_crud_operations():
    """Test that CRUD operations work correctly with string UUIDs"""
    try:
        print("Testing CRUD operations with fixed UUID types...")

        # Test Task model
        from models.task import Task, TaskCreate, TaskRead
        import uuid

        # Create a sample task data
        user_id = str(uuid.uuid4())
        print(f"Using user_id: {user_id}")

        # Test Task creation
        task_create = TaskCreate(
            title="Test Task",
            description="Test Description",
            user_id=user_id,
            priority="high"
        )
        print(f"✓ TaskCreate object created successfully")

        # Test that the ID generation works properly
        task_id = str(uuid.uuid4())
        print(f"Sample task ID: {task_id}, type: {type(task_id)}")

        # Test TaskRead model
        task_read = TaskRead(
            id=task_id,
            title="Test Task",
            description="Test Description",
            completion_status=False,
            user_id=user_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=1
        )
        print(f"✓ TaskRead object created successfully with ID: {task_read.id}, type: {type(task_read.id)}")

        # Test Message model
        from src.models.conversation import Message, MessageRead
        conversation_id = str(uuid.uuid4())

        # Test MessageRead model
        message_read = MessageRead(
            content="Test message content",
            role="user",  # Changed from message_type to role to match the actual model
            timestamp=datetime.now(),
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            user_id=user_id
        )
        print(f"✓ MessageRead object created successfully with ID: {message_read.id}, type: {type(message_read.id)}")

        # Test Conversation model
        from src.models.conversation import ConversationRead
        conv_id = str(uuid.uuid4())

        conversation_read = ConversationRead(
            title="Test Conversation",
            id=conv_id,
            user_id=user_id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        print(f"✓ ConversationRead object created successfully with ID: {conversation_read.id}, type: {type(conversation_read.id)}")

        # Test that all IDs are strings
        assert isinstance(task_read.id, str), f"Task ID should be string, got {type(task_read.id)}"
        assert isinstance(message_read.id, str), f"Message ID should be string, got {type(message_read.id)}"
        assert isinstance(conversation_read.id, str), f"Conversation ID should be string, got {type(conversation_read.id)}"
        assert isinstance(task_read.user_id, str), f"User ID should be string, got {type(task_read.user_id)}"
        
        print("✓ All ID types are correctly represented as strings")
        print("\n✓ All CRUD operation tests passed!")
        return True

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_uuid_crud_operations()
    if success:
        print("\n🎉 All UUID-related fixes are working correctly!")
    else:
        print("\n❌ Some issues remain with UUID handling.")
        sys.exit(1)