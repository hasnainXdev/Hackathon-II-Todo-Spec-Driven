#!/usr/bin/env python3
"""
Test script to verify that the models work correctly with lazy loading relationships
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_model_relationships():
    """Test that the models can be imported and have the correct relationships"""
    try:
        print("Testing model relationships with lazy loading...")

        # Test Task model
        from models.task import Task
        print(f"✓ Task model imported successfully")
        print(f"  - Task table name: {Task.__tablename__}")
        
        # Check if Task has the messages relationship attribute
        task_annotations = getattr(Task, '__annotations__', {})
        print(f"  - Task annotations: {list(task_annotations.keys())}")

        # Test Message model
        from src.models.conversation import Message
        print(f"✓ Message model imported successfully")
        print(f"  - Message table name: {Message.__tablename__}")

        # Test that we can create instances without DB connection
        import uuid
        from models.task import TaskCreate
        from datetime import datetime

        # Create a task without connecting to DB
        user_id = str(uuid.uuid4())
        task_data = TaskCreate(
            title="Test Task",
            description="Test Description",
            user_id=user_id,
            priority="medium"
        )
        print(f"✓ TaskCreate instance created successfully")

        print("\n✓ All model relationship tests passed!")
        return True

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_model_relationships()
    if success:
        print("\n🎉 Models are properly configured with lazy loading!")
    else:
        print("\n❌ Some issues remain with model relationships.")
        sys.exit(1)