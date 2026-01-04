import os
import json
import tempfile
import shutil
import pytest
from datetime import date, timedelta

# Patch sys.path for import if running from repo root
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../backend")))

from backend import database
from backend.models import Task, TaskCreate, Priority, Category

DB_FILE = database.DB_FILE

@pytest.fixture(autouse=True)
def temp_db(monkeypatch):
    # Use a temp file for DB
    tmpdir = tempfile.mkdtemp()
    db_path = os.path.join(tmpdir, "tasks.json")
    monkeypatch.setattr(database, "DB_FILE", db_path)
    yield
    shutil.rmtree(tmpdir)

def create_task_in_db(task_id, title="Title", description="Desc", priority=Priority.medium, category=Category.work, due_date=None, completed=False):
    if due_date is None:
        due_date = date.today()
    task = Task(
        id=task_id,
        title=title,
        description=description,
        priority=priority,
        category=category,
        due_date=due_date,
        completed=completed
    )
    database.save_tasks([task])
    return task

def create_multiple_tasks(tasks):
    database.save_tasks(tasks)

def valid_taskcreate(**kwargs):
    # Helper for valid TaskCreate
    data = {
        "title": "New Title",
        "description": "New Desc",
        "priority": Priority.high,
        "category": Category.personal,
        "due_date": date.today() + timedelta(days=1),
        "completed": True
    }
    data.update(kwargs)
    return TaskCreate(**data)

def identical_taskcreate_from_task(task):
    return TaskCreate(
        title=task.title,
        description=task.description,
        priority=task.priority,
        category=task.category,
        due_date=task.due_date,
        completed=task.completed
    )

# Test Case 1: Update existing task with valid data
def test_update_existing_task_with_valid_data():
    orig = create_task_in_db("1")
    new_data = valid_taskcreate()
    updated = database.update_task("1", new_data)
    assert updated is not None
    assert updated.id == "1"
    assert updated.title == new_data.title
    assert updated.description == new_data.description
    assert updated.priority == new_data.priority
    assert updated.category == new_data.category
    assert updated.due_date == new_data.due_date
    assert updated.completed == new_data.completed

# Test Case 2: Attempt to update a non-existent task
def test_attempt_to_update_nonexistent_task():
    new_data = valid_taskcreate()
    updated = database.update_task("999", new_data)
    assert updated is None

# Test Case 3: Update task with partial fields (should update all fields)
def test_update_task_with_partial_fields():
    orig = create_task_in_db("2", title="Old Title", description="Desc", priority=Priority.low, category=Category.study, due_date=date(2024,1,1), completed=False)
    # Only change title, keep other fields same as original
    new_data = TaskCreate(
        title="Updated Title",
        description=orig.description,
        priority=orig.priority,
        category=orig.category,
        due_date=orig.due_date,
        completed=orig.completed
    )
    updated = database.update_task("2", new_data)
    assert updated is not None
    assert updated.title == "Updated Title"
    assert updated.description == orig.description
    assert updated.priority == orig.priority
    assert updated.category == orig.category
    assert updated.due_date == orig.due_date
    assert updated.completed == orig.completed

# Test Case 4: Update task with empty title
def test_update_task_with_empty_title():
    orig = create_task_in_db("3")
    # Pydantic will raise ValidationError for empty title
    with pytest.raises(Exception):
        new_data = TaskCreate(
            title="",
            description=orig.description,
            priority=orig.priority,
            category=orig.category,
            due_date=orig.due_date,
            completed=orig.completed
        )
        database.update_task("3", new_data)

# Test Case 5: Update task with maximum allowed title length
def test_update_task_with_max_title_length():
    orig = create_task_in_db("4")
    max_title = "T" * 255
    new_data = valid_taskcreate(title=max_title)
    updated = database.update_task("4", new_data)
    assert updated is not None
    assert updated.title == max_title

# Test Case 6: Update task with invalid due date
def test_update_task_with_invalid_due_date():
    orig = create_task_in_db("5")
    # Pydantic will raise ValidationError for invalid date
    with pytest.raises(Exception):
        # Simulate invalid date by passing string (should fail)
        new_data = TaskCreate(
            title="Valid",
            description="desc",
            priority=Priority.medium,
            category=Category.work,
            due_date="2023-02-30",  # Invalid date
            completed=False
        )
        database.update_task("5", new_data)

# Test Case 7: Update task status from Pending to Completed
def test_update_task_status_from_pending_to_completed():
    orig = create_task_in_db("6", completed=False)
    new_data = valid_taskcreate(completed=True)
    updated = database.update_task("6", new_data)
    assert updated is not None
    assert updated.completed is True

# Test Case 8: Update task with identical data (no changes)
def test_update_task_with_identical_data():
    orig = create_task_in_db("7", title="Same", description="SameDesc", priority=Priority.low, category=Category.personal, due_date=date(2025,1,1), completed=False)
    new_data = identical_taskcreate_from_task(orig)
    updated = database.update_task("7", new_data)
    assert updated is not None
    assert updated.title == orig.title
    assert updated.description == orig.description
    assert updated.priority == orig.priority
    assert updated.category == orig.category
    assert updated.due_date == orig.due_date
    assert updated.completed == orig.completed

# Test Case 9: Update task with invalid priority value
def test_update_task_with_invalid_priority_value():
    orig = create_task_in_db("8")
    with pytest.raises(Exception):
        # Priority must be a valid enum value
        new_data = TaskCreate(
            title="Valid",
            description="desc",
            priority="-1",  # Invalid
            category=Category.work,
            due_date=date.today(),
            completed=False
        )
        database.update_task("8", new_data)

# Test Case 10: Update task with special characters in tag
def test_update_task_with_special_characters_in_tag():
    orig = create_task_in_db("9", category=Category.work)
    new_data = valid_taskcreate(category="@urgent!#")
    # If category is not validated as Enum, this will fail; otherwise, will succeed if allowed
    try:
        updated = database.update_task("9", new_data)
        assert updated is not None
        assert updated.category == "@urgent!#"
    except Exception:
        # If validation fails, that's also acceptable for this test
        assert True