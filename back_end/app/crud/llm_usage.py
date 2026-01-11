from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models import LLMUsage


class CRUDLLMUsage:
    async def create(self, db: AsyncSession, obj_in: dict) -> LLMUsage:
        db_obj = LLMUsage(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_user(self, db: AsyncSession, user_id: int) -> List[LLMUsage]:
        result = await db.execute(select(LLMUsage).filter(LLMUsage.user_id == user_id))
        return result.scalars().all()

    async def get_total_cost_by_user(self, db: AsyncSession, user_id: int) -> int:
        result = await db.execute(
            select(func.sum(LLMUsage.cost_usd)).filter(LLMUsage.user_id == user_id)
        )
        return result.scalar() or 0


llm_usage = CRUDLLMUsage()
