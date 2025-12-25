import pika # type: ignore
import json
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

            # АСИНХРОННОЕ ВЗАИМОДЕЙСТВИЕ: Отправка уведомления в RabbitMQ
            try:
                # Подключаемся к брокеру (имя хоста совпадает с именем сервиса в docker-compose)
                connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
                channel = connection.channel()
                
                # Объявляем очередь (на случай, если она еще не создана)
                channel.queue_declare(queue='task_notifications')

                message = {
                    "task_id": task.id,
                    "user_id": user_id,
                    "title": task.title,
                    "status": "completed"
                }

                channel.basic_publish(
                    exchange='',
                    routing_key='task_notifications',
                    body=json.dumps(message)
                )
                connection.close()
                print(f" [AMQP] Сообщение о выполнении задачи {task.id} отправлено в очередь.")
            except Exception as e:
                # Печатаем ошибку в консоль, чтобы сервис не упал (требование стабильности)
                print(f" [AMQP] Ошибка отправки сообщения: {e}")

            return task
        return None