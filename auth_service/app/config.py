import os

class Settings:
    """Простая конфигурация без внешних зависимостей"""
    DATABASE_URL = os.getenv(
        "DATABASE_URL", 
        "postgresql://auth_user:auth_password@auth_db:5432/auth_db"
    )
    
    # JWT настройки (ИЗМЕНИТЕ ЭТО В PRODUCTION!)
    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "development-secret-key-change-this-in-production-12345"
    )
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

settings = Settings()