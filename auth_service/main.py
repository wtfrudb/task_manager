from fastapi import FastAPI, HTTPException # type: ignore
from pydantic import BaseModel # type: ignore
from datetime import datetime

app = FastAPI(
    title="Auth Service",
    version="1.0.0"
)

# Простые модели
class UserCreate(BaseModel):
    email: str
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Простая база данных в памяти
users_db = []
current_id = 1

@app.get("/")
def root():
    return {
        "service": "Auth Service",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/register", response_model=UserResponse, status_code=201)
def register(user: UserCreate):
    global current_id
    
    # Проверяем уникальность email
    for existing_user in users_db:
        if existing_user["email"] == user.email:
            raise HTTPException(400, "Email already exists")
    
    # Создаем нового пользователя
    new_user = {
        "id": current_id,
        "email": user.email,
        "username": user.username,
        "created_at": datetime.now()
    }
    
    users_db.append(new_user)
    current_id += 1
    
    return new_user

@app.post("/login", response_model=Token)
def login(username: str, password: str):
    # Простая проверка (без OAuth2PasswordRequestForm для упрощения)
    user_found = None
    for user in users_db:
        if user["email"] == username or user["username"] == username:
            user_found = user
            break
    
    if not user_found:
        raise HTTPException(401, "Invalid credentials")
    
    # Возвращаем фейковый токен
    return {
        "access_token": "fake-jwt-token-for-testing",
        "token_type": "bearer"
    }

@app.get("/users", response_model=list[UserResponse])
def get_all_users():
    return users_db

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    for user in users_db:
        if user["id"] == user_id:
            return user
    raise HTTPException(404, "User not found")

if __name__ == "__main__":
    import uvicorn # type: ignore
    uvicorn.run(app, host="0.0.0.0", port=8000)