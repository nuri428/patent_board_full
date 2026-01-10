from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database import get_db
from back_end.app.crud import get_patent_crud
from back_end.app.schemas import Patent, PatentSearchRequest, PatentSearchResponse, PatentDetail
from back_end.app.api.v1.endpoints.auth import get_current_user
from typing import List, Optional
import time

router = APIRouter()


@router.get("/", response_model=List[Patent])
async def get_patents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get patents with pagination and filtering"""
    patent_crud = get_patent_crud(db)
    patents = await patent_crud.get_multi(
        skip=skip, 
        limit=limit, 
        status=status_filter
    )
    return patents


@router.get("/{patent_id}", response_model=PatentDetail)
async def get_patent(
    patent_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get patent details by ID"""
    patent_crud = get_patent_crud(db)
    patent = await patent_crud.get(patent_id)
    
    if not patent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patent not found"
        )
    
    # Get similar patents
    similar_patents = await patent_crud.get_similar_patents(patent_id, limit=5)
    
    return PatentDetail(
        **patent.__dict__,
        similar_patents=similar_patents
    )


@router.get("/number/{patent_number}", response_model=Patent)
async def get_patent_by_number(
    patent_number: str,
    db: AsyncSession = Depends(get_db)
):
    """Get patent by patent number"""
    patent_crud = get_patent_crud(db)
    patent = await patent_crud.get_by_number(patent_number)
    
    if not patent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patent not found"
        )
    
    return patent


@router.post("/search", response_model=PatentSearchResponse)
async def search_patents(
    search_params: PatentSearchRequest,
    current_user: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search patents with various query types"""
    patent_crud = get_patent_crud(db)
    
    # Record start time for performance tracking
    start_time = time.time()
    
    # Perform search
    patents, total_count = await patent_crud.search(
        query=search_params.query,
        query_type=search_params.query_type,
        filters=search_params.filters,
        limit=search_params.limit,
        offset=search_params.offset
    )
    
    # Log search query for analytics
    execution_time_ms = int((time.time() - start_time) * 1000)
    await patent_crud.log_search_query(
        user_id=current_user,
        query_text=search_params.query,
        query_type=search_params.query_type,
        filters=search_params.filters,
        results_count=total_count,
        execution_time_ms=execution_time_ms
    )
    
    return PatentSearchResponse(
        patents=patents,
        total_count=total_count,
        query=search_params.query,
        query_type=search_params.query_type,
        execution_time_ms=execution_time_ms
    )


@router.get("/{patent_id}/similar", response_model=List[Patent])
async def get_similar_patents(
    patent_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get patents similar to the given patent"""
    patent_crud = get_patent_crud(db)
    
    # Check if patent exists
    patent = await patent_crud.get(patent_id)
    if not patent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patent not found"
        )
    
    similar_patents = await patent_crud.get_similar_patents(patent_id, limit)
    return similar_patents


@router.post("/", response_model=Patent)
async def create_patent(
    patent_data: Patent,
    current_user: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new patent (admin only)"""
    patent_crud = get_patent_crud(db)
    
    # Check if patent already exists
    existing = await patent_crud.get_by_number(patent_data.patent_number)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patent with this number already exists"
        )
    
    # Create patent
    new_patent = await patent_crud.create(patent_data)
    return new_patent


@router.put("/{patent_id}", response_model=Patent)
async def update_patent(
    patent_id: int,
    patent_data: Patent,
    current_user: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update patent (admin only)"""
    patent_crud = get_patent_crud(db)
    
    # Check if patent exists
    patent = await patent_crud.get(patent_id)
    if not patent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patent not found"
        )
    
    # Update patent
    updated_patent = await patent_crud.update(patent_id, patent_data)
    return updated_patent


@router.delete("/{patent_id}")
async def delete_patent(
    patent_id: int,
    current_user: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete patent (admin only)"""
    patent_crud = get_patent_crud(db)
    
    # Check if patent exists
    patent = await patent_crud.get(patent_id)
    if not patent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patent not found"
        )
    
    # Delete patent
    success = await patent_crud.delete(patent_id)
    if success:
        return {"message": "Patent deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete patent"
        )