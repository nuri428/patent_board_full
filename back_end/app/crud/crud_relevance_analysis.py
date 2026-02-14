import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.relevance_analysis import RelevanceAnalysis


class RelevanceAnalysisCRUD:
    """Async CRUD operations for relevance analysis records."""

    def __init__(self, db: AsyncSession):
        """Initialize CRUD with an async database session."""
        self.db = db

    async def create(
        self,
        session_id: str | None,
        user_id: int,
        query_text: str,
        response_text: str,
        relevance_score: float,
        analysis_metadata: dict[str, object] | None = None,
    ) -> RelevanceAnalysis:
        """Create a relevance analysis entry."""
        analysis = RelevanceAnalysis(
            id=str(uuid.uuid4()),
            session_id=session_id,
            user_id=user_id,
            query_text=query_text,
            response_text=response_text,
            relevance_score=max(0.0, min(1.0, relevance_score)),
            analysis_metadata=analysis_metadata or {},
        )
        self.db.add(analysis)
        await self.db.commit()
        await self.db.refresh(analysis)
        return analysis

    async def get_by_session(
        self, session_id: str, skip: int = 0, limit: int = 100
    ) -> list[RelevanceAnalysis]:
        """List relevance analyses for a session ordered by newest first."""
        result = await self.db.execute(
            select(RelevanceAnalysis)
            .where(RelevanceAnalysis.session_id == session_id)
            .order_by(RelevanceAnalysis.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[RelevanceAnalysis]:
        """List relevance analyses for a user ordered by newest first."""
        result = await self.db.execute(
            select(RelevanceAnalysis)
            .where(RelevanceAnalysis.user_id == user_id)
            .order_by(RelevanceAnalysis.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_recent_analyses(
        self,
        limit: int = 50,
        user_id: int | None = None,
        session_id: str | None = None,
    ) -> list[RelevanceAnalysis]:
        """Get recent relevance analyses with optional user/session filtering."""
        query = select(RelevanceAnalysis)

        if user_id is not None:
            query = query.where(RelevanceAnalysis.user_id == user_id)
        if session_id is not None:
            query = query.where(RelevanceAnalysis.session_id == session_id)

        result = await self.db.execute(
            query.order_by(RelevanceAnalysis.created_at.desc()).limit(limit)
        )
        return result.scalars().all()


def get_relevance_analysis_crud(db: AsyncSession) -> RelevanceAnalysisCRUD:
    """Create CRUD helper instance for dependency usage."""
    return RelevanceAnalysisCRUD(db)
