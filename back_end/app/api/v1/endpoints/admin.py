from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.crud import patent_crud
from app.schemas import PatentCreate, PatentUpdate, Patent
from typing import List
import uuid
from datetime import datetime

router = APIRouter()


@router.post("/", response_model=Patent)
async def create_patent(
    patent: PatentCreate,
    db: AsyncSession = Depends(get_db)
):
    db_patent = await patent_crud.get_by_id(db, patent.patent_id)
    if db_patent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patent with this ID already exists"
        )
    
    created_patent = await patent_crud.create(db, patent)
    return Patent.model_validate(created_patent)


@router.put("/{patent_id}", response_model=Patent)
async def update_patent(
    patent_id: str,
    patent_update: PatentUpdate,
    db: AsyncSession = Depends(get_db)
):
    updated_patent = await patent_crud.update(db, patent_id, patent_update)
    if not updated_patent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patent not found"
        )
    return Patent.model_validate(updated_patent)


@router.delete("/{patent_id}")
async def delete_patent(
    patent_id: str,
    db: AsyncSession = Depends(get_db)
):
    success = await patent_crud.delete(db, patent_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patent not found"
        )
    return {"message": "Patent deleted successfully"}


@router.post("/bulk", response_model=List[Patent])
async def create_patents_bulk(
    patents: List[PatentCreate],
    db: AsyncSession = Depends(get_db)
):
    created_patents = []
    for patent in patents:
        if not patent.patent_id:
            patent.patent_id = str(uuid.uuid4())
        
        existing = await patent_crud.get_by_id(db, patent.patent_id)
        if not existing:
            created_patent = await patent_crud.create(db, patent)
            created_patents.append(Patent.model_validate(created_patent))
    
    return created_patents


@router.get("/statistics")
async def get_patent_statistics(
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import select, func
    from app.models import PatentModel
    
    total_query = select(func.count()).select_from(PatentModel)
    total_result = await db.execute(total_query)
    total_patents = total_result.scalar()
    
    status_query = (
        select(PatentModel.status, func.count(PatentModel.patent_id))
        .group_by(PatentModel.status)
    )
    status_result = await db.execute(status_query)
    status_counts = dict(status_result.all())
    
    assignee_query = (
        select(PatentModel.assignee, func.count(PatentModel.patent_id))
        .where(PatentModel.assignee.isnot(None))
        .group_by(PatentModel.assignee)
        .order_by(func.count(PatentModel.patent_id).desc())
        .limit(10)
    )
    assignee_result = await db.execute(assignee_query)
    top_assignees = dict(assignee_result.all())
    
    return {
        "total_patents": total_patents or 0,
        "status_distribution": status_counts,
        "top_assignees": top_assignees
    }


@router.post("/{patent_id}/status")
async def update_patent_status(
    patent_id: str,
    new_status: str,
    db: AsyncSession = Depends(get_db)
):
    valid_statuses = ["pending", "granted", "expired", "abandoned"]
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    patent_update = PatentUpdate(status=new_status)
    updated_patent = await patent_crud.update(db, patent_id, patent_update)
    
    if not updated_patent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patent not found"
        )
    
    return Patent.model_validate(updated_patent)


@router.get("/export/csv")
async def export_patents_csv(
    db: AsyncSession = Depends(get_db)
):
    patents = await patent_crud.get_all(db, skip=0, limit=10000)
    
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        'Patent ID', 'Title', 'Abstract', 'Status', 
        'Assignee', 'Inventors', 'Filing Date', 'Created At'
    ])
    
    for patent in patents:
        writer.writerow([
            patent.patent_id,
            patent.title,
            patent.abstract,
            patent.status,
            patent.assignee or '',
            '; '.join(patent.inventors or []),
            patent.filing_date.isoformat() if patent.filing_date else '',
            patent.created_at.isoformat()
        ])
    
    output.seek(0)
    return {
        "content": output.getvalue(),
        "filename": f"patents_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    }