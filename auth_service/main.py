from fastapi import FastAPI, HTTPException, status # type: ignore
from pydantic import BaseModel # type: ignore
from datetime import datetime

app = FastAPI(title="Auth Service", version="1.0.0")

class UserCreate(BaseModel):
    email: str
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime

# Временное хранилище в памяти (для теста)
fake_db = {}
current_id = 1

@app.get("/")
def read_root():
    return {"message": "Auth Service is running!"}

@app.post("/register", response_model=UserResponse)
def register(user: UserCreate):
    global current_id
    if user.email in fake_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    new_user = {
        "id": current_id,
        "email": user.email,
        "username": user.username,
        "created_at": datetime.now()
    }
    fake_db[user.email] = new_user
    current_id += 1
    return new_user

@app.get("/users")
def list_users():
    return list(fake_db.values())