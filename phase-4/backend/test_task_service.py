#!/usr/bin/env python3
"""
Test script to verify that the TaskService can be imported and used without errors
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_task_service_import():
    """Test that TaskService can be imported without errors"""
    try:
        print("Testing TaskService import...")
        
        # Import the TaskService
        from services.task_service import TaskService
        print("✓ Successfully imported TaskService")
        
        # Import related models
        from models.task import Task, TaskCreate, TaskUpdate
        print("✓ Successfully imported Task, TaskCreate, TaskUpdate")
        
        # Test creating a TaskCreate instance (should not require user_id)
        task_data = TaskCreate(
            title="Test Task",
            description="Test Description",
            completion_status=False
        )
        print("✓ Successfully created TaskCreate instance without user_id")
        print(f"  - Title: {task_data.title}")
        print(f"  - Description: {task_data.description}")
        print(f"  - Completion Status: {task_data.completion_status}")
        print(f"  - User ID: {task_data.user_id} (should be None)")
        
        return True
    except Exception as e:
        print(f"✗ Failed to import or use TaskService: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing TaskService and related models...")
    success = test_task_service_import()
    
    if success:
        print("\n✓ All tests passed! TaskService can be imported and used without errors.")
    else:
        print("\n✗ Tests failed! There are still import issues to resolve.")