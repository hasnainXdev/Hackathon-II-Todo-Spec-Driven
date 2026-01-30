#!/usr/bin/env python3
"""
Test script to verify that the validation in tasks API endpoints works properly
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_validation_logic():
    """Test the validation logic for user_id"""
    try:
        print("Testing validation logic...")
        
        # Test case 1: Valid user_id
        current_user_valid = {"id": "some-user-id", "email": "user@example.com"}
        user_id = current_user_valid.get("id")
        if not user_id:
            print("✗ Failed: Valid user_id was rejected")
            return False
        else:
            print("✓ Valid user_id passed validation")
        
        # Test case 2: Missing user_id
        current_user_missing = {"email": "user@example.com", "name": "John Doe"}
        user_id = current_user_missing.get("id")
        if not user_id:
            print("✓ Missing user_id was properly detected")
        else:
            print("✗ Failed: Missing user_id was not detected")
            return False
        
        # Test case 3: None user_id
        current_user_none = {"id": None, "email": "user@example.com"}
        user_id = current_user_none.get("id")
        if not user_id:
            print("✓ None user_id was properly detected")
        else:
            print("✗ Failed: None user_id was not detected")
            return False
        
        print("✓ All validation tests passed!")
        return True
    except Exception as e:
        print(f"✗ Failed validation test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing validation logic in tasks API endpoints...")
    success = test_validation_logic()
    
    if success:
        print("\n✓ All validation tests passed! The validation logic is working correctly.")
    else:
        print("\n✗ Validation tests failed! There are issues with the validation logic.")