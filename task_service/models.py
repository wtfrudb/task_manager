from sqlalchemy import Column, Integer, String, Boolean, Date # type: ignore
from database import Base

class TaskModel(Base):
    """Класс-сущность задачи для ORM SQLAlchemy"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    is_completed = Column(Boolean, default=False)
    due_date = Column(Date, nullable=True)  # Опциональный срок выполнения
    user_id = Column(Integer)  # ID пользователя из Auth Service