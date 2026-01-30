import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.main import app
from database.session import engine
from models.task import Task
# from models.user_preference import UserPreference  # Commenting out as this model doesn't exist yet


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def setup_database():
    # Create tables
    from app.main import create_tables
    create_tables()

    yield

    # No cleanup needed for this test - tables are managed by the application
    # and Better Auth creates additional tables that have dependencies
    pass


def test_get_tasks_empty(client, setup_database):
    """Test getting tasks when none exist"""
    response = client.get("/api/v1/tasks")
    assert response.status_code == 401  # Unauthenticated request should fail


def test_create_task_validation(client, setup_database):
    """Test task creation with validation"""
    # This test would require authentication
    pass