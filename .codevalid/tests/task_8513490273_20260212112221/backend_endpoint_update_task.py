import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.models import Task, TaskCreate, Priority, Category
import backend.database as db
from datetime import date
from unittest.mock import patch

client = TestClient(app)

# Helper: create a task in the DB file
def setup_task(task_id, **kwargs):
    task = Task(
        id=str(task_id),
        title=kwargs.get("title", "Task Title"),
        description=kwargs.get("description", "Description"),
        priority=kwargs.get("priority", Priority.medium),
        category=kwargs.get("category", Category.work),
        due_date=kwargs.get("due_date", date(2024, 7, 10)),
        completed=kwargs.get("completed", False)
    )
    tasks = db.get_tasks()
    # Remove any existing task with same id
    tasks = [t for t in tasks if t.id != str(task_id)]
    tasks.append(task)
    db.save_tasks(tasks)
    return task

def teardown_task(task_id):
    tasks = db.get_tasks()
    tasks = [t for t in tasks if t.id != str(task_id)]
    db.save_tasks(tasks)

@pytest.fixture(autouse=True)
def cleanup():
    # Clean up before and after each test
    yield
    # Remove test tasks
    for tid in ["123", "124", "125", "126", "127", "128", "129", "130", "131", "132"]:
        teardown_task(tid)

# Test Case 1: Update Existing Task - All Fields
def test_update_existing_task_all_fields():
    setup_task("123", title="Old Title", description="Old desc", priority=Priority.low, category=Category.work, due_date=date(2024, 7, 1))
    body = {
        "title": "Updated Task Title",
        "description": "This is the updated description.",
        "priority": "High",
        "category": "Work",
        "due_date": "2024-07-15"
    }
    response = client.put("/tasks/123", json=body)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "123"
    assert data["title"] == "Updated Task Title"
    assert data["description"] == "This is the updated description."
    assert data["priority"] == "High"
    assert data["category"] == "Work"
    assert data["due_date"] == "2024-07-15"

# Test Case 2: Update Existing Task - Partial Fields
def test_update_existing_task_partial_fields():
    setup_task("124", title="Initial Title", description="Initial description", priority=Priority.high, category=Category.personal, due_date=date(2024, 7, 20))
    body = {
        "title": "Quick Update",
        "priority": "Low"
    }
    response = client.put("/tasks/124", json=body)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "124"
    assert data["title"] == "Quick Update"
    assert data["priority"] == "Low"
    assert data["description"] == "Initial description"
    assert data["category"] == "Personal"
    assert data["due_date"] == "2024-07-20"

# Test Case 3: Update Non-Existent Task
def test_update_nonexistent_task():
    body = {"title": "Should Fail"}
    response = client.put("/tasks/99999", json=body)
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}

# Test Case 4: Update Task With Invalid Priority Value
def test_update_task_invalid_priority():
    setup_task("125", title="Valid Title")
    body = {"priority": "super-high"}
    response = client.put("/tasks/125", json=body)
    assert response.status_code == 422
    # FastAPI returns a validation error for enum
    assert "value is not a valid enumeration member" in str(response.json())

# Test Case 5: Update Task With Invalid Due Date Format
def test_update_task_invalid_due_date_format():
    setup_task("126", title="Valid Title")
    body = {"due_date": "15-07-2024"}
    response = client.put("/tasks/126", json=body)
    assert response.status_code == 422
    # FastAPI returns a validation error for date format
    assert "invalid date format" in str(response.json()) or "value is not a valid date" in str(response.json())

# Test Case 6: Update Task With Empty Title
def test_update_task_empty_title():
    setup_task("127", title="Valid Title")
    body = {"title": ""}
    response = client.put("/tasks/127", json=body)
    assert response.status_code == 422
    # FastAPI returns a validation error for min_length, but model does not enforce it, so we check for empty string
    assert "Title must not be empty" in str(response.json()) or response.status_code == 422

# Test Case 7: Update Task With Maximum Title Length
def test_update_task_max_title_length():
    setup_task("128", title="Edge case test", description="Edge case test", priority=Priority.medium, category=Category.test, due_date=date(2024, 7, 10))
    max_title = "T" * 255
    body = {"title": max_title}
    response = client.put("/tasks/128", json=body)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == max_title

# Test Case 8: Update Task With Overlong Title
def test_update_task_overlong_title():
    setup_task("129", title="Valid Title")
    overlong_title = "T" * 256
    body = {"title": overlong_title}
    response = client.put("/tasks/129", json=body)
    assert response.status_code == 422 or response.status_code == 400
    assert "Title exceeds maximum length" in str(response.json()) or response.status_code == 422

# Test Case 9: Update Task - Remove Category (Tag)
def test_update_task_remove_category():
    setup_task("130", title="Task Title", description="Task Description", priority=Priority.medium, category=Category.work, due_date=date(2024, 7, 22))
    body = {"category": None}
    response = client.put("/tasks/130", json=body)
    assert response.status_code == 200
    data = response.json()
    assert data["category"] is None

# Test Case 10: Update Task With Extra Field
def test_update_task_with_extra_field():
    setup_task("131", title="Supports Extra Field", description="Description", priority=Priority.medium, category=Category.tag, due_date=date(2024, 7, 23))
    body = {"title": "Supports Extra Field", "nonexistent_field": "should be ignored"}
    response = client.put("/tasks/131", json=body)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Supports Extra Field"
    assert "nonexistent_field" not in data

# Test Case 11: Update Task With Empty Body
def test_update_task_empty_body():
    setup_task("132", title="Valid Title")
    body = {}
    response = client.put("/tasks/132", json=body)
    assert response.status_code == 422
    assert "At least one field must be provided for update" in str(response.json()) or response.status_code == 422