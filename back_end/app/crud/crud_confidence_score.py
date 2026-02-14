import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.confidence_score import ConfidenceScore


class ConfidenceScoreCRUD:
    """Async CRUD operations for confidence score records."""

    def __init__(self, db: AsyncSession):
        """Initialize CRUD with an async database session."""
        self.db = db

    async def create(
        self,
        session_id: str | None,
        user_id: int,
        confidence_value: float,
        confidence_level: str,
        source_factors: dict[str, object] | None = None,
    ) -> ConfidenceScore:
        """Create a confidence score entry."""
        score = ConfidenceScore(
            id=str(uuid.uuid4()),
            session_id=session_id,
            user_id=user_id,
            confidence_value=max(0.0, min(1.0, confidence_value)),
            confidence_level=confidence_level,
            source_factors=source_factors or {},
        )
        self.db.add(score)
        await self.db.commit()
        await self.db.refresh(score)
        return score

    async def get_by_session(
        self, session_id: str, skip: int = 0, limit: int = 100
    ) -> list[ConfidenceScore]:
        """List confidence scores for a session ordered by newest first."""
        result = await self.db.execute(
            select(ConfidenceScore)
            .where(ConfidenceScore.session_id == session_id)
            .order_by(ConfidenceScore.calculated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[ConfidenceScore]:
        """List confidence scores for a user ordered by newest first."""
        result = await self.db.execute(
            select(ConfidenceScore)
            .where(ConfidenceScore.user_id == user_id)
            .order_by(ConfidenceScore.calculated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_recent_scores(
        self,
        limit: int = 50,
        user_id: int | None = None,
        session_id: str | None = None,
    ) -> list[ConfidenceScore]:
        """Get recent confidence scores with optional user/session filtering."""
        query = select(ConfidenceScore)

        if user_id is not None:
            query = query.where(ConfidenceScore.user_id == user_id)
        if session_id is not None:
            query = query.where(ConfidenceScore.session_id == session_id)

        result = await self.db.execute(
            query.order_by(ConfidenceScore.calculated_at.desc()).limit(limit)
        )
        return result.scalars().all()


def get_confidence_score_crud(db: AsyncSession) -> ConfidenceScoreCRUD:
    """Create CRUD helper instance for dependency usage."""
    return ConfidenceScoreCRUD(db)
