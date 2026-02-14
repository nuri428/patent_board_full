from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from typing import Optional, Literal, Any, List, Dict
from datetime import datetime


class MCPKeyBase(BaseModel):
    name: str
    description: Optional[str] = None
    key_type: Literal["simple", "graph", "all"] = "simple"

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, value: Any) -> Optional[str]:
        return value if isinstance(value, str) else None


class MCPKeyCreate(MCPKeyBase):
    pass


class MCPKeyRead(MCPKeyBase):
    id: int
    api_key: str  # We might mask this in the frontend or backend
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class MCPKeyResult(MCPKeyRead):
    pass


class ProxyToolCall(BaseModel):
    tool_name: str
    arguments: Optional[dict[str, Any]] = None


class ProxyResult(BaseModel):
    status: str
    data: Any
    confidence: Literal["High", "Medium", "Low", "General"] = "General"
    interpretation_note: Optional[str] = None
    source: Optional[str] = None


class SemanticSearchRequest(BaseModel):
    query: str = Field(..., description="Query for semantic search")
    limit: int = Field(default=10, ge=1, le=100)
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    analysis_run_id: Optional[str] = Field(None, description="Filter by analysis run")

    @field_validator("query")
    @classmethod
    def validate_query_not_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("query must not be empty")
        return value


class NetworkAnalysisRequest(BaseModel):
    company_name: str
    analysis_options: List[Literal["centrality", "community", "path", "clustering"]] = Field(
        default_factory=lambda: ["centrality"]
    )
    node_types: Optional[List[str]] = Field(
        default=["Corporation", "Technology", "Patent"],
        description="Node types to analyze"
    )
    include_centrality: bool = Field(True, description="Include centrality metrics")
    include_communities: bool = Field(True, description="Include community analysis")
    include_link_prediction: bool = Field(True, description="Include link prediction")


class TechMappingRequest(BaseModel):
    patent_id: str = Field(..., description="Patent application number")
    technology_name: Optional[str] = Field(default=None, description="Technology name")
    confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)

    technology_id: Optional[str] = Field(default=None, description="Technology ID")
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Confidence score")
    method: str = Field(default="manual", description="Classification method")
    analysis_run_id: str = Field(default="", description="Analysis run ID")
    is_partial: bool = Field(False, description="Partial classification")

    @model_validator(mode="after")
    def populate_compatibility_fields(self) -> "TechMappingRequest":
        if self.technology_name is None and self.technology_id is not None:
            self.technology_name = self.technology_id
        if self.technology_id is None:
            self.technology_id = self.technology_name or ""
        if self.confidence is None:
            self.confidence = self.confidence_threshold
        return self


class AnalysisWorkbenchRequest(BaseModel):
    analysis_type: Literal["semantic", "network", "tech", "charts"] = Field(
        ..., description="Type of analysis to run"
    )
    parameters: Dict[str, Any] = Field(default={}, description="Analysis parameters")
