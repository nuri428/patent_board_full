from pydantic import BaseModel, Field
from typing import Optional, Literal, Any, List, Dict
from datetime import datetime


class MCPKeyBase(BaseModel):
    name: str
    key_type: Literal["simple", "graph", "all"] = "simple"


class MCPKeyCreate(MCPKeyBase):
    pass


class MCPKeyRead(MCPKeyBase):
    id: int
    api_key: str  # We might mask this in the frontend or backend
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MCPKeyResult(MCPKeyRead):
    pass


class ProxyToolCall(BaseModel):
    tool_name: str
    arguments: dict


class ProxyResult(BaseModel):
    status: str
    data: Any
    confidence: Optional[Literal["High", "Medium", "Low"]] = None
    interpretation_note: Optional[str] = None
    source: str = "KIPRIS"


class SemanticSearchRequest(BaseModel):
    query: str = Field(..., description="Query for semantic search")
    limit: int = Field(default=10, le=50)
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    analysis_run_id: Optional[str] = Field(None, description="Filter by analysis run")


class NetworkAnalysisRequest(BaseModel):
    node_types: Optional[List[str]] = Field(
        default=["Corporation", "Technology", "Patent"],
        description="Node types to analyze"
    )
    include_centrality: bool = Field(True, description="Include centrality metrics")
    include_communities: bool = Field(True, description="Include community analysis")
    include_link_prediction: bool = Field(True, description="Include link prediction")


class TechMappingRequest(BaseModel):
    patent_id: str = Field(..., description="Patent application number")
    technology_id: str = Field(..., description="Technology ID")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    method: str = Field(..., description="Classification method")
    analysis_run_id: str = Field(..., description="Analysis run ID")
    is_partial: bool = Field(False, description="Partial classification")


class AnalysisWorkbenchRequest(BaseModel):
    analysis_type: str = Field(..., description="Type of analysis to run")
    parameters: Dict[str, Any] = Field(default={}, description="Analysis parameters")
