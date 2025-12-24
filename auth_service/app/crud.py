from sqlalchemy.orm import Session # type: ignore
from passlib.context import CryptContext # type: ignore
from . import models, schemas

# Класс, инкапсулирующий логику работы с пользователями
class UserCRUD:
    def __init__(self, db: Session):
        self.db = db
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def _hash_password(self, password: str) -> str:
        """Приватный метод для хеширования пароля (ООП: инкапсуляция)."""
        return self.pwd_context.hash(password)

    def create_user(self, user_data: schemas.UserCreate) -> models.User:
        """Создает нового пользователя в БД."""
        # Хешируем пароль перед сохранением
        hashed_password = self._hash_password(user_data.password)
        # Создаем объект-модель User (ООП)
        db_user = models.User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password
        )
        # Добавляем объект в сессию и сохраняем
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)  # Обновляем объект данными из БД (например, ID)
        return db_user

    def get_user_by_email(self, email: str) -> models.User | None:
        """Находит пользователя по email."""
        return self.db.query(models.User).filter(models.User.email == email).first()