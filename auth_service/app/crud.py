from sqlalchemy.orm import Session # type: ignore
from passlib.context import CryptContext # type: ignore
from datetime import datetime
from typing import Optional
from . import models, schemas

class UserCRUD:
    def __init__(self, db: Session):
        self.db = db
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def _hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_user(self, user_data: schemas.UserCreate) -> models.User:
        # Проверяем существование пользователя
        existing_email = self.get_user_by_email(user_data.email)
        if existing_email:
            raise ValueError(f"Email {user_data.email} already registered")
        
        existing_username = self.get_user_by_username(user_data.username)
        if existing_username:
            raise ValueError(f"Username {user_data.username} already taken")
        
        # Создаем пользователя
        hashed_password = self._hash_password(user_data.password)
        db_user = models.User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def get_user_by_email(self, email: str) -> Optional[models.User]:
        return self.db.query(models.User).filter(models.User.email == email).first()
    
    def get_user_by_username(self, username: str) -> Optional[models.User]:
        return self.db.query(models.User).filter(models.User.username == username).first()
    
    def get_user_by_id(self, user_id: int) -> Optional[models.User]:
        return self.db.query(models.User).filter(models.User.id == user_id).first()
    
    def authenticate_user(self, email: str, password: str) -> Optional[models.User]:
        user = self.get_user_by_email(email)
        if not user:
            return None
        if not self._verify_password(password, user.hashed_password):
            return None
        return user