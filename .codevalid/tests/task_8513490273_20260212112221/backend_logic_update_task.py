import pytest
from backend.database import update_task

# Helper functions to mock storage
class MockStorage:
    def __init__(self, tasks):
        self.tasks = tasks.copy()

    def load_tasks(self):
        return self.tasks.copy()

    def save_tasks(self, tasks):
        self.tasks = tasks.copy()

@pytest.fixture
def patch_storage(monkeypatch):
    def _patch(tasks):
        storage = MockStorage(tasks)
        monkeypatch.setattr("backend.database.load_tasks", storage.load_tasks)
        monkeypatch.setattr("backend.database.save_tasks", storage.save_tasks)
        return storage
    return _patch

def test_update_existing_task_with_all_fields(patch_storage):
    given = {
        'task_id': '123',
        'task_update': {
            'category': 'Personal',
            'completed': True,
            'description': 'New Description',
            'due_date': '2024-08-01',
            'priority': 3,
            'title': 'New Title'
        },
        'tasks': [{
            'category': 'Work',
            'completed': False,
            'description': 'Old Description',
            'due_date': '2024-07-01',
            'id': '123',
            'priority': 1,
            'title': 'Old Title'
        }]
    }
    storage = patch_storage(given['tasks'])
    updated_task = update_task(given['task_id'], given['task_update'])
    expected = {
        'category': 'Personal',
        'completed': True,
        'description': 'New Description',
        'due_date': '2024-08-01',
        'id': '123',
        'priority': 3,
        'title': 'New Title'
    }
    assert updated_task == expected
    assert storage.tasks == [expected]

def test_update_task_with_partial_fields(patch_storage):
    given = {
        'task_id': '124',
        'task_update': {
            'priority': 4,
            'title': 'Updated Title'
        },
        'tasks': [{
            'category': 'Home',
            'completed': False,
            'description': 'Task Description',
            'due_date': '2024-09-01',
            'id': '124',
            'priority': 2,
            'title': 'Task Title'
        }]
    }
    storage = patch_storage(given['tasks'])
    updated_task = update_task(given['task_id'], given['task_update'])
    expected = {
        'category': 'Home',
        'completed': False,
        'description': 'Task Description',
        'due_date': '2024-09-01',
        'id': '124',
        'priority': 4,
        'title': 'Updated Title'
    }
    assert updated_task == expected
    assert storage.tasks == [expected]

def test_update_nonexistent_task(patch_storage):
    given = {
        'task_id': '999',
        'task_update': {'title': 'Should Not Update'},
        'tasks': [{
            'category': 'Errand',
            'completed': False,
            'description': 'Desc',
            'due_date': '2024-07-15',
            'id': '125',
            'priority': 2,
            'title': 'Existing Task'
        }]
    }
    storage = patch_storage(given['tasks'])
    updated_task = update_task(given['task_id'], given['task_update'])
    expected = {
        'category': 'Errand',
        'completed': False,
        'description': 'Desc',
        'due_date': '2024-07-15',
        'id': '125',
        'priority': 2,
        'title': 'Existing Task'
    }
    assert updated_task is None
    assert storage.tasks == [expected]

def test_update_task_with_empty_update(patch_storage):
    given = {
        'task_id': '126',
        'task_update': {},
        'tasks': [{
            'category': 'Study',
            'completed': False,
            'description': 'Unchanged Desc',
            'due_date': '2024-10-01',
            'id': '126',
            'priority': 1,
            'title': 'Unchanged Task'
        }]
    }
    storage = patch_storage(given['tasks'])
    updated_task = update_task(given['task_id'], given['task_update'])
    expected = {
        'category': 'Study',
        'completed': False,
        'description': 'Unchanged Desc',
        'due_date': '2024-10-01',
        'id': '126',
        'priority': 1,
        'title': 'Unchanged Task'
    }
    assert updated_task == expected
    assert storage.tasks == [expected]

