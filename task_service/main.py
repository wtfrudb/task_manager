from fastapi import FastAPI, Depends, HTTPException, status # type: ignore
from fastapi.security import OAuth2PasswordBearer # type: ignore
from jose import JWTError, jwt # type: ignore
from sqlalchemy.orm import Session # type: ignore
import os

from database import get_db, engine
import models, schemas
from repositories import TaskRepository

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Service")

# Настройки безопасности
SECRET_KEY = os.getenv("JWT_SECRET", "super-secret-key")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8001/login")

def get_current_user_id(token: str = Depends(oauth2_scheme)):
    """Функция проверки токена (Требование безопасности)"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return int(user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

@app.post("/tasks/", response_model=schemas.TaskResponse)
def create_task(
    task_data: schemas.TaskCreate, 
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id) # Теперь ID берется из токена!
):
    repo = TaskRepository(db)
    return repo.create_task(
        title=task_data.title, 
        description=task_data.description, 
        user_id=current_user_id
    )