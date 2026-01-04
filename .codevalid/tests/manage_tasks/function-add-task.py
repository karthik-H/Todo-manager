import os
import json
import tempfile
import shutil
import pytest
from datetime import date, timedelta
from backend import database
from backend.models import Task, TaskCreate, Priority, Category

DB_FILE = database.DB_FILE

@pytest.fixture(autouse=True)
def isolate_tasks_json(tmp_path, monkeypatch):
    """Redirect tasks.json to a temp file for isolation."""
    temp_db = tmp_path / "tasks.json"
    monkeypatch.setattr(database, "DB_FILE", str(temp_db))
    yield
    # No cleanup needed, tmp_path is auto-removed

def write_tasks_json(data, db_path):
    with open(db_path, "w") as f:
        json.dump(data, f)

def read_tasks_json(db_path):
    with open(db_path, "r") as f:
        return json.load(f)

def make_task_create(**kwargs):
    # Provide defaults for all required fields
    base = {
        "title": "Test Task",
        "description": "Test Description",
        "priority": Priority.medium,
        "category": Category.work,
        "due_date": date.today() + timedelta(days=1),
        "completed": False,
    }
    base.update(kwargs)
    return TaskCreate(**base)

def test_add_task_with_all_valid_fields(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_FILE", str(tmp_path / "tasks.json"))
    task_create = make_task_create()
    result = database.add_task(task_create)
    assert result.title == task_create.title
    assert result.description == task_create.description
    assert result.priority == task_create.priority
    assert result.category == task_create.category
    assert result.due_date == task_create.due_date
    assert result.completed == task_create.completed
    assert result.id is not None
    # Check file written
    with open(tmp_path / "tasks.json") as f:
        tasks = json.load(f)
        assert any(t["id"] == result.id for t in tasks)

def test_add_task_missing_title(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_FILE", str(tmp_path / "tasks.json"))
    data = {
        "description": "desc",
        "priority": Priority.low,
        "category": Category.personal,
        "due_date": date.today(),
        "completed": False,
    }
    with pytest.raises(TypeError):
        TaskCreate(**data)

def test_add_task_missing_description(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_FILE", str(tmp_path / "tasks.json"))
    data = {
        "title": "No Desc",
        "priority": Priority.low,
        "category": Category.personal,
        "due_date": date.today(),
        "completed": False,
    }
    # description is Optional, so should succeed
    task_create = TaskCreate(**data)
    result = database.add_task(task_create)
    assert result.title == "No Desc"
    assert result.description is None

def test_add_task_missing_priority(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_FILE", str(tmp_path / "tasks.json"))
    data = {
        "title": "No Priority",
        "description": "desc",
        "category": Category.personal,
        "due_date": date.today(),
        "completed": False,
    }
    # priority is required, should raise TypeError
    with pytest.raises(TypeError):
        TaskCreate(**data)

def test_add_task_missing_due_date(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_FILE", str(tmp_path / "tasks.json"))
    data = {
        "title": "No Due",
        "description": "desc",
        "priority": Priority.low,
        "category": Category.personal,
        "completed": False,
    }
    # due_date is Optional, so should succeed
    task_create = TaskCreate(**data)
    result = database.add_task(task_create)
    assert result.due_date is None

def test_add_task_missing_tag(tmp_path, monkeypatch):
    # There is no 'tag' field in the model, so this test is not applicable.
    # We'll assert that TaskCreate does not accept a 'tag' argument.
    with pytest.raises(TypeError):
        TaskCreate(tag="urgent")

def test_add_task_empty_title(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_FILE", str(tmp_path / "tasks.json"))
    task_create = make_task_create(title="")
    result = database.add_task(task_create)
    # No explicit validation, so empty string is accepted
    assert result.title == ""

def test_add_task_long_title(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_FILE", str(tmp_path / "tasks.json"))
    long_title = "T" * 255
    task_create = make_task_create(title=long_title)
    result = database.add_task(task_create)
    assert result.title == long_title

def test_add_task_invalid_priority(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_FILE", str(tmp_path / "tasks.json"))
    # priority as -1 (invalid)
    with pytest.raises(ValueError):
        make_task_create(priority=-1)
    # priority as string not in enum
    with pytest.raises(ValueError):
        make_task_create(priority="high")

def test_add_task_past_due_date(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_FILE", str(tmp_path / "tasks.json"))
    past_date = date.today() - timedelta(days=1)
    task_create = make_task_create(due_date=past_date)
    result = database.add_task(task_create)
    assert result.due_date == past_date

def test_add_task_duplicate_title(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_FILE", str(tmp_path / "tasks.json"))
    title = "Duplicate"
    task_create1 = make_task_create(title=title)
    task_create2 = make_task_create(title=title)
    result1 = database.add_task(task_create1)
    result2 = database.add_task(task_create2)
    assert result1.title == result2.title
    assert result1.id != result2.id

def test_add_task_special_characters_tag(tmp_path, monkeypatch):
    # There is no 'tag' field in the model, so this test is not applicable.
    # We'll assert that TaskCreate does not accept a 'tag' argument.
    with pytest.raises(TypeError):
        TaskCreate(tag="@urgent!")

def test_add_task_tasks_json_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_FILE", str(tmp_path / "tasks.json"))
    # Ensure file does not exist
    if (tmp_path / "tasks.json").exists():
        os.remove(tmp_path / "tasks.json")
    task_create = make_task_create()
    result = database.add_task(task_create)
    assert result.title == task_create.title
    assert (tmp_path / "tasks.json").exists()

def test_add_task_tasks_json_corrupted(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_FILE", str(tmp_path / "tasks.json"))
    with open(tmp_path / "tasks.json", "w") as f:
        f.write("{not valid json}")
    task_create = make_task_create()
    # The implementation returns [] on JSONDecodeError, so it will just overwrite
    result = database.add_task(task_create)
    assert result.title == task_create.title

def test_add_task_minimal_valid_due_date(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_FILE", str(tmp_path / "tasks.json"))
    today = date.today()
    task_create = make_task_create(due_date=today)
    result = database.add_task(task_create)
    assert result.due_date == today

def test_add_task_maximal_valid_due_date(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_FILE", str(tmp_path / "tasks.json"))
    max_date = date(2099, 12, 31)
    task_create = make_task_create(due_date=max_date)
    result = database.add_task(task_create)
    assert result.due_date == max_date

def test_add_task_unicode_title(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_FILE", str(tmp_path / "tasks.json"))
    unicode_title = "任务"
    task_create = make_task_create(title=unicode_title)
    result = database.add_task(task_create)
    assert result.title == unicode_title

def test_add_task_empty_tasks_list(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_FILE", str(tmp_path / "tasks.json"))
    with open(tmp_path / "tasks.json", "w") as f:
        f.write("[]")
    task_create = make_task_create()
    result = database.add_task(task_create)
    assert result.title == task_create.title
    with open(tmp_path / "tasks.json") as f:
        tasks = json.load(f)
        assert any(t["id"] == result.id for t in tasks)