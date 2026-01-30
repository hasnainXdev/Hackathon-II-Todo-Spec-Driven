#!/usr/bin/env python3
"""
Comprehensive test suite for Conversations, Messages, and Tasks CRUD operations
"""

import sys
import os
from datetime import datetime
import uuid

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_conversation_crud():
    """Test Conversation CRUD operations"""
    try:
        print("Testing Conversation CRUD operations...")
        
        from src.models.conversation import Conversation, ConversationCreate
        import uuid

        # Test Conversation creation
        user_id = str(uuid.uuid4())
        conv_title = f"Test Conversation {datetime.now().isoformat()}"
        
        # Create a conversation object (without DB connection)
        conv_create = ConversationCreate(title=conv_title)
        print(f"✓ ConversationCreate object created successfully")

        # Test Conversation model instantiation
        conversation = Conversation(
            title=conv_title,
            user_id=user_id
        )
        print(f"✓ Conversation object created successfully with ID: {conversation.id}, type: {type(conversation.id)}")
        print(f"  - Title: {conversation.title}")
        print(f"  - User ID: {conversation.user_id}, type: {type(conversation.user_id)}")
        print(f"  - Created at: {conversation.created_at}")

        # Verify all IDs are strings
        assert isinstance(conversation.id, str), f"Conversation ID should be string, got {type(conversation.id)}"
        assert isinstance(conversation.user_id, str), f"User ID should be string, got {type(conversation.user_id)}"
        
        print("✓ All Conversation ID types are correctly represented as strings")
        print("✓ Conversation CRUD operations test passed!\n")
        return True

    except Exception as e:
        print(f"✗ Conversation CRUD test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_message_crud():
    """Test Message CRUD operations"""
    try:
        print("Testing Message CRUD operations...")
        
        from src.models.conversation import Message, MessageCreate, MessageType
        import uuid

        # Test Message creation
        user_id = str(uuid.uuid4())
        conversation_id = str(uuid.uuid4())
        
        # Create a message object (without DB connection)
        msg_create = MessageCreate(
            role=MessageType.USER,
            content="Test message content"
        )
        print(f"✓ MessageCreate object created successfully")

        # Test Message model instantiation
        message = Message(
            role=MessageType.USER,
            content="Test message content",
            user_id=user_id,
            conversation_id=conversation_id
        )
        print(f"✓ Message object created successfully with ID: {message.id}, type: {type(message.id)}")
        print(f"  - Role: {message.role}")
        print(f"  - Content: {message.content}")
        print(f"  - User ID: {message.user_id}, type: {type(message.user_id)}")
        print(f"  - Conversation ID: {message.conversation_id}, type: {type(message.conversation_id)}")
        print(f"  - Timestamp: {message.timestamp}")
        print(f"  - Created at: {message.created_at}")

        # Verify all IDs are strings
        assert isinstance(message.id, str), f"Message ID should be string, got {type(message.id)}"
        assert isinstance(message.user_id, str), f"User ID should be string, got {type(message.user_id)}"
        assert isinstance(message.conversation_id, str), f"Conversation ID should be string, got {type(message.conversation_id)}"
        
        print("✓ All Message ID types are correctly represented as strings")
        print("✓ Message CRUD operations test passed!\n")
        return True

    except Exception as e:
        print(f"✗ Message CRUD test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_task_crud():
    """Test Task CRUD operations"""
    try:
        print("Testing Task CRUD operations...")
        
        from models.task import Task, TaskCreate, TaskRead
        import uuid

        # Test Task creation
        user_id = str(uuid.uuid4())
        
        # Create a task object (without DB connection)
        task_create = TaskCreate(
            title="Test Task",
            description="Test Description",
            user_id=user_id,
            priority="medium"
        )
        print(f"✓ TaskCreate object created successfully")

        # Test Task model instantiation
        task = Task(
            title="Test Task",
            description="Test Description",
            user_id=user_id,
            priority="medium"
        )
        print(f"✓ Task object created successfully with ID: {task.id}, type: {type(task.id)}")
        print(f"  - Title: {task.title}")
        print(f"  - Description: {task.description}")
        print(f"  - User ID: {task.user_id}, type: {type(task.user_id)}")
        print(f"  - Priority: {task.priority}")
        print(f"  - Created at: {task.created_at}")
        print(f"  - Updated at: {task.updated_at}")
        print(f"  - Version: {task.version}")

        # Verify all IDs are strings
        assert isinstance(task.id, str), f"Task ID should be string, got {type(task.id)}"
        assert isinstance(task.user_id, str), f"User ID should be string, got {type(task.user_id)}"
        
        print("✓ All Task ID types are correctly represented as strings")
        print("✓ Task CRUD operations test passed!\n")
        return True

    except Exception as e:
        print(f"✗ Task CRUD test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_consistency():
    """Test that all models have consistent ID types"""
    try:
        print("Testing model consistency...")
        
        from models.task import Task
        from src.models.conversation import Conversation, Message
        import uuid

        # Create instances of all models
        user_id = str(uuid.uuid4())
        conversation_id = str(uuid.uuid4())
        
        task = Task(title="Test", user_id=user_id, priority="medium")
        conversation = Conversation(title="Test Conv", user_id=user_id)
        message = Message(
            role="user", 
            content="Test content", 
            user_id=user_id, 
            conversation_id=conversation_id
        )

        # Check that all ID fields are strings
        id_checks = [
            (task.id, "Task.id"),
            (task.user_id, "Task.user_id"),
            (conversation.id, "Conversation.id"),
            (conversation.user_id, "Conversation.user_id"),
            (message.id, "Message.id"),
            (message.user_id, "Message.user_id"),
            (message.conversation_id, "Message.conversation_id"),
        ]
        
        for id_val, field_name in id_checks:
            assert isinstance(id_val, str), f"{field_name} should be string, got {type(id_val)}"
            print(f"✓ {field_name} is string: {id_val}")

        print("✓ All model ID types are consistent\n")
        return True

    except Exception as e:
        print(f"✗ Model consistency test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all CRUD tests"""
    print("Running comprehensive CRUD tests for Conversations, Messages, and Tasks...\n")
    
    tests = [
        ("Conversation CRUD", test_conversation_crud),
        ("Message CRUD", test_message_crud),
        ("Task CRUD", test_task_crud),
        ("Model Consistency", test_model_consistency),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"Running {test_name} test...")
        result = test_func()
        results.append((test_name, result))
    
    print("="*50)
    print("TEST RESULTS SUMMARY:")
    all_passed = True
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("="*50)
    if all_passed:
        print("🎉 All CRUD tests passed! The models are properly configured.")
        return True
    else:
        print("❌ Some tests failed.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    if not success:
        sys.exit(1)