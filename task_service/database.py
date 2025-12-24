import os
import time
from sqlalchemy import create_engine # type: ignore
from sqlalchemy.ext.declarative import declarative_base # type: ignore
from sqlalchemy.orm import sessionmaker # type: ignore
from sqlalchemy.exc import OperationalError # type: ignore

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://task_user:task_password@task_db:5432/task_db")

# Функция для создания движка с ожиданием готовности БД
def get_engine_with_retry(url, max_retries=5, delay=3):
    for i in range(max_retries):
        try:
            engine = create_engine(url)
            # Пробуем реально подключиться
            connection = engine.connect()
            connection.close()
            return engine
        except OperationalError:
            if i < max_retries - 1:
                print(f"Ожидание базы данных {url}... Попытка {i+1}")
                time.sleep(delay)
            else:
                raise

engine = get_engine_with_retry(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()