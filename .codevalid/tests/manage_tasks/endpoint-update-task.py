import pytest
from fastapi.testclient import TestClient
from backend.main import app

import backend.database as database

client = TestClient(app)

# --- Fixtures and Mocks ---

@pytest.fixture(autouse=True)
def setup_tasks(monkeypatch):
    """
    Setup the database mock for tasks.
    This will be reset before each test.
    """
    # In-memory "database"
    tasks = {
        1: {
            "id": 1,
            "title": "Original Task Title",
            "description": "Original description",
            "priority": 1,
            "due_date": "2026-01-10",
            "tag": "work",
            "status": "Pending"
        },
        2: {
            "id": 2,
            "title": "Original Title",
            "description": "Original description",
            "priority": 1,
            "due_date": "2026-01-15",
            "tag": "personal",
            "status": "Pending"
        },
        3: {
            "id": 3,
            "title": "Original Title",
            "description": "Original description",
            "priority": 1,
            "due_date": "2026-01-20",
            "tag": "edge",
            "status": "Pending"
        }
    }

    def get_task(task_id):
        return tasks.get(task_id)

    def update_task(task_id, task_data):
        if task_id not in tasks:
            return None
        # Simulate partial update
        for k, v in task_data.items():
            if v is not None:
                tasks[task_id][k] = v
        return tasks[task_id]

    monkeypatch.setattr(database, "get_task", get_task)
    monkeypatch.setattr(database, "update_task", update_task)

# --- Test Cases ---

def test_update_task_with_all_valid_fields():
    """
    Test Case 1: Update Task with All Valid Fields
    """
    data = {
        "title": "Updated Task Title",
        "description": "Updated description",
        "priority": 2,
        "due_date": "2026-01-10",
        "tag": "work",
        "status": "Pending"
    }
    response = client.put("/tasks/1", json=data)
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "Updated Task Title",
        "description": "Updated description",
        "priority": 2,
        "due_date": "2026-01-10",
        "tag": "work",
        "status": "Pending"
    }

def test_update_task_with_partial_fields():
    """
    Test Case 2: Update Task with Partial Fields
    """
    data = {
        "title": "Partially Updated Title"
    }
    response = client.put("/tasks/2", json=data)
    assert response.status_code == 200
    assert response.json() == {
        "id": 2,
        "title": "Partially Updated Title",
        "description": "Original description",
        "priority": 1,
        "due_date": "2026-01-15",
        "tag": "personal",
        "status": "Pending"
    }

def test_update_nonexistent_task():
    """
    Test Case 3: Update Nonexistent Task
    """
    data = {
        "title": "Any Title"
    }
    response = client.put("/tasks/9999", json=data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}

def test_update_task_with_invalid_priority():
    """
    Test Case 4: Update Task with Invalid Priority
    """
    data = {
        "priority": -1
    }
    response = client.put("/tasks/1", json=data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid priority value"}

def test_update_task_with_empty_title():
    """
    Test Case 5: Update Task with Empty Title
    """
    data = {
        "title": ""
    }
    response = client.put("/tasks/1", json=data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Title cannot be empty"}

def test_update_task_with_invalid_due_date_format():
    """
    Test Case 6: Update Task with Invalid Due Date Format
    """
    data = {
        "due_date": "01-10-2026"
    }
    response = client.put("/tasks/1", json=data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid due_date format"}

def test_update_task_with_maximum_title_length():
    """
    Test Case 7: Update Task with Maximum Title Length
    """
    max_title = "T" * 255
    data = {
        "title": max_title
    }
    response = client.put("/tasks/3", json=data)
    assert response.status_code == 200
    assert response.json() == {
        "id": 3,
        "title": max_title,
        "description": "Original description",
        "priority": 1,
        "due_date": "2026-01-20",
        "tag": "edge",
        "status": "Pending"
    }

def test_update_task_with_title_exceeding_maximum_length():
    """
    Test Case 8: Update Task with Title Exceeding Maximum Length
    """
    too_long_title = "T" * 256
    data = {
        "title": too_long_title
    }
    response = client.put("/tasks/3", json=data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Title exceeds maximum length"}

def test_update_task_missing_content_type_header():
    """
    Test Case 9: Update Task Missing Content-Type Header
    """
    data = {
        "title": "No Header"
    }
    # Send as data, not json, and omit content-type
    response = client.put("/tasks/1", data=str(data))
    assert response.status_code == 415
    assert response.json() == {"detail": "Unsupported Media Type"}

def test_update_task_with_invalid_status_value():
    """
    Test Case 10: Update Task with Invalid Status Value
    """
    data = {
        "status": "In Progress"
    }
    response = client.put("/tasks/1", json=data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid status value"}