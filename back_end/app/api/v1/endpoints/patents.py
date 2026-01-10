from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.crud import patent_crud
from app.schemas import Patent, PatentSearch, PatentSearchResponse
from typing import List, Optional

router = APIRouter()


@router.get("/", response_model=List[Patent])
async def get_patents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    patents = await patent_crud.get_all(db, skip=skip, limit=limit)
    return [Patent.model_validate(patent) for patent in patents]


@router.get("/{patent_id}", response_model=Patent)
async def get_patent(
    patent_id: str,
    db: AsyncSession = Depends(get_db)
):
    patent = await patent_crud.get_by_id(db, patent_id)
    if not patent:
        raise HTTPException(status_code=404, detail="Patent not found")
    return Patent.model_validate(patent)


@router.post("/search", response_model=PatentSearchResponse)
async def search_patents(
    search_params: PatentSearch,
    db: AsyncSession = Depends(get_db)
):
    patents, total_count = await patent_crud.advanced_search(db, search_params)
    
    patent_schemas = [Patent.model_validate(patent) for patent in patents]
    
    page = search_params.offset // search_params.limit + 1
    total_pages = (total_count + search_params.limit - 1) // search_params.limit
    has_next = page < total_pages
    has_prev = page > 1
    
    return PatentSearchResponse(
        patents=patent_schemas,
        total_count=total_count,
        page=page,
        page_size=search_params.limit,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev
    )


@router.get("/search/simple", response_model=List[Patent])
async def simple_search_patents(
    query: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    patents = await patent_crud.search(db, query, skip=skip, limit=limit)
    return [Patent.model_validate(patent) for patent in patents]