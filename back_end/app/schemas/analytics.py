from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime


class AnalyticsData(BaseModel):
    """General analytics data structure"""
    metric_name: str
    value: float
    unit: Optional[str] = None
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = {}


class SystemMetrics(BaseModel):
    """System-wide metrics"""
    total_patents: int = 0
    total_reports: int = 0
    active_users: int = 0
    daily_searches: int = 0
    average_response_time_ms: Optional[float] = None
    system_load_percentage: Optional[float] = None
    database_connections: int = 0
    uptime_hours: float = 0.0
    last_updated: datetime


class UserAnalytics(BaseModel):
    """User-specific analytics"""
    user_id: int
    total_searches: int = 0
    total_reports_generated: int = 0
    average_search_time_ms: Optional[float] = None
    most_searched_topics: Optional[list] = []
    last_activity: datetime


class PatentAnalytics(BaseModel):
    """Patent-specific analytics"""
    patent_id: int
    view_count: int = 0
    search_appearances: int = 0
    citation_count: int = 0
    relevance_score: Optional[float] = None
    last_accessed: Optional[datetime] = None