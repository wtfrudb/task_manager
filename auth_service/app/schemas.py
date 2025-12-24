from pydantic import BaseModel, EmailStr, constr # type: ignore
from datetime import datetime
from typing import Optional

# Базовый класс для схем (ООП: наследование)
class UserBase(BaseModel):
    email: EmailStr
    username: str

# Класс для создания пользователя (ООП: наследование + расширение)
class UserCreate(UserBase):
    password: constr(min_length=8)  # type: ignore # Валидация: пароль не короче 8 символов

# Класс для ответа API (исключаем хеш пароля)
class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True  # Позволяет создавать схему из объекта SQLAlchemy

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"