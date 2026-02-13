from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.models.archived_session import ArchivedSession
import json


class ArchivedSessionCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        session_id: str,
        user_id: int,
        title: str,
        messages: List[dict],
        context: dict,
    ) -> ArchivedSession:
        """Create archived session"""
        archived_session = ArchivedSession(
            session_id=session_id,
            user_id=user_id,
            title=title,
            messages=json.dumps(messages),
            context=json.dumps(context) if context else None,
        )
        self.db.add(archived_session)
        await self.db.commit()
        await self.db.refresh(archived_session)
        return archived_session

    async def get_by_session_id(self, session_id: str) -> Optional[ArchivedSession]:
        """Get archived session by session_id"""
        result = await self.db.execute(
            select(ArchivedSession).where(ArchivedSession.session_id == session_id)
        )
        return result.scalar_one_or_none()

    async def list_by_user_id(self, user_id: int) -> List[ArchivedSession]:
        """List archived sessions for user"""
        result = await self.db.execute(
            select(ArchivedSession)
            .where(ArchivedSession.user_id == user_id)
            .order_by(ArchivedSession.archived_at.desc())
        )
        return result.scalars().all()

    async def restore_session_to_redis(self, session_id: str) -> str:
        """Restore session to Redis (will integrate with Task 1's Redis client)"""
        # Get archived session
        archived = await self.get_by_session_id(session_id)
        if not archived:
            raise ValueError(f"Session {session_id} not found in archive")

        # Restore to Redis
        try:
            from app.db.redis_client import redis_client

            session_data = {
                "session_id": archived.session_id,
                "user_id": archived.user_id,
                "title": archived.title,
                "messages": json.loads(archived.messages) if archived.messages else [],
                "context": json.loads(archived.context) if archived.context else {},
                "created_at": archived.created_at.isoformat(),
                "last_access": archived.archived_at.isoformat(),
            }
            await redis_client.set_session(session_id, session_data)
            return session_id
        except ImportError:
            # Redis client not available yet (Task 1)
            raise RuntimeError("Redis client not available")
        except Exception as e:
            raise RuntimeError(f"Failed to restore session to Redis: {e}")


def get_archived_session_crud(db: AsyncSession) -> ArchivedSessionCRUD:
    """Helper function to get archived session CRUD instance"""
    return ArchivedSessionCRUD(db)
