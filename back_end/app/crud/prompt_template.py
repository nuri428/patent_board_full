from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import PromptTemplate


class CRUDPromptTemplate:
    async def get(self, db: AsyncSession, id: int) -> Optional[PromptTemplate]:
        result = await db.execute(
            select(PromptTemplate).filter(PromptTemplate.id == id)
        )
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[PromptTemplate]:
        result = await db.execute(select(PromptTemplate).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_by_type(
        self, db: AsyncSession, report_type: str
    ) -> List[PromptTemplate]:
        result = await db.execute(
            select(PromptTemplate).filter(
                PromptTemplate.report_type == report_type,
                PromptTemplate.is_active == True,
            )
        )
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj_in: dict) -> PromptTemplate:
        db_obj = PromptTemplate(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


prompt_template = CRUDPromptTemplate()
