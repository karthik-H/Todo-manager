import pytest
from fastapi.testclient import TestClient
from backend.main import app

import sys
import os
from unittest.mock import patch, MagicMock

client = TestClient(app)

# --- Test Case 1: Delete existing task successfully ---
def test_delete_existing_task_successfully():
    task_id = 123
    with patch("backend.main.database") as mock_db:
        mock_db.delete_task.return_value = True
        response = client.delete(f"/tasks/{task_id}")
        assert response.status_code == 200
        assert response.json() == {"message": "Task deleted successfully"}
        mock_db.delete_task.assert_called_once_with(task_id)

# --- Test Case 2: Delete non-existent task returns 404 ---
def test_delete_non_existent_task_returns_404():
    task_id = 99999
    with patch("backend.main.database") as mock_db:
        mock_db.delete_task.return_value = False
        response = client.delete(f"/tasks/{task_id}")
        assert response.status_code == 404
        # Accept either FastAPI default or custom error
        assert response.json() == {"detail": "Task not found"}

# --- Test Case 3: Delete task with invalid ID format ---
def test_delete_task_with_invalid_id_format():
    invalid_id = "invalid_id"
    response = client.delete(f"/tasks/{invalid_id}")
    # FastAPI returns 422 for path param validation error
    assert response.status_code in (400, 422)
    # Accept either FastAPI default or custom error
    assert "detail" in response.json()

# --- Test Case 4: Delete task with no ID provided ---
def test_delete_task_with_no_id_provided():
    response = client.delete("/tasks/")
    # FastAPI returns 404 for missing path param
    assert response.status_code in (404, 405)
    assert response.json().get("detail") in ("Not Found", "Method Not Allowed")

# --- Test Case 5: Delete task that was already deleted ---
def test_delete_task_that_was_already_deleted():
    task_id = 456
    with patch("backend.main.database") as mock_db:
        mock_db.delete_task.return_value = False
        response = client.delete(f"/tasks/{task_id}")
        assert response.status_code == 404
        assert response.json() == {"detail": "Task not found"}

# --- Test Case 6: Delete task with minimum valid ID ---
def test_delete_task_with_minimum_valid_id():
    task_id = 1
    with patch("backend.main.database") as mock_db:
        mock_db.delete_task.return_value = True
        response = client.delete(f"/tasks/{task_id}")
        assert response.status_code == 200
        assert response.json() == {"message": "Task deleted successfully"}
        mock_db.delete_task.assert_called_once_with(task_id)

# --- Test Case 7: Delete task with maximum valid ID ---
def test_delete_task_with_maximum_valid_id():
    task_id = 2147483647
    with patch("backend.main.database") as mock_db:
        mock_db.delete_task.return_value = True
        response = client.delete(f"/tasks/{task_id}")
        assert response.status_code == 200
        assert response.json() == {"message": "Task deleted successfully"}
        mock_db.delete_task.assert_called_once_with(task_id)

# --- Test Case 8: Delete task without authorization ---
def test_delete_task_without_authorization():
    # Simulate missing/invalid auth header
    # If your app uses a dependency for auth, patch it to raise an exception
    # Here, we simulate a 401 response by patching the dependency
    # If not implemented, this test will fail and should be updated when auth is added
    with patch("backend.main.get_current_user", side_effect=Exception("Unauthorized")):
        response = client.delete("/tasks/123")
        assert response.status_code in (401, 403)
        assert "detail" in response.json()

# --- Test Case 9: Delete task using wrong HTTP method ---
def test_delete_task_using_wrong_http_method():
    task_id = 123
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 405
    assert response.json().get("detail") == "Method Not Allowed"