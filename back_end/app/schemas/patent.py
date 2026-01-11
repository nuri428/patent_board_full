from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class PatentBase(BaseModel):
    patent_id: str
    title: str
    abstract: Optional[str] = None
    description: Optional[str] = None
    assignee: Optional[str] = None
    filing_date: Optional[datetime] = None
    publication_date: Optional[datetime] = None
    grant_date: Optional[datetime] = None
    status: str = "pending"
    patent_type: Optional[str] = None
    classification: Optional[str] = None


class PatentCreate(PatentBase):
    inventors: Optional[List[str]] = []
    claims: Optional[List[Dict[str, Any]]] = []
    citations: Optional[List[Dict[str, Any]]] = []
    keywords: Optional[List[str]] = []


class PatentUpdate(BaseModel):
    title: Optional[str] = None
    abstract: Optional[str] = None
    description: Optional[str] = None
    assignee: Optional[str] = None
    filing_date: Optional[datetime] = None
    publication_date: Optional[datetime] = None
    grant_date: Optional[datetime] = None
    status: Optional[str] = None
    patent_type: Optional[str] = None
    classification: Optional[str] = None
    inventors: Optional[List[str]] = None
    claims: Optional[List[Dict[str, Any]]] = None
    citations: Optional[List[Dict[str, Any]]] = None
    keywords: Optional[List[str]] = None


class Patent(PatentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    inventors: Optional[List[str]] = []
    claims: Optional[List[Dict[str, Any]]] = []
    citations: Optional[List[Dict[str, Any]]] = []
    keywords: Optional[List[str]] = []
    created_at: datetime
    updated_at: Optional[datetime] = None


class PatentSearchRequest(BaseModel):
    query: str
    query_type: str = "keyword"  # keyword, semantic, graph
    filters: Optional[Dict[str, Any]] = {}
    limit: int = 25
    offset: int = 0
    sort_by: str = "relevance"  # relevance, date, title


class PatentSearchResponse(BaseModel):
    patents: List[Patent]
    total_count: int
    query: str
    query_type: str
    execution_time_ms: Optional[int] = None


class PatentDetail(Patent):
    """Extended patent details with additional relationships"""

    similar_patents: Optional[List[Patent]] = []
    cited_patents: Optional[List[Patent]] = []
    citing_patents: Optional[List[Patent]] = []


class PatentSearch(BaseModel):
    limit: int = 100
    offset: int = 0
    title: Optional[str] = None
    abstract: Optional[str] = None
    assignee: Optional[str] = None
    status: Optional[str] = None
    filing_date_from: Optional[datetime] = None
    filing_date_to: Optional[datetime] = None
