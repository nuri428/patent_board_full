"""
CRUD operations for Patent Analysis

Handles database operations for the patent_analyses table with multi-source patent support.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from app.models.patent_analysis import PatentAnalysis, PatentSource, PatentSourceType


class PatentAnalysisCRUD:
    """CRUD operations for patent analysis"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        session_id: Optional[str],
        user_id: int,
        analyzed_patents: Optional[List[Dict[str, Any]]],
        patent_source: Optional[PatentSource] = None,
        confidence_score: float = 0.5,
        relevant_sections: Optional[List[str]] = None,
        analysis_metadata: Optional[Dict[str, Any]] = None,
        source_type: Optional[PatentSourceType] = PatentSourceType.PATENT,
    ) -> PatentAnalysis:
        """Create a new patent analysis record"""
        patent_analysis = PatentAnalysis(
            id=str(uuid.uuid4()),
            session_id=session_id,
            user_id=user_id,
            analyzed_patents=analyzed_patents,
            patent_source=patent_source.value if patent_source else None,
            confidence_score=confidence_score,
            relevant_sections=relevant_sections,
            analysis_metadata=analysis_metadata,
            source_type=source_type.value if source_type else None,
        )
        self.db.add(patent_analysis)
        await self.db.commit()
        await self.db.refresh(patent_analysis)
        return patent_analysis

    async def get_by_id(self, analysis_id: str) -> Optional[PatentAnalysis]:
        """Get patent analysis by ID"""
        result = await self.db.execute(
            select(PatentAnalysis).where(PatentAnalysis.id == analysis_id)
        )
        return result.scalar_one_or_none()

    async def get_by_session_id(self, session_id: str) -> List[PatentAnalysis]:
        """Get all patent analyses for a specific session"""
        result = await self.db.execute(
            select(PatentAnalysis)
            .where(PatentAnalysis.session_id == session_id)
            .order_by(PatentAnalysis.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_user_id(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[PatentAnalysis]:
        """Get all patent analyses for a specific user"""
        result = await self.db.execute(
            select(PatentAnalysis)
            .where(PatentAnalysis.user_id == user_id)
            .order_by(PatentAnalysis.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_patent_source(
        self, patent_source: PatentSource, skip: int = 0, limit: int = 100
    ) -> List[PatentAnalysis]:
        """Get all patent analyses from a specific source"""
        result = await self.db.execute(
            select(PatentAnalysis)
            .where(PatentAnalysis.patent_source == patent_source.value)
            .order_by(PatentAnalysis.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def update(
        self,
        analysis_id: str,
        analyzed_patents: Optional[List[Dict[str, Any]]] = None,
        patent_source: Optional[PatentSource] = None,
        confidence_score: Optional[float] = None,
        relevant_sections: Optional[List[str]] = None,
        analysis_metadata: Optional[Dict[str, Any]] = None,
        source_type: Optional[PatentSourceType] = None,
    ) -> Optional[PatentAnalysis]:
        """Update a patent analysis record"""
        db_obj = await self.get_by_id(analysis_id)
        if db_obj:
            if analyzed_patents is not None:
                db_obj.analyzed_patents = analyzed_patents
            if patent_source is not None:
                db_obj.patent_source = patent_source.value
            if confidence_score is not None:
                db_obj.confidence_score = confidence_score
            if relevant_sections is not None:
                db_obj.relevant_sections = relevant_sections
            if analysis_metadata is not None:
                db_obj.analysis_metadata = analysis_metadata
            if source_type is not None:
                db_obj.source_type = source_type.value
            db_obj.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, analysis_id: str) -> bool:
        """Delete a patent analysis record"""
        db_obj = await self.get_by_id(analysis_id)
        if db_obj:
            await self.db.delete(db_obj)
            await self.db.commit()
            return True
        return False

    async def search(
        self,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
        patent_source: Optional[PatentSource] = None,
        min_confidence: Optional[float] = None,
        source_type: Optional[PatentSourceType] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[PatentAnalysis]:
        """
        Search patent analyses with multiple filters
        """
        filters = []

        if user_id:
            filters.append(PatentAnalysis.user_id == user_id)
        if session_id:
            filters.append(PatentAnalysis.session_id == session_id)
        if patent_source:
            filters.append(PatentAnalysis.patent_source == patent_source.value)
        if min_confidence:
            filters.append(PatentAnalysis.confidence_score >= min_confidence)
        if source_type:
            filters.append(PatentAnalysis.source_type == source_type.value)

        query = select(PatentAnalysis)

        if filters:
            query = query.where(and_(*filters))

        result = await self.db.execute(
            query.order_by(PatentAnalysis.created_at.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def get_multi_source_patents(
        self, session_id: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all patents from all sources for a session, grouped by source
        """
        analyses = await self.get_by_session_id(session_id)
        patents_by_source = {}

        for analysis in analyses:
            source = analysis.patent_source or "unknown"
            if source not in patents_by_source:
                patents_by_source[source] = []
            if analysis.analyzed_patents:
                patents_by_source[source].extend(analysis.analyzed_patents)

        return patents_by_source

    async def get_patent_count_by_source(
        self, user_id: Optional[int] = None
    ) -> Dict[str, int]:
        """Get count of patent analyses grouped by source"""
        query = select(PatentAnalysis.patent_source)

        if user_id:
            query = query.where(PatentAnalysis.user_id == user_id)

        result = await self.db.execute(query)
        sources = result.scalars().all()

        counts = {}
        for source in sources:
            counts[source] = counts.get(source, 0) + 1

        return counts


def get_patent_analysis_crud(db: AsyncSession) -> PatentAnalysisCRUD:
    """Helper function to get patent analysis CRUD instance"""
    return PatentAnalysisCRUD(db)
