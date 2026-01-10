from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from typing import Optional, List, Dict, Any
from back_end.app.models import Patent, SearchQuery
from back_end.app.schemas import PatentCreate, PatentUpdate
import json


class PatentCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, patent_id: int) -> Optional[Patent]:
        """Get patent by ID"""
        result = await self.db.execute(
            select(Patent).where(Patent.id == patent_id)
        )
        return result.scalar_one_or_none()

    async def get_by_number(self, patent_number: str) -> Optional[Patent]:
        """Get patent by patent number"""
        result = await self.db.execute(
            select(Patent).where(Patent.patent_number == patent_number)
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Patent]:
        """Get multiple patents with pagination"""
        query = select(Patent)
        if status:
            query = query.where(Patent.status == status)
        
        query = query.offset(skip).limit(limit).order_by(Patent.filing_date.desc())
        result = await self.db.execute(query)
        return result.scalars().all()

    async def search(
        self,
        query: str,
        query_type: str = "keyword",
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 25,
        offset: int = 0
    ) -> tuple[List[Patent], int]:
        """Search patents with various query types"""
        
        # Build base query
        base_query = select(Patent)
        count_query = select(func.count(Patent.id))
        
        # Apply filters
        if filters:
            if filters.get("status"):
                base_query = base_query.where(Patent.status == filters["status"])
                count_query = count_query.where(Patent.status == filters["status"])
            
            if filters.get("assignee"):
                base_query = base_query.where(Patent.assignee.ilike(f"%{filters['assignee']}%"))
                count_query = count_query.where(Patent.assignee.ilike(f"%{filters['assignee']}%"))
            
            if filters.get("patent_type"):
                base_query = base_query.where(Patent.patent_type == filters["patent_type"])
                count_query = count_query.where(Patent.patent_type == filters["patent_type"])
        
        # Apply search query
        if query_type == "keyword":
            search_condition = or_(
                Patent.title.ilike(f"%{query}%"),
                Patent.abstract.ilike(f"%{query}%"),
                Patent.description.ilike(f"%{query}%"),
                Patent.keywords.ilike(f"%{query}%")
            )
            base_query = base_query.where(search_condition)
            count_query = count_query.where(search_condition)
        
        # Get total count
        total_result = await self.db.execute(count_query)
        total_count = total_result.scalar()
        
        # Apply pagination and ordering
        base_query = base_query.offset(offset).limit(limit)
        base_query = base_query.order_by(desc(Patent.filing_date))
        
        result = await self.db.execute(base_query)
        patents = result.scalars().all()
        
        return patents, total_count

    async def create(self, patent_create: PatentCreate) -> Patent:
        """Create new patent"""
        db_patent = Patent(
            patent_number=patent_create.patent_number,
            title=patent_create.title,
            abstract=patent_create.abstract,
            description=patent_create.description,
            assignee=patent_create.assignee,
            filing_date=patent_create.filing_date,
            publication_date=patent_create.publication_date,
            grant_date=patent_create.grant_date,
            status=patent_create.status,
            patent_type=patent_create.patent_type,
            classification=patent_create.classification,
            inventors=json.dumps(patent_create.inventors) if patent_create.inventors else None,
            claims=json.dumps(patent_create.claims) if patent_create.claims else None,
            citations=json.dumps(patent_create.citations) if patent_create.citations else None,
            keywords=json.dumps(patent_create.keywords) if patent_create.keywords else None,
        )
        
        self.db.add(db_patent)
        await self.db.commit()
        await self.db.refresh(db_patent)
        return db_patent

    async def update(
        self, 
        patent_id: int, 
        patent_update: PatentUpdate
    ) -> Optional[Patent]:
        """Update patent"""
        db_patent = await self.get(patent_id)
        if not db_patent:
            return None
        
        update_data = patent_update.model_dump(exclude_unset=True)
        
        # Handle JSON fields
        json_fields = ["inventors", "claims", "citations", "keywords"]
        for field in json_fields:
            if field in update_data and update_data[field] is not None:
                update_data[field] = json.dumps(update_data[field])
        
        for field, value in update_data.items():
            setattr(db_patent, field, value)
        
        await self.db.commit()
        await self.db.refresh(db_patent)
        return db_patent

    async def delete(self, patent_id: int) -> bool:
        """Delete patent"""
        db_patent = await self.get(patent_id)
        if not db_patent:
            return False
        
        await self.db.delete(db_patent)
        await self.db.commit()
        return True

    async def get_similar_patents(
        self, 
        patent_id: int, 
        limit: int = 10
    ) -> List[Patent]:
        """Get similar patents based on classification and keywords"""
        patent = await self.get(patent_id)
        if not patent or not patent.classification:
            return []
        
        # Find patents with same classification
        query = select(Patent).where(
            and_(
                Patent.id != patent_id,
                Patent.classification == patent.classification
            )
        ).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def log_search_query(
        self,
        user_id: int,
        query_text: str,
        query_type: str,
        filters: Optional[Dict[str, Any]],
        results_count: int,
        execution_time_ms: int
    ) -> SearchQuery:
        """Log search query for analytics"""
        search_query = SearchQuery(
            user_id=user_id,
            query_text=query_text,
            query_type=query_type,
            filters=json.dumps(filters) if filters else None,
            results_count=results_count,
            execution_time_ms=execution_time_ms
        )
        
        self.db.add(search_query)
        await self.db.commit()
        await self.db.refresh(search_query)
        return search_query

    async def get_recent_searches(
        self, 
        user_id: int, 
        limit: int = 10
    ) -> List[SearchQuery]:
        """Get recent searches by user"""
        result = await self.db.execute(
            select(SearchQuery)
            .where(SearchQuery.user_id == user_id)
            .order_by(desc(SearchQuery.created_at))
            .limit(limit)
        )
        return result.scalars().all()


# Helper function to get patent CRUD instance
def get_patent_crud(db: AsyncSession) -> PatentCRUD:
    return PatentCRUD(db)