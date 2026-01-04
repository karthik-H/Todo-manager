import pytest
from fastapi.testclient import TestClient
from backend.main import app

import sys
from unittest.mock import patch, MagicMock

client = TestClient(app)

# --- Fixtures and Mocks ---

@pytest.fixture
def mock_get_tasks():
    with patch("backend.database.get_tasks") as mock:
        yield mock

@pytest.fixture
def mock_auth_required():
    """Patch authentication dependency to simulate authentication required."""
    with patch("backend.main.get_current_user") as mock:
        mock.side_effect = Exception("Not authenticated")
        yield mock

# --- Test Cases ---

def test_retrieve_all_tasks_when_tasks_exist(mock_get_tasks):
    """
    Test Case 1: Retrieve all tasks when tasks exist
    Verify that the endpoint returns a list of all tasks when tasks are present in the database.
    """
    tasks = [
        {
            "id": 1,
            "title": "Task 1",
            "description": "Description 1",
            "priority": "High",
            "due_date": "2026-01-10",
            "tag": "Work",
            "status": "Pending"
        },
        {
            "id": 2,
            "title": "Task 2",
            "description": "Description 2",
            "priority": "Low",
            "due_date": "2026-01-15",
            "tag": "Personal",
            "status": "Completed"
        }
    ]
    mock_get_tasks.return_value = tasks

    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == {"tasks": tasks}

def test_retrieve_all_tasks_when_no_tasks_exist(mock_get_tasks):
    """
    Test Case 2: Retrieve all tasks when no tasks exist
    Verify that the endpoint returns an empty list when there are no tasks in the database.
    """
    mock_get_tasks.return_value = []

    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == {"tasks": []}

def test_retrieve_all_tasks_with_large_number_of_tasks(mock_get_tasks):
    """
    Test Case 3: Retrieve all tasks with a large number of tasks
    Verify that the endpoint can handle and return a large number of tasks efficiently.
    """
    tasks = [
        {
            "id": i + 1,
            "title": f"Task {i + 1}",
            "description": f"Description {i + 1}",
            "priority": "Medium",
            "due_date": "2026-01-10",
            "tag": "General",
            "status": "Pending"
        }
        for i in range(1000)
    ]
    mock_get_tasks.return_value = tasks

    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == {"tasks": tasks}

def test_invalid_method_post_to_read_tasks():
    """
    Test Case 4: Invalid method POST to read_tasks
    Verify that using an unsupported HTTP method (POST) returns the correct error.
    """
    response = client.post("/tasks", json={})
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}

def test_invalid_method_put_to_read_tasks():
    """
    Test Case 5: Invalid method PUT to read_tasks
    Verify that using an unsupported HTTP method (PUT) returns the correct error.
    """
    response = client.put("/tasks", json={})
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}

def test_retrieve_tasks_with_special_characters(mock_get_tasks):
    """
    Test Case 6: Retrieve tasks with special characters
    Verify that tasks with special characters in their fields are returned correctly.
    """
    tasks = [
        {
            "id": 1,
            "title": "Task with emoji 🚀",
            "description": "Description with newline\nand tab\tcharacters",
            "priority": "High",
            "due_date": "2026-01-10",
            "tag": "Special",
            "status": "Pending"
        }
    ]
    mock_get_tasks.return_value = tasks

    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == {"tasks": tasks}

def test_unauthorized_access_to_read_tasks(monkeypatch):
    """
    Test Case 7: Unauthorized access to read_tasks
    Verify that the endpoint returns 401 Unauthorized if authentication is required and not provided.
    """
    # Patch the dependency that checks authentication to raise an exception
    # The actual dependency name may differ; adjust as needed for your app
    # Here, we simulate FastAPI's HTTPException for 401
    from fastapi import HTTPException

    def raise_unauth(*args, **kwargs):
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Patch the dependency in the app
    with patch("backend.main.get_current_user", side_effect=raise_unauth):
        response = client.get("/tasks")
        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}

def test_retrieve_tasks_with_missing_optional_fields(mock_get_tasks):
    """
    Test Case 8: Retrieve tasks with missing optional fields
    Verify that tasks with missing optional fields (e.g., description, tag) are returned correctly.
    """
    tasks = [
        {
            "id": 1,
            "title": "Task without description",
            "priority": "Medium",
            "due_date": "2026-01-12",
            "status": "Pending"
            # 'description' and 'tag' are omitted
        }
    ]
    mock_get_tasks.return_value = tasks

    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == {"tasks": tasks}