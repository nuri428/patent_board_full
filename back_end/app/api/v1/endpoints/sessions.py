from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import logging

from app.api.deps import get_current_user
from app.models import User
from app.db.redis_client import get_redis

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class SessionCreate(BaseModel):
    title: str
    user_id: int
    metadata: Optional[Dict[str, Any]] = None


class SessionUpdate(BaseModel):
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    messages: Optional[List[Dict[str, Any]]] = None


class SessionResponse(BaseModel):
    session_id: str
    title: str
    user_id: int
    messages: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime


class SessionListResponse(BaseModel):
    sessions: List[str]
    count: int


class LockResponse(BaseModel):
    lock_acquired: bool
    message: Optional[str] = None


class SuccessResponse(BaseModel):
    message: str


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    current_user: User = Depends(get_current_user),
    redis_client=Depends(get_redis),
):
    """Create a new chat session in Redis"""
    session_id = str(uuid.uuid4())

    # Verify user_id matches authenticated user
    if session_data.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create session for different user",
        )

    session_payload = {
        "session_id": session_id,
        "title": session_data.title,
        "user_id": session_data.user_id,
        "messages": [],
        "metadata": session_data.metadata or {},
        "created_at": datetime.utcnow().isoformat(),
    }

    success = await redis_client.set_session(session_id, session_payload)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create session",
        )

    return SessionResponse(**session_payload)


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    redis_client=Depends(get_redis),
):
    """Get session details by session_id"""
    session = await redis_client.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # Verify user owns the session
    if session.get("user_id") != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this session",
        )

    return SessionResponse(**session)


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: str,
    session_update: SessionUpdate,
    current_user: User = Depends(get_current_user),
    redis_client=Depends(get_redis),
):
    """Update session data"""
    session = await redis_client.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # Verify user owns the session
    if session.get("user_id") != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this session",
        )

    # Update only provided fields
    if session_update.title is not None:
        session["title"] = session_update.title
    if session_update.metadata is not None:
        session["metadata"] = session_update.metadata
    if session_update.messages is not None:
        session["messages"] = session_update.messages

    success = await redis_client.update_session(session_id, session)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update session",
        )

    return SessionResponse(**session)


@router.delete("/{session_id}", response_model=SuccessResponse)
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    redis_client=Depends(get_redis),
):
    """Delete a session"""
    session = await redis_client.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # Verify user owns the session
    if session.get("user_id") != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this session",
        )

    success = await redis_client.delete_session(session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete session",
        )

    return SuccessResponse(message="Session deleted successfully")


@router.get("/users/{user_id}/sessions", response_model=SessionListResponse)
async def list_user_sessions(
    user_id: int,
    current_user: User = Depends(get_current_user),
    redis_client=Depends(get_redis),
):
    """List all session IDs for a user"""
    # Verify user_id matches authenticated user or user is admin
    if user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to other user's sessions",
        )

    session_ids = await redis_client.list_user_sessions(user_id)

    return SessionListResponse(sessions=session_ids, count=len(session_ids))


@router.post("/{session_id}/lock", response_model=LockResponse)
async def acquire_session_lock(
    session_id: str,
    current_user: User = Depends(get_current_user),
    redis_client=Depends(get_redis),
):
    """Acquire a lock on a session to prevent concurrent access"""
    session = await redis_client.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # Verify user owns the session
    if session.get("user_id") != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this session",
        )

    lock_acquired = await redis_client.acquire_lock(session_id)

    if not lock_acquired:
        return LockResponse(
            lock_acquired=False,
            message="Session is locked by another operation",
        )

    return LockResponse(lock_acquired=True, message="Lock acquired successfully")


@router.post("/{session_id}/unlock", response_model=LockResponse)
async def release_session_lock(
    session_id: str,
    current_user: User = Depends(get_current_user),
    redis_client=Depends(get_redis),
):
    """Release a lock on a session"""
    session = await redis_client.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # Verify user owns the session
    if session.get("user_id") != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this session",
        )

    success = await redis_client.release_lock(session_id)

    return LockResponse(
        lock_acquired=True,
        message="Lock released successfully" if success else "Lock already released",
    )
