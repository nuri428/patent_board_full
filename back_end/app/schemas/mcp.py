from pydantic import BaseModel
from typing import Optional, Literal, Any
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
