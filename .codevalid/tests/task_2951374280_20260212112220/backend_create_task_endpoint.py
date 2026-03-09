import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.models import Task, TaskCreate, Priority
import backend.database as db
from datetime import datetime, timedelta

client = TestClient(app)

def setup_module(module):
    # Clean up tasks.json before tests
    import os
    if os.path.exists("tasks.json"):
        os.remove("tasks.json")

def teardown_module(module):
    import os
    if os.path.exists("tasks.json"):
        os.remove("tasks.json")

def generate_future_date():
    return (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")

def generate_past_date():
    return (datetime.utcnow() - timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ")

def repeat_char(char, n):
    return char * n

# Test Case 1: create_task_successful
def test_create_task_successful():
    payload = {
        "description": "Write and review documentation for project release.",
        "due_date": "2024-07-01T23:59:00Z",
        "priority": "high",
        "tag": "documentation",
        "title": "Complete Project Documentation"
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 201 or response.status_code == 200
    data = response.json()
    assert data["description"] == payload["description"]
    assert data["due_date"] == payload["due_date"]
    assert data["priority"].lower() == payload["priority"]
    assert data["tag"] == payload["tag"]
    assert data["title"] == payload["title"]
    assert "id" in data

# Test Case 2: create_task_missing_title
def test_create_task_missing_title():
    payload = {
        "description": "Write and review documentation for project release.",
        "due_date": "2024-07-01T23:59:00Z",
        "priority": "high",
        "tag": "documentation"
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Title is required."

# Test Case 3: create_task_missing_description
def test_create_task_missing_description():
    payload = {
        "due_date": "2024-07-01T23:59:00Z",
        "priority": "high",
        "title": "Complete Project Documentation"
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Description is required."

# Test Case 4: create_task_missing_priority
def test_create_task_missing_priority():
    payload = {
        "description": "Write and review documentation for project release.",
        "due_date": "2024-07-01T23:59:00Z",
        "title": "Complete Project Documentation"
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Priority is required."

# Test Case 5: create_task_missing_due_date
def test_create_task_missing_due_date():
    payload = {
        "description": "Write and review documentation for project release.",
        "priority": "high",
        "title": "Complete Project Documentation"
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Due date is required."

# Test Case 6: create_task_optional_tag_omitted
def test_create_task_optional_tag_omitted():
    payload = {
        "description": "Write and review documentation for project release.",
        "due_date": "2024-07-01T23:59:00Z",
        "priority": "high",
        "title": "Complete Project Documentation"
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 201 or response.status_code == 200
    data = response.json()
    assert data["description"] == payload["description"]
    assert data["due_date"] == payload["due_date"]
    assert data["priority"].lower() == payload["priority"]
    assert data["tag"] is None
    assert data["title"] == payload["title"]
    assert "id" in data

# Test Case 7: create_task_invalid_priority_value
def test_create_task_invalid_priority_value():
    payload = {
        "description": "Write and review documentation for project release.",
        "due_date": "2024-07-01T23:59:00Z",
        "priority": "urgent",
        "title": "Complete Project Documentation"
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Priority must be one of: low, medium, high."

# Test Case 8: create_task_due_date_in_past
def test_create_task_due_date_in_past():
    payload = {
        "description": "Task with past due date.",
        "due_date": "2020-01-01T00:00:00Z",
        "priority": "medium",
        "title": "Finish old task"
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Due date must be in the future."

# Test Case 9: create_task_extra_field_rejected
def test_create_task_extra_field_rejected():
    payload = {
        "description": "Write and review documentation for project release.",
        "due_date": "2024-07-01T23:59:00Z",
        "extra_field": "not_allowed",
        "priority": "high",
        "tag": "documentation",
        "title": "Complete Project Documentation"
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Unexpected field: extra_field."

# Test Case 10: create_task_empty_title
def test_create_task_empty_title():
    payload = {
        "description": "Write and review documentation for project release.",
        "due_date": "2024-07-01T23:59:00Z",
        "priority": "high",
        "title": ""
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Title cannot be empty."

# Test Case 11: create_task_title_max_length
def test_create_task_title_max_length():
    max_title = repeat_char("T", 255)
    payload = {
        "description": "Edge case for title max length.",
        "due_date": "2024-07-01T23:59:00Z",
        "priority": "medium",
        "title": max_title
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 201 or response.status_code == 200
    data = response.json()
    assert data["description"] == payload["description"]
    assert data["due_date"] == payload["due_date"]
    assert data["priority"].lower() == payload["priority"]
    assert data["tag"] is None
    assert data["title"] == payload["title"]
    assert "id" in data

# Test Case 12: create_task_title_exceeds_max_length
def test_create_task_title_exceeds_max_length():
    long_title = repeat_char("T", 256)
    payload = {
        "description": "Exceed title max length.",
        "due_date": "2024-07-01T23:59:00Z",
        "priority": "medium",
        "title": long_title
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Title exceeds maximum length of 255 characters."

# Test Case 13: create_task_invalid_due_date_format
def test_create_task_invalid_due_date_format():
    payload = {
        "description": "Write and review documentation for project release.",
        "due_date": "July 1, 2024",
        "priority": "high",
        "title": "Complete Project Documentation"
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Due date must be a valid ISO8601 datetime string."

# Test Case 14: create_task_view_and_edit_after_creation
def test_create_task_view_and_edit_after_creation():
    payload = {
        "description": "Initial Task Description",
        "due_date": "2024-07-01T23:59:00Z",
        "priority": "low",
        "tag": "initial",
        "title": "Initial Task Title"
    }
    # Create task
    response = client.post("/tasks", json=payload)
    assert response.status_code == 201 or response.status_code == 200
    data = response.json()
    task_id = data["id"]
    assert data["description"] == payload["description"]
    assert data["due_date"] == payload["due_date"]
    assert data["priority"].lower() == payload["priority"]
    assert data["tag"] == payload["tag"]
    assert data["title"] == payload["title"]

    # View task
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["id"] == task_id
    assert get_data["title"] == payload["title"]

    # Edit task
    patch_payload = {
        "description": "Updated Task Description",
        "due_date": "2024-07-01T23:59:00Z",
        "priority": "medium",
        "title": "Updated Task Title"
    }
    patch_response = client.put(f"/tasks/{task_id}", json=patch_payload)
    assert patch_response.status_code == 200
    patch_data = patch_response.json()
    assert patch_data["id"] == task_id
    assert patch_data["description"] == patch_payload["description"]
    assert patch_data["title"] == patch_payload["title"]