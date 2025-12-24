from pydantic import BaseModel # type: ignore
from typing import Optional

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None

class TaskCreate(TaskBase):
    pass  # Используется при создании (то, что присылает пользователь)

class TaskResponse(TaskBase):
    id: int
    is_completed: bool
    user_id: int

    class Config:
        from_attributes = True # Позволяет Pydantic работать с моделями SQLAlchemy