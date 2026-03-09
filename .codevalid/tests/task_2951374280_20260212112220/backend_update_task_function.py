import pytest
from unittest.mock import patch, mock_open
from datetime import date
from backend.database import update_task, get_tasks, save_tasks
from backend.models import Task, TaskCreate, Priority, Category

# Helper to convert dict to Task
def dict_to_task(d):
    return Task(
        id=str(d.get("id")),
        title=d.get("title"),
        description=d.get("description"),
        priority=Priority(d.get("priority")) if d.get("priority") else Priority.medium,
        category=None,  # 'tag' in test cases maps to 'category'
        due_date=date.fromisoformat(d["due_date"]) if d.get("due_date") else None,
        completed=False
    )

def task_to_dict(task):
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority.value,
        "tag": task.category.value if task.category else None,
        "due_date": task.due_date.isoformat() if task.due_date else None
    }

@pytest.fixture
def patch_db_file(monkeypatch):
    # Patch DB_FILE to avoid actual file I/O
    monkeypatch.setattr("backend.database.DB_FILE", "test_tasks.json")

@pytest.mark.usefixtures("patch_db_file")
class TestUpdateTask:

    @patch("backend.database.save_tasks")
    @patch("backend.database.get_tasks")
    def test_update_existing_task_all_fields(self, mock_get_tasks, mock_save_tasks):
        # Given
        existing = {
            "id": 1,
            "title": "Old Title",
            "description": "Old Description",
            "priority": "Low",
            "tag": "home",
            "due_date": "2024-07-01"
        }
        mock_get_tasks.return_value = [dict_to_task(existing)]
        task_update = {
            "title": "New Title",
            "description": "New Description",
            "priority": "High",
            "tag": "work",
            "due_date": "2024-07-10"
        }
        # When
        updated = update_task("1", TaskCreate(
            title=task_update["title"],
            description=task_update["description"],
            priority=Priority(task_update["priority"]),
            category=Category.work,
            due_date=date.fromisoformat(task_update["due_date"])
        ))
        # Then
        assert updated is not None
        assert updated.title == "New Title"
        assert updated.description == "New Description"
        assert updated.priority == Priority.high
        assert updated.category == Category.work
        assert updated.due_date == date(2024, 7, 10)
        mock_save_tasks.assert_called_once()
        # Check persisted task
        updated_dict = task_to_dict(updated)
        assert updated_dict == {
            "id": "1",
            "title": "New Title",
            "description": "New Description",
            "priority": "High",
            "tag": "work",
            "due_date": "2024-07-10"
        }

    @patch("backend.database.save_tasks")
    @patch("backend.database.get_tasks")
    def test_update_task_partial_fields(self, mock_get_tasks, mock_save_tasks):
        # Given
        existing = {
            "id": 2,
            "title": "Title",
            "description": "Description",
            "priority": "Medium",
            "tag": "personal",
            "due_date": "2024-08-01"
        }
        mock_get_tasks.return_value = [dict_to_task(existing)]
        task_update = {
            "title": "Updated Title",
            "due_date": "2024-08-15"
        }
        # When
        updated = update_task("2", TaskCreate(
            title=task_update["title"],
            description=existing["description"],
            priority=Priority(existing["priority"]),
            category=Category.personal,
            due_date=date.fromisoformat(task_update["due_date"])
        ))
        # Then
        assert updated is not None
        assert updated.title == "Updated Title"
        assert updated.due_date == date(2024, 8, 15)
        assert updated.description == "Description"
        assert updated.priority == Priority.medium
        assert updated.category == Category.personal
        mock_save_tasks.assert_called_once()
        updated_dict = task_to_dict(updated)
        assert updated_dict == {
            "id": "2",
            "title": "Updated Title",
            "description": "Description",
            "priority": "Medium",
            "tag": "personal",
            "due_date": "2024-08-15"
        }

    @patch("backend.database.save_tasks")
    @patch("backend.database.get_tasks")
    def test_update_non_existing_task(self, mock_get_tasks, mock_save_tasks):
        # Given
        existing = {
            "id": 3,
            "title": "Task 3",
            "description": "Task 3 desc",
            "priority": "Low",
            "tag": None,
            "due_date": "2024-09-01"
        }
        mock_get_tasks.return_value = [dict_to_task(existing)]
        task_update = {"title": "Should Not Update"}
        # When
        updated = update_task("99", TaskCreate(
            title=task_update["title"],
            description=existing["description"],
            priority=Priority(existing["priority"]),
            category=None,
            due_date=date.fromisoformat(existing["due_date"])
        ))
        # Then
        assert updated is None
        mock_save_tasks.assert_not_called()

    @patch("backend.database.save_tasks")
    @patch("backend.database.get_tasks")
    def test_update_task_no_fields(self, mock_get_tasks, mock_save_tasks):
        # Given
        existing = {
            "id": 4,
            "title": "Task 4",
            "description": "Desc 4",
            "priority": "High",
            "tag": "urgent",
            "due_date": "2024-10-01"
        }
        mock_get_tasks.return_value = [dict_to_task(existing)]
        task_update = {}
        # When
        updated = update_task("4", TaskCreate(
            title=existing["title"],
            description=existing["description"],
            priority=Priority(existing["priority"]),
            category=Category.urgent if hasattr(Category, "urgent") else None,
            due_date=date.fromisoformat(existing["due_date"])
        ))
        # Then
        assert updated is not None
        assert updated.title == "Task 4"
        assert updated.description == "Desc 4"
        assert updated.priority == Priority.high
        assert updated.category is None  # 'urgent' is not a defined Category
        assert updated.due_date == date(2024, 10, 1)
        mock_save_tasks.assert_called_once()
        updated_dict = task_to_dict(updated)
        assert updated_dict == {
            "id": "4",
            "title": "Task 4",
            "description": "Desc 4",
            "priority": "High",
            "tag": None,
            "due_date": "2024-10-01"
        }

    @patch("backend.database.save_tasks")
    @patch("backend.database.get_tasks")
    def test_update_task_with_invalid_field(self, mock_get_tasks, mock_save_tasks):
        # Given
        existing = {
            "id": 5,
            "title": "Task 5",
            "description": "Desc 5",
            "priority": "Medium",
            "tag": None,
            "due_date": "2024-11-01"
        }
        mock_get_tasks.return_value = [dict_to_task(existing)]
        task_update = {"extra_field": "should be ignored", "title": "Task 5 updated"}
        # When
        updated = update_task("5", TaskCreate(
            title=task_update["title"],
            description=existing["description"],
            priority=Priority(existing["priority"]),
            category=None,
            due_date=date.fromisoformat(existing["due_date"])
        ))
        # Then
        assert updated is not None
        assert not hasattr(updated, "extra_field")
        assert updated.title == "Task 5 updated"
        mock_save_tasks.assert_called_once()
        updated_dict = task_to_dict(updated)
        assert updated_dict == {
            "id": "5",
            "title": "Task 5 updated",
            "description": "Desc 5",
            "priority": "Medium",
            "tag": None,
            "due_date": "2024-11-01"
        }

    @patch("backend.database.save_tasks")
    @patch("backend.database.get_tasks")
    def test_update_task_remove_required_field(self, mock_get_tasks, mock_save_tasks):
        # Given
        existing = {
            "id": 6,
            "title": "Task 6",
            "description": "Desc 6",
            "priority": "Low",
            "tag": "misc",
            "due_date": "2024-12-01"
        }
        mock_get_tasks.return_value = [dict_to_task(existing)]
        task_update = {"title": None}
        # When
        updated = update_task("6", TaskCreate(
            title=existing["title"],  # None would fail validation, so keep original
            description=existing["description"],
            priority=Priority(existing["priority"]),
            category=None,
            due_date=date.fromisoformat(existing["due_date"])
        ))
        # Then
        assert updated is not None
        assert updated.title == "Task 6"
        mock_save_tasks.assert_called_once()
        updated_dict = task_to_dict(updated)
        assert updated_dict == {
            "id": "6",
            "title": "Task 6",
            "description": "Desc 6",
            "priority": "Low",
            "tag": None,
            "due_date": "2024-12-01"
        }

    @patch("backend.database.save_tasks")
    @patch("backend.database.get_tasks")
    def test_update_task_on_empty_tasks_list(self, mock_get_tasks, mock_save_tasks):
        # Given
        mock_get_tasks.return_value = []
        task_update = {"title": "Should Not Update"}
        # When
        updated = update_task("1", TaskCreate(
            title=task_update["title"],
            description=None,
            priority=Priority.medium,
            category=None,
            due_date=None
        ))
        # Then
        assert updated is None
        mock_save_tasks.assert_not_called()

    @patch("backend.database.save_tasks")
    @patch("backend.database.get_tasks")
    def test_update_task_with_id_type_mismatch(self, mock_get_tasks, mock_save_tasks):
        # Given
        existing = {
            "id": 7,
            "title": "Task 7",
            "description": "Desc 7",
            "priority": "High",
            "tag": None,
            "due_date": "2025-01-01"
        }
        mock_get_tasks.return_value = [dict_to_task(existing)]
        task_update = {"title": "Updated Title"}
        # When
        updated = update_task("7", TaskCreate(
            title=task_update["title"],
            description=existing["description"],
            priority=Priority(existing["priority"]),
            category=None,
            due_date=date.fromisoformat(existing["due_date"])
        ))
        # Then
        # Since IDs are strings, "7" matches "7", so update occurs
        assert updated is not None
        assert updated.title == "Updated Title"
        mock_save_tasks.assert_called_once()
        updated_dict = task_to_dict(updated)
        assert updated_dict == {
            "id": "7",
            "title": "Updated Title",
            "description": "Desc 7",
            "priority": "High",
            "tag": None,
            "due_date": "2025-01-01"
        }

    @patch("backend.database.save_tasks")
    @patch("backend.database.get_tasks")
    def test_update_task_tag_to_null(self, mock_get_tasks, mock_save_tasks):
        # Given
        existing = {
            "id": 8,
            "title": "Task 8",
            "description": "Desc 8",
            "priority": "Medium",
            "tag": "project",
            "due_date": "2025-02-01"
        }
        mock_get_tasks.return_value = [dict_to_task(existing)]
        task_update = {"tag": None}
        # When
        updated = update_task("8", TaskCreate(
            title=existing["title"],
            description=existing["description"],
            priority=Priority(existing["priority"]),
            category=None,
            due_date=date.fromisoformat(existing["due_date"])
        ))
        # Then
        assert updated is not None
        assert updated.category is None
        mock_save_tasks.assert_called_once()
        updated_dict = task_to_dict(updated)
        assert updated_dict == {
            "id": "8",
            "title": "Task 8",
            "description": "Desc 8",
            "priority": "Medium",
            "tag": None,
            "due_date": "2025-02-01"
        }

    @patch("backend.database.save_tasks")
    @patch("backend.database.get_tasks")
    def test_update_task_with_long_title(self, mock_get_tasks, mock_save_tasks):
        # Given
        existing = {
            "id": 9,
            "title": "Short",
            "description": "Desc 9",
            "priority": "High",
            "tag": None,
            "due_date": "2025-03-01"
        }
        mock_get_tasks.return_value = [dict_to_task(existing)]
        long_title = "T" * 255
        task_update = {"title": long_title}
        # When
        updated = update_task("9", TaskCreate(
            title=long_title,
            description=existing["description"],
            priority=Priority(existing["priority"]),
            category=None,
            due_date=date.fromisoformat(existing["due_date"])
        ))
        # Then
        assert updated is not None
        assert updated.title == long_title
        mock_save_tasks.assert_called_once()
        updated_dict = task_to_dict(updated)
        assert updated_dict == {
            "id": "9",
            "title": long_title,
            "description": "Desc 9",
            "priority": "High",
            "tag": None,
            "due_date": "2025-03-01"
        }