def test_update_task_with_invalid_priority(patch_storage):
    given = {
        'task_id': '127',
        'task_update': {'priority': -1},
        'tasks': [{
            'category': 'Work',
            'completed': False,
            'description': 'Desc',
            'due_date': '2024-07-20',
            'id': '127',
            'priority': 3,
            'title': 'Priority Check'
        }]
    }
    storage = patch_storage(given['tasks'])
    updated_task = update_task(given['task_id'], given['task_update'])
    expected = {
        'category': 'Work',
        'completed': False,
        'description': 'Desc',
        'due_date': '2024-07-20',
        'id': '127',
        'priority': -1,
        'title': 'Priority Check'
    }
    assert updated_task == expected
    assert storage.tasks == [expected]

def test_update_task_with_empty_title(patch_storage):
    given = {
        'task_id': '128',
        'task_update': {'title': ''},
        'tasks': [{
            'category': 'Home',
            'completed': False,
            'description': 'Desc',
            'due_date': '2024-08-10',
            'id': '128',
            'priority': 2,
            'title': 'Nonempty Title'
        }]
    }
    storage = patch_storage(given['tasks'])
    updated_task = update_task(given['task_id'], given['task_update'])
    expected = {
        'category': 'Home',
        'completed': False,
        'description': 'Desc',
        'due_date': '2024-08-10',
        'id': '128',
        'priority': 2,
        'title': ''
    }
    assert updated_task == expected
    assert storage.tasks == [expected]

def test_update_task_with_invalid_due_date_format(patch_storage):
    given = {
        'task_id': '129',
        'task_update': {'due_date': '10-09-2024'},
        'tasks': [{
            'category': 'Work',
            'completed': False,
            'description': 'Desc',
            'due_date': '2024-09-10',
            'id': '129',
            'priority': 2,
            'title': 'Date Format'
        }]
    }
    storage = patch_storage(given['tasks'])
    updated_task = update_task(given['task_id'], given['task_update'])
    expected = {
        'category': 'Work',
        'completed': False,
        'description': 'Desc',
        'due_date': '10-09-2024',
        'id': '129',
        'priority': 2,
        'title': 'Date Format'
    }
    assert updated_task == expected
    assert storage.tasks == [expected]

def test_update_task_with_long_title(patch_storage):
    long_title = 'T' * 255
    given = {
        'task_id': '130',
        'task_update': {'title': long_title},
        'tasks': [{
            'category': 'Errand',
            'completed': False,
            'description': 'Desc',
            'due_date': '2024-08-20',
            'id': '130',
            'priority': 1,
            'title': 'Short Title'
        }]
    }
    storage = patch_storage(given['tasks'])
    updated_task = update_task(given['task_id'], given['task_update'])
    expected = {
        'category': 'Errand',
        'completed': False,
        'description': 'Desc',
        'due_date': '2024-08-20',
        'id': '130',
        'priority': 1,
        'title': long_title
    }
    assert updated_task == expected
    assert storage.tasks == [expected]

def test_update_task_toggle_completed(patch_storage):
    given = {
        'task_id': '131',
        'task_update': {'completed': True},
        'tasks': [{
            'category': 'Work',
            'completed': False,
            'description': 'Project Desc',
            'due_date': '2024-07-05',
            'id': '131',
            'priority': 3,
            'title': 'Finish Project'
        }]
    }
    storage = patch_storage(given['tasks'])
    updated_task = update_task(given['task_id'], given['task_update'])
    expected = {
        'category': 'Work',
        'completed': True,
        'description': 'Project Desc',
        'due_date': '2024-07-05',
        'id': '131',
        'priority': 3,
        'title': 'Finish Project'
    }
    assert updated_task == expected
    assert storage.tasks == [expected]

def test_update_task_storage_empty(patch_storage):
    given = {
        'task_id': '200',
        'task_update': {'title': 'Any Title'},
        'tasks': []
    }
    storage = patch_storage(given['tasks'])
    updated_task = update_task(given['task_id'], given['task_update'])
    assert updated_task is None
    assert storage.tasks == []