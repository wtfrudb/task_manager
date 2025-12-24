from fastapi import FastAPI, Depends, HTTPException, status # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from fastapi.security import OAuth2PasswordRequestForm # type: ignore
from sqlalchemy.orm import Session # type: ignore
from datetime import timedelta, datetime
import logging
import os

# Импортируем наши модули
from app.database import get_db, engine
from app.models import Base
from app import schemas, crud, auth, dependencies

# Создаем приложение ОДИН РАЗ
app = FastAPI(
    title="Auth Service with JWT Authentication",
    description="Микросервис аутентификации",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создаем таблицы в БД
Base.metadata.create_all(bind=engine)

# ========== ЭНДПОИНТЫ ==========

@app.get("/", tags=["Health Check"])
def read_root():
    return {"service": "Auth Service", "version": "1.0.0"}

@app.post("/register", response_model=schemas.UserResponse, tags=["Authentication"])
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    user_crud = crud.UserCRUD(db)
    try:
        return user_crud.create_user(user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ИСПРАВЛЕННЫЙ ЛОГИН (теперь имя схемы совпадает с тем, что в твоем schemas.py)
@app.post("/login", response_model=schemas.Token, tags=["Authentication"])
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), # Это «подружит» код с окном Swagger
    db: Session = Depends(get_db)
):
    """
    Вход в систему. Теперь работает через кнопку Authorize в Swagger.
    """
    user_crud = crud.UserCRUD(db)
    
    # OAuth2PasswordRequestForm всегда называет поле 'username', 
    # даже если пользователь вводит туда свой email.
    user = user_crud.get_user_by_email(form_data.username) or \
           user_crud.get_user_by_username(form_data.username)
    
    if not user or not user_crud.authenticate_user(user.email, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth.create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.UserResponse, tags=["Users"])
def read_users_me(current_user: schemas.UserResponse = Depends(dependencies.get_current_user)):
    return current_user

@app.get("/users", response_model=list[schemas.UserResponse], tags=["Users"])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    user_crud = crud.UserCRUD(db)
    return user_crud.get_all_users(skip=skip, limit=limit)

@app.on_event("startup")
async def startup_event():
    logger.info("Auth Service запущен на порту 8001")

if __name__ == "__main__":
    import uvicorn # type: ignore
    uvicorn.run(app, host="0.0.0.0", port=8001)