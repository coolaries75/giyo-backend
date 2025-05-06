from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from passlib.hash import bcrypt
from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "giyo-secret-key"
ALGORITHM = "HS256"

router = APIRouter()

# Temporary in-memory user (replace with DB in future)
users_db = {
    "admin@giyo.com": {
        "password": "$2b$12$u1yG58/FZrGbG/pP5r8nXeAiJ9tH3NUoxOZ3sO0WFejK8/E.XmT8K",  # password: admin123
        "role": "super_admin",
        "branch_id": None
    }
}

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/api/auth/login")
def login(request: LoginRequest):
    user = users_db.get(request.email)
    if not user or not bcrypt.verify(request.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = jwt.encode({
        "sub": request.email,
        "role": user["role"],
        "branch_id": user["branch_id"],
        "exp": datetime.utcnow() + timedelta(hours=24)
    }, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": token}
