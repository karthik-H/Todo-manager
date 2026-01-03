from pydantic import BaseModel
from typing import Optional
from datetime import date
from enum import Enum

class Priority(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"

class Category(str, Enum):
    work = "Work"
    personal = "Personal"
    study = "Study"

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Priority = Priority.medium
    category: Optional[Category] = None
    due_date: Optional[date] = None
    completed: bool = False

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: str
