import pika # type: ignore
import json
from sqlalchemy.orm import Session # type: ignore
from sqlalchemy import and_ # type: ignore
from datetime import date
from models import TaskModel

class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def _send_notification(self, task_id: int, user_id: int, title: str, status: str):
        """Вспомогательный метод для отправки сообщений в RabbitMQ"""
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
            channel = connection.channel()
            channel.queue_declare(queue='task_notifications')

            message = {
                "task_id": task_id,
                "user_id": user_id,
                "title": title,
                "status": status
            }

            channel.basic_publish(
                exchange='',
                routing_key='task_notifications',
                body=json.dumps(message)
            )
            connection.close()
            print(f" [AMQP] Событие '{status}' для задачи {task_id} отправлено.")
        except Exception as e:
            print(f" [AMQP] Ошибка отправки: {e}")

    def create_task(self, title: str, description: str, user_id: int, due_date=None, is_important: bool = False):
        """Создание задачи с учетом флага важности"""
        db_task = TaskModel(
            title=title, 
            description=description, 
            user_id=user_id,
            due_date=due_date,
            is_important=is_important
        )
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        
        self._send_notification(db_task.id, user_id, title, "created")
        return db_task

    def update_task(self, task_id: int, user_id: int, update_data: dict):
        """Универсальный метод обновления задачи"""
        task = self.db.query(TaskModel).filter(
            TaskModel.id == task_id, 
            TaskModel.user_id == user_id
        ).first()
        
        if task:
            for key, value in update_data.items():
                if value is not None:
                    setattr(task, key, value)
            
            self.db.commit()
            self.db.refresh(task)
            self._send_notification(task.id, user_id, task.title, "updated")
            return task
        return None

    def get_all_by_user(self, user_id: int):
        """Получение всех задач с сортировкой"""
        return self.db.query(TaskModel).filter(
            TaskModel.user_id == user_id
        ).order_by(TaskModel.is_important.desc(), TaskModel.due_date.asc()).all()

    def get_filtered_tasks(self, user_id: int, start_date: date = None, end_date: date = None, no_deadline: bool = False, overdue: bool = False):
        """Строгая фильтрация по категориям"""
        query = self.db.query(TaskModel).filter(TaskModel.user_id == user_id)

        # 1. Фильтр просроченных: дата < сегодня и задача не выполнена
        if overdue is True:
            today = date.today()
            query = query.filter(and_(TaskModel.due_date < today, TaskModel.is_completed == False))
        
        # 2. Фильтр задач без даты
        elif no_deadline is True:
            query = query.filter(TaskModel.due_date == None)
        
        # 3. Фильтр по диапазону дат
        elif start_date and end_date:
            query = query.filter(and_(TaskModel.due_date >= start_date, TaskModel.due_date <= end_date))
        
        # 4. Фильтр на конкретный день
        elif start_date:
            query = query.filter(TaskModel.due_date == start_date)

        # Возвращаем результат с сортировкой: Важные -> Ближайшие по дате
        return query.order_by(TaskModel.is_important.desc(), TaskModel.due_date.asc()).all()

    def delete_task(self, task_id: int, user_id: int):
        task = self.db.query(TaskModel).filter(
            TaskModel.id == task_id, 
            TaskModel.user_id == user_id
        ).first()
        
        if task:
            task_title = task.title 
            self.db.delete(task)
            self.db.commit()
            self._send_notification(task_id, user_id, task_title, "deleted")
            return True
        return False

    def mark_as_completed(self, task_id: int, user_id: int):
        return self.update_task(task_id, user_id, {"is_completed": True})