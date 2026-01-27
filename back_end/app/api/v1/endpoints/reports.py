from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '..', '..', '..', 'shared'))
from shared.database import get_db
from app.crud.report_version import report_version as version_crud
from app.api import deps
from app.models import User

router = APIRouter()


@router.post("/generate")
async def generate_report():
    return {"message": "Generate report endpoint"}


@router.get("/{report_id}/versions")
async def get_report_versions(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Get all versions of a report.
    """
    versions = await version_crud.get_by_report_id(db, report_id=report_id)
    return versions


@router.get("/{report_id}")
async def get_report(report_id: str):
    return {"message": f"Get report {report_id}"}


@router.get("/")
async def list_reports(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    from app.crud.report import get_report_crud

    crud = get_report_crud(db)
    reports = await crud.get_multi(skip=skip, limit=limit, owner_id=current_user.id)
    return reports
