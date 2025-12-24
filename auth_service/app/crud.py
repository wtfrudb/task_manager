from sqlalchemy.orm import Session # type: ignore
from passlib.context import CryptContext # type: ignore
from . import models, schemas

class UserCRUD:
    """
    Класс для операций с пользователями в БД.
    Демонстрирует ООП: инкапсуляция бизнес-логики.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def create_user(self, user_data: schemas.UserCreate) -> models.User:
        """
        Создает нового пользователя в БД.
        Возвращает объект модели User.
        """
        # Проверяем уникальность email и username
        existing_email = self.get_user_by_email(user_data.email)
        if existing_email:
            raise ValueError(f"Email {user_data.email} уже зарегистрирован")
        
        existing_username = self.get_user_by_username(user_data.username)
        if existing_username:
            raise ValueError(f"Username {user_data.username} уже занят")
        
        # Хешируем пароль
        hashed_password = self.pwd_context.hash(user_data.password)
        
        # Создаем объект пользователя (ООП: инстанцирование класса)
        db_user = models.User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            is_active=True
        )
        
        # Сохраняем в БД
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def get_user_by_email(self, email: str):
        """Находит пользователя по email"""
        return self.db.query(models.User).filter(models.User.email == email).first()
    
    def get_user_by_username(self, username: str):
        """Находит пользователя по username"""
        return self.db.query(models.User).filter(models.User.username == username).first()
    
    def get_user_by_id(self, user_id: int):
        """Находит пользователя по ID"""
        return self.db.query(models.User).filter(models.User.id == user_id).first()
    
    def get_all_users(self, skip: int = 0, limit: int = 100):
        """Возвращает список всех пользователей"""
        return self.db.query(models.User).offset(skip).limit(limit).all()
    
    def authenticate_user(self, email: str, password: str):
        """Аутентифицирует пользователя по email и паролю"""
        user = self.get_user_by_email(email)
        if not user:
            return None
        if not self.pwd_context.verify(password, user.hashed_password):
            return None
        return user