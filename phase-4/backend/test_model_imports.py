#!/usr/bin/env python3
"""
Test script to verify that models can be imported without table definition conflicts
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_model_imports():
    """Test that models can be imported without conflicts"""
    try:
        print("Testing model imports...")
        
        # Import the main models package
        from models import Task, User, Conversation, Message
        print("✓ Successfully imported Task, User, Conversation, Message from models")
        
        # Import specific models
        from models.task import TaskCreate, TaskRead
        print("✓ Successfully imported TaskCreate, TaskRead")
        
        from src.models.conversation import ConversationCreate, MessageCreate
        print("✓ Successfully imported ConversationCreate, MessageCreate")
        
        # Test creating a TaskCreate instance (should not require user_id)
        task_data = TaskCreate(
            title="Test Task",
            description="Test Description",
            completion_status=False
        )
        print("✓ Successfully created TaskCreate instance without user_id")
        
        return True
    except Exception as e:
        print(f"✗ Failed to import models: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing model imports to ensure no table definition conflicts...")
    success = test_model_imports()
    
    if success:
        print("\n✓ All tests passed! Models can be imported without conflicts.")
    else:
        print("\n✗ Tests failed! There are still model import issues to resolve.")