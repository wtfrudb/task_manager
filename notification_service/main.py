import pika # type: ignore
import json
import time
import logging

# Настраиваем логирование (Требование Шага 3)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NotificationService")

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        # Имитируем отправку уведомления
        logger.info(f"!!! УВЕДОМЛЕНИЕ !!! Задача '{data['title']}' (ID: {data['task_id']}) "
                    f"пользователя {data['user_id']} помечена как ВЫПОЛНЕННАЯ.")
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")

def start_worker():
    # Цикл, чтобы сервис не падал, если RabbitMQ еще не загрузился
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
            channel = connection.channel()
            channel.queue_declare(queue='task_notifications')
            
            channel.basic_consume(queue='task_notifications', on_message_callback=callback, auto_ack=True)
            
            logger.info('Notification Service успешно запущен и ждет сообщений...')
            channel.start_consuming()
        except Exception as e:
            logger.warning(f"RabbitMQ недоступен, ждем 5 секунд... ({e})")
            time.sleep(5)

if __name__ == "__main__":
    start_worker()