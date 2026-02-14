from datetime import datetime
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.crud.crud_session_favorite import get_session_favorite_crud
from app.models import User
from shared.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


class SessionFavoriteCreate(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=36)
    notes: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    is_pinned: bool = False


class SessionFavoriteUpdate(BaseModel):
    notes: Optional[str] = None
    keywords: Optional[List[str]] = None
    is_pinned: Optional[bool] = None


class SessionFavoriteResponse(BaseModel):
    id: str
    user_id: int
    session_id: str
    notes: Optional[str]
    keywords: List[str] = Field(default_factory=list)
    is_pinned: bool
    created_at: datetime
    updated_at: Optional[datetime]


class SessionFavoriteListResponse(BaseModel):
    data: List[SessionFavoriteResponse]
    metadata: Dict[str, Any]


class SuccessResponse(BaseModel):
    message: str


def _to_response(favorite) -> SessionFavoriteResponse:
    return SessionFavoriteResponse(
        id=favorite.id,
        user_id=favorite.user_id,
        session_id=favorite.session_id,
        notes=favorite.notes,
        keywords=favorite.keywords or [],
        is_pinned=favorite.is_pinned,
        created_at=favorite.created_at,
        updated_at=favorite.updated_at,
    )


@router.post("", response_model=SessionFavoriteResponse, status_code=status.HTTP_201_CREATED)
async def create_session_favorite(
    payload: SessionFavoriteCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a chat session to current user's favorites."""
    crud = get_session_favorite_crud(db)

    existing = await crud.get_by_user_and_session(current_user.id, payload.session_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Session is already in favorites",
        )

    try:
        favorite = await crud.create(
            user_id=current_user.id,
            session_id=payload.session_id,
            notes=payload.notes,
            keywords=payload.keywords,
            is_pinned=payload.is_pinned,
        )
    except Exception:
        logger.exception(
            "Failed to create session favorite for user_id=%s session_id=%s",
            current_user.id,
            payload.session_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create session favorite",
        )

    logger.info(
        "Session favorite created id=%s user_id=%s session_id=%s",
        favorite.id,
        current_user.id,
        payload.session_id,
    )
    return _to_response(favorite)


@router.get("", response_model=SessionFavoriteListResponse)
async def list_session_favorites(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List current user's session favorites with pagination metadata."""
    crud = get_session_favorite_crud(db)

    try:
        favorites = await crud.get_by_user(current_user.id, skip=skip, limit=limit)
        total = await crud.count_by_user(current_user.id)
    except Exception:
        logger.exception("Failed to list session favorites for user_id=%s", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list session favorites",
        )

    return SessionFavoriteListResponse(
        data=[_to_response(favorite) for favorite in favorites],
        metadata={"skip": skip, "limit": limit, "total": total},
    )


@router.get("/search", response_model=SessionFavoriteListResponse)
async def search_session_favorites(
    keywords: List[str] = Query(default=[]),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Search current user's favorites by keywords across notes and keyword arrays."""
    crud = get_session_favorite_crud(db)

    if not keywords:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one keyword is required",
        )

    try:
        favorites = await crud.search_by_keywords(
            user_id=current_user.id,
            keywords=keywords,
            skip=skip,
            limit=limit,
        )
    except Exception:
        logger.exception(
            "Failed to search session favorites for user_id=%s keywords=%s",
            current_user.id,
            keywords,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search session favorites",
        )

    return SessionFavoriteListResponse(
        data=[_to_response(favorite) for favorite in favorites],
        metadata={
            "skip": skip,
            "limit": limit,
            "count": len(favorites),
            "keywords": keywords,
        },
    )


@router.get("/{favorite_id}", response_model=SessionFavoriteResponse)
async def get_session_favorite(
    favorite_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific favorite owned by the current user."""
    crud = get_session_favorite_crud(db)
    favorite = await crud.get_by_id(favorite_id)

    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session favorite not found",
        )

    if favorite.user_id != current_user.id:
        logger.warning(
            "Forbidden favorite access user_id=%s favorite_id=%s owner_id=%s",
            current_user.id,
            favorite_id,
            favorite.user_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this session favorite",
        )

    return _to_response(favorite)


@router.put("/{favorite_id}", response_model=SessionFavoriteResponse)
async def update_session_favorite(
    favorite_id: str,
    payload: SessionFavoriteUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update notes, keywords, or pin state for a favorite."""
    crud = get_session_favorite_crud(db)
    favorite = await crud.get_by_id(favorite_id)

    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session favorite not found",
        )

    if favorite.user_id != current_user.id:
        logger.warning(
            "Forbidden favorite update user_id=%s favorite_id=%s owner_id=%s",
            current_user.id,
            favorite_id,
            favorite.user_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this session favorite",
        )

    try:
        updated = await crud.update(
            favorite_id=favorite_id,
            notes=payload.notes,
            keywords=payload.keywords,
            is_pinned=payload.is_pinned,
        )
    except Exception:
        logger.exception(
            "Failed to update session favorite user_id=%s favorite_id=%s",
            current_user.id,
            favorite_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update session favorite",
        )

    return _to_response(updated)


@router.delete("/{favorite_id}", response_model=SuccessResponse)
async def delete_session_favorite(
    favorite_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a favorite owned by the current user."""
    crud = get_session_favorite_crud(db)
    favorite = await crud.get_by_id(favorite_id)

    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session favorite not found",
        )

    if favorite.user_id != current_user.id:
        logger.warning(
            "Forbidden favorite delete user_id=%s favorite_id=%s owner_id=%s",
            current_user.id,
            favorite_id,
            favorite.user_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this session favorite",
        )

    try:
        deleted = await crud.delete(favorite_id)
    except Exception:
        logger.exception(
            "Failed to delete session favorite user_id=%s favorite_id=%s",
            current_user.id,
            favorite_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete session favorite",
        )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session favorite not found",
        )

    logger.info("Session favorite deleted id=%s user_id=%s", favorite_id, current_user.id)
    return SuccessResponse(message="Session favorite removed")


@router.post("/{favorite_id}/pin", response_model=SessionFavoriteResponse)
async def toggle_pin_session_favorite(
    favorite_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Toggle pinned state for an owned favorite."""
    crud = get_session_favorite_crud(db)
    favorite = await crud.get_by_id(favorite_id)

    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session favorite not found",
        )

    if favorite.user_id != current_user.id:
        logger.warning(
            "Forbidden favorite pin toggle user_id=%s favorite_id=%s owner_id=%s",
            current_user.id,
            favorite_id,
            favorite.user_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this session favorite",
        )

    try:
        updated = await crud.toggle_pin(favorite_id)
    except Exception:
        logger.exception(
            "Failed to toggle pin user_id=%s favorite_id=%s",
            current_user.id,
            favorite_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update favorite pin status",
        )

    return _to_response(updated)
