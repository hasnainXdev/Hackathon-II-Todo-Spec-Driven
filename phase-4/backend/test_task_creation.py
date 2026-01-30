#!/usr/bin/env python3
"""
Test script to verify task creation endpoint works with local JWT token
"""

import asyncio
from datetime import timedelta
from core.security import create_access_token
from core.config import settings
from fastapi.testclient import TestClient
from main import app
from database.session import engine
from sqlmodel import SQLModel


def test_task_creation():
    # Create all tables
    SQLModel.metadata.create_all(engine)

    # Create a test client
    client = TestClient(app)

    # Create a local JWT token for testing
    user_data = {
        "sub": "test-user-id",
        "email": "test@example.com",
        "name": "Test User"
    }
    token = create_access_token(user_data, expires_delta=timedelta(hours=1))

    # Test the root endpoint first
    response = client.get("/")
    print(f"Root endpoint response: {response.status_code} - {response.json()}")

    # Test the task creation endpoint
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    task_data = {
        "title": "Test Task",
        "description": "This is a test task",
        "completion_status": False
    }

    # Try both possible endpoints
    print("\nTesting POST /api/v1/tasks/ (with trailing slash)")
    response = client.post("/api/v1/tasks/", json=task_data, headers=headers)
    print(f"Response: {response.status_code}")
    print(f"Response body: {response.json() if response.content else 'No content'}")

    print("\nTesting POST /api/v1/tasks (without trailing slash)")
    response = client.post("/api/v1/tasks", json=task_data, headers=headers)
    print(f"Response: {response.status_code}")
    print(f"Response body: {response.json() if response.content else 'No content'}")

    # Also test getting tasks
    print("\nTesting GET /api/v1/tasks/")
    response = client.get("/api/v1/tasks/", headers=headers)
    print(f"Response: {response.status_code}")
    print(f"Response body: {response.json() if response.content else 'No content'}")


if __name__ == "__main__":
    test_task_creation()