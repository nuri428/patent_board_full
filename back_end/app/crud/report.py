from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict, Any
from app.models import Report, ReportPatent, ReportAnalytics, Patent
from app.schemas import ReportCreate, ReportUpdate
import json


class ReportCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, report_id: int) -> Optional[Report]:
        """Get report by ID with related data"""
        result = await self.db.execute(
            select(Report)
            .options(selectinload(Report.patents), selectinload(Report.analytics))
            .where(Report.id == report_id)
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        owner_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> List[Report]:
        """Get multiple reports with pagination"""
        query = select(Report).options(
            selectinload(Report.patents), selectinload(Report.analytics)
        )

        if owner_id:
            query = query.where(Report.owner_id == owner_id)
        if status:
            query = query.where(Report.status == status)

        query = query.offset(skip).limit(limit).order_by(Report.created_at.desc())
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(self, report_create: ReportCreate, owner_id: int) -> Report:
        """Create new report"""
        db_report = Report(
            title=report_create.title,
            description=report_create.description,
            report_type=report_create.report_type,
            topic=report_create.topic,
            owner_id=owner_id,
            status="pending",
        )

        self.db.add(db_report)
        await self.db.commit()
        await self.db.refresh(db_report)

        # Add patents to report if provided
        if report_create.patent_ids:
            for patent_id in report_create.patent_ids:
                report_patent = ReportPatent(
                    report_id=db_report.id,
                    patent_id=patent_id,
                    relevance_score=5,  # Default relevance
                )
                self.db.add(report_patent)

        await self.db.commit()
        return db_report

    async def update(
        self, report_id: int, report_update: ReportUpdate
    ) -> Optional[Report]:
        """Update report"""
        db_report = await self.get(report_id)
        if not db_report:
            return None

        update_data = report_update.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_report, field, value)

        await self.db.commit()
        await self.db.refresh(db_report)
        return db_report

    async def delete(self, report_id: int) -> bool:
        """Delete report"""
        db_report = await self.get(report_id)
        if not db_report:
            return False

        await self.db.delete(db_report)
        await self.db.commit()
        return True

    async def add_patent(
        self,
        report_id: int,
        patent_id: int,
        relevance_score: Optional[int] = None,
        analysis_notes: Optional[str] = None,
    ) -> Optional[ReportPatent]:
        """Add patent to report"""
        # Check if already exists
        existing = await self.db.execute(
            select(ReportPatent).where(
                and_(
                    ReportPatent.report_id == report_id,
                    ReportPatent.patent_id == patent_id,
                )
            )
        )
        if existing.scalar_one_or_none():
            return None

        report_patent = ReportPatent(
            report_id=report_id,
            patent_id=patent_id,
            relevance_score=relevance_score,
            analysis_notes=analysis_notes,
        )

        self.db.add(report_patent)
        await self.db.commit()
        await self.db.refresh(report_patent)
        return report_patent

    async def remove_patent(self, report_id: int, patent_id: int) -> bool:
        """Remove patent from report"""
        result = await self.db.execute(
            select(ReportPatent).where(
                and_(
                    ReportPatent.report_id == report_id,
                    ReportPatent.patent_id == patent_id,
                )
            )
        )
        report_patent = result.scalar_one_or_none()

        if not report_patent:
            return False

        await self.db.delete(report_patent)
        await self.db.commit()
        return True

    async def update_patent_relevance(
        self,
        report_id: int,
        patent_id: int,
        relevance_score: int,
        analysis_notes: Optional[str] = None,
    ) -> Optional[ReportPatent]:
        """Update patent relevance in report"""
        result = await self.db.execute(
            select(ReportPatent).where(
                and_(
                    ReportPatent.report_id == report_id,
                    ReportPatent.patent_id == patent_id,
                )
            )
        )
        report_patent = result.scalar_one_or_none()

        if not report_patent:
            return None

        report_patent.relevance_score = relevance_score
        if analysis_notes is not None:
            report_patent.analysis_notes = analysis_notes

        await self.db.commit()
        await self.db.refresh(report_patent)
        return report_patent

    async def get_report_patents(self, report_id: int) -> List[ReportPatent]:
        """Get all patents in a report"""
        result = await self.db.execute(
            select(ReportPatent)
            .where(ReportPatent.report_id == report_id)
            .order_by(desc(ReportPatent.relevance_score))
        )
        return result.scalars().all()

    async def create_analytics(
        self,
        report_id: int,
        patent_count: int,
        processing_time_seconds: Optional[int] = None,
        generation_tokens_used: Optional[int] = None,
        query_complexity_score: Optional[int] = None,
    ) -> ReportAnalytics:
        """Create or update report analytics"""
        # Check if analytics already exist
        existing = await self.db.execute(
            select(ReportAnalytics).where(ReportAnalytics.report_id == report_id)
        )
        analytics = existing.scalar_one_or_none()

        if analytics:
            # Update existing
            analytics.patent_count = patent_count
            if processing_time_seconds is not None:
                analytics.processing_time_seconds = processing_time_seconds
            if generation_tokens_used is not None:
                analytics.generation_tokens_used = generation_tokens_used
            if query_complexity_score is not None:
                analytics.query_complexity_score = query_complexity_score
        else:
            # Create new
            analytics = ReportAnalytics(
                report_id=report_id,
                patent_count=patent_count,
                processing_time_seconds=processing_time_seconds,
                generation_tokens_used=generation_tokens_used,
                query_complexity_score=query_complexity_score,
            )
            self.db.add(analytics)

        await self.db.commit()
        await self.db.refresh(analytics)
        return analytics

    async def update_user_satisfaction(
        self, report_id: int, rating: int
    ) -> Optional[ReportAnalytics]:
        """Update user satisfaction rating"""
        result = await self.db.execute(
            select(ReportAnalytics).where(ReportAnalytics.report_id == report_id)
        )
        analytics = result.scalar_one_or_none()

        if not analytics:
            return None

        analytics.user_satisfaction_rating = rating
        await self.db.commit()
        await self.db.refresh(analytics)
        return analytics


# Helper function to get report CRUD instance
def get_report_crud(db: AsyncSession) -> ReportCRUD:
    return ReportCRUD(db)
