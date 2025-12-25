from fastapi import FastAPI, Depends, HTTPException, status, Request # type: ignore
from fastapi.responses import JSONResponse # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from fastapi.security import OAuth2PasswordRequestForm # type: ignore
from fastapi.exceptions import RequestValidationError # type: ignore
from sqlalchemy.orm import Session # type: ignore
from datetime import timedelta
import logging
import os

# Импортируем наши модули
from app.database import get_db, engine
from app.models import Base
from app import schemas, crud, auth, dependencies

# Настройка логирования (Требование Шага 3)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AuthService")

# Создаем приложение
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

# Создаем таблицы в БД
Base.metadata.create_all(bind=engine)

# ========== ОБРАБОТЧИКИ ОШИБОК (Защита от 500-х ошибок) ==========

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Ловим ошибки валидации данных (неверный JSON и т.д.)"""
    logger.error(f"Ошибка валидации данных: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Переданы некорректные данные", "errors": exc.errors()},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Глобальный предохранитель: ловит все ошибки, предотвращая 500 Internal Server Error"""
    logger.critical(f"Критическая ошибка сервера: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Произошла внутренняя ошибка сервера, запрос не может быть выполнен."},
    )

# ========== ЭНДПОИНТЫ ==========

@app.get("/", tags=["Health Check"])
def read_root():
    logger.info("Health check вызван")
    return {"service": "Auth Service", "version": "1.0.0"}

@app.post("/register", response_model=schemas.UserResponse, tags=["Authentication"])
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Попытка регистрации пользователя: {user_data.username}")
    user_crud = crud.UserCRUD(db)
    try:
        new_user = user_crud.create_user(user_data)
        logger.info(f"Пользователь {user_data.username} успешно зарегистрирован")
        return new_user
    except ValueError as e:
        logger.warning(f"Ошибка регистрации {user_data.username}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/login", response_model=schemas.Token, tags=["Authentication"])
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    logger.info(f"Попытка входа пользователя: {form_data.username}")
    user_crud = crud.UserCRUD(db)
    
    user = user_crud.get_user_by_email(form_data.username) or \
           user_crud.get_user_by_username(form_data.username)
    
    if not user or not user_crud.authenticate_user(user.email, form_data.password):
        logger.warning(f"Неудачная попытка входа: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth.create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=timedelta(minutes=30)
    )
    logger.info(f"Пользователь {user.username} успешно вошел в систему")
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
    logger.info("--- Auth Service успешно запущен на порту 8001 ---")

if __name__ == "__main__":
    import uvicorn # type: ignore
    uvicorn.run(app, host="0.0.0.0", port=8001)