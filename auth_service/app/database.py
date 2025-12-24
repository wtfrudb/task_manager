from sqlalchemy import create_engine # type: ignore
from sqlalchemy.ext.declarative import declarative_base # type: ignore
from sqlalchemy.orm import sessionmaker # type: ignore
import os

# Получаем URL базы данных из переменных окружения
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://auth_user:auth_password@auth_db:5432/auth_db"
)

# Создаем движок SQLAlchemy
engine = create_engine(DATABASE_URL)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

# Зависимость для получения сессии БД
def get_db():
    """
    Генератор сессий БД для использования в зависимостях FastAPI.
    Гарантирует закрытие сессии после использования.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()