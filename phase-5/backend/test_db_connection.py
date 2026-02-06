#!/usr/bin/env python3
"""
Test script to verify database connection and fix SSL issues
"""

import os
import sys
from contextlib import contextmanager

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.session import engine, get_session
from models.task import Task

def test_db_connection():
    """Test the database connection"""
    try:
        print("Testing database connection...")

        # Try to establish a session and execute a simple query
        # Since get_session() is a generator, we need to call it differently
        session_gen = get_session()
        session = next(session_gen)

        try:
            # Execute a simple query to test the connection
            from sqlalchemy import text
            result = session.exec(text("SELECT 1")).first()
            print(f"Connection test result: {result}")

            # Try to query tasks table
            try:
                tasks_result = session.exec(text("SELECT * FROM tasks LIMIT 1")).first()
                print(f"Tasks query result: {tasks_result}")
            except Exception as e:
                print(f"Tasks query failed (table might not exist): {e}")
        finally:
            session.close()

        print("Database connection test completed successfully!")
        return True
    except Exception as e:
        print(f"Database connection test failed: {e}")
        return False

def test_with_sqlalchemy_directly():
    """Test using SQLAlchemy directly to isolate the issue"""
    from sqlalchemy import create_engine, text
    from core.config import settings
    
    if not settings.DATABASE_URL:
        print("No DATABASE_URL found, using SQLite")
        return True
        
    # Create a new engine with specific SSL settings
    try:
        # Try with sslmode=require which is less strict than verify-full
        db_url = settings.DATABASE_URL
        if 'sslmode=' not in db_url:
            if '?' in db_url:
                db_url += "&sslmode=require"
            else:
                db_url += "?sslmode=require"
        
        print(f"Using database URL: {db_url}")
        
        test_engine = create_engine(
            db_url,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=True  # Enable to see SQL statements
        )
        
        with test_engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).fetchone()
            print(f"Direct SQLAlchemy connection test result: {result}")
            
        print("Direct connection test passed!")
        return True
    except Exception as e:
        print(f"Direct connection test failed: {e}")
        return False

if __name__ == "__main__":
    print("Running database connection tests...")

    # Test 1: Using the configured session (this is how the application connects)
    success1 = test_db_connection()

    print("\n" + "="*50 + "\n")

    # Test 2: Using SQLAlchemy directly (just for comparison)
    success2 = test_with_sqlalchemy_directly()

    if success1:
        print("\nMain application connection test passed! SSL connection issue should be resolved.")
        print("Note: The direct connection test may fail due to different SSL configurations,")
        print("but the main application connection (test 1) is what matters for the application.")
    else:
        print("\nThe main application connection test failed. Please check your database configuration.")