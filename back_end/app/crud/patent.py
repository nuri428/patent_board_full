from typing import List, Optional, Tuple, TYPE_CHECKING
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from app.models import Patent
from app.schemas import PatentSearch

if TYPE_CHECKING:
    from app.schemas import PatentSearch


class PatentCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, id: int) -> Optional[Patent]:
        result = await self.db.execute(select(Patent).filter(Patent.id == id))
        return result.scalars().first()

    async def get_by_patent_id(self, patent_id: str) -> Optional[Patent]:
        result = await self.db.execute(
            select(Patent).filter(Patent.patent_id == patent_id)
        )
        return result.scalars().first()

    async def create(self, obj_in: dict) -> Patent:
        if hasattr(obj_in, "model_dump"):
            obj_in = obj_in.model_dump()
        db_obj = Patent(**obj_in)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, patent_id: str, obj_in: dict) -> Optional[Patent]:
        if hasattr(obj_in, "model_dump"):
            update_data = obj_in.model_dump(exclude_unset=True)
        else:
            update_data = obj_in

        db_obj = await self.get_by_patent_id(patent_id)
        if not db_obj:
            return None

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, patent_id: str) -> bool:
        db_obj = await self.get_by_patent_id(patent_id)
        if not db_obj:
            return False
        await self.db.delete(db_obj)
        await self.db.commit()
        return True

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Patent]:
        result = await self.db.execute(select(Patent).offset(skip).limit(limit))
        return result.scalars().all()

    async def advanced_search(
        self, search_params: "PatentSearch"
    ) -> tuple[List[Patent], int]:
        from sqlalchemy import or_

        query = select(Patent)
        conditions = []

        if search_params.title:
            conditions.append(Patent.title.ilike(f"%{search_params.title}%"))
        if search_params.abstract:
            conditions.append(Patent.abstract.ilike(f"%{search_params.abstract}%"))
        if search_params.assignee:
            conditions.append(Patent.assignee.ilike(f"%{search_params.assignee}%"))
        if search_params.status:
            conditions.append(Patent.status == search_params.status)
        if search_params.filing_date_from:
            conditions.append(Patent.filing_date >= search_params.filing_date_from)
        if search_params.filing_date_to:
            conditions.append(Patent.filing_date <= search_params.filing_date_to)

        if conditions:
            query = query.where(and_(*conditions))

        # Get total count (simplified for now, ideally separate count query)
        count_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0

        query = query.offset(search_params.offset).limit(search_params.limit)
        result = await self.db.execute(query)
        return result.scalars().all(), total


def get_patent_crud(db: AsyncSession) -> PatentCRUD:
    return PatentCRUD(db)
