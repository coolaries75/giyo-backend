# auth_api.py - Clean downgraded bcrypt version (no passlib)
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from jose import jwt
from datetime import datetime, timedelta
import logging
import bcrypt  # low-level only

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Verified in-memory user database
users_db = {
    "admin@giyo.com": {
        "password": "$2b$12$tmFv9vaxhRFDr4DuoonNqeHUaxAPdNENszAutXUBC3YV.XvU.e2TW",  # admin123
        "role": "super_admin",
        "branch_id": None
    }
}

# JWT config
SECRET_KEY = "giyo-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

router = APIRouter(tags=["Authentication"])

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/api/auth/login")
async def login(request: LoginRequest):
    try:
        logger.info(f"Login attempt for: {request.email}")
        logger.info(f"Provided password length: {len(request.password)} chars")

        user = users_db.get(request.email)
        if not user:
            logger.error("User not found in database")
            raise HTTPException(status_code=401, detail="Invalid credentials")

        logger.info(f"Stored hash: {user['password']}")
        logger.info("Hash verification starting...")

        # Final: bcrypt.checkpw with encoded values only
        if not bcrypt.checkpw(request.password.encode(), user["password"].encode()):
            logger.error("Password verification failed")
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token_data = {
            "sub": request.email,
            "role": user["role"],
            "branch_id": user["branch_id"],
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

        logger.info("Login successful")
        return {"access_token": token, "token_type": "bearer"}

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
