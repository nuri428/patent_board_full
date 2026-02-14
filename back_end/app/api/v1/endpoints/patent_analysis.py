"""
Patent Analysis API Endpoints

REST endpoints for managing patent analyses with multi-source patent support.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request

from app.crud.patent_analysis import PatentAnalysisCRUD, get_patent_analysis_crud
from app.api import deps
from app.models import User
from app.schemas.patent_analysis import (
    PatentAnalysisCreate,
    PatentAnalysisResponse,
    PatentAnalysisUpdate,
    PatentAnalysisListResponse,
    MultiSourcePatentResponse,
    PatentSourceCountResponse,
    PatentAnalysisSearchParams,
)
from app.models.patent_analysis import PatentSource, PatentSourceType
from shared.database import get_db

router = APIRouter()


@router.post("/", response_model=PatentAnalysisResponse)
async def create_patent_analysis(
    request: Request,
    analysis_data: PatentAnalysisCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new patent analysis record.

    Stores analysis results from multi-source patent searches including:
    - KIPRIS (Korean patents)
    - USPTO (US patents)
    - EPO (European patents)
    - KIPO (Korean Intellectual Property Office)
    - WIPO (World Intellectual Property Organization)
    - JPO (Japan Patent Office)
    - CNIPA (China National Intellectual Property Administration)
    """
    crud = get_patent_analysis_crud(db)

    # Ensure user_id is set from authenticated user
    analysis_data.user_id = current_user.id

    patent_analysis = await crud.create(
        session_id=analysis_data.session_id,
        user_id=analysis_data.user_id,
        analyzed_patents=analysis_data.analyzed_patents,
        patent_source=analysis_data.patent_source,
        confidence_score=analysis_data.confidence_score,
        relevant_sections=analysis_data.relevant_sections,
        analysis_metadata=analysis_data.analysis_metadata,
        source_type=analysis_data.source_type,
    )

    return patent_analysis


@router.get("/{analysis_id}", response_model=PatentAnalysisResponse)
async def get_patent_analysis(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a specific patent analysis by ID.
    """
    crud = get_patent_analysis_crud(db)
    patent_analysis = await crud.get_by_id(analysis_id)

    if not patent_analysis:
        raise HTTPException(status_code=404, detail="Patent analysis not found")

    # Check if user owns this analysis or is admin
    if patent_analysis.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this analysis")

    return patent_analysis


@router.get("/session/{session_id}", response_model=PatentAnalysisListResponse)
async def get_patent_analyses_by_session(
    session_id: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all patent analyses for a specific session.
    """
    crud = get_patent_analysis_crud(db)
    analyses = await crud.get_by_session_id(session_id)

    # Filter by user ownership
    filtered_analyses = [
        a for a in analyses if a.user_id == current_user.id or current_user.role == "admin"
    ]

    total_count = len(filtered_analyses)
    paginated_analyses = filtered_analyses[skip : skip + limit]

    return PatentAnalysisListResponse(
        total_count=total_count,
        analyses=paginated_analyses,
        skip=skip,
        limit=limit,
    )


@router.get("/user/{user_id}", response_model=PatentAnalysisListResponse)
async def get_patent_analyses_by_user(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all patent analyses for a specific user.
    """
    # Check authorization
    if user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access these analyses")

    crud = get_patent_analysis_crud(db)
    analyses = await crud.get_by_user_id(user_id, skip=skip, limit=limit)

    # Get total count
    all_analyses = await crud.get_by_user_id(user_id)
    total_count = len(all_analyses)

    return PatentAnalysisListResponse(
        total_count=total_count,
        analyses=analyses,
        skip=skip,
        limit=limit,
    )


@router.get("/source/{patent_source}", response_model=PatentAnalysisListResponse)
async def get_patent_analyses_by_source(
    patent_source: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all patent analyses from a specific source.

    Available sources: kipris, uspto, epo, kipo, wipo, jpo, cnipa, other
    """
    try:
        source_enum = PatentSource(patent_source.lower())
    except ValueError:
        raise HTTPException(
            status_code=400, detail=f"Invalid source. Must be one of: {[s.value for s in PatentSource]}"
        )

    crud = get_patent_analysis_crud(db)
    analyses = await crud.get_by_patent_source(source_enum, skip=skip, limit=limit)

    # Filter by user ownership
    filtered_analyses = [
        a for a in analyses if a.user_id == current_user.id or current_user.role == "admin"
    ]

    total_count = len(filtered_analyses)
    paginated_analyses = filtered_analyses[skip : skip + limit]

    return PatentAnalysisListResponse(
        total_count=total_count,
        analyses=paginated_analyses,
        skip=skip,
        limit=limit,
    )


@router.put("/{analysis_id}", response_model=PatentAnalysisResponse)
async def update_patent_analysis(
    analysis_id: str,
    analysis_update: PatentAnalysisUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an existing patent analysis.
    """
    crud = get_patent_analysis_crud(db)
    patent_analysis = await crud.get_by_id(analysis_id)

    if not patent_analysis:
        raise HTTPException(status_code=404, detail="Patent analysis not found")

    # Check authorization
    if patent_analysis.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update this analysis")

    updated_analysis = await crud.update(
        analysis_id=analysis_id,
        analyzed_patents=analysis_update.analyzed_patents,
        patent_source=analysis_update.patent_source,
        confidence_score=analysis_update.confidence_score,
        relevant_sections=analysis_update.relevant_sections,
        analysis_metadata=analysis_update.analysis_metadata,
        source_type=analysis_update.source_type,
    )

    return updated_analysis


@router.delete("/{analysis_id}")
async def delete_patent_analysis(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a patent analysis.
    """
    crud = get_patent_analysis_crud(db)
    patent_analysis = await crud.get_by_id(analysis_id)

    if not patent_analysis:
        raise HTTPException(status_code=404, detail="Patent analysis not found")

    # Check authorization
    if patent_analysis.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this analysis")

    success = await crud.delete(analysis_id)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete patent analysis")

    return {"message": "Patent analysis deleted successfully"}


@router.post("/search", response_model=PatentAnalysisListResponse)
async def search_patent_analyses(
    search_params: PatentAnalysisSearchParams,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Search patent analyses with multiple filters.

    Supports filtering by:
    - user_id
    - session_id
    - patent_source
    - min_confidence
    - source_type
    """
    crud = get_patent_analysis_crud(db)

    # Add user_id filter from authenticated user if not provided
    if not search_params.user_id:
        search_params.user_id = current_user.id

    analyses = await crud.search(
        user_id=search_params.user_id,
        session_id=search_params.session_id,
        patent_source=search_params.patent_source,
        min_confidence=search_params.min_confidence,
        source_type=search_params.source_type,
        skip=search_params.skip,
        limit=search_params.limit,
    )

    # Get total count (simplified, in production use a separate count query)
    all_analyses = await crud.search(
        user_id=search_params.user_id,
        session_id=search_params.session_id,
        patent_source=search_params.patent_source,
        min_confidence=search_params.min_confidence,
        source_type=search_params.source_type,
        skip=0,
        limit=10000,
    )
    total_count = len(all_analyses)

    return PatentAnalysisListResponse(
        total_count=total_count,
        analyses=analyses,
        skip=search_params.skip,
        limit=search_params.limit,
    )


@router.get("/multi-source/session/{session_id}", response_model=MultiSourcePatentResponse)
async def get_multi_source_patents(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all patents from all sources for a session, grouped by source.

    Returns patents organized by their source (KIPRIS, USPTO, EPO, etc.).
    """
    crud = get_patent_analysis_crud(db)
    patents_by_source = await crud.get_multi_source_patents(session_id)

    total_patents = sum(len(patents) for patents in patents_by_source.values())
    sources_count = len(patents_by_source)

    return MultiSourcePatentResponse(
        patents_by_source=patents_by_source,
        total_patents=total_patents,
        sources_count=sources_count,
    )


@router.get("/statistics/source-counts", response_model=PatentSourceCountResponse)
async def get_patent_source_counts(
    user_id: int = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get count of patent analyses grouped by source.

    If user_id is not provided, counts for the authenticated user are returned.
    """
    # Use authenticated user's ID if not provided
    if user_id is None:
        user_id = current_user.id
    elif user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access these statistics")

    crud = get_patent_analysis_crud(db)
    source_counts = await crud.get_patent_count_by_source(user_id=user_id)
    total_analyses = sum(source_counts.values())

    return PatentSourceCountResponse(
        source_counts=source_counts, total_analyses=total_analyses
    )
