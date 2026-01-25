#!/usr/bin/env python3
"""
Test script to verify the UUID to string conversion fix
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_fix_verification():
    """Test that the Task model properly handles ID as string"""
    try:
        print("Testing the UUID to string conversion fix...")
        
        from models.task import Task, TaskRead
        import uuid
        
        # Test the GUID type decorator functionality
        from models.task import GUID
        import sqlalchemy as sa
        
        # Create a GUID instance
        guid_col = GUID()
        
        # Test the process_result_value method (this simulates what happens when DB returns a UUID)
        uuid_obj = uuid.uuid4()
        print(f"Original UUID object: {uuid_obj}, type: {type(uuid_obj)}")
        
        # Simulate what happens when DB returns a UUID object
        processed_result = guid_col.process_result_value(uuid_obj, None)
        print(f"After process_result_value: {processed_result}, type: {type(processed_result)}")
        
        # Verify it's now a string
        assert isinstance(processed_result, str), f"Expected string, got {type(processed_result)}"
        print("✓ UUID object is properly converted to string")
        
        # Test the field validator in TaskRead
        # Create a mock TaskRead with a UUID object as ID
        uuid_for_test = uuid.uuid4()
        task_read_dict = {
            'id': uuid_for_test,  # Pass UUID object
            'title': 'Test Task',
            'description': 'Test Description',
            'completion_status': False,
            'user_id': str(uuid.uuid4()),
            'created_at': None,
            'updated_at': None,
            'version': 1
        }
        
        # Test field validation
        validated_id = TaskRead.validate_id(uuid_for_test)
        print(f"Validated ID: {validated_id}, type: {type(validated_id)}")
        assert isinstance(validated_id, str), f"Expected string, got {type(validated_id)}"
        print("✓ Field validator properly converts UUID to string")
        
        print("\n✓ All tests passed! The UUID to string conversion fix is working.")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_fix_verification()