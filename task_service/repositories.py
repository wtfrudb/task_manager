from sqlalchemy.orm import Session # type: ignore
from models import TaskModel

class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_task(self, title: str, description: str, user_id: int, due_date=None):
        db_task = TaskModel(
            title=title, 
            description=description, 
            user_id=user_id,
            due_date=due_date
        )
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        return db_task

    def get_all_by_user(self, user_id: int):
        return self.db.query(TaskModel).filter(TaskModel.user_id == user_id).all()

    def delete_task(self, task_id: int, user_id: int):
        task = self.db.query(TaskModel).filter(
            TaskModel.id == task_id, 
            TaskModel.user_id == user_id
        ).first()
        if task:
            self.db.delete(task)
            self.db.commit()
            return True
        return False

    def mark_as_completed(self, task_id: int, user_id: int):
        task = self.db.query(TaskModel).filter(
            TaskModel.id == task_id, 
            TaskModel.user_id == user_id
        ).first()
        if task:
            task.is_completed = True
            self.db.commit()
            self.db.refresh(task)
            return task
        return None