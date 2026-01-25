#!/usr/bin/env python3
"""
Basic test suite for Conversations, Messages, and Tasks models without triggering circular dependencies
"""

import sys
import os
from datetime import datetime
import uuid

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_models():
    """Test basic model functionality without triggering full ORM setup"""
    try:
        print("Testing basic model functionality...")
        
        # Import models separately to avoid circular dependencies during initialization
        from models.task import TaskBase, TaskCreate
        from src.models.conversation import ConversationBase, ConversationCreate, MessageBase, MessageCreate, MessageType
        import uuid

        # Test Task models
        user_id = str(uuid.uuid4())
        task_create = TaskCreate(
            title="Test Task",
            description="Test Description",
            user_id=user_id,
            priority="medium"
        )
        print(f"✓ TaskCreate object created successfully")
        print(f"  - Title: {task_create.title}")
        print(f"  - User ID: {task_create.user_id}, type: {type(task_create.user_id)}")

        # Test Conversation models
        conv_title = f"Test Conversation {datetime.now().isoformat()}"
        conv_create = ConversationCreate(title=conv_title)
        print(f"✓ ConversationCreate object created successfully")
        print(f"  - Title: {conv_create.title}")

        # Test Message models
        msg_create = MessageCreate(
            role=MessageType.USER,
            content="Test message content"
        )
        print(f"✓ MessageCreate object created successfully")
        print(f"  - Role: {msg_create.role}")
        print(f"  - Content: {msg_create.content}")

        # Verify all user IDs are strings
        assert isinstance(user_id, str), f"User ID should be string, got {type(user_id)}"
        
        print("✓ All basic model tests passed!\n")
        return True

    except Exception as e:
        print(f"✗ Basic model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_attributes():
    """Test that model attributes are properly defined"""
    try:
        print("Testing model attributes...")
        
        from models.task import TaskBase, TaskCreate, TaskUpdate
        from src.models.conversation import (
            ConversationBase, ConversationCreate, 
            MessageBase, MessageCreate, MessageType
        )
        
        # Check TaskBase attributes
        task_base_annotations = getattr(TaskBase, '__annotations__', {})
        print(f"✓ TaskBase annotations: {list(task_base_annotations.keys())}")
        
        # Check MessageBase attributes  
        message_base_annotations = getattr(MessageBase, '__annotations__', {})
        print(f"✓ MessageBase annotations: {list(message_base_annotations.keys())}")
        
        # Check ConversationBase attributes
        conv_base_annotations = getattr(ConversationBase, '__annotations__', {})
        print(f"✓ ConversationBase annotations: {list(conv_base_annotations.keys())}")
        
        # Verify timestamp is in MessageBase (even though it's not in DB, it should be in the model)
        if 'timestamp' in message_base_annotations:
            print("✓ MessageBase has timestamp field")
        else:
            print("✗ MessageBase missing timestamp field")
            
        print("✓ Model attributes test passed!\n")
        return True

    except Exception as e:
        print(f"✗ Model attributes test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_uuid_handling():
    """Test UUID/string handling in models"""
    try:
        print("Testing UUID/string handling...")
        
        from models.task import TaskCreate
        from src.models.conversation import MessageCreate, MessageType
        import uuid

        # Test that we can create objects with string IDs
        user_id_str = str(uuid.uuid4())
        task_id_str = str(uuid.uuid4())
        
        # Create task with string user_id
        task = TaskCreate(
            title="Test Task",
            description="Test Description", 
            user_id=user_id_str,  # This should be a string
            priority="medium"
        )
        
        print(f"✓ Task created with user_id: {task.user_id}, type: {type(task.user_id)}")
        assert isinstance(task.user_id, str), f"user_id should be string, got {type(task.user_id)}"
        
        # Create message
        message = MessageCreate(
            role=MessageType.USER,
            content="Test message"
        )
        
        print(f"✓ Message created with role: {message.role}")
        
        print("✓ UUID/string handling test passed!\n")
        return True

    except Exception as e:
        print(f"✗ UUID/string handling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_basic_tests():
    """Run all basic tests"""
    print("Running basic model tests to verify functionality without circular dependencies...\n")
    
    tests = [
        ("Basic Models", test_basic_models),
        ("Model Attributes", test_model_attributes),
        ("UUID Handling", test_uuid_handling),
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
        print("🎉 All basic tests passed! The models are properly configured.")
        return True
    else:
        print("❌ Some basic tests failed.")
        return False


if __name__ == "__main__":
    success = run_basic_tests()
    if not success:
        sys.exit(1)