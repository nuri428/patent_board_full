from datetime import datetime
from typing import List, Optional
import uuid

from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session_favorite import SessionFavorite


class SessionFavoriteCRUD:
    """Async CRUD operations for session favorites."""

    def __init__(self, db: AsyncSession):
        """Initialize CRUD with an async database session."""
        self.db = db

    async def create(
        self,
        user_id: int,
        session_id: str,
        notes: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        is_pinned: bool = False,
    ) -> SessionFavorite:
        """Create a favorite record for a user session."""
        favorite = SessionFavorite(
            id=str(uuid.uuid4()),
            user_id=user_id,
            session_id=session_id,
            notes=notes,
            keywords=keywords or [],
            is_pinned=is_pinned,
        )
        self.db.add(favorite)
        await self.db.commit()
        await self.db.refresh(favorite)
        return favorite

    async def get_by_id(self, favorite_id: str) -> Optional[SessionFavorite]:
        """Fetch a favorite by its id."""
        result = await self.db.execute(
            select(SessionFavorite).where(SessionFavorite.id == favorite_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[SessionFavorite]:
        """List a user's favorites ordered by pinned and recency."""
        result = await self.db.execute(
            select(SessionFavorite)
            .where(SessionFavorite.user_id == user_id)
            .order_by(SessionFavorite.is_pinned.desc(), SessionFavorite.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_user_and_session(
        self, user_id: int, session_id: str
    ) -> Optional[SessionFavorite]:
        """Fetch a favorite by user and session id."""
        result = await self.db.execute(
            select(SessionFavorite).where(
                SessionFavorite.user_id == user_id,
                SessionFavorite.session_id == session_id,
            )
        )
        return result.scalar_one_or_none()

    async def count_by_user(self, user_id: int) -> int:
        """Count favorites for a user."""
        result = await self.db.execute(
            select(func.count()).where(SessionFavorite.user_id == user_id)
        )
        return result.scalar_one()

    async def update(
        self,
        favorite_id: str,
        notes: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        is_pinned: Optional[bool] = None,
    ) -> Optional[SessionFavorite]:
        """Update mutable fields for a favorite."""
        favorite = await self.get_by_id(favorite_id)
        if not favorite:
            return None

        if notes is not None:
            favorite.notes = notes
        if keywords is not None:
            favorite.keywords = keywords
        if is_pinned is not None:
            favorite.is_pinned = is_pinned

        favorite.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(favorite)
        return favorite

    async def delete(self, favorite_id: str) -> bool:
        """Delete a favorite by id."""
        favorite = await self.get_by_id(favorite_id)
        if not favorite:
            return False
        await self.db.delete(favorite)
        await self.db.commit()
        return True

    async def search_by_keywords(
        self,
        user_id: int,
        keywords: List[str],
        skip: int = 0,
        limit: int = 100,
    ) -> List[SessionFavorite]:
        """Search favorites by keywords against notes and keyword JSON."""
        query = select(SessionFavorite).where(SessionFavorite.user_id == user_id)

        if keywords:
            normalized = [kw.strip().lower() for kw in keywords if kw and kw.strip()]
            if normalized:
                conditions = []
                for keyword in normalized:
                    like_pattern = f"%{keyword}%"
                    conditions.append(SessionFavorite.notes.ilike(like_pattern))
                    conditions.append(
                        cast(SessionFavorite.keywords, String).ilike(like_pattern)
                    )
                query = query.where(or_(*conditions))

        result = await self.db.execute(
            query.order_by(
                SessionFavorite.is_pinned.desc(), SessionFavorite.updated_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def toggle_pin(self, favorite_id: str) -> Optional[SessionFavorite]:
        """Toggle pinned state for a favorite."""
        favorite = await self.get_by_id(favorite_id)
        if not favorite:
            return None

        favorite.is_pinned = not favorite.is_pinned
        favorite.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(favorite)
        return favorite


def get_session_favorite_crud(db: AsyncSession) -> SessionFavoriteCRUD:
    """Create CRUD helper instance for dependency usage."""
    return SessionFavoriteCRUD(db)
