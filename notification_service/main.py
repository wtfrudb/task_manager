import pika # type: ignore
import json
import time
import logging

# Настройка красивого вывода логов
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("NotificationService")

def callback(ch, method, properties, body):
    try:
        # Декодируем сообщение из RabbitMQ
        data = json.loads(body)
        status = data.get("status", "unknown").lower()
        task_title = data.get("title", "Без названия")
        task_id = data.get("task_id", "?")
        user_id = data.get("user_id", "?")

        # Логика уведомлений в зависимости от статуса
        if status == "created":
            logger.info(f" [НОВАЯ ЗАДАЧА] Пользователь {user_id} создал задачу: '{task_title}' (ID: {task_id})")
        
        elif status == "completed":
            logger.info(f" [ВЫПОЛНЕНО] Задача '{task_title}' (ID: {task_id}) пользователя {user_id} успешно ЗАВЕРШЕНА.")
        
        elif status == "deleted":
            logger.info(f" [УДАЛЕНО] Задача '{task_title}' (ID: {task_id}) была УДАЛЕНА пользователем {user_id}.")
        
        else:
            logger.info(f" [УВЕДОМЛЕНИЕ] Задача '{task_title}': статус изменен на {status}")

    except Exception as e:
        logger.error(f" Ошибка обработки сообщения: {e}")

def start_worker():
    while True:
        try:
            # Подключение к RabbitMQ
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
            channel = connection.channel()
            
            # Объявляем ту же очередь, что и в Task Service
            channel.queue_declare(queue='task_notifications')
            
            # Подписываемся на сообщения
            channel.basic_consume(
                queue='task_notifications', 
                on_message_callback=callback, 
                auto_ack=True
            )
            
            logger.info('--- Notification Service запущен и ждет событий ---')
            channel.start_consuming()
            
        except Exception as e:
            logger.warning(" Соединение с RabbitMQ прервано. Повтор через 5 секунд...")
            time.sleep(5)

if __name__ == "__main__":
    start_worker()