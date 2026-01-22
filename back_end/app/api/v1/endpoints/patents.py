from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.patent_db import get_patentdb_crud
from app.schemas.patent import PatentSearch
from shared.database import get_patentdb

router = APIRouter()


@router.post("/search", response_model=dict)
async def search_patents(
    search_params: PatentSearch, db: AsyncSession = Depends(get_patentdb)
) -> Any:
    """
    Search patents from patent_master (KR) and foreign_patent_master (US/Foreign).
    """
    crud = get_patentdb_crud(db)
    patents, total = await crud.search_all_patents(search_params)

    return {"patents": patents, "total": total}


@router.get("/{patent_id}", response_model=dict)
async def get_patent_detail(
    patent_id: str, db: AsyncSession = Depends(get_patentdb)
) -> Any:
    """
    Get patent detail by ID (application_number for KR, document_number for foreign).
    """
    crud = get_patentdb_crud(db)
    patent = await crud.get_patent_detail(patent_id)

    if not patent:
        raise HTTPException(status_code=404, detail="Patent not found")

    return patent
