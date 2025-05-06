# auth_api.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from passlib.hash import bcrypt
from jose import jwt
from datetime import datetime, timedelta

# In-memory user database (temporary)
users_db = {
    "admin@giyo.com": {
        "password": "$2b$12$C6JhI0GIXYHzBk4iyw0/UeP8HHTPW.hMwvZo0uGE3geFMaGIs1pda",  # admin123
        "role": "super_admin",
        "branch_id": None
    }
}

# JWT config
SECRET_KEY = "giyo-secret-key"
ALGORITHM = "HS256"

router = APIRouter()

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
