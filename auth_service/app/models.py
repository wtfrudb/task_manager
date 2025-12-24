from sqlalchemy import Column, Integer, String, Boolean, DateTime # type: ignore
from sqlalchemy.ext.declarative import declarative_base # type: ignore
from datetime import datetime

Base = declarative_base()  # Базовый класс для всех моделей (ООП)

class User(Base):
    """Класс-модель, представляющий таблицу 'users' в БД."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)  # Пароль хранится в хешированном виде
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Метод для удобного отображения объекта (ООП: магический метод)
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
    