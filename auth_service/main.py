from fastapi import FastAPI, Depends, HTTPException, status # type: ignore
from sqlalchemy.orm import Session # type: ignore
import logging
from datetime import datetime

# Импортируем наши модули
from app.database import get_db, engine
from app.models import Base
from app import schemas, crud

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создаем таблицы в БД
Base.metadata.create_all(bind=engine)
logger.info("Таблицы базы данных созданы")

# Создаем приложение FastAPI
app = FastAPI(
    title="Auth Service with PostgreSQL",
    description="Микросервис аутентификации с реальной базой данных PostgreSQL",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ========== ЭНДПОИНТЫ ==========

@app.get("/", tags=["Health Check"])
def read_root():
    """Корневой эндпоинт для проверки работы сервиса"""
    return {
        "service": "Auth Service",
        "status": "running",
        "database": "PostgreSQL",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", tags=["Health Check"])
def health_check(db: Session = Depends(get_db)):
    """Проверка здоровья сервиса и подключения к БД"""
    try:
        # Проверяем подключение к БД
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
        logger.error(f"Database connection error: {e}")
    
    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.now().isoformat(),
        "service": "auth"
    }

@app.post("/register", 
          response_model=schemas.UserResponse, 
          status_code=status.HTTP_201_CREATED,
          tags=["Authentication"])
def register(
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    """
    Регистрация нового пользователя.
    
    - **email**: Email пользователя (должен быть уникальным)
    - **username**: Имя пользователя (должно быть уникальным)
    - **password**: Пароль (минимум 8 символов)
    """
    logger.info(f"Попытка регистрации: {user_data.email}")
    
    user_crud = crud.UserCRUD(db)
    
    try:
        new_user = user_crud.create_user(user_data)
        logger.info(f"Пользователь создан: {new_user.email} (ID: {new_user.id})")
        
        return new_user
        
    except ValueError as e:
        logger.error(f"Ошибка регистрации: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error(f"Неожиданная ошибка при регистрации: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.get("/users", response_model=list[schemas.UserResponse], tags=["Users"])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Возвращает список всех пользователей"""
    user_crud = crud.UserCRUD(db)
    users = user_crud.get_all_users(skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=schemas.UserResponse, tags=["Users"])
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Возвращает пользователя по ID"""
    user_crud = crud.UserCRUD(db)
    user = user_crud.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    return user

# ========== ОБРАБОТКА ОШИБОК ==========

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP ошибка {exc.status_code}: {exc.detail}")
    return {
        "error": True,
        "status_code": exc.status_code,
        "detail": exc.detail,
        "timestamp": datetime.now().isoformat()
    }

# ========== СОБЫТИЯ ==========

@app.on_event("startup")
async def startup_event():
    logger.info("=" * 60)
    logger.info("Auth Service успешно запущен")
    logger.info("База данных: PostgreSQL")
    logger.info(f"Документация: http://localhost:8001/docs")
    logger.info("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Auth Service останавливается...")

# ========== ТЕСТОВЫЙ ЭНДПОИНТ ==========

@app.get("/test/db", tags=["Test"])
def test_database(db: Session = Depends(get_db)):
    """Тестовый эндпоинт для проверки работы БД"""
    try:
        # Пробуем выполнить простой запрос
        result = db.execute("SELECT version()").fetchone()
        db_version = result[0] if result else "unknown"
        
        # Пробуем получить количество пользователей
        from app.models import User
        user_count = db.query(User).count()
        
        return {
            "database": "PostgreSQL",
            "version": db_version,
            "users_count": user_count,
            "status": "working"
        }
        
    except Exception as e:
        logger.error(f"Database test failed: {e}")
        return {
            "database": "PostgreSQL",
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn # type: ignore
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")