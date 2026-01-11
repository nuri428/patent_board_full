from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import ReportVersion


class CRUDReportVersion:
    async def get(self, db: AsyncSession, id: int) -> Optional[ReportVersion]:
        result = await db.execute(select(ReportVersion).filter(ReportVersion.id == id))
        return result.scalars().first()

    async def get_by_report_id(
        self, db: AsyncSession, report_id: int
    ) -> List[ReportVersion]:
        result = await db.execute(
            select(ReportVersion)
            .filter(ReportVersion.report_id == report_id)
            .order_by(ReportVersion.version.desc())
        )
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj_in: dict) -> ReportVersion:
        # Auto-increment version
        result = await db.execute(
            select(ReportVersion)
            .filter(ReportVersion.report_id == obj_in["report_id"])
            .order_by(ReportVersion.version.desc())
        )
        last_version = result.scalars().first()
        new_version = (last_version.version + 1) if last_version else 1

        obj_in["version"] = new_version
        db_obj = ReportVersion(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


report_version = CRUDReportVersion()
