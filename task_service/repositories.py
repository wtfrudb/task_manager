from sqlalchemy.orm import Session # type: ignore
from models import TaskModel

class BaseRepository:
    """Базовый класс для реализации принципа наследования"""
    def __init__(self, db: Session):
        self.db = db

class TaskRepository(BaseRepository):
    """Класс для управления задачами. Реализует инкапсуляцию запросов к БД."""
    
    def get_all_by_user(self, user_id: int):
        return self.db.query(TaskModel).filter(TaskModel.user_id == user_id).all()

    def create_task(self, title: str, description: str, user_id: int):
        new_task = TaskModel(
            title=title, 
            description=description, 
            user_id=user_id
        )
        self.db.add(new_task)
        self.db.commit()
        self.db.refresh(new_task)
        return new_task

    def delete_task(self, task_id: int, user_id: int):
        task = self.db.query(TaskModel).filter(TaskModel.id == task_id, TaskModel.user_id == user_id).first()
        if task:
            self.db.delete(task)
            self.db.commit()
            return True
        return False