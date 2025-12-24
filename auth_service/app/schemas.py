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

# ========== ДОБАВЛЕННЫЕ СХЕМЫ ДЛЯ JWT ==========

class Token(BaseModel):
    """Схема для JWT токена (ответ от /login)"""
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwidXNlcm5hbWUiOiJqb2huZG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c")
    token_type: str = Field(default="bearer", example="bearer")

class TokenData(BaseModel):
    """Данные, которые хранятся внутри JWT токена"""
    user_id: Optional[int] = None
    username: Optional[str] = None

class LoginRequest(BaseModel):
    """Схема для запроса на логин (альтернатива OAuth2PasswordRequestForm)"""
    username: str = Field(..., example="user@example.com")
    password: str = Field(..., example="password123")