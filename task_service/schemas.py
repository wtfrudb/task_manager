from pydantic import BaseModel # type: ignore
from typing import Optional
from datetime import date

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None # Формат в JSON: "YYYY-MM-DD"

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: int
    is_completed: bool
    user_id: int

    class Config:
        from_attributes = True