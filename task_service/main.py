from fastapi import FastAPI, Depends, HTTPException, status # type: ignore
from fastapi.security import OAuth2PasswordBearer # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore # Добавлено для Swagger
from sqlalchemy.orm import Session # type: ignore
from jose import JWTError, jwt # type: ignore
import os

from database import get_db, engine
import models, schemas
from repositories import TaskRepository

# СОЗДАНИЕ ТАБЛИЦ (Решает ошибку "relation tasks does not exist")
models.Base.metadata.create_all(bind=engine)

# Настройки безопасности (должны совпадать с Auth Service)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8001/login")

app = FastAPI(title="Task Service")

# НАСТРОЙКА CORS (Чтобы кнопка Authorize и запросы работали в браузере)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Функция проверки токена
def get_current_user_id(token: str = Depends(oauth2_scheme)):
    try:
        # Расшифровываем токен
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid token"
            )
        return int(user_id)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Could not validate credentials"
        )

# ЭНДПОИНТЫ

@app.post("/tasks/", response_model=schemas.TaskResponse)
def create_task(
    task_data: schemas.TaskCreate, 
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    repo = TaskRepository(db)
    return repo.create_task(
        title=task_data.title, 
        description=task_data.description, 
        user_id=current_user_id
    )

@app.get("/tasks/", response_model=list[schemas.TaskResponse])
def get_my_tasks(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    repo = TaskRepository(db)
    return repo.get_all_by_user(current_user_id)

@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    repo = TaskRepository(db)
    success = repo.delete_task(task_id, current_user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted"}