from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import get_patent_crud
from app.schemas.patent import PatentSearch
from shared.database import get_db

router = APIRouter()


@router.post("/search", response_model=dict)
async def search_patents(
    search_params: PatentSearch, db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Search patents based on criteria.
    """
    patent_crud = get_patent_crud(db)
    patents, total = await patent_crud.advanced_search(search_params)

    return {"patents": patents, "total": total}
