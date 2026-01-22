from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_
from app.models.patent_db import PatentMaster, ForeignPatentMaster
from app.schemas.patent import PatentSearch


class PatentDBCRUD:
    """patent_db 데이터베이스용 CRUD (한국/해외 특허)"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def search_kr_patents(
        self, search_params: PatentSearch
    ) -> Tuple[List[dict], int]:
        """한국 특허 검색 (patent_master)"""
        query = select(PatentMaster)
        conditions = []

        if search_params.title:
            conditions.append(PatentMaster.title.ilike(f"%{search_params.title}%"))
        if search_params.abstract:
            conditions.append(
                PatentMaster.abstract.ilike(f"%{search_params.abstract}%")
            )
        if search_params.status:
            conditions.append(PatentMaster.patent_status == search_params.status)
        if search_params.filing_date_from:
            conditions.append(
                PatentMaster.applicate_date >= search_params.filing_date_from
            )
        if search_params.filing_date_to:
            conditions.append(
                PatentMaster.applicate_date <= search_params.filing_date_to
            )

        if conditions:
            query = query.where(and_(*conditions))

        # Get total count
        count_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0

        query = query.offset(search_params.offset).limit(search_params.limit)
        result = await self.db.execute(query)
        patents = result.scalars().all()

        # Convert to dict for JSON response
        patent_dicts = [
            {
                "id": p.application_number,
                "patent_id": p.application_number,
                "title": p.title,
                "abstract": p.abstract,
                "filing_date": str(p.applicate_date) if p.applicate_date else None,
                "publication_date": str(p.publication_date)
                if p.publication_date
                else None,
                "status": p.patent_status,
                "country": "KR",
            }
            for p in patents
        ]

        return patent_dicts, total

    async def search_foreign_patents(
        self, search_params: PatentSearch
    ) -> Tuple[List[dict], int]:
        """해외 특허 검색 (foreign_patent_master)"""
        query = select(ForeignPatentMaster)
        conditions = []

        if search_params.title:
            conditions.append(
                ForeignPatentMaster.invention_name.ilike(f"%{search_params.title}%")
            )
        if search_params.abstract:
            conditions.append(
                ForeignPatentMaster.abstract.ilike(f"%{search_params.abstract}%")
            )
        if search_params.status:
            conditions.append(ForeignPatentMaster.patent_status == search_params.status)
        if search_params.filing_date_from:
            conditions.append(
                ForeignPatentMaster.application_date >= search_params.filing_date_from
            )
        if search_params.filing_date_to:
            conditions.append(
                ForeignPatentMaster.application_date <= search_params.filing_date_to
            )

        if conditions:
            query = query.where(and_(*conditions))

        # Get total count
        count_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0

        query = query.offset(search_params.offset).limit(search_params.limit)
        result = await self.db.execute(query)
        patents = result.scalars().all()

        # Convert to dict for JSON response
        patent_dicts = [
            {
                "id": p.document_number,
                "patent_id": p.document_number,
                "title": p.invention_name,
                "abstract": p.abstract,
                "filing_date": str(p.application_date) if p.application_date else None,
                "publication_date": str(p.publication_date)
                if p.publication_date
                else None,
                "status": p.patent_status,
                "country": p.country_code,
            }
            for p in patents
        ]

        return patent_dicts, total

    async def search_all_patents(
        self, search_params: PatentSearch
    ) -> Tuple[List[dict], int]:
        """한국 + 해외 특허 통합 검색"""
        kr_patents, kr_total = await self.search_kr_patents(search_params)
        foreign_patents, foreign_total = await self.search_foreign_patents(
            search_params
        )

        all_patents = kr_patents + foreign_patents
        total = kr_total + foreign_total

        # Sort by filing_date descending, handle limit/offset for combined results
        # For now, just return combined results (pagination applied per-source)
        return all_patents, total

    async def get_patent_detail(self, patent_id: str) -> Optional[dict]:
        """특허 상세 정보 조회 (KR: application_number, Foreign: document_number)"""
        # Try KR patent first
        result = await self.db.execute(
            select(PatentMaster).where(PatentMaster.application_number == patent_id)
        )
        patent = result.scalars().first()

        if patent:
            return {
                "id": patent.application_number,
                "patent_id": patent.application_number,
                "title": patent.title,
                "abstract": patent.abstract,
                "publication_number": patent.publication_number,
                "registration_number": patent.registration_number,
                "filing_date": str(patent.applicate_date)
                if patent.applicate_date
                else None,
                "publication_date": str(patent.publication_date)
                if patent.publication_date
                else None,
                "registration_date": str(patent.registration_date)
                if patent.registration_date
                else None,
                "status": patent.patent_status,
                "country": "KR",
            }

        # Try foreign patent
        result = await self.db.execute(
            select(ForeignPatentMaster).where(
                ForeignPatentMaster.document_number == patent_id
            )
        )
        patent = result.scalars().first()

        if patent:
            return {
                "id": patent.document_number,
                "patent_id": patent.document_number,
                "title": patent.invention_name,
                "abstract": patent.abstract,
                "application_number": patent.application_number,
                "publication_number": patent.publication_number,
                "registration_number": patent.registration_number,
                "filing_date": str(patent.application_date)
                if patent.application_date
                else None,
                "publication_date": str(patent.publication_date)
                if patent.publication_date
                else None,
                "registration_date": str(patent.registration_date)
                if patent.registration_date
                else None,
                "status": patent.patent_status,
                "country": patent.country_code,
                "priority_number": patent.priority_number,
                "priority_date": str(patent.priority_date)
                if patent.priority_date
                else None,
            }

        return None


def get_patentdb_crud(db: AsyncSession) -> PatentDBCRUD:
    return PatentDBCRUD(db)
