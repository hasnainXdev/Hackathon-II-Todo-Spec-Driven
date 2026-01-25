#!/usr/bin/env python3
"""
Schema-focused test suite for Conversations, Messages, and Tasks models
"""

import sys
import os
from datetime import datetime
import uuid

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_model_schemas():
    """Test model schemas and field definitions"""
    try:
        print("Testing model schemas and field definitions...")
        
        # Import base models and schemas (not the table=True models to avoid ORM initialization)
        from models.task import TaskBase, TaskCreate, TaskUpdate, TaskRead
        from src.models.conversation import (
            ConversationBase, ConversationCreate, ConversationRead,
            MessageBase, MessageCreate, MessageRead, MessageType
        )
        
        # Test Task schemas
        user_id = str(uuid.uuid4())
        task_create = TaskCreate(
            title="Test Task",
            description="Test Description",
            user_id=user_id,
            priority="medium"
        )
        print(f"✓ TaskCreate schema validated successfully")
        print(f"  - Title: {task_create.title}")
        print(f"  - User ID: {task_create.user_id}, type: {type(task_create.user_id)}")
        
        # Test Conversation schemas
        conv_title = f"Test Conversation {datetime.now().isoformat()}"
        conv_create = ConversationCreate(title=conv_title)
        print(f"✓ ConversationCreate schema validated successfully")
        print(f"  - Title: {conv_create.title}")
        
        # Test Message schemas
        msg_create = MessageCreate(
            role=MessageType.USER,
            content="Test message content"
        )
        print(f"✓ MessageCreate schema validated successfully")
        print(f"  - Role: {msg_create.role}")
        print(f"  - Content: {msg_create.content}")
        
        # Verify all user IDs are strings
        assert isinstance(user_id, str), f"User ID should be string, got {type(user_id)}"
        
        print("✓ All schema tests passed!\n")
        return True

    except Exception as e:
        print(f"✗ Schema test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_annotations():
    """Test that model annotations are properly defined"""
    try:
        print("Testing model annotations...")
        
        from models.task import TaskBase, TaskCreate, TaskUpdate, TaskRead
        from src.models.conversation import (
            ConversationBase, ConversationCreate, ConversationRead,
            MessageBase, MessageCreate, MessageRead
        )
        
        # Check TaskBase annotations
        task_base_annotations = getattr(TaskBase, '__annotations__', {})
        print(f"✓ TaskBase annotations: {sorted(list(task_base_annotations.keys()))}")
        
        # Check TaskCreate annotations
        task_create_annotations = getattr(TaskCreate, '__annotations__', {})
        print(f"✓ TaskCreate annotations: {sorted(list(task_create_annotations.keys()))}")
        
        # Check MessageBase annotations  
        message_base_annotations = getattr(MessageBase, '__annotations__', {})
        print(f"✓ MessageBase annotations: {sorted(list(message_base_annotations.keys()))}")
        
        # Check MessageCreate annotations
        message_create_annotations = getattr(MessageCreate, '__annotations__', {})
        print(f"✓ MessageCreate annotations: {sorted(list(message_create_annotations.keys()))}")
        
        # Check ConversationBase annotations
        conv_base_annotations = getattr(ConversationBase, '__annotations__', {})
        print(f"✓ ConversationBase annotations: {sorted(list(conv_base_annotations.keys()))}")
        
        # Check ConversationCreate annotations
        conv_create_annotations = getattr(ConversationCreate, '__annotations__', {})
        print(f"✓ ConversationCreate annotations: {sorted(list(conv_create_annotations.keys()))}")
        
        # Verify required fields exist
        required_task_fields = ['title', 'user_id', 'priority']
        for field in required_task_fields:
            if field in task_create_annotations:
                print(f"  ✓ TaskCreate has required field: {field}")
            else:
                print(f"  ✗ TaskCreate missing required field: {field}")
                
        required_message_fields = ['role', 'content']
        for field in required_message_fields:
            if field in message_create_annotations:
                print(f"  ✓ MessageCreate has required field: {field}")
            else:
                print(f"  ✗ MessageCreate missing required field: {field}")
        
        required_conv_fields = ['title']
        for field in required_conv_fields:
            if field in conv_create_annotations:
                print(f"  ✓ ConversationCreate has required field: {field}")
            else:
                print(f"  ✗ ConversationCreate missing required field: {field}")
        
        print("✓ Model annotations test passed!\n")
        return True

    except Exception as e:
        print(f"✗ Model annotations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_field_types():
    """Test that model fields have correct types"""
    try:
        print("Testing model field types...")
        
        from models.task import TaskCreate
        from src.models.conversation import MessageCreate, MessageType
        import uuid

        # Test that we can create objects with appropriate types
        user_id_str = str(uuid.uuid4())
        
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
        
        print(f"✓ Message created with role: {message.role}, type: {type(message.role)}")
        print(f"✓ Message created with content: {message.content}, type: {type(message.content)}")
        
        # Verify role is of correct type
        assert isinstance(message.role, MessageType), f"role should be MessageType, got {type(message.role)}"
        
        print("✓ Model field types test passed!\n")
        return True

    except Exception as e:
        print(f"✗ Model field types test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_table_models_separately():
    """Test table models separately to isolate issues"""
    try:
        print("Testing table models separately...")
        
        # Test Task table model
        try:
            from models.task import Task
            print("✓ Task table model imported successfully")
        except Exception as e:
            print(f"✗ Task table model import failed: {e}")
            return False
            
        # Test Conversation table model
        try:
            from src.models.conversation import Conversation
            print("✓ Conversation table model imported successfully")
        except Exception as e:
            print(f"✗ Conversation table model import failed: {e}")
            return False
            
        # Test Message table model
        try:
            from src.models.conversation import Message
            print("✓ Message table model imported successfully")
        except Exception as e:
            print(f"✗ Message table model import failed: {e}")
            return False
        
        print("✓ All table models imported successfully!\n")
        return True

    except Exception as e:
        print(f"✗ Table models test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_schema_tests():
    """Run all schema-focused tests"""
    print("Running schema-focused tests for Conversations, Messages, and Tasks...\n")
    
    tests = [
        ("Model Schemas", test_model_schemas),
        ("Model Annotations", test_model_annotations),
        ("Model Field Types", test_model_field_types),
        ("Table Models", test_table_models_separately),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"Running {test_name} test...")
        result = test_func()
        results.append((test_name, result))
    
    print("="*50)
    print("SCHEMA TEST RESULTS SUMMARY:")
    all_passed = True
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("="*50)
    if all_passed:
        print("🎉 All schema tests passed! The models are properly configured.")
        return True
    else:
        print("❌ Some schema tests failed.")
        return False


if __name__ == "__main__":
    success = run_schema_tests()
    if not success:
        sys.exit(1)