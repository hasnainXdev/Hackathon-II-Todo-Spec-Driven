import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_preferences_endpoints_exist(client):
    """Test that preferences endpoints exist"""
    # These endpoints would require authentication to test properly
    # Just checking they exist and return appropriate status codes
    response = client.get("/api/v1/preferences")
    # Should return 401 for unauthenticated request
    assert response.status_code in [401, 422]  # 422 if missing auth header format


def test_get_specific_preference(client):
    """Test getting a specific preference"""
    response = client.get("/api/v1/preferences/test_key")
    # Should return 401 for unauthenticated request
    assert response.status_code in [401, 422]


def test_update_preference(client):
    """Test updating a preference"""
    response = client.put("/api/v1/preferences/test_key", json={"preference_value": "test_value"})
    # Should return 401 for unauthenticated request
    assert response.status_code in [401, 422]


def test_delete_preference(client):
    """Test deleting a preference"""
    response = client.delete("/api/v1/preferences/test_key")
    # Should return 401 for unauthenticated request
    assert response.status_code in [401, 422]