from pydantic_settings import BaseSettings # type: ignore

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://auth_user:auth_password@auth_db:5432/auth_db"
    JWT_SECRET_KEY: str = "your-secret-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()