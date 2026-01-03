import requests
import sys

BASE_URL = "http://localhost:8000"

def test_api():
    print("Testing API...")
    
    # 1. Create Task
    task_data = {
        "title": "Test Task",
        "priority": "High",
        "category": "Work",
        "completed": False
    }
    res = requests.post(f"{BASE_URL}/tasks", json=task_data)
    if res.status_code != 200:
        print(f"Failed to create task: {res.text}")
        sys.exit(1)
    task = res.json()
    task_id = task['id']
    print(f"Created task: {task_id}")

    # 2. Get Tasks
    res = requests.get(f"{BASE_URL}/tasks")
    tasks = res.json()
    if len(tasks) == 0:
        print("No tasks found")
        sys.exit(1)
    print(f"Found {len(tasks)} tasks")

    # 3. Update Task
    update_data = task.copy()
    update_data['title'] = "Updated Task"
    res = requests.put(f"{BASE_URL}/tasks/{task_id}", json=update_data)
    if res.status_code != 200:
        print("Failed to update task")
        sys.exit(1)
    print("Updated task")

    # 4. Delete Task
    res = requests.delete(f"{BASE_URL}/tasks/{task_id}")
    if res.status_code != 200:
        print("Failed to delete task")
        sys.exit(1)
    print("Deleted task")

    print("API Verified Successfully!")

if __name__ == "__main__":
    try:
        test_api()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
