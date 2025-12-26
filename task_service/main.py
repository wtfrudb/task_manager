from fastapi import FastAPI, Depends, HTTPException, status, Request # type: ignore
from fastapi.responses import JSONResponse # type: ignore
from fastapi.security import OAuth2PasswordBearer # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from fastapi.exceptions import RequestValidationError # type: ignore
from sqlalchemy.orm import Session # type: ignore
from jose import JWTError, jwt # type: ignore
import os
import logging
from datetime import date
from typing import Optional

from database import get_db, engine
import models, schemas
from repositories import TaskRepository

# 1. Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("TaskService")

# 2. Создание таблиц при запуске
models.Base.metadata.create_all(bind=engine)

# 3. Инициализация приложения
app = FastAPI(title="Task Service API")

# 4. Настройки безопасности
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8001/login")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== ОБРАБОТЧИКИ ОШИБОК ==========

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Ошибка валидации данных: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Некорректный формат данных", "errors": exc.errors()},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.critical(f"Необработанное исключение: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": f"Внутренняя ошибка сервиса задач: {str(exc)}"},
    )

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

def get_current_user_id(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return int(user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

# --- ЭНДПОИНТЫ ---

@app.post("/tasks/", response_model=schemas.TaskResponse)
def create_task(
    task_data: schemas.TaskCreate, 
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    logger.info(f"Создание задачи для пользователя {current_user_id}")
    repo = TaskRepository(db)
    return repo.create_task(
        title=task_data.title, 
        description=task_data.description, 
        due_date=task_data.due_date,
        is_important=task_data.is_important,
        user_id=current_user_id
    )

@app.get("/tasks/", response_model=list[schemas.TaskResponse])
def get_my_tasks(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    repo = TaskRepository(db)
    return repo.get_all_by_user(current_user_id)

@app.get("/tasks/filter", response_model=list[schemas.TaskResponse])
def filter_tasks(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    no_deadline: bool = False,
    overdue: bool = False,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    ЭНДПОИНТ ФИЛЬТРАЦИИ:
    Позволяет искать задачи на сегодня, завтра, неделю, без дедлайна или просроченные.
    """
    repo = TaskRepository(db)
    return repo.get_filtered_tasks(
        user_id=current_user_id,
        start_date=start_date,
        end_date=end_date,
        no_deadline=no_deadline,
        overdue=overdue
    )

@app.patch("/tasks/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    repo = TaskRepository(db)
    update_data = task_update.dict(exclude_unset=True)
    task = repo.update_task(task_id, current_user_id, update_data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.patch("/tasks/{task_id}/complete", response_model=schemas.TaskResponse)
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    repo = TaskRepository(db)
    task = repo.mark_as_completed(task_id, current_user_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    repo = TaskRepository(db)
    if not repo.delete_task(task_id, current_user_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted"}

@app.on_event("startup")
async def startup_event():
    logger.info("--- Task Service успешно запущен на порту 8002 ---")