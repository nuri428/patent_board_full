"""
Simple LangGraph Chatbot API Service for testing
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime
import asyncio
import logging

# Simple models
class ChatMessage(BaseModel):
    content: str = Field(..., description="Message content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class ChatRequest(BaseModel):
    user_id: str = Field(..., description="User identifier")
    message: ChatMessage = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Existing session ID")
    title: Optional[str] = Field(None, description="Conversation title")

class CreateSessionRequest(BaseModel):
    user_id: str = Field(..., description="User identifier")
    title: Optional[str] = Field(None, description="Conversation title")

class ChatResponse(BaseModel):
    success: bool
    session_id: str
    response: Optional[Dict[str, Any]]
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

# Simple in-memory storage for testing
sessions = {}
messages = {}
user_properties = {}

# FastAPI app
app = FastAPI(
    title="LangGraph Chatbot API",
    description="Simple test version",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React frontend
        "http://localhost:8002",
        "http://localhost:3300",
        "http://localhost:3301",
        "http://localhost:8003",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "langgraph-chatbot"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_message(request: ChatRequest):
    """Process a chat message"""
    
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Store the message
        if session_id not in messages:
            messages[session_id] = []
        
        messages[session_id].append({
            "role": "user",
            "content": request.message.content,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Simple echo response for testing
        response_content = f"I received your message: {request.message.content}"
        
        # Store the response
        messages[session_id].append({
            "role": "assistant",
            "content": response_content,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Create session if it doesn't exist
        if session_id not in sessions:
            sessions[session_id] = {
                "id": session_id,
                "user_id": request.user_id,
                "title": request.title or "New Conversation",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "context": {}
            }
        
        # Update session
        sessions[session_id]["updated_at"] = datetime.utcnow().isoformat()
        sessions[session_id]["message_count"] = len(messages[session_id])
        
        return ChatResponse(
            success=True,
            session_id=session_id,
            response={"content": response_content, "patent_urls": []},
            context=sessions[session_id]["context"],
            user_properties=user_properties.get(request.user_id, {}),
            total_messages=len(messages[session_id])
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sessions", response_model=Dict[str, str])
async def create_session(request: CreateSessionRequest):
    """Create a new conversation session"""
    
    try:
        session_id = str(uuid.uuid4())
        
        # Create session
        sessions[session_id] = {
            "id": session_id,
            "user_id": request.user_id,
            "title": request.title or "New Conversation",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "context": {}
        }
        
        return {"session_id": session_id}
        
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{session_id}", response_model=SessionInfo)
async def get_session_info(session_id: str):
    """Get session information"""
    
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = sessions[session_id]
        
        return SessionInfo(
            session_id=session["id"],
            user_id=session["user_id"],
            title=session["title"],
            created_at=session["created_at"],
            updated_at=session["updated_at"],
            message_count=len(messages.get(session_id, [])),
            context=session["context"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}/sessions", response_model=List[SessionInfo])
async def get_user_sessions(user_id: str):
    """Get all sessions for a user"""
    
    try:
        user_sessions = [session for session in sessions.values() if session["user_id"] == user_id]
        
        session_infos = []
        for session in user_sessions:
            session_infos.append(SessionInfo(
                session_id=session["id"],
                user_id=session["user_id"],
                title=session["title"],
                created_at=session["created_at"],
                updated_at=session["updated_at"],
                message_count=len(messages.get(session["id"], [])),
                context=session["context"]
            ))
        
        return session_infos
        
    except Exception as e:
        logger.error(f"Error getting user sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/users/{user_id}/properties")
async def set_user_properties(user_id: str, properties: Dict[str, Any]):
    """Set multiple user properties"""
    
    try:
        user_properties[user_id] = properties
        return {"success": True, "message": f"Properties set successfully"}
        
    except Exception as e:
        logger.error(f"Error setting user properties: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}/properties")
async def get_user_properties(user_id: str):
    """Get all user properties"""
    
    try:
        return user_properties.get(user_id, {})
        
    except Exception as e:
        logger.error(f"Error getting user properties: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)