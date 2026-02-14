"""
Patents Search API Endpoints

Multi-source patent search with filtering, pagination, and sorting.
Searches within analyzed_patents JSON field from PatentAnalysis model.
"""

from typing import Any, List, Dict, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc
from pydantic import BaseModel, Field, field_validator

from app.crud.crud_patent_analysis import get_patent_analysis_crud
from app.api import deps
from app.models import User
from app.models.patent_analysis import PatentSource, PatentAnalysis
from shared.database import get_db

router = APIRouter(prefix="/api/v1/patents", tags=["patents", "search"])


class PatentSearchRequest(BaseModel):
    """Request model for patent search"""
    query: str = Field(..., min_length=2, description="Search query")
    source: Optional[PatentSource] = Field(default=None, description="Filter by patent source")
    keywords: Optional[str] = Field(default=None, description="Additional keywords to filter results")
    date_range_start: Optional[datetime] = Field(default=None, description="Filter patents from this date")
    date_range_end: Optional[datetime] = Field(default=None, description="Filter patents until this date")
    confidence_min: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Minimum confidence score")
    confidence_max: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Maximum confidence score")
    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    per_page: int = Field(default=20, ge=1, le=100, description="Results per page")
    sort_by: str = Field(default="date", description="Sort by: date, confidence, source, relevance")

    @field_validator('sort_by')
    @classmethod
    def validate_sort_by(cls, v: str) -> str:
        allowed_sorts = ['date', 'confidence', 'source', 'relevance']
        if v not in allowed_sorts:
            raise ValueError(f"sort_by must be one of {allowed_sorts}")
        return v


class PatentSearchResult(BaseModel):
    """Response model for patent search"""
    patents: List[Dict[str, Any]] = Field(default_factory=list, description="List of patent objects")
    total_count: int = Field(default=0, description="Total number of patents matching the search")
    page: int = Field(default=1, description="Current page number")
    per_page: int = Field(default=20, description="Number of results per page")
    total_pages: int = Field(default=0, description="Total number of pages")
    has_next: bool = Field(default=False, description="Whether there is a next page")
    has_previous: bool = Field(default=False, description="Whether there is a previous page")
    filters_applied: Dict[str, Any] = Field(default_factory=dict, description="Summary of filters applied")


class PatentDetail(BaseModel):
    """Response model for single patent detail"""
    patent: Dict[str, Any] = Field(..., description="Patent object with all details")
    source: Optional[str] = Field(default=None, description="Patent source")
    analysis_id: Optional[str] = Field(default=None, description="Parent analysis ID")


@router.post("/search", response_model=PatentSearchResult, status_code=status.HTTP_200_OK)
async def search_patents(
    request: PatentSearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Search patents with multi-source support and advanced filtering.

    Features:
    - Multi-source search across KIPRIS, USPTO, EPO, WIPO, JPO, CNIPA
    - Keyword filtering within title, abstract, and claims
    - Date range filtering by publication/filing date
    - Confidence score filtering
    - Pagination with metadata
    - Sorting by date, confidence, source, or relevance

    Authentication: Required (JWT token)
    Authorization: User can only search their own patent analyses
    """
    crud = get_patent_analysis_crud(db)

    # Build base query for user's patent analyses
    filters = [PatentAnalysis.user_id == current_user.id]

    # Apply source filter
    if request.source:
        filters.append(PatentAnalysis.patent_source == request.source.value)

    # Apply confidence range filter
    if request.confidence_min is not None:
        filters.append(PatentAnalysis.confidence_score >= request.confidence_min)
    if request.confidence_max is not None:
        filters.append(PatentAnalysis.confidence_score <= request.confidence_max)

    # Apply date range filter on analysis creation date
    if request.date_range_start:
        filters.append(PatentAnalysis.created_at >= request.date_range_start)
    if request.date_range_end:
        filters.append(PatentAnalysis.created_at <= request.date_range_end)

    # Execute query to get matching analyses
    query = select(PatentAnalysis).where(and_(*filters))

    # Apply sorting
    if request.sort_by == "date":
        query = query.order_by(desc(PatentAnalysis.created_at))
    elif request.sort_by == "confidence":
        query = query.order_by(desc(PatentAnalysis.confidence_score))
    elif request.sort_by == "source":
        query = query.order_by(PatentAnalysis.patent_source)
    else:  # relevance - default to created_at desc
        query = query.order_by(desc(PatentAnalysis.created_at))

    # Get all matching analyses (pagination applied to patent results, not analyses)
    result = await db.execute(query)
    analyses = result.scalars().all()

    # Extract patents from analyses
    all_patents = []
    for analysis in analyses:
        if analysis.analyzed_patents:
            # Source filter for individual patents
            if request.source:
                # Filter patents by source within the analyzed_patents JSON
                source_patents = [
                    p for p in analysis.analyzed_patents
                    if p.get('source', '').lower() == request.source.value
                ]
            else:
                source_patents = analysis.analyzed_patents

            # Query filter
            if request.query:
                query_lower = request.query.lower()
                filtered_patents = []
                for patent in source_patents:
                    # Search in title, abstract, number, and claims
                    searchable_text = " ".join([
                        patent.get('title', ''),
                        patent.get('abstract', ''),
                        patent.get('number', ''),
                        patent.get('claims', ''),
                        patent.get('description', '')
                    ]).lower()

                    if query_lower in searchable_text:
                        filtered_patents.append(patent)
                source_patents = filtered_patents

            # Keywords filter
            if request.keywords:
                keywords_list = request.keywords.lower().split()
                keyword_filtered = []
                for patent in source_patents:
                    searchable_text = " ".join([
                        patent.get('title', ''),
                        patent.get('abstract', ''),
                        patent.get('number', ''),
                        patent.get('claims', '')
                    ]).lower()

                    if all(keyword in searchable_text for keyword in keywords_list):
                        keyword_filtered.append(patent)
                source_patents = keyword_filtered

            # Patent-level date filter
            if request.date_range_start or request.date_range_end:
                date_filtered = []
                for patent in source_patents:
                    pub_date = patent.get('publication_date')
                    if pub_date:
                        try:
                            # Try to parse the date (multiple formats)
                            if isinstance(pub_date, str):
                                # Try ISO format
                                try:
                                    pub_datetime = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                                except ValueError:
                                    # Try other common formats
                                    try:
                                        pub_datetime = datetime.strptime(pub_date, '%Y-%m-%d')
                                    except ValueError:
                                        pub_datetime = None
                            else:
                                pub_datetime = pub_date

                            if pub_datetime:
                                if request.date_range_start and pub_datetime < request.date_range_start:
                                    continue
                                if request.date_range_end and pub_datetime > request.date_range_end:
                                    continue
                                date_filtered.append(patent)
                        except Exception:
                            pass
                source_patents = date_filtered

            all_patents.extend(source_patents)

    # Remove duplicates based on patent ID
    seen_patent_ids = set()
    unique_patents = []
    for patent in all_patents:
        patent_id = patent.get('number') or patent.get('id') or patent.get('patent_id')
        if patent_id and patent_id not in seen_patent_ids:
            unique_patents.append(patent)
            seen_patent_ids.add(patent_id)
        elif not patent_id:  # Include patents without ID
            unique_patents.append(patent)

    # Calculate total count
    total_count = len(unique_patents)

    # Apply pagination to patent results
    total_pages = (total_count + request.per_page - 1) // request.per_page
    offset = (request.page - 1) * request.per_page
    paginated_patents = unique_patents[offset:offset + request.per_page]

    # Build filters summary
    filters_applied = {
        "query": request.query,
    }
    if request.source:
        filters_applied["source"] = request.source.value
    if request.keywords:
        filters_applied["keywords"] = request.keywords
    if request.date_range_start or request.date_range_end:
        filters_applied["date_range"] = {
            "start": request.date_range_start.isoformat() if request.date_range_start else None,
            "end": request.date_range_end.isoformat() if request.date_range_end else None,
        }
    if request.confidence_min is not None or request.confidence_max is not None:
        filters_applied["confidence"] = {
            "min": request.confidence_min,
            "max": request.confidence_max,
        }

    return PatentSearchResult(
        patents=paginated_patents,
        total_count=total_count,
        page=request.page,
        per_page=request.per_page,
        total_pages=total_pages,
        has_next=request.page < total_pages,
        has_previous=request.page > 1,
        filters_applied=filters_applied,
    )


@router.get("/{patent_id}", response_model=PatentDetail, status_code=status.HTTP_200_OK)
async def get_patent_details(
    patent_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get detailed information for a specific patent.

    Searches within user's patent analyses to find the patent by ID.
    Returns complete patent information including source and analysis metadata.

    Authentication: Required (JWT token)
    Authorization: User can only view patents from their own analyses
    """
    crud = get_patent_analysis_crud(db)

    # Get all user's analyses
    analyses = await crud.get_by_user_id(current_user.id, skip=0, limit=10000)

    # Search for the patent
    found_patent = None
    source = None
    analysis_id = None

    for analysis in analyses:
        if analysis.analyzed_patents:
            for patent in analysis.analyzed_patents:
                patent_number = patent.get('number') or patent.get('id') or patent.get('patent_id')
                if patent_number == patent_id:
                    found_patent = patent
                    source = analysis.patent_source
                    analysis_id = analysis.id
                    break
        if found_patent:
            break

    if not found_patent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patent with ID '{patent_id}' not found in your analyses"
        )

    return PatentDetail(
        patent=found_patent,
        source=source,
        analysis_id=analysis_id,
    )


@router.get("/sources/list", response_model=List[str])
async def get_available_patent_sources(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get list of available patent sources for the current user.

    Returns a list of patent sources that the user has patents from.
    """
    return [source.value for source in PatentSource]


@router.get("/search/suggestions", response_model=List[str])
async def get_search_suggestions(
    query: str = Query(..., min_length=1, description="Partial query for suggestions"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get search suggestions based on existing patents.

    Returns a list of suggested keywords/phrases based on patent titles and abstracts.
    """
    crud = get_patent_analysis_crud(db)

    # Get user's analyses
    analyses = await crud.get_by_user_id(current_user.id, skip=0, limit=1000)

    # Extract keywords from patents
    keywords_set = set()
    query_lower = query.lower()

    for analysis in analyses:
        if analysis.analyzed_patents:
            for patent in analysis.analyzed_patents:
                # Extract words from title and abstract
                title = patent.get('title', '')
                abstract = patent.get('abstract', '')

                # Split into words and filter by query
                for word in (title + ' ' + abstract).split():
                    word = word.strip('.,;:!?()[]{}"\'').lower()
                    if word and len(word) > 2 and query_lower in word:
                        keywords_set.add(word)

    # Return top 10 suggestions
    suggestions = sorted(list(keywords_set))[:10]
    return suggestions
