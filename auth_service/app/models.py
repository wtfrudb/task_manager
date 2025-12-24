from sqlalchemy import Column, Integer, String, Boolean, DateTime # type: ignore
from .database import Base
from datetime import datetime

class User(Base):
    """
    Модель пользователя - представляет таблицу 'users' в БД.
    Класс демонстрирует принципы ООП: инкапсуляция, наследование.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        """Строковое представление объекта (магический метод)"""
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"
    
    def to_dict(self):
        """Преобразование объекта в словарь (инкапсуляция логики)"""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }