from pydantic import BaseModel
from typing import Optional, Literal
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
