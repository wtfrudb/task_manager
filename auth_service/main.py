from fastapi import FastAPI, Depends, HTTPException, status # type: ignore
from sqlalchemy.orm import Session # type: ignore
from pydantic import BaseModel # type: ignore
from typing import List
from datetime import datetime
import logging

# Импортируем наши модули
from app.database import get_db, engine
from app.models import Base, User

# Создаем таблицы
Base.metadata.create_all(bind=engine)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Приложение
app = FastAPI(
    title="Auth Service with Database",
    version="1.0.0"
)

# Pydantic модели
class UserCreate(BaseModel):
    email: str
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Эндпоинты
@app.get("/")
def root():
    return {"message": "Auth Service с PostgreSQL работает!"}

@app.get("/health")
def health(db: Session = Depends(get_db)):
    # Проверяем подключение к БД
    try:
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/register", response_model=UserResponse, status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Проверяем существование пользователя
    existing_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email или username уже существуют"
        )
    
    # Создаем нового пользователя (пока без хеширования пароля)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=user.password,  # Позже захешируем
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    logger.info(f"Создан пользователь: {user.email}")
    
    return UserResponse.from_orm(db_user)

@app.get("/users", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

if __name__ == "__main__":
    import uvicorn # type: ignore
    uvicorn.run(app, host="0.0.0.0", port=8000)