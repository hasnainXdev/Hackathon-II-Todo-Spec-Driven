#!/usr/bin/env python3
"""
Test script to verify that the TaskCreate model accepts requests without user_id
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.task import TaskCreate

def test_task_create_without_user_id():
    """Test that TaskCreate model can be instantiated without user_id"""
    try:
        # This should work now that user_id is optional in TaskCreate
        task_data = TaskCreate(
            title="Test Task",
            description="Test Description",
            completion_status=False
        )
        
        print("✓ TaskCreate model successfully created without user_id")
        print(f"  Title: {task_data.title}")
        print(f"  Description: {task_data.description}")
        print(f"  Completion Status: {task_data.completion_status}")
        print(f"  User ID: {task_data.user_id}")  # Should be None
        
        return True
    except Exception as e:
        print(f"✗ Failed to create TaskCreate model without user_id: {e}")
        return False

if __name__ == "__main__":
    print("Testing TaskCreate model without user_id field...")
    success = test_task_create_without_user_id()
    
    if success:
        print("\n✓ Test passed! The API should now accept requests without user_id in the body.")
    else:
        print("\n✗ Test failed! Further changes may be needed.")