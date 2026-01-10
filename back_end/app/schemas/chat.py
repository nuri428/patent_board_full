from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatSessionBase(BaseModel):
    title: Optional[str] = None
    is_active: bool = True


class ChatSessionCreate(ChatSessionBase):
    pass


class ChatSession(ChatSessionBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    session_id: str
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class ChatMessageBase(BaseModel):
    message_type: str  # user, assistant, system
    content: str


class ChatMessageCreate(ChatMessageBase):
    session_id: int
    patent_references: Optional[List[str]] = []
    sources: Optional[List[Dict[str, Any]]] = []


class ChatMessage(ChatMessageBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    session_id: int
    patent_references: Optional[List[str]] = []
    sources: Optional[List[Dict[str, Any]]] = []
    timestamp: datetime


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    patent_context: Optional[List[str]] = []
    search_depth: str = "standard"  # basic, standard, deep


class ChatResponse(BaseModel):
    message_id: int
    session_id: str
    content: str
    sources: Optional[List[Dict[str, Any]]] = []
    patent_references: Optional[List[str]] = []
    response_time_ms: Optional[int] = None
    timestamp: datetime


class ChatSessionDetail(ChatSession):
    """Extended session with messages"""
    messages: Optional[List[ChatMessage]] = []