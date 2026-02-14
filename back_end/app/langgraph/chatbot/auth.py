"""
Authentication utilities for LangGraph Chatbot API
"""

from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import cast
import logging

logger = logging.getLogger(__name__)

# Simple Bearer token authentication
security = HTTPBearer()

# Demo tokens for testing (in production, use proper JWT validation)
DEMO_TOKENS = {
    "demo_token": {"user_id": "demo_user", "permissions": ["read", "write", "full_access"]},
    "limited_token": {"user_id": "limited_user", "permissions": ["read", "basic_chat"]},
}


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get current user from token
    For demo purposes, accepts predefined tokens
    In production, implement proper JWT validation
    """
    try:
        token = credentials.credentials
        
        if token not in DEMO_TOKENS:
            logger.warning(f"Invalid token: {token}")
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_info = DEMO_TOKENS[token]
        return {
            "user_id": user_info["user_id"],
            "permissions": user_info["permissions"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_permission(permission: str):
    """
    Dependency to check if user has specific permission
    """
    async def permission_checker(user: dict[str, object] = Depends(get_current_user)):
        permissions = cast(list[str], user.get("permissions", []))
        if permission not in permissions:
            logger.warning(f"Permission denied: {permission} for user {user.get('user_id')}")
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required: {permission}"
            )
        return user
    return permission_checker


async def optional_auth(request: Request):
    """
    Optional authentication - returns user if authenticated, None otherwise
    """
    try:
        credentials = await security(request)
        if credentials is None:
            return None
        return await get_current_user(credentials)
    except Exception:
        return None


async def is_authenticated(request: Request):
    """
    Check if request has valid authentication
    """
    try:
        credentials = await security(request)
        if credentials is None:
            return False
        await get_current_user(credentials)
        return True
    except Exception:
        return False
