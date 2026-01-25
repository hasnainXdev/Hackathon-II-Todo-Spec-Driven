#!/usr/bin/env python3
"""
Test script to check the actual Task model structure and types
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_task_model_types():
    """Test the types in the Task model"""
    try:
        print("Testing Task model types...")
        
        from models.task import Task, TaskCreate, TaskRead
        import uuid
        
        # Check the annotation for the id field in Task
        task_annotations = Task.__annotations__ if hasattr(Task, '__annotations__') else {}
        print(f"Task model id field type: {task_annotations.get('id', 'Not found')}")
        
        # Check the annotation for the id field in TaskRead
        task_read_annotations = TaskRead.__annotations__ if hasattr(TaskRead, '__annotations__') else {}
        print(f"TaskRead model id field type: {task_read_annotations.get('id', 'Not found')}")
        
        # Check the field definition in Task model
        if hasattr(Task, '__fields__'):  # For older Pydantic versions
            print(f"Task __fields__ id type: {Task.__fields__.get('id', {}).type_ if 'id' in Task.__fields__ else 'Not found'}")
        
        # Create a sample TaskCreate object
        task_create = TaskCreate(
            title="Test Task",
            description="Test Description",
            completion_status=False
        )
        print(f"TaskCreate object created successfully")
        
        # Check the type of a newly generated ID
        new_id = str(uuid.uuid4())
        print(f"New ID: {new_id}, Type: {type(new_id)}, Is string: {isinstance(new_id, str)}")
        
        return True
    except Exception as e:
        print(f"✗ Failed to test Task model types: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_task_model_types()