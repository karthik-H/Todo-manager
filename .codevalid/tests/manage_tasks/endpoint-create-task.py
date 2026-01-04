import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

import sys
import os

# Ensure backend is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../backend")))

from main import app

client = TestClient(app)

# Utility for generating a future date string
def future_date_str(days=5):
    return (datetime.utcnow() + timedelta(days=days)).strftime("%Y-%m-%d")

# Utility for generating a past date string
def past_date_str(days=5):
    return (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")

# Utility for max length title
def max_length_title():
    return "T" * 255

@pytest.fixture(autouse=True)
def clear_db():
    # If the backend provides a way to clear/reset the DB, do it here.
    # Otherwise, tests must be written to not depend on DB state.
    # For now, assume DB is in-memory or reset between tests.
    pass

def test_create_task_with_all_valid_fields():
    """
    Test Case 1: Create Task with All Valid Fields
    """
    data = {
        "title": "Buy groceries",
        "description": "Milk, eggs, bread",
        "priority": 2,
        "due_date": future_date_str(6),
        "tag": "Personal"
    }
    response = client.post("/tasks", json=data)
    assert response.status_code == 201
    resp = response.json()
    assert resp["title"] == data["title"]
    assert resp["description"] == data["description"]
    assert resp["priority"] == data["priority"]
    assert resp["due_date"] == data["due_date"]
    assert resp["tag"] == data["tag"]
    assert resp["status"] == "Pending"
    assert "id" in resp

def test_create_task_missing_title():
    """
    Test Case 2: Create Task Missing Title
    """
    data = {
        "description": "No title provided",
        "priority": 1,
        "due_date": future_date_str(7),
        "tag": "Work"
    }
    response = client.post("/tasks", json=data)
    assert response.status_code == 422
    assert response.json() == {"detail": "Field 'title' is required"}

def test_create_task_with_empty_title():
    """
    Test Case 3: Create Task with Empty Title
    """
    data = {
        "title": "",
        "description": "Empty title",
        "priority": 1,
        "due_date": future_date_str(7),
        "tag": "Work"
    }
    response = client.post("/tasks", json=data)
    assert response.status_code == 422
    assert response.json() == {"detail": "Field 'title' cannot be empty"}

def test_create_task_with_maximum_title_length():
    """
    Test Case 4: Create Task with Maximum Title Length
    """
    data = {
        "title": max_length_title(),
        "description": "Max length title",
        "priority": 1,
        "due_date": future_date_str(7),
        "tag": "Edge"
    }
    response = client.post("/tasks", json=data)
    assert response.status_code == 201
    resp = response.json()
    assert resp["title"] == data["title"]
    assert resp["description"] == data["description"]
    assert resp["priority"] == data["priority"]
    assert resp["due_date"] == data["due_date"]
    assert resp["tag"] == data["tag"]
    assert resp["status"] == "Pending"
    assert "id" in resp

def test_create_task_with_priority_out_of_range():
    """
    Test Case 5: Create Task with Priority Out of Range
    """
    data = {
        "title": "Invalid priority",
        "description": "Priority is -1",
        "priority": -1,
        "due_date": future_date_str(7),
        "tag": "Work"
    }
    response = client.post("/tasks", json=data)
    assert response.status_code == 422
    assert response.json() == {"detail": "Field 'priority' must be between 1 and 5"}

def test_create_task_with_past_due_date():
    """
    Test Case 6: Create Task with Past Due Date
    """
    data = {
        "title": "Past due date",
        "description": "Due date is in the past",
        "priority": 2,
        "due_date": past_date_str(10),
        "tag": "Work"
    }
    response = client.post("/tasks", json=data)
    assert response.status_code == 422
    assert response.json() == {"detail": "Field 'due_date' cannot be in the past"}

def test_create_task_without_tag():
    """
    Test Case 7: Create Task Without Tag
    """
    data = {
        "title": "No tag",
        "description": "Task without tag",
        "priority": 3,
        "due_date": future_date_str(7)
    }
    response = client.post("/tasks", json=data)
    assert response.status_code == 201
    resp = response.json()
    assert resp["title"] == data["title"]
    assert resp["description"] == data["description"]
    assert resp["priority"] == data["priority"]
    assert resp["due_date"] == data["due_date"]
    assert resp["tag"] is None
    assert resp["status"] == "Pending"
    assert "id" in resp

def test_create_task_with_invalid_due_date_format():
    """
    Test Case 8: Create Task with Invalid Due Date Format
    """
    data = {
        "title": "Invalid due date",
        "description": "Due date is not a date",
        "priority": 2,
        "due_date": "not-a-date",
        "tag": "Work"
    }
    response = client.post("/tasks", json=data)
    assert response.status_code == 422
    assert response.json() == {"detail": "Field 'due_date' must be a valid date"}

def test_create_task_with_duplicate_title():
    """
    Test Case 9: Create Task with Duplicate Title
    """
    # First, create the task
    data = {
        "title": "Buy groceries",
        "description": "Milk, eggs, bread",
        "priority": 2,
        "due_date": future_date_str(7),
        "tag": "Personal"
    }
    response = client.post("/tasks", json=data)
    assert response.status_code == 201

    # Now, try to create with the same title
    data2 = {
        "title": "Buy groceries",
        "description": "Duplicate title",
        "priority": 2,
        "due_date": future_date_str(8),
        "tag": "Personal"
    }
    response2 = client.post("/tasks", json=data2)
    assert response2.status_code == 409
    assert response2.json() == {"detail": "Task with this title already exists"}

def test_create_task_with_minimum_priority():
    """
    Test Case 10: Create Task with Minimum Priority
    """
    data = {
        "title": "Low priority task",
        "description": "Priority is minimum",
        "priority": 1,
        "due_date": future_date_str(7),
        "tag": "Low"
    }
    response = client.post("/tasks", json=data)
    assert response.status_code == 201
    resp = response.json()
    assert resp["title"] == data["title"]
    assert resp["description"] == data["description"]
    assert resp["priority"] == data["priority"]
    assert resp["due_date"] == data["due_date"]
    assert resp["tag"] == data["tag"]
    assert resp["status"] == "Pending"
    assert "id" in resp

def test_create_task_with_maximum_priority():
    """
    Test Case 11: Create Task with Maximum Priority
    """
    data = {
        "title": "High priority task",
        "description": "Priority is maximum",
        "priority": 5,
        "due_date": future_date_str(7),
        "tag": "High"
    }
    response = client.post("/tasks", json=data)
    assert response.status_code == 201
    resp = response.json()
    assert resp["title"] == data["title"]
    assert resp["description"] == data["description"]
    assert resp["priority"] == data["priority"]
    assert resp["due_date"] == data["due_date"]
    assert resp["tag"] == data["tag"]
    assert resp["status"] == "Pending"
    assert "id" in resp

def test_create_task_with_non_integer_priority():
    """
    Test Case 12: Create Task with Non-integer Priority
    """
    data = {
        "title": "Non-integer priority",
        "description": "Priority is a string",
        "priority": "high",
        "due_date": future_date_str(7),
        "tag": "Work"
    }
    response = client.post("/tasks", json=data)
    assert response.status_code == 422
    assert response.json() == {"detail": "Field 'priority' must be an integer"}

def test_create_task_with_extra_fields():
    """
    Test Case 13: Create Task with Extra Fields
    """
    data = {
        "title": "Extra field",
        "description": "Has extra field",
        "priority": 2,
        "due_date": future_date_str(7),
        "tag": "Work",
        "extra_field": "should not be here"
    }
    response = client.post("/tasks", json=data)
    assert response.status_code == 422
    assert response.json() == {"detail": "Unexpected field 'extra_field'"}