import os
import json
import uuid
import pytest
from datetime import date, datetime
from backend.database import add_task, get_tasks, save_tasks, update_task
from backend.models import Task, TaskCreate, Priority

DB_FILE = "tasks.json"

def setup_tasks(pre_existing_tasks):
    # Convert dicts to Task objects and save
    tasks = []
    for t in pre_existing_tasks:
        # Convert due_date to date object if string
        if 'due_date' in t and isinstance(t['due_date'], str):
            try:
                t['due_date'] = datetime.strptime(t['due_date'], "%Y-%m-%d").date()
            except Exception:
                t['due_date'] = None
        tasks.append(Task(**t))
    save_tasks(tasks)

def cleanup():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

@pytest.fixture(autouse=True)
def run_around_tests():
    cleanup()
    yield
    cleanup()

def task_persisted(task_id):
    tasks = get_tasks()
    return any(t.id == task_id for t in tasks)

def get_task_by_id(task_id):
    tasks = get_tasks()
    for t in tasks:
        if t.id == task_id:
            return t
    return None

# Test Case 1: add_valid_task_all_fields
def test_add_valid_task_all_fields():
    setup_tasks([])
    task_create = TaskCreate(
        title="Buy groceries",
        description="Milk, eggs, bread",
        priority=Priority.high,
        due_date=date(2024, 7, 1),
        category="personal"
    )
    new_task = add_task(task_create)
    assert new_task.title == "Buy groceries"
    assert new_task.description == "Milk, eggs, bread"
    assert new_task.priority == Priority.high
    assert new_task.due_date == date(2024, 7, 1)
    assert new_task.category == "personal"
    assert new_task.id is not None
    assert task_persisted(new_task.id)

# Test Case 2: add_valid_task_required_fields_only
def test_add_valid_task_required_fields_only():
    setup_tasks([])
    task_create = TaskCreate(
        title="Finish report",
        description="Complete the Q2 report",
        priority=Priority.medium,
        due_date=date(2024, 7, 10)
    )
    new_task = add_task(task_create)
    assert new_task.title == "Finish report"
    assert new_task.description == "Complete the Q2 report"
    assert new_task.priority == Priority.medium
    assert new_task.due_date == date(2024, 7, 10)
    assert new_task.category is None
    assert new_task.id is not None
    assert task_persisted(new_task.id)

# Test Case 3: add_task_missing_title
def test_add_task_missing_title():
    setup_tasks([])
    with pytest.raises(Exception):
        task_create = TaskCreate(
            description="No title provided",
            priority=Priority.low,
            due_date=date(2024, 7, 15)
        )
        add_task(task_create)
    assert not os.path.exists(DB_FILE) or len(get_tasks()) == 0

# Test Case 4: add_task_missing_description
def test_add_task_missing_description():
    setup_tasks([])
    with pytest.raises(Exception):
        task_create = TaskCreate(
            title="Call mom",
            priority=Priority.high,
            due_date=date(2024, 7, 5)
        )
        add_task(task_create)
    assert not os.path.exists(DB_FILE) or len(get_tasks()) == 0

# Test Case 5: add_task_missing_priority
def test_add_task_missing_priority():
    setup_tasks([])
    with pytest.raises(Exception):
        task_create = TaskCreate(
            title="Do laundry",
            description="Wash all clothes",
            due_date=date(2024, 7, 8)
        )
        add_task(task_create)
    assert not os.path.exists(DB_FILE) or len(get_tasks()) == 0

# Test Case 6: add_task_missing_due_date
def test_add_task_missing_due_date():
    setup_tasks([])
    with pytest.raises(Exception):
        task_create = TaskCreate(
            title="Pay bills",
            description="Electricity and water bill",
            priority=Priority.medium
        )
        add_task(task_create)
    assert not os.path.exists(DB_FILE) or len(get_tasks()) == 0

# Test Case 7: add_task_with_extra_field
def test_add_task_with_extra_field():
    setup_tasks([])
    with pytest.raises(TypeError):
        task_create = TaskCreate(
            title="Read book",
            description="Read '1984' by Orwell",
            priority=Priority.low,
            due_date=date(2024, 7, 18),
            category="leisure",
            extra="not allowed"
        )
        add_task(task_create)
    assert not os.path.exists(DB_FILE) or len(get_tasks()) == 0

# Test Case 8: add_duplicate_task_content
def test_add_duplicate_task_content():
    pre_existing = [{
        "id": "1",
        "title": "Walk the dog",
        "description": "Evening walk",
        "priority": Priority.high,
        "due_date": date(2024, 7, 20),
        "category": None
    }]
    setup_tasks(pre_existing)
    task_create = TaskCreate(
        title="Walk the dog",
        description="Evening walk",
        priority=Priority.high,
        due_date=date(2024, 7, 20)
    )
    new_task = add_task(task_create)
    assert new_task.id != "1"
    assert task_persisted(new_task.id)

# Test Case 9: add_task_to_empty_list
def test_add_task_to_empty_list():
    setup_tasks([])
    task_create = TaskCreate(
        title="Start project",
        description="Kickoff meeting",
        priority=Priority.high,
        due_date=date(2024, 7, 21)
    )
    new_task = add_task(task_create)
    assert new_task.title == "Start project"
    assert new_task.description == "Kickoff meeting"
    assert new_task.priority == Priority.high
    assert new_task.due_date == date(2024, 7, 21)
    assert new_task.category is None
    assert new_task.id is not None
    assert task_persisted(new_task.id)

# Test Case 10: add_task_title_max_length
def test_add_task_title_max_length():
    setup_tasks([])
    max_title = "T" * 255
    task_create = TaskCreate(
        title=max_title,
        description="Edge case for title length",
        priority=Priority.medium,
        due_date=date(2024, 7, 22)
    )
    new_task = add_task(task_create)
    assert new_task.title == max_title
    assert task_persisted(new_task.id)

# Test Case 11: add_task_title_exceeds_max_length
def test_add_task_title_exceeds_max_length():
    setup_tasks([])
    too_long_title = "T" * 256
    with pytest.raises(Exception):
        task_create = TaskCreate(
            title=too_long_title,
            description="Title too long",
            priority=Priority.high,
            due_date=date(2024, 7, 23)
        )
        add_task(task_create)
    assert not os.path.exists(DB_FILE) or len(get_tasks()) == 0

# Test Case 12: add_task_due_date_invalid_format
def test_add_task_due_date_invalid_format():
    setup_tasks([])
    with pytest.raises(Exception):
        task_create = TaskCreate(
            title="Invalid date",
            description="Test bad due date",
            priority=Priority.low,
            due_date="07/24/2024"
        )
        add_task(task_create)
    assert not os.path.exists(DB_FILE) or len(get_tasks()) == 0

# Test Case 13: add_task_priority_invalid_value
def test_add_task_priority_invalid_value():
    setup_tasks([])
    with pytest.raises(Exception):
        task_create = TaskCreate(
            title="Test priority",
            description="Invalid priority",
            priority="urgent",
            due_date=date(2024, 7, 25)
        )
        add_task(task_create)
    assert not os.path.exists(DB_FILE) or len(get_tasks()) == 0

# Test Case 14: edit_task_after_creation
def test_edit_task_after_creation():
    setup_tasks([])
    task_create = TaskCreate(
        title="Initial title",
        description="Initial desc",
        priority=Priority.low,
        due_date=date(2024, 7, 26)
    )
    new_task = add_task(task_create)
    assert task_persisted(new_task.id)
    # Edit task
    updated_create = TaskCreate(
        title="Initial title",
        description="Updated description",
        priority=Priority.low,
        due_date=date(2024, 7, 26)
    )
    updated_task = update_task(new_task.id, updated_create)
    assert updated_task is not None
    assert updated_task.description == "Updated description"
    assert task_persisted(new_task.id)

# Test Case 15: add_task_null_tag_field
def test_add_task_null_tag_field():
    setup_tasks([])
    task_create = TaskCreate(
        title="Null tag",
        description="Test null tag",
        priority=Priority.medium,
        due_date=date(2024, 7, 27),
        category=None
    )
    new_task = add_task(task_create)
    assert new_task.title == "Null tag"
    assert new_task.description == "Test null tag"
    assert new_task.priority == Priority.medium
    assert new_task.due_date == date(2024, 7, 27)
    assert new_task.category is None
    assert new_task.id is not None
    assert task_persisted(new_task.id)

# Test Case 16: add_task_all_fields_empty_strings
def test_add_task_all_fields_empty_strings():
    setup_tasks([])
    with pytest.raises(Exception):
        task_create = TaskCreate(
            title="",
            description="",
            priority="",
            due_date=""
        )
        add_task(task_create)
    assert not os.path.exists(DB_FILE) or len(get_tasks()) == 0