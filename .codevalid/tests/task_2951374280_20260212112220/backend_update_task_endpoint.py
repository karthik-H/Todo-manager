import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.models import Task, TaskCreate, Priority, Category
from unittest.mock import patch

client = TestClient(app)

# Helper functions for mapping test case fields to model fields
def priority_from_int(val):
    mapping = {1: Priority.low, 2: Priority.medium, 3: Priority.high, 4: Priority.high, 5: Priority.high}
    # For edge cases, map 1 to low, 2 to medium, 3 to high, 4/5 to high (since only 3 levels in Enum)
    return mapping.get(val, Priority.medium)

def category_from_tag(tag):
    mapping = {
        "work": Category.work,
        "personal": Category.personal,
        "study": Category.study,
        "urgent": Category.work,
        "misc": Category.work,
        "low": Category.work,
        "high": Category.work,
        "none": None,
        "maxlen": Category.work,
        "overflow": Category.work,
        "error": Category.work,
        "invalid": Category.work,
    }
    return mapping.get(tag, None)

def make_task(id, data):
    return Task(
        id=str(id),
        title=data.get("title", ""),
        description=data.get("description", ""),
        priority=priority_from_int(data.get("priority", 2)),
        category=category_from_tag(data.get("tag", None)),
        due_date=data.get("due_date", None),
        completed=False
    )

# Test Case 1: Update an existing task with valid data
def test_update_existing_task_valid_data():
    task_id = "123"
    initial_task = make_task(task_id, {
        "title": "Initial Title",
        "description": "Initial description.",
        "priority": 1,
        "tag": "work",
        "due_date": "2024-06-01"
    })
    updated_data = {
        "title": "Updated Title",
        "description": "Updated description.",
        "priority": 2,
        "tag": "work",
        "due_date": "2024-07-01"
    }
    updated_task = make_task(task_id, updated_data)
    with patch("backend.database.update_task", return_value=updated_task):
        response = client.put(f"/tasks/{task_id}", json=updated_data)
        assert response.status_code == 200
        resp = response.json()
        assert resp["id"] == task_id
        assert resp["title"] == updated_data["title"]
        assert resp["description"] == updated_data["description"]
        assert resp["priority"] == priority_from_int(updated_data["priority"])
        assert resp["category"] == category_from_tag(updated_data["tag"])
        assert resp["due_date"] == updated_data["due_date"]

# Test Case 2: Update fails when title is missing
def test_update_fails_missing_title():
    task_id = "124"
    data = {
        "description": "No title here.",
        "priority": 1,
        "tag": "urgent",
        "due_date": "2024-07-10"
    }
    with patch("backend.database.update_task", return_value=None):
        response = client.put(f"/tasks/{task_id}", json=data)
        assert response.status_code == 422
        assert response.json()["detail"] == "Field 'title' is required."

# Test Case 3: Update fails when description is missing
def test_update_fails_missing_description():
    task_id = "125"
    data = {
        "title": "No Description",
        "priority": 3,
        "tag": "personal",
        "due_date": "2024-08-15"
    }
    with patch("backend.database.update_task", return_value=None):
        response = client.put(f"/tasks/{task_id}", json=data)
        assert response.status_code == 422
        assert response.json()["detail"] == "Field 'description' is required."

# Test Case 4: Update fails when priority is missing
def test_update_fails_missing_priority():
    task_id = "126"
    data = {
        "title": "No Priority",
        "description": "Missing priority.",
        "tag": "low",
        "due_date": "2024-09-01"
    }
    with patch("backend.database.update_task", return_value=None):
        response = client.put(f"/tasks/{task_id}", json=data)
        assert response.status_code == 422
        assert response.json()["detail"] == "Field 'priority' is required."

# Test Case 5: Update fails when due_date is missing
def test_update_fails_missing_due_date():
    task_id = "127"
    data = {
        "title": "No Due Date",
        "description": "Missing due date.",
        "priority": 1,
        "tag": "work"
    }
    with patch("backend.database.update_task", return_value=None):
        response = client.put(f"/tasks/{task_id}", json=data)
        assert response.status_code == 422
        assert response.json()["detail"] == "Field 'due_date' is required."

# Test Case 6: Update fails with extra field
def test_update_fails_extra_field():
    task_id = "128"
    data = {
        "title": "Extra Field",
        "description": "Payload contains an extra field.",
        "priority": 2,
        "tag": "misc",
        "due_date": "2024-07-15",
        "unexpected_field": "should not be here"
    }
    with patch("backend.database.update_task", return_value=None):
        response = client.put(f"/tasks/{task_id}", json=data)
        assert response.status_code == 422
        assert response.json()["detail"] == "Unexpected field: 'unexpected_field'. Only ['title', 'description', 'priority', 'due_date', 'tag'] are allowed."

# Test Case 7: Update task without optional tag
def test_update_task_without_optional_tag():
    task_id = "129"
    data = {
        "title": "No Tag",
        "description": "Tag is omitted.",
        "priority": 3,
        "due_date": "2024-08-10"
    }
    updated_task = make_task(task_id, {**data, "tag": None})
    with patch("backend.database.update_task", return_value=updated_task):
        response = client.put(f"/tasks/{task_id}", json=data)
        assert response.status_code == 200
        resp = response.json()
        assert resp["id"] == task_id
        assert resp["title"] == data["title"]
        assert resp["description"] == data["description"]
        assert resp["priority"] == priority_from_int(data["priority"])
        assert resp["category"] is None
        assert resp["due_date"] == data["due_date"]

# Test Case 8: Update a non-existent task
def test_update_nonexistent_task():
    task_id = "99999"
    data = {
        "title": "Should Fail",
        "description": "Trying to update a non-existent task.",
        "priority": 1,
        "tag": "none",
        "due_date": "2024-12-31"
    }
    with patch("backend.database.update_task", return_value=None):
        response = client.put(f"/tasks/{task_id}", json=data)
        assert response.status_code == 404
        assert response.json()["detail"] == f"Task with id {task_id} not found."

# Test Case 9: Update task with lowest allowed priority
def test_update_task_lowest_priority():
    task_id = "130"
    data = {
        "title": "Low Priority",
        "description": "Priority is set to minimum.",
        "priority": 1,
        "tag": "low",
        "due_date": "2024-10-01"
    }
    updated_task = make_task(task_id, data)
    with patch("backend.database.update_task", return_value=updated_task):
        response = client.put(f"/tasks/{task_id}", json=data)
        assert response.status_code == 200
        resp = response.json()
        assert resp["id"] == task_id
        assert resp["priority"] == priority_from_int(data["priority"])

# Test Case 10: Update task with highest allowed priority
def test_update_task_highest_priority():
    task_id = "131"
    data = {
        "title": "High Priority",
        "description": "Priority is set to maximum.",
        "priority": 5,
        "tag": "high",
        "due_date": "2024-10-02"
    }
    updated_task = make_task(task_id, data)
    with patch("backend.database.update_task", return_value=updated_task):
        response = client.put(f"/tasks/{task_id}", json=data)
        assert response.status_code == 200
        resp = response.json()
        assert resp["id"] == task_id
        assert resp["priority"] == priority_from_int(data["priority"])

# Test Case 11: Update fails with priority below allowed minimum
def test_update_fails_priority_below_min():
    task_id = "132"
    data = {
        "title": "Priority Too Low",
        "description": "Priority is below minimum.",
        "priority": 0,
        "tag": "error",
        "due_date": "2024-10-03"
    }
    with patch("backend.database.update_task", return_value=None):
        response = client.put(f"/tasks/{task_id}", json=data)
        assert response.status_code == 422
        assert response.json()["detail"] == "'priority' must be between 1 and 5."

# Test Case 12: Update fails with priority above allowed maximum
def test_update_fails_priority_above_max():
    task_id = "133"
    data = {
        "title": "Priority Too High",
        "description": "Priority is above maximum.",
        "priority": 6,
        "tag": "error",
        "due_date": "2024-10-04"
    }
    with patch("backend.database.update_task", return_value=None):
        response = client.put(f"/tasks/{task_id}", json=data)
        assert response.status_code == 422
        assert response.json()["detail"] == "'priority' must be between 1 and 5."

# Test Case 13: Update fails with invalid due_date format
def test_update_fails_invalid_due_date_format():
    task_id = "134"
    data = {
        "title": "Invalid Date",
        "description": "Due date is not valid.",
        "priority": 3,
        "tag": "invalid",
        "due_date": "31/12/2024"
    }
    with patch("backend.database.update_task", return_value=None):
        response = client.put(f"/tasks/{task_id}", json=data)
        assert response.status_code == 422
        assert response.json()["detail"] == "'due_date' must be in 'YYYY-MM-DD' format."

# Test Case 14: Update task with maximum allowed title length
def test_update_task_max_title_length():
    task_id = "135"
    max_title = "T" * 255
    data = {
        "title": max_title,
        "description": "Title is at max length.",
        "priority": 2,
        "tag": "maxlen",
        "due_date": "2024-11-01"
    }
    updated_task = make_task(task_id, data)
    with patch("backend.database.update_task", return_value=updated_task):
        response = client.put(f"/tasks/{task_id}", json=data)
        assert response.status_code == 200
        resp = response.json()
        assert resp["id"] == task_id
        assert resp["title"] == max_title

# Test Case 15: Update fails when title exceeds maximum length
def test_update_fails_title_exceeds_max_length():
    task_id = "136"
    too_long_title = "T" * 256
    data = {
        "title": too_long_title,
        "description": "Title exceeds max length.",
        "priority": 2,
        "tag": "overflow",
        "due_date": "2024-11-02"
    }
    with patch("backend.database.update_task", return_value=None):
        response = client.put(f"/tasks/{task_id}", json=data)
        assert response.status_code == 422
        assert response.json()["detail"] == "'title' must not exceed 255 characters."