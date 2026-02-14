from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import logging
import json

from app.api.deps import get_current_user
from app.models import User
from app.db.redis_client import get_redis
from app.scheduler import get_scheduler
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database import get_db
from app.crud.crud_archived_session import get_archived_session_crud

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


class ArchivedSessionResponse(BaseModel):
    session_id: str
    title: str
    user_id: int
    messages: List[Dict[str, Any]]
    context: Optional[Dict[str, Any]]
    created_at: datetime
    archived_at: datetime


class RestoreResponse(BaseModel):
    session_id: str
    restored: bool
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


@router.post("/{session_id}/archive", response_model=SuccessResponse)
async def archive_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    redis_client=Depends(get_redis),
):
    """
    On-demand archival of a specific session.

    Manually triggers archival of a session, moving it from Redis to MariaDB.
    Useful when a user explicitly ends a session.
    """
    # Get session to verify ownership
    session = await redis_client.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # Verify user owns session
    if session.get("user_id") != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this session",
        )

    # Get scheduler and archive session
    archival_scheduler = get_scheduler()
    success = await archival_scheduler.archive_session(session_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to archive session",
        )

    return SuccessResponse(message="Session archived successfully")


@router.post("/archive-all", response_model=Dict[str, Any])
async def archive_all_sessions(
    current_user: User = Depends(get_current_user),
):
    """
    Trigger archival of all inactive sessions.

    Manually triggers the archival job to archive all inactive sessions.
    Useful for testing or immediate cleanup.
    """
    # Only allow admin users to trigger full archival
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can trigger full archival",
        )

    # Get scheduler and run archival job
    archival_scheduler = get_scheduler()
    stats = await archival_scheduler.archive_inactive_sessions()

    return stats


@router.get("/archived/{session_id}", response_model=ArchivedSessionResponse)
async def get_archived_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get archived session details from MariaDB"""
    archived_crud = get_archived_session_crud(db)
    archived_session = await archived_crud.get_by_session_id(session_id)

    if not archived_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archived session not found",
        )

    # Verify user owns the archived session
    if archived_session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this archived session",
        )

    # Parse JSON fields
    messages = json.loads(archived_session.messages) if archived_session.messages else []
    context = json.loads(archived_session.context) if archived_session.context else {}

    return ArchivedSessionResponse(
        session_id=archived_session.session_id,
        title=archived_session.title,
        user_id=archived_session.user_id,
        messages=messages,
        context=context,
        created_at=archived_session.created_at,
        archived_at=archived_session.archived_at,
    )


@router.post("/{session_id}/restore", response_model=RestoreResponse)
async def restore_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis_client=Depends(get_redis),
):
    """
    Restore archived session from MariaDB to Redis.

    Restores a previously archived session back to Redis for active use.
    The archived copy remains in MariaDB for future reference.
    """
    archived_crud = get_archived_session_crud(db)
    archived_session = await archived_crud.get_by_session_id(session_id)

    if not archived_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archived session not found",
        )

    # Verify user owns the archived session
    if archived_session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this archived session",
        )

    # Check if session already exists in Redis
    existing_session = await redis_client.get_session(session_id)
    if existing_session:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Session already exists in Redis. Cannot restore an active session.",
        )

    # Restore session to Redis
    try:
        restored_session_id = await archived_crud.restore_session_to_redis(session_id)
        return RestoreResponse(
            session_id=restored_session_id,
            restored=True,
            message="Session restored successfully",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except RuntimeError as e:
        logger.error(f"Failed to restore session: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable. Failed to restore session to Redis.",
        )
