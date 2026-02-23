from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal, Any, List, Dict
from datetime import datetime


class MCPKeyBase(BaseModel):
    name: str
    description: Optional[str] = None
    key_type: Literal["simple", "graph", "all"] = "simple"

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, value: Any) -> Optional[str]:
        if value is None or isinstance(value, str):
            return value
        return None


class MCPKeyCreate(MCPKeyBase):
    pass


class MCPKeyRead(MCPKeyBase):
    id: int
    api_key: str  # We might mask this in the frontend or backend
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class MCPKeyResult(MCPKeyRead):
    pass


class ProxyToolCall(BaseModel):
    tool_name: str
    arguments: Optional[Dict[str, Any]] = None


class ProxyResult(BaseModel):
    status: str
    data: Any
    confidence: Literal["High", "Medium", "Low", "General"] = "General"
    interpretation_note: Optional[str] = None
    source: Optional[str] = None


class SemanticSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Query for semantic search")
    limit: int = Field(default=10, ge=1, le=100)
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    analysis_run_id: Optional[str] = Field(None, description="Filter by analysis run")


class NetworkAnalysisRequest(BaseModel):
    company_name: str = Field(..., min_length=1, description="Company name to analyze")
    analysis_options: List[Literal["centrality", "community", "path", "clustering"]] = Field(
        default_factory=lambda: ["centrality"],
        description="Requested analysis options",
    )
    node_types: Optional[List[str]] = Field(
        default_factory=lambda: ["Corporation", "Technology", "Patent"],
        description="Node types to analyze"
    )
    include_centrality: bool = Field(True, description="Include centrality metrics")
    include_communities: bool = Field(True, description="Include community analysis")
    include_link_prediction: bool = Field(True, description="Include link prediction")


class TechMappingRequest(BaseModel):
    patent_id: str = Field(..., description="Patent application number")
    technology_name: Optional[str] = Field(None, min_length=1, description="Technology name")
    confidence_threshold: float = Field(
        0.7,
        ge=0.0,
        le=1.0,
        description="Confidence threshold",
    )
    technology_id: Optional[str] = Field(None, description="Technology ID")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score")
    method: Optional[str] = Field(None, description="Classification method")
    analysis_run_id: Optional[str] = Field(None, description="Analysis run ID")
    is_partial: bool = Field(False, description="Partial classification")


class AnalysisWorkbenchRequest(BaseModel):
    analysis_type: Literal["semantic", "network", "tech", "charts"] = Field(
        ...,
        description="Type of analysis to run",
    )
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Analysis parameters")
