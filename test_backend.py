#!/usr/bin/env python3
"""
Simple test backend for chatbot modes integration testing
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Test Chatbot API",
    description="Test backend for chatbot modes integration",
    version="1.0.0"
)

# CORS middleware - allow all origins for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatMessage(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    success: bool
    session_id: str
    response: ChatMessage
    context: Dict[str, Any]
    user_properties: Dict[str, Any]
    total_messages: int

class SessionInfo(BaseModel):
    session_id: str
    user_id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int
    context: Dict[str, Any]

class UserProperties(BaseModel):
    mode: str
    authenticated: bool
    features: List[str]
    restrictions: List[str]

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "test-chatbot-backend"
    }

@app.post("/chat")
async def chat_message(message: ChatMessage, session_id: Optional[str] = None):
    """Send chat message - requires authentication"""
    # Check for demo token in header (simplified auth check)
    # In a real app, this would validate JWT tokens
    
    return ChatResponse(
        success=True,
        session_id=session_id or f"session_{uuid.uuid4().hex[:8]}",
        response=ChatMessage(
            content="This is a test response from the authenticated chatbot API."
        ),
        context={
            "mode": "full",
            "authenticated": True,
            "timestamp": datetime.now().isoformat()
        },
        user_properties={
            "mode": "full",
            "authenticated": True,
            "features": ["full_chat", "patent_analysis", "report_generation"],
            "restrictions": []
        },
        total_messages=1
    )

@app.post("/sessions")
async def create_session(user_id: str):
    """Create new chat session"""
    return {
        "session_id": f"session_{uuid.uuid4().hex[:8]}",
        "user_id": user_id,
        "created_at": datetime.now().isoformat(),
        "message_count": 0
    }

@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session information"""
    return SessionInfo(
        session_id=session_id,
        user_id="test_user",
        title="Test Session",
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
        message_count=0,
        context={"mode": "full", "authenticated": True}
    )

@app.get("/users/{user_id}/sessions")
async def get_user_sessions(user_id: str):
    """Get user's sessions"""
    return []

@app.get("/users/{user_id}/properties")
async def get_user_properties(user_id: str):
    """Get user properties"""
    return UserProperties(
        mode="full",
        authenticated=True,
        features=["full_chat", "patent_analysis", "report_generation"],
        restrictions=[]
    )

@app.post("/users/{user_id}/properties")
async def set_user_properties(user_id: str, properties: Dict[str, Any]):
    """Set user properties"""
    return {"success": True, "message": "Properties updated"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)