"""
Patent Country Search API Endpoints

Country-specific patent search with advanced filtering, pagination, and statistics.
Supports 10 countries: KR, US, CN, EP, JP, KIPO, JPO, EPO, PCT, WO
"""

from typing import Any, List, Dict, Optional
from datetime import datetime, date
from enum import Enum
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc
from pydantic import BaseModel, Field, field_validator

from app.crud.patent_db import get_patentdb_crud
from app.api import deps
from app.models import User
from app.models.patent_analysis import PatentSource, PatentAnalysis
from app.schemas.patent import PatentSearch
from shared.database import get_db

router = APIRouter(prefix="/api/v1/patent-country", tags=["patents", "country-search"])


class PatentCountry(str, Enum):
    """Patent country enumerations for country-specific search"""
    KR = "KR"  # South Korea
    US = "US"  # United States
    CN = "CN"  # China
    EP = "EP"  # European Union
    JP = "JP"  # Japan
    KIPO = "KIPO"  # Korean Intellectual Property Office
    JPO = "JPO"  # Japan Patent Office
    EPO = "EPO"  # European Patent Office
    PCT = "PCT"  # Patent Cooperation Treaty
    WO = "WO"  # World Intellectual Property Organization
    OTHER = "OTHER"


class PatentCountryResponse(BaseModel):
    """Response model for country list"""
    code: str = Field(..., description="Country code")
    name: str = Field(..., description="Country name")


class PatentCountrySearchRequest(BaseModel):
    """Request model for country-specific patent search"""
    country: PatentCountry = Field(..., description="Country to search")
    query: Optional[str] = Field(default=None, description="Search query for semantic/keyword search")
    keywords: Optional[str] = Field(default=None, description="Additional keywords to filter results")
    application_number: Optional[str] = Field(default=None, description="Filter by application number")
    filing_date: Optional[date] = Field(default=None, description="Filter by filing date")
    date_range_start: Optional[date] = Field(default=None, description="Filter patents from this date")
    date_range_end: Optional[date] = Field(default=None, description="Filter patents until this date")
    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    per_page: int = Field(default=20, ge=1, le=100, description="Results per page")
    sort_by: str = Field(default="date", description="Sort by: date, relevance, title")

    @field_validator('sort_by')
    @classmethod
    def validate_sort_by(cls, v: str) -> str:
        allowed_sorts = ['date', 'relevance', 'title']
        if v not in allowed_sorts:
            raise ValueError(f"sort_by must be one of {allowed_sorts}")
        return v


class PatentCountryResult(BaseModel):
    """Response model for country search result"""
    patents: List[Dict[str, Any]] = Field(default_factory=list, description="List of patent objects")
    country_code: str = Field(..., description="Country code")
    country_name: str = Field(..., description="Country name")
    total_count: int = Field(default=0, description="Total number of patents")
    statistics: Dict[str, Any] = Field(default_factory=dict, description="Country-specific statistics")
    page: int = Field(default=1, description="Current page number")
    per_page: int = Field(default=20, description="Results per page")
    total_pages: int = Field(default=0, description="Total number of pages")
    has_next: bool = Field(default=False, description="Whether there is a next page")
    has_previous: bool = Field(default=False, description="Whether there is a previous page")
    filters_applied: Dict[str, Any] = Field(default_factory=dict, description="Summary of filters applied")


class PatentCountryStatistics(BaseModel):
    """Response model for country statistics"""
    country: str = Field(..., description="Country code")
    country_name: str = Field(..., description="Country name")
    total_patents: int = Field(default=0, description="Total patents for this country")
    avg_confidence: Optional[float] = Field(default=None, description="Average confidence score")
    latest_patent_date: Optional[str] = Field(default=None, description="Latest patent date")
    patents_by_status: Dict[str, int] = Field(default_factory=dict, description="Patents grouped by status")


# Country name mapping
COUNTRY_NAMES = {
    "KR": "South Korea",
    "US": "United States",
    "CN": "China",
    "EP": "European Union",
    "JP": "Japan",
    "KIPO": "Korean Intellectual Property Office",
    "JPO": "Japan Patent Office",
    "EPO": "European Patent Office",
    "PCT": "Patent Cooperation Treaty",
    "WO": "World Intellectual Property Organization",
    "OTHER": "Other",
}


@router.get("/countries/list", response_model=List[PatentCountryResponse])
async def list_countries():
    """
    Get list of available countries for patent search.

    Returns all supported countries with their codes and names.
    No authentication required for this endpoint.
    """
    countries = [
        PatentCountryResponse(code=code, name=COUNTRY_NAMES.get(code, code))
        for code in [
            PatentCountry.KR,
            PatentCountry.US,
            PatentCountry.CN,
            PatentCountry.EP,
            PatentCountry.JP,
            PatentCountry.KIPO,
            PatentCountry.JPO,
            PatentCountry.EPO,
            PatentCountry.PCT,
            PatentCountry.WO,
        ]
    ]
    return countries


@router.post("/search", response_model=PatentCountryResult, status_code=status.HTTP_200_OK)
async def search_by_country(
    request: PatentCountrySearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Search patents by country with advanced filtering.

    Features:
    - Country-specific patent search across 10 countries
    - Keyword and semantic search support
    - Application number filter
    - Date range filtering
    - Pagination with metadata
    - Country-specific statistics

    Authentication: Required (JWT token)
    Authorization: User can only search their own patent analyses

    Country mappings:
    - KR: South Korea (KIPRIS)
    - US: United States (USPTO)
    - CN: China (CNIPA)
    - EP: European Union (EPO)
    - JP: Japan (JPO)
    - KIPO: Korean Intellectual Property Office
    - JPO: Japan Patent Office
    - EPO: European Patent Office
    - PCT: Patent Cooperation Treaty
    - WO: World Intellectual Property Organization (WIPO)
    """
    crud = get_patentdb_crud(db)
    country_code = request.country.value
    country_name = COUNTRY_NAMES.get(country_code, country_code)

    # Map country to database source
    # KR -> PatentMaster, others -> ForeignPatentMaster with country_code
    if country_code == "KR":
        # Search Korean patents
        patents, total = await _search_kr_patents(db, request, current_user.id)
    else:
        # Search foreign patents
        patents, total = await _search_foreign_patents(db, request, current_user.id, country_code)

    # Calculate statistics
    statistics = _calculate_country_statistics(patents, country_code)

    # Calculate pagination
    total_pages = (total + request.per_page - 1) // request.per_page
    offset = (request.page - 1) * request.per_page
    paginated_patents = patents[offset:offset + request.per_page]

    # Build filters summary
    filters_applied = {
        "country": country_code,
    }
    if request.query:
        filters_applied["query"] = request.query
    if request.keywords:
        filters_applied["keywords"] = request.keywords
    if request.application_number:
        filters_applied["application_number"] = request.application_number
    if request.filing_date:
        filters_applied["filing_date"] = request.filing_date.isoformat()
    if request.date_range_start or request.date_range_end:
        filters_applied["date_range"] = {
            "start": request.date_range_start.isoformat() if request.date_range_start else None,
            "end": request.date_range_end.isoformat() if request.date_range_end else None,
        }

    return PatentCountryResult(
        patents=paginated_patents,
        country_code=country_code,
        country_name=country_name,
        total_count=total,
        statistics=statistics,
        page=request.page,
        per_page=request.per_page,
        total_pages=total_pages,
        has_next=request.page < total_pages,
        has_previous=request.page > 1,
        filters_applied=filters_applied,
    )


@router.get("/statistics", response_model=List[PatentCountryStatistics])
async def get_country_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get patent statistics for all countries.

    Returns patent counts and statistics grouped by country.
    Only includes data from the current user's analyses.
    """
    # Get user's patent analyses
    result = await db.execute(
        select(PatentAnalysis).where(PatentAnalysis.user_id == current_user.id)
    )
    analyses = result.scalars().all()

    # Aggregate patents by country
    country_stats: Dict[str, List[Dict[str, Any]]] = {}
    for analysis in analyses:
        if analysis.analyzed_patents:
            for patent in analysis.analyzed_patents:
                country = patent.get('country', 'OTHER')
                if country not in country_stats:
                    country_stats[country] = []
                country_stats[country].append(patent)

    # Build statistics response
    statistics = []
    for country_code, patents in country_stats.items():
        country_name = COUNTRY_NAMES.get(country_code, country_code)

        # Calculate statistics
        status_counts: Dict[str, int] = {}
        dates = []
        for patent in patents:
            status = patent.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1

            pub_date = patent.get('publication_date') or patent.get('filing_date')
            if pub_date:
                try:
                    if isinstance(pub_date, str):
                        dates.append(datetime.fromisoformat(pub_date.replace('Z', '+00:00')))
                except Exception:
                    pass

        latest_date = max(dates).isoformat() if dates else None

        statistics.append(
            PatentCountryStatistics(
                country=country_code,
                country_name=country_name,
                total_patents=len(patents),
                avg_confidence=None,  # Would need confidence score in patent data
                latest_patent_date=latest_date,
                patents_by_status=status_counts,
            )
        )

    # Sort by total patents descending
    statistics.sort(key=lambda x: x.total_patents, reverse=True)

    return statistics


async def _search_kr_patents(
    db: AsyncSession,
    request: PatentCountrySearchRequest,
    user_id: int
) -> tuple[List[Dict[str, Any]], int]:
    """Search Korean patents with filters"""
    from app.models.patent_db import PatentMaster

    query = select(PatentMaster)
    conditions = []

    # Query filter (title/abstract)
    if request.query:
        query_lower = request.query.lower()
        conditions.append(
            or_(
                PatentMaster.title.ilike(f"%{request.query}%"),
                PatentMaster.abstract.ilike(f"%{request.query}%"),
            )
        )

    # Keywords filter
    if request.keywords:
        keywords_list = request.keywords.lower().split()
        for keyword in keywords_list:
            conditions.append(
                or_(
                    PatentMaster.title.ilike(f"%{keyword}%"),
                    PatentMaster.abstract.ilike(f"%{keyword}%"),
                )
            )

    # Application number filter
    if request.application_number:
        conditions.append(PatentMaster.application_number.ilike(f"%{request.application_number}%"))

    # Filing date filter
    if request.filing_date:
        conditions.append(PatentMaster.applicate_date == request.filing_date)

    # Date range filter
    if request.date_range_start:
        conditions.append(PatentMaster.applicate_date >= request.date_range_start)
    if request.date_range_end:
        conditions.append(PatentMaster.applicate_date <= request.date_range_end)

    if conditions:
        query = query.where(and_(*conditions))

    # Get total count
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar() or 0

    # Apply sorting
    if request.sort_by == "date":
        query = query.order_by(desc(PatentMaster.applicate_date))
    elif request.sort_by == "title":
        query = query.order_by(PatentMaster.title)
    else:  # relevance
        query = query.order_by(desc(PatentMaster.applicate_date))

    # Get results
    result = await db.execute(query)
    patents = result.scalars().all()

    # Convert to dict format
    patent_dicts = [
        {
            "id": p.application_number,
            "patent_id": p.application_number,
            "title": p.title,
            "abstract": p.abstract,
            "filing_date": str(p.applicate_date) if p.applicate_date else None,
            "publication_date": str(p.publication_date) if p.publication_date else None,
            "registration_date": str(p.registration_date) if p.registration_date else None,
            "status": p.patent_status,
            "country": "KR",
        }
        for p in patents
    ]

    return patent_dicts, total


async def _search_foreign_patents(
    db: AsyncSession,
    request: PatentCountrySearchRequest,
    user_id: int,
    country_code: str
) -> tuple[List[Dict[str, Any]], int]:
    """Search foreign patents with filters"""
    from app.models.patent_db import ForeignPatentMaster

    # Map country codes to database values
    country_mapping = {
        "US": "US",
        "CN": "CN",
        "EP": "EP",
        "JP": "JP",
        "WO": "WO",
        "PCT": "WO",  # PCT uses WO numbers
        "KIPO": "KR",  # KIPO maps to KR
        "JPO": "JP",  # JPO maps to JP
        "EPO": "EP",  # EPO maps to EP
    }

    db_country = country_mapping.get(country_code, country_code)

    query = select(ForeignPatentMaster)
    conditions = [ForeignPatentMaster.country_code == db_country]

    # Query filter (title/abstract)
    if request.query:
        conditions.append(
            or_(
                ForeignPatentMaster.invention_name.ilike(f"%{request.query}%"),
                ForeignPatentMaster.abstract.ilike(f"%{request.query}%"),
            )
        )

    # Keywords filter
    if request.keywords:
        keywords_list = request.keywords.lower().split()
        for keyword in keywords_list:
            conditions.append(
                or_(
                    ForeignPatentMaster.invention_name.ilike(f"%{keyword}%"),
                    ForeignPatentMaster.abstract.ilike(f"%{keyword}%"),
                )
            )

    # Application number filter
    if request.application_number:
        conditions.append(ForeignPatentMaster.application_number.ilike(f"%{request.application_number}%"))

    # Filing date filter
    if request.filing_date:
        conditions.append(ForeignPatentMaster.application_date == request.filing_date)

    # Date range filter
    if request.date_range_start:
        conditions.append(ForeignPatentMaster.application_date >= request.date_range_start)
    if request.date_range_end:
        conditions.append(ForeignPatentMaster.application_date <= request.date_range_end)

    query = query.where(and_(*conditions))

    # Get total count
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar() or 0

    # Apply sorting
    if request.sort_by == "date":
        query = query.order_by(desc(ForeignPatentMaster.application_date))
    elif request.sort_by == "title":
        query = query.order_by(ForeignPatentMaster.invention_name)
    else:  # relevance
        query = query.order_by(desc(ForeignPatentMaster.application_date))

    # Get results
    result = await db.execute(query)
    patents = result.scalars().all()

    # Convert to dict format
    patent_dicts = [
        {
            "id": p.document_number,
            "patent_id": p.document_number,
            "title": p.invention_name,
            "abstract": p.abstract,
            "filing_date": str(p.application_date) if p.application_date else None,
            "publication_date": str(p.publication_date) if p.publication_date else None,
            "registration_date": str(p.registration_date) if p.registration_date else None,
            "status": p.patent_status,
            "country": p.country_code,
            "application_number": p.application_number,
        }
        for p in patents
    ]

    return patent_dicts, total


def _calculate_country_statistics(patents: List[Dict[str, Any]], country_code: str) -> Dict[str, Any]:
    """Calculate country-specific statistics"""
    statistics = {
        f"total_{country_code.lower()}_count": len(patents),
    }

    if patents:
        # Status distribution
        status_counts: Dict[str, int] = {}
        for patent in patents:
            status = patent.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1

        statistics[f"{country_code.lower()}_by_status"] = status_counts

        # Date range
        dates = []
        for patent in patents:
            pub_date = patent.get('publication_date') or patent.get('filing_date')
            if pub_date:
                try:
                    if isinstance(pub_date, str):
                        dates.append(datetime.fromisoformat(pub_date.replace('Z', '+00:00')))
                except Exception:
                    pass

        if dates:
            statistics["earliest_date"] = min(dates).isoformat()
            statistics["latest_date"] = max(dates).isoformat()

    return statistics
