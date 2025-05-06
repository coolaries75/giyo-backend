# auth_api.py - Updated with verified hash and debug logging
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from passlib.hash import bcrypt
from jose import jwt
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Verified in-memory user database (hash generated with bcrypt 3.2.0)
# Hash for "admin123": $2b$12$YOCEbLxW94Q5Y0Z8QQm0S.VNccXPiLPduNWr0Qt1M9ss2zkCTT2u2
users_db = {
    "admin@giyo.com": {
        "password": "$2b$12$YOCEbLxW94Q5Y0Z8QQm0S.VNccXPiLPduNWr0Qt1M9ss2zkCTT2u2",
        "role": "super_admin",
        "branch_id": None
    }
}

# JWT config
SECRET_KEY = "giyo-secret-key"  # In production, use env variable!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

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
        logger.info(f"Hash verification starting...")
        
        # Verify password with bcrypt 3.2.0
        if not bcrypt.verify(request.password, user["password"]):
            logger.error("Password verification failed")
            logger.info(f"Hash of provided password: {bcrypt.hash(request.password)}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create JWT token
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