from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional, List


class PatentBase(BaseModel):
    title: str
    abstract: str
    filing_date: Optional[datetime] = None
    status: str = "pending"


class PatentCreate(PatentBase):
    patent_id: str
    assignee: Optional[str] = None
    inventors: Optional[List[str]] = []


class PatentUpdate(BaseModel):
    title: Optional[str] = None
    abstract: Optional[str] = None
    status: Optional[str] = None


class Patent(PatentBase):
    patent_id: str
    assignee: Optional[str] = None
    inventors: Optional[List[str]] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PatentSearch(BaseModel):
    query: Optional[str] = None
    limit: int = 10
    offset: int = 0
    title: Optional[str] = None
    abstract: Optional[str] = None
    assignee: Optional[str] = None
    inventors: Optional[List[str]] = []
    status: Optional[str] = None
    filing_date_from: Optional[datetime] = None
    filing_date_to: Optional[datetime] = None
    sort_by: Optional[str] = "created_at"
    sort_order: Optional[str] = "desc"
    search_mode: Optional[str] = "all"


class PatentSearchResponse(BaseModel):
    patents: List[Patent]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


class ChatMessage(BaseModel):
    message: str
    timestamp: datetime = datetime.now(timezone.utc)


class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[str]] = []
    timestamp: datetime = datetime.now(timezone.utc)


class ReportRequest(BaseModel):
    topic: str
    patent_ids: Optional[List[str]] = []
    report_type: str = "analysis"


class Report(BaseModel):
    id: str
    topic: str
    content: str
    patent_ids: List[str]
    created_at: datetime
    report_type: str = "analysis"

    class Config:
        from_attributes = True