from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request
from app.crud.audit import get_audit_crud
from app.api import deps
from app.models import User
from app.crud.patent_db import get_patentdb_crud
from app.schemas.patent import PatentSearch
from shared.database import get_patentdb

router = APIRouter()


@router.post("/search", response_model=dict)
async def search_patents(
    request: Request,
    search_params: PatentSearch,
    db: AsyncSession = Depends(get_patentdb),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Search patents from patent_master (KR) and foreign_patent_master (US/Foreign).
    """
    crud = get_patentdb_crud(db)
    patents, total = await crud.search_all_patents(search_params)

    # Audit Log
    # Note: Use a separate session for audit if needed, but here we use the default db from deps
    # However, patents endpoint uses get_patentdb which might be a different session
    # Let's get a standard db session for audit logs
    from shared.database import get_db

    async for audit_db in get_db():
        audit_crud = get_audit_crud(audit_db)
        await audit_crud.log(
            action="patent_search",
            user_id=current_user.id,
            username=current_user.email,
            resource_type="patent",
            description=f"Searched patents with query: {search_params.query}",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            payload={"params": search_params.model_dump()},
        )
        break

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
