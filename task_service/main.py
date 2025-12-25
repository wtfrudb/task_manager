from fastapi import FastAPI, Depends, HTTPException, status # type: ignore
from fastapi.security import OAuth2PasswordBearer # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from sqlalchemy.orm import Session # type: ignore
from jose import JWTError, jwt # type: ignore
import os

from database import get_db, engine
import models, schemas
from repositories import TaskRepository

# Создание таблиц при запуске
models.Base.metadata.create_all(bind=engine)

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key")
ALGORITHM = "HS256"

# Ссылка на сервис авторизации для получения токена в Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8001/login")

app = FastAPI(title="Task Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_current_user_id(token: str = Depends(oauth2_scheme)):
    try:
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

# --- ЭНДПОИНТЫ ---

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
        due_date=task_data.due_date,
        user_id=current_user_id
    )

@app.get("/tasks/", response_model=list[schemas.TaskResponse])
def get_my_tasks(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    repo = TaskRepository(db)
    return repo.get_all_by_user(current_user_id)

@app.patch("/tasks/{task_id}/complete", response_model=schemas.TaskResponse)
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    repo = TaskRepository(db)
    task = repo.mark_as_completed(task_id, current_user_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or access denied")
    return task

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