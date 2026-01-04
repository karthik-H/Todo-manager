import os
import json
import tempfile
import shutil
import pytest

from backend import database
from backend.models import Task, TaskCreate, Priority, Category

DB_FILE = database.DB_FILE

def setup_module(module):
    # Backup the original DB file if it exists
    if os.path.exists(DB_FILE):
        shutil.copy(DB_FILE, DB_FILE + ".bak")

def teardown_module(module):
    # Restore the original DB file if it was backed up
    if os.path.exists(DB_FILE + ".bak"):
        shutil.move(DB_FILE + ".bak", DB_FILE)
    elif os.path.exists(DB_FILE):
        os.remove(DB_FILE)

def write_tasks(tasks):
    # Helper to write raw tasks to the DB file
    with open(DB_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

def read_tasks():
    # Helper to read tasks from the DB file
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r") as f:
        return json.load(f)

def make_task(id, **kwargs):
    # Helper to create a dict representing a Task
    base = {
        "id": str(id),
        "title": f"Task {id}",
        "description": None,
        "priority": "Medium",
        "category": None,
        "due_date": None,
        "completed": False
    }
    base.update(kwargs)
    return base

@pytest.fixture(autouse=True)
def cleanup_db():
    # Clean DB file before each test
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    yield
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

def test_delete_existing_task_by_valid_id():
    # Given
    tasks = [make_task(1), make_task(2), make_task(3)]
    write_tasks(tasks)
    # When
    result = database.delete_task("2")
    # Then
    assert result is True
    stored = read_tasks()
    ids = [t["id"] for t in stored]
    assert ids == ["1", "3"]

def test_attempt_to_delete_non_existent_task():
    # Given
    tasks = [make_task(1), make_task(2), make_task(3)]
    write_tasks(tasks)
    # When
    result = database.delete_task("99")
    # Then
    assert result is False
    stored = read_tasks()
    ids = [t["id"] for t in stored]
    assert ids == ["1", "2", "3"]

def test_attempt_to_delete_from_empty_storage():
    # Given
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    # When
    result = database.delete_task("1")
    # Then
    assert result is False
    stored = read_tasks()
    assert stored == []

def test_delete_when_multiple_tasks_have_the_same_id():
    # Given
    tasks = [make_task(1), make_task(2), make_task(2), make_task(3)]
    write_tasks(tasks)
    # When
    result = database.delete_task("2")
    # Then
    assert result is True
    stored = read_tasks()
    ids = [t["id"] for t in stored]
    assert ids == ["1", "3"]

def test_delete_with_id_as_string_type():
    # Given
    tasks = [make_task(1), make_task(2), make_task(3)]
    write_tasks(tasks)
    # When
    result = database.delete_task('2')  # Should succeed, since IDs are stored as strings
    # Then
    assert result is True
    stored = read_tasks()
    ids = [t["id"] for t in stored]
    assert ids == ["1", "3"]

def test_delete_with_id_as_null():
    # Given
    tasks = [make_task(1), make_task(2), make_task(3)]
    write_tasks(tasks)
    # When
    result = database.delete_task(None)
    # Then
    assert result is False
    stored = read_tasks()
    ids = [t["id"] for t in stored]
    assert ids == ["1", "2", "3"]

def test_delete_with_negative_id():
    # Given
    tasks = [make_task(1), make_task(2), make_task(3)]
    write_tasks(tasks)
    # When
    result = database.delete_task("-1")
    # Then
    assert result is False
    stored = read_tasks()
    ids = [t["id"] for t in stored]
    assert ids == ["1", "2", "3"]

def test_delete_with_id_zero():
    # Given
    tasks = [make_task(0), make_task(1), make_task(2)]
    write_tasks(tasks)
    # When
    result = database.delete_task("0")
    # Then
    assert result is True
    stored = read_tasks()
    ids = [t["id"] for t in stored]
    assert ids == ["1", "2"]

def test_storage_is_not_a_list():
    # Given: storage is None
    with open(DB_FILE, "w") as f:
        f.write("null")
    # When/Then
    with pytest.raises(Exception):
        database.delete_task("1")
    # Given: storage is a dict
    with open(DB_FILE, "w") as f:
        json.dump({"id": "1"}, f)
    with pytest.raises(Exception):
        database.delete_task("1")

def test_delete_with_id_as_float():
    # Given
    tasks = [make_task(1), make_task(2), make_task(3)]
    write_tasks(tasks)
    # When
    result = database.delete_task(2.0)
    # Then
    assert result is False
    stored = read_tasks()
    ids = [t["id"] for t in stored]
    assert ids == ["1", "2", "3"]

def test_delete_with_a_very_large_integer_id():
    # Given
    tasks = [make_task(1), make_task(2), make_task(3)]
    write_tasks(tasks)
    # When
    result = database.delete_task(str(999999999))
    # Then
    assert result is False
    stored = read_tasks()
    ids = [t["id"] for t in stored]
    assert ids == ["1", "2", "3"]

def test_delete_with_id_as_special_characters():
    # Given
    tasks = [make_task(1), make_task(2), make_task(3)]
    write_tasks(tasks)
    # When
    result = database.delete_task("@!#")
    # Then
    assert result is False
    stored = read_tasks()
    ids = [t["id"] for t in stored]
    assert ids == ["1", "2", "3"]