import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from main import app
from database.session import engine
from models.task import Task
from models.user_preference import UserPreference


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def setup_database():
    # Create tables
    from main import create_tables
    create_tables()
    
    yield
    
    # Cleanup if needed
    from sqlmodel import SQLModel
    SQLModel.metadata.drop_all(engine)


def test_get_tasks_empty(client, setup_database):
    """Test getting tasks when none exist"""
    response = client.get("/api/v1/tasks")
    assert response.status_code == 401  # Unauthenticated request should fail


def test_create_task_validation(client, setup_database):
    """Test task creation with validation"""
    # This test would require authentication
    pass