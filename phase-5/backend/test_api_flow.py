#!/usr/bin/env python3
"""
Test script to simulate the API flow and check the ID type issue
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_api_flow():
    """Test the API flow to see where the ID type issue occurs"""
    try:
        print("Testing API flow for ID type issue...")
        
        from models.task import Task, TaskCreate, TaskRead
        from sqlmodel import create_engine, Session
        from core.config import settings
        import uuid
        
        # Create an in-memory SQLite database for testing
        engine = create_engine("sqlite:///:memory:")
        
        # Create tables
        from sqlmodel import SQLModel
        SQLModel.metadata.create_all(engine)
        
        # Create a test task data
        task_data = TaskCreate(
            title="Test Task",
            description="Test Description",
            completion_status=False
        )
        
        print(f"TaskCreate data: title='{task_data.title}', id type for new task will be determined at creation")
        
        # Simulate what happens in the service layer
        with Session(engine) as session:
            # Create a new task instance
            task = Task(
                title=task_data.title,
                description=task_data.description,
                completion_status=task_data.completion_status,
                user_id="test-user-id",  # Need to provide user_id since it's required in TaskBase
                due_date=task_data.due_date,
                priority=task_data.priority
            )
            
            print(f"Before adding to session - Task ID: {task.id}, Type: {type(task.id)}")
            
            session.add(task)
            session.commit()
            session.refresh(task)  # This is where the ID gets assigned from the database
            
            print(f"After refresh - Task ID: {task.id}, Type: {type(task.id)}")
            
            # Convert to TaskRead model (this is what gets returned by the API)
            task_read = TaskRead.from_orm(task) if hasattr(TaskRead, 'from_orm') else TaskRead.model_validate(task)
            
            print(f"TaskRead ID: {task_read.id}, Type: {type(task_read.id)}")
            print(f"Is TaskRead ID a string? {isinstance(task_read.id, str)}")
            
        return True
    except Exception as e:
        print(f"✗ Failed to test API flow: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_api_flow()