from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional, List, Dict, Any
from back_end.app.models import Report, Patent, User, SearchQuery, ReportAnalytics
from back_end.app.schemas import SystemMetrics, UserAnalytics, PatentAnalytics
from datetime import datetime, timedelta


class AnalyticsCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_system_metrics(self) -> SystemMetrics:
        """Get system-wide metrics"""
        # Get total counts
        patents_result = await self.db.execute(select(func.count(Patent.id)))
        reports_result = await self.db.execute(select(func.count(Report.id)))
        users_result = await self.db.execute(
            select(func.count(User.id)).where(User.is_active == True)
        )
        
        # Get daily searches (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        daily_searches_result = await self.db.execute(
            select(func.count(SearchQuery.id))
            .where(SearchQuery.created_at >= yesterday)
        )
        
        # Get average response time (last 100 searches)
        avg_time_result = await self.db.execute(
            select(func.avg(SearchQuery.execution_time_ms))
            .order_by(desc(SearchQuery.created_at))
            .limit(100)
        )
        
        total_patents = patents_result.scalar() or 0
        total_reports = reports_result.scalar() or 0
        active_users = users_result.scalar() or 0
        daily_searches = daily_searches_result.scalar() or 0
        avg_response_time = avg_time_result.scalar()
        
        return SystemMetrics(
            total_patents=total_patents,
            total_reports=total_reports,
            active_users=active_users,
            daily_searches=daily_searches,
            average_response_time_ms=float(avg_response_time) if avg_response_time else None,
            database_connections=1,  # This would come from connection pool monitoring
            uptime_hours=24.0,  # This would come from application monitoring
            last_updated=datetime.utcnow()
        )

    async def get_user_analytics(self, user_id: int) -> UserAnalytics:
        """Get analytics for specific user"""
        # Get user's search count
        searches_result = await self.db.execute(
            select(func.count(SearchQuery.id))
            .where(SearchQuery.user_id == user_id)
        )
        
        # Get user's report count
        reports_result = await self.db.execute(
            select(func.count(Report.id))
            .where(Report.owner_id == user_id)
        )
        
        # Get average search time
        avg_time_result = await self.db.execute(
            select(func.avg(SearchQuery.execution_time_ms))
            .where(SearchQuery.user_id == user_id)
        )
        
        # Get last activity
        last_search_result = await self.db.execute(
            select(SearchQuery.created_at)
            .where(SearchQuery.user_id == user_id)
            .order_by(desc(SearchQuery.created_at))
            .limit(1)
        )
        
        total_searches = searches_result.scalar() or 0
        total_reports = reports_result.scalar() or 0
        avg_time = avg_time_result.scalar()
        last_activity = last_search_result.scalar() or datetime.utcnow()
        
        return UserAnalytics(
            user_id=user_id,
            total_searches=total_searches,
            total_reports_generated=total_reports,
            average_search_time_ms=float(avg_time) if avg_time else None,
            most_searched_topics=[],  # This would require query analysis
            last_activity=last_activity
        )

    async def get_patent_analytics(self, patent_id: int) -> PatentAnalytics:
        """Get analytics for specific patent"""
        # Get view count (would need to implement view tracking)
        # For now, return basic analytics
        patent = await self.db.execute(
            select(Patent).where(Patent.id == patent_id)
        )
        patent_obj = patent.scalar_one_or_none()
        
        if not patent_obj:
            return PatentAnalytics(patent_id=patent_id)
        
        return PatentAnalytics(
            patent_id=patent_id,
            view_count=0,  # Would need to implement view tracking
            search_appearances=0,  # Would need to track search appearances
            citation_count=0,  # Would need to parse and count citations
            relevance_score=None,  # Would need to implement scoring
            last_accessed=None  # Would need to implement access tracking
        )

    async def get_search_analytics(
        self, 
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get search analytics over time period"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        result = await self.db.execute(
            select(
                SearchQuery.query_type,
                func.count(SearchQuery.id).label('count'),
                func.avg(SearchQuery.execution_time_ms).label('avg_time'),
                func.avg(SearchQuery.results_count).label('avg_results')
            )
            .where(SearchQuery.created_at >= start_date)
            .group_by(SearchQuery.query_type)
            .order_by(desc('count'))
        )
        
        return [
            {
                'query_type': row.query_type,
                'count': row.count,
                'avg_time_ms': float(row.avg_time) if row.avg_time else 0,
                'avg_results': float(row.avg_results) if row.avg_results else 0
            }
            for row in result
        ]

    async def get_report_analytics(
        self, 
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get report generation analytics"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        result = await self.db.execute(
            select(
                Report.report_type,
                func.count(Report.id).label('count'),
                func.avg(ReportAnalytics.processing_time_seconds).label('avg_time')
            )
            .select_from(Report.__table__.outerjoin(ReportAnalytics.__table__))
            .where(Report.created_at >= start_date)
            .group_by(Report.report_type)
            .order_by(desc('count'))
        )
        
        return [
            {
                'report_type': row.report_type,
                'count': row.count,
                'avg_time_seconds': float(row.avg_time) if row.avg_time else 0
            }
            for row in result
        ]

    async def get_top_searches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most common search queries"""
        result = await self.db.execute(
            select(
                SearchQuery.query_text,
                func.count(SearchQuery.id).label('count')
            )
            .group_by(SearchQuery.query_text)
            .order_by(desc('count'))
            .limit(limit)
        )
        
        return [
            {
                'query': row.query_text,
                'count': row.count
            }
            for row in result
        ]

    async def log_metric(
        self, 
        metric_name: str, 
        value: float,
        unit: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log a custom metric (would integrate with time series database in production)"""
        # For now, this would just print or store in a simple log table
        pass


# Helper function to get analytics CRUD instance
def get_analytics_crud(db: AsyncSession) -> AnalyticsCRUD:
    return AnalyticsCRUD(db)