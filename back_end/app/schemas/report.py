from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class ReportBase(BaseModel):
    title: str
    description: Optional[str] = None
    report_type: str  # comprehensive, technical, market, strategic
    topic: str


class ReportCreate(ReportBase):
    patent_ids: Optional[List[int]] = []
    parameters: Optional[Dict[str, Any]] = {}


class ReportUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    content: Optional[str] = None


class Report(ReportBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    content: Optional[str] = None
    status: str = "pending"
    generated_at: Optional[datetime] = None
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class ReportPatent(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    report_id: int
    patent_id: int
    relevance_score: Optional[int] = None
    analysis_notes: Optional[str] = None
    added_at: datetime


class ReportAnalytics(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    report_id: int
    patent_count: int = 0
    processing_time_seconds: Optional[int] = None
    generation_tokens_used: Optional[int] = None
    query_complexity_score: Optional[int] = None
    user_satisfaction_rating: Optional[int] = None
    created_at: datetime


class ReportDetail(Report):
    """Extended report details with related data"""
    patents: Optional[List[ReportPatent]] = []
    analytics: Optional[ReportAnalytics] = None


class ReportGenerationRequest(BaseModel):
    topic: str
    report_type: str = "comprehensive"
    patent_ids: Optional[List[int]] = []
    parameters: Optional[Dict[str, Any]] = {}
    priority: str = "normal"  # low, normal, high


class ReportGenerationStatus(BaseModel):
    report_id: int
    status: str
    progress_percentage: Optional[int] = 0
    current_stage: Optional[str] = None
    estimated_completion: Optional[datetime] = None
    error_message: Optional[str] = None