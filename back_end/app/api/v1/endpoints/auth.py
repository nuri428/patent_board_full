from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
import jwt

from app.core.config import settings
from shared.database import get_db
from app.crud import get_user_crud
from app.schemas import UserCreate, User
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request
from app.crud.audit import get_audit_crud


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
    role: str = "analyst"
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            credentials.credentials, settings.SECRET_KEY, algorithms=["HS256"]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        return int(user_id)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )


@router.post("/login", response_model=Token)
async def login(request: Request, user: UserLogin, db: AsyncSession = Depends(get_db)):
    """사용자 로그인"""
    user_crud = get_user_crud(db)

    # Authenticate user
    db_user = await user_crud.authenticate(user.email, user.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(db_user.id)}, expires_delta=access_token_expires
    )

    # Audit Log
    audit_crud = get_audit_crud(db)
    await audit_crud.log(
        action="login",
        user_id=db_user.id,
        username=db_user.email,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        status="success",
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": int(access_token_expires.total_seconds()),
        "user": {
            "id": str(db_user.id),
            "email": db_user.email,
            "full_name": db_user.full_name,
            "role": db_user.role,
        },
    }


@router.post("/register", response_model=User)
async def register(
    request: Request, user: UserRegister, db: AsyncSession = Depends(get_db)
):
    """사용자 회원가입"""
    user_crud = get_user_crud(db)

    # Check if user already exists
    existing_user = await user_crud.get_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create new user
    db_user = await user_crud.create(
        UserCreate(
            email=user.email,
            password=user.password,
            full_name=user.full_name,
            username=user.email.split("@")[0],  # Use email prefix as username
        )
    )

    # Audit Log
    audit_crud = get_audit_crud(db)
    await audit_crud.log(
        action="register",
        user_id=db_user.id,
        username=db_user.email,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        status="success",
    )

    return db_user


@router.post("/logout")
async def logout():
    """사용자 로그아웃"""
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """현재 사용자 정보 조회"""
    user_crud = get_user_crud(db)
    user = await user_crud.get(current_user)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


@router.post("/refresh", response_model=Token)
async def refresh_token(request: dict, db: AsyncSession = Depends(get_db)):
    """토큰 리프레시"""
    refresh_token = request.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token required"
        )

    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    # Get user and generate new tokens
    user_crud = get_user_crud(db)
    user = await user_crud.get(int(user_id))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": int(access_token_expires.total_seconds()),
        "refresh_token": refresh_token,  # Return same refresh token
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "is_admin": user.is_admin,
        },
    }
