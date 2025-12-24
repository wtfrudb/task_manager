from sqlalchemy import Column, Integer, String, Boolean # type: ignore
from database import Base

class TaskModel(Base):
    """Класс-сущность задачи для ORM SQLAlchemy"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    is_completed = Column(Boolean, default=False)
    user_id = Column(Integer)  # Сюда мы будем записывать ID пользователя из токена