from pydantic import BaseModel, Field # type: ignore
from typing import Optional
from datetime import date

class TaskBase(BaseModel):
    """Базовая схема задачи"""
    # Здесь примеры для СОЗДАНИЯ (TaskCreate наследует это)
    title: str = Field(..., example="Новая задача")
    description: Optional[str] = Field(None, example="Описание")
    due_date: Optional[date] = Field(None, example="2025-12-26")
    is_important: bool = Field(default=False, example=False)

class TaskCreate(TaskBase):
    """Схема для создания задачи"""
    pass

class TaskUpdate(BaseModel):
    """Схема для РЕДАКТИРОВАНИЯ задачи (все поля необязательны)"""
    title: Optional[str] = Field(None, example="Новое название")
    description: Optional[str] = Field(None, example="Описание")
    due_date: Optional[date] = Field(None, example="2025-12-26")
    is_completed: Optional[bool] = Field(None, example=False)
    is_important: Optional[bool] = Field(None, example=False)

    class Config:
        # Теперь Swagger покажет ПОЛНЫЙ список полей в примере
            json_schema_extra = {
            "example": {
                "title": "Новое название",
                "description": "Описание",
                "due_date": "2025-12-26",
                "is_completed": False,
                "is_important": False
            }
        }

class TaskResponse(TaskBase):
    """Схема для ответа API"""
    id: int
    is_completed: bool
    user_id: int

    class Config:
        from_attributes = True