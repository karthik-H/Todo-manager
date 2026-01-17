import json
import os
from typing import List, Optional
from models import Task, TaskCreate
import uuid

DB_FILE = "tasks.json"

def get_tasks() -> List[Task]:
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r") as f:
        try:
            data = json.load(f)
            return [Task(**t) for t in data]
        except json.JSONDecodeError:
            return []

def save_tasks(tasks: List[Task]):
    with open(DB_FILE, "w") as f:
        # Convert date objects to isoformat string automatically via pydantic's model_dump/dict inside FastAPI usually, 
        # but here we are manually saving.
        # Pydantic v2 model_dump with mode='json' handles dates.
        json_data = [t.model_dump(mode='json') for t in tasks]
        json.dump(json_data, f, indent=4)

def add_task(task_create: TaskCreate) -> Task:
    tasks = get_tasks()
    new_task = Task(id=str(uuid.uuid4()), **task_create.model_dump())
    tasks.append(new_task)
    save_tasks(tasks)
    return new_task

def update_task(task_id: str, task_update: TaskCreate) -> Optional[Task]:
    tasks = get_tasks()
    for i, task in enumerate(tasks):
        if task.id == task_id:
            updated_task = Task(id=task_id, **task_update.model_dump())
            tasks[i] = updated_task
            return updated_task
    return None

def delete_task(task_id: str) -> bool:
    tasks = get_tasks()
    initial_len = len(tasks)
    tasks = [t for t in tasks if t.id != task_id]
    if len(tasks) < initial_len:
        save_tasks(tasks)
        return True
    return False

def get_task(task_id: str) -> Optional[Task]:
    tasks = get_tasks()
    for task in tasks:
        if task.id == task_id:
            return task
    return None
