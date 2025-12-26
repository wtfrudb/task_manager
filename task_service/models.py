from sqlalchemy import Column, Integer, String, Boolean, Date # type: ignore
from database import Base

class TaskModel(Base):
    """Класс-сущность задачи для ORM SQLAlchemy (ООП представление таблицы)"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_completed = Column(Boolean, default=False)
    is_important = Column(Boolean, default=False)  # НОВОЕ ПОЛЕ: отметка важности
    due_date = Column(Date, nullable=True)         # Опциональный срок выполнения
    user_id = Column(Integer, nullable=False)      # ID пользователя из Auth Service