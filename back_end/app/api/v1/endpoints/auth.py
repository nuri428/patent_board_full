from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
import jwt

from app.core.config import settings


router = APIRouter()

security = HTTPBearer()

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

async def get_current_user(token: str = Depends(security)):
    credentials = HTTPAuthorizationCredentials(scheme="bearer")
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.SECRET_KEY, 
            algorithms=["HS256"]
        )
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials"
            )
        return email
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )

@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    """사용자 로그인"""
    if user.email == "admin@patent-board.com" and user.password == "admin123":
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, 
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": access_token_expires.total_seconds(),
            "user": {
                "id": "admin",
                "email": user.email,
                "full_name": "Admin User"
            }
        }
    else:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )

@router.post("/register", response_model=UserResponse)
async def register(user: UserRegister):
    """사용자 회원가입"""
    user_id = f"user_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    created_at = datetime.utcnow()
    
    return {
        "id": user_id,
        "email": user.email,
        "full_name": user.full_name,
        "created_at": created_at
    }

@router.post("/logout")
async def logout():
    """사용자 로그아웃"""
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=dict)
async def get_current_user_info(current_user: str = Depends(get_current_user)):
    """현재 사용자 정보 조회"""
    return {
        "user_id": current_user,
        "email": current_user,
        "is_authenticated": True
    }