"""
Pydantic schemas for Patent Analysis API
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PatentSource(str, Enum):
    """Patent source enumerations"""
    KIPRIS = "kipris"
    USPTO = "uspto"
    EPO = "epo"
    KIPO = "kipo"
    WIPO = "wipo"
    JPO = "jpo"
    CNIPA = "cnipa"
    OTHER = "other"


class PatentSourceType(str, Enum):
    """Patent source type enumerations"""
    PATENT = "patent"
    DOCUMENT = "document"
    OTHER = "other"


class PatentAnalysisBase(BaseModel):
    """Base schema for patent analysis"""
    session_id: Optional[str] = None
    user_id: int
    analyzed_patents: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="List of patent objects from all sources")
    patent_source: Optional[PatentSource] = Field(default=None, description="Primary patent source")
    confidence_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Analysis confidence score")
    relevant_sections: Optional[List[str]] = Field(default=None, description="List of relevant patent sections")
    analysis_metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional analysis metadata")
    source_type: Optional[PatentSourceType] = Field(default=PatentSourceType.PATENT, description="Source type")


class PatentAnalysisCreate(PatentAnalysisBase):
    """Schema for creating a new patent analysis"""
    pass


class PatentAnalysisUpdate(BaseModel):
    """Schema for updating an existing patent analysis"""
    analyzed_patents: Optional[List[Dict[str, Any]]] = None
    patent_source: Optional[PatentSource] = None
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    relevant_sections: Optional[List[str]] = None
    analysis_metadata: Optional[Dict[str, Any]] = None
    source_type: Optional[PatentSourceType] = None


class PatentAnalysisResponse(PatentAnalysisBase):
    """Schema for patent analysis response"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class PatentAnalysisListResponse(BaseModel):
    """Schema for patent analysis list response"""
    total_count: int
    analyses: List[PatentAnalysisResponse]
    skip: int
    limit: int


class MultiSourcePatentResponse(BaseModel):
    """Schema for multi-source patent response grouped by source"""
    patents_by_source: Dict[str, List[Dict[str, Any]]]
    total_patents: int
    sources_count: int


class PatentSourceCountResponse(BaseModel):
    """Schema for patent count by source"""
    source_counts: Dict[str, int]
    total_analyses: int


class PatentAnalysisSearchParams(BaseModel):
    """Schema for patent analysis search parameters"""
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    patent_source: Optional[PatentSource] = None
    min_confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    source_type: Optional[PatentSourceType] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=1000)
