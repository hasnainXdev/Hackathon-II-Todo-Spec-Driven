#!/usr/bin/env python3
"""
Test script to check the type of ID being generated
"""

import uuid
from typing import Optional
from sqlmodel import Field

def test_uuid_generation():
    """Test the UUID generation function"""
    print("Testing UUID generation...")
    
    # Test the lambda function that generates the ID
    id_func = lambda: str(uuid.uuid4())
    generated_id = id_func()
    
    print(f"Generated ID: {generated_id}")
    print(f"Type of generated ID: {type(generated_id)}")
    print(f"Is it a string? {isinstance(generated_id, str)}")
    
    # Test creating a UUID directly
    direct_uuid = uuid.uuid4()
    print(f"\nDirect UUID: {direct_uuid}")
    print(f"Type of direct UUID: {type(direct_uuid)}")
    print(f"Is it a string? {isinstance(direct_uuid, str)}")
    
    # Test converting to string
    str_uuid = str(direct_uuid)
    print(f"\nString UUID: {str_uuid}")
    print(f"Type of string UUID: {type(str_uuid)}")
    print(f"Is it a string? {isinstance(str_uuid, str)}")

if __name__ == "__main__":
    test_uuid_generation()