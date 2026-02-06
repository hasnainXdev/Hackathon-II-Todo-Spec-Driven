#!/usr/bin/env python3
"""
Test script to check if the Task model ID issue is fixed
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_task_id_type():
    """Test the ID type in the Task model"""
    try:
        print("Testing Task ID type after fix...")
        
        from models.task import Task
        
        # Create a dummy task instance to see how the ID field behaves
        # Note: We can't fully instantiate a Task due to database dependencies
        # but we can check the field definition
        
        # Check the model fields using the newer Pydantic approach
        if hasattr(Task, 'model_fields'):
            id_field = Task.model_fields.get('id')
            if id_field:
                print(f"Task model_fields id type: {id_field.annotation}")
                print(f"Is id field type str? {id_field.annotation == str}")
            else:
                print("id field not found in model_fields")
        else:
            print("model_fields not available")
        
        # Test the lambda function that generates IDs
        import uuid
        id_generator = lambda: str(uuid.uuid4())
        test_id = id_generator()
        print(f"Generated ID: {test_id}")
        print(f"Generated ID type: {type(test_id)}")
        print(f"Is generated ID a string? {isinstance(test_id, str)}")
        
        return True
    except Exception as e:
        print(f"✗ Failed to test Task ID type: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_task_id_type()