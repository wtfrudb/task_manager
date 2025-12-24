from pydantic import BaseModel, EmailStr, Field # type: ignore
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    """Базовый класс для схем пользователя (ООП: наследование)"""
    email: EmailStr = Field(..., example="user@example.com")
    username: str = Field(..., example="johndoe", min_length=3, max_length=50)

class UserCreate(UserBase):
    """Схема для создания пользователя"""
    password: str = Field(..., example="password123", min_length=8)

class UserResponse(UserBase):
    """Схема для ответа API (исключает пароль)"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Позволяет создавать из объектов SQLAlchemy