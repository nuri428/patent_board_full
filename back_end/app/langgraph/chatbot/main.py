"""
LangGraph Chatbot API Service
Context-aware patent analysis chatbot with long-term memory and MCP integration.
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, AsyncGenerator
import uuid
from datetime import datetime
import asyncio
import logging
import json

# Import our modules
from .memory import MemoryManager
from .backends.sql_memory import SQLMemoryBackend
from .backends.redis_memory import RedisMemoryBackend
from .agents import ChatbotAgent, ContextEngineering
from .agents.patent_agent import PatentAgent
from ..mcp_client import get_mcp_client, MCPClient
from .models.database import PropertyType
from app.core.config import settings
from .auth_main import validate_jwt_token

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="LangGraph Chatbot API",
    description="Context-aware patent analysis chatbot with long-term memory",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
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

class UserPropertyRequest(BaseModel):
    key: str = Field(..., description="Property key")
    value: Any = Field(..., description="Property value")
    type: str = Field(..., description="Property type (preference, setting, context, profile)")

# Global variables
memory_manager: Optional[MemoryManager] = None
chatbot_agent: Optional[ChatbotAgent] = None
context_engineering: Optional[ContextEngineering] = None
patent_agent: Optional[PatentAgent] = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global memory_manager, chatbot_agent, context_engineering, patent_agent
    
    logger.info("Initializing LangGraph Chatbot API...")
    
    try:
        # Initialize database backends
        sql_backend = SQLMemoryBackend(
            database_url=settings.PA_SYSTEM_DB_URL
        )
        
        redis_backend = RedisMemoryBackend(
            redis_url=settings.REDIS_URL
        )
        
        # Create memory manager
        memory_manager = MemoryManager(
            primary_backend=sql_backend,
            cache_backend=redis_backend
        )
        
        # Initialize MCP client
        mcp_client = await get_mcp_client()
        
        # Initialize context engineering with MCP client
        context_engineering = ContextEngineering(mcp_client=mcp_client)
        
        # Initialize chatbot agent
        chatbot_agent = ChatbotAgent(
            memory_manager=memory_manager,
            context_engineering=context_engineering
        )
        
        # Initialize patent agent with MCP client
        patent_agent = PatentAgent(mcp_client=mcp_client)
        
        logger.info("LangGraph Chatbot API initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down LangGraph Chatbot API...")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "langgraph-chatbot"
    }


async def stream_chat_response(
    user_id: str,
    session_id: str,
    message: str,
    message_metadata: Optional[Dict[str, Any]] = None,
    title: Optional[str] = None,
    request: Optional[Request] = None,
) -> AsyncGenerator[str, None]:
    """
    Async generator that streams chat response tokens as SSE events.

    Args:
        user_id: User identifier
        session_id: Session identifier
        message: User message content
        message_metadata: Optional message metadata
        title: Optional conversation title
        request: FastAPI Request object for disconnect detection

    Yields:
        SSE formatted event strings
    """
    event_id = 0
    patent_urls = []

    try:
        # Analyze user message for patent content using PatentAgent
        patent_analysis = None
        if patent_agent:
            try:
                patent_analysis = await patent_agent.analyze_patent_text(message)
            except Exception as e:
                logger.warning(f"Patent analysis failed: {e}")

        # Process the message with enhanced context
        result = await chatbot_agent.process_message(
            user_id=user_id,
            session_id=session_id,
            message_content=message,
            message_metadata=message_metadata or {},
            initial_state={
                "context": {
                    "session_title": title or "New Conversation",
                    "patent_analysis": patent_analysis
                }
            }
        )

        # Extract patent URLs from analysis
        if patent_analysis:
            if isinstance(patent_analysis, dict) and 'patent_urls' in patent_analysis:
                patent_urls = patent_analysis['patent_urls']
            elif hasattr(patent_analysis, 'get'):
                patent_urls = patent_analysis.get('patent_urls', [])

        # Get the response content
        response = result.get("response", {})
        content = ""

        if isinstance(response, dict):
            content = response.get("content", str(response))
        else:
            content = str(response)

        # Stream token-by-token
        for char in content:
            # Check if client disconnected
            if request and await request.is_disconnected():
                logger.info(f"Client disconnected during streaming (session: {session_id})")
                break

            event_id += 1

            # Format SSE event with metadata
            event_data = {
                "token": char,
                "session_id": session_id,
                "type": "token"
            }

            sse_event = (
                f"event: message\n"
                f"id: {event_id}\n"
                f"data: {json.dumps(event_data)}\n\n"
            )

            yield sse_event

            # Small delay to prevent overwhelming the client
            await asyncio.sleep(0.01)

        # Send final event with patent URLs metadata
        if patent_urls:
            event_id += 1
            final_event_data = {
                "session_id": session_id,
                "patent_urls": patent_urls,
                "type": "metadata"
            }
            final_event = (
                f"event: metadata\n"
                f"id: {event_id}\n"
                f"data: {json.dumps(final_event_data)}\n\n"
            )
            yield final_event

        # Send done event
        event_id += 1
        done_event = (
            f"event: done\n"
            f"id: {event_id}\n"
            f"data: {json.dumps({'session_id': session_id, 'type': 'done'})}\n\n"
        )
        yield done_event

    except Exception as e:
        # Log error but don't crash - send error event
        logger.error(f"Error during streaming (session: {session_id}): {e}")
        event_id += 1
        error_event = (
            f"event: error\n"
            f"id: {event_id}\n"
            f"data: {json.dumps({'error': str(e), 'session_id': session_id, 'type': 'error'})}\n\n"
        )
        yield error_event


@app.get("/chat/stream")
async def chat_stream(
    message: str = Query(..., description="User message"),
    session_id: Optional[str] = Query(None, description="Existing session ID"),
    user_id: str = Query(..., description="User identifier"),
    title: Optional[str] = Query(None, description="Conversation title"),
    request: Request = None,
    current_user_id: int = Depends(validate_jwt_token)
):
    """
    SSE streaming endpoint for real-time chat responses.

    Streams chat response tokens one by one using Server-Sent Events.

    Query Parameters:
        message: User message content
        session_id: Optional existing session ID (auto-generated if not provided)
        user_id: User identifier
        title: Optional conversation title

    Headers:
        Authorization: Bearer JWT token (required)
        Last-Event-ID: Last received event ID for reconnection support

    Returns:
        StreamingResponse with text/event-stream content type
    """
    # Verify user_id matches authenticated user
    if str(current_user_id) != user_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: user_id does not match authenticated user"
        )

    # Generate session ID if not provided
    final_session_id = session_id or str(uuid.uuid4())

    # Get Last-Event-ID for reconnection support
    last_event_id = request.headers.get("Last-Event-ID")

    # Log reconnection if applicable
    if last_event_id:
        logger.info(f"Client reconnecting from event ID: {last_event_id}")

    # Return streaming response
    return StreamingResponse(
        stream_chat_response(
            user_id=user_id,
            session_id=final_session_id,
            message=message,
            message_metadata={},
            title=title,
            request=request
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.post("/chat", response_model=ChatResponse)
async def chat_message(request: ChatRequest):
    """Process a chat message with patent intelligence integration"""
    
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Analyze user message for patent content using PatentAgent
        patent_analysis = None
        if patent_agent:
            try:
                patent_analysis = await patent_agent.analyze_patent_text(request.message.content)
            except Exception as e:
                logger.warning(f"Patent analysis failed: {e}")
        
        # Process the message with enhanced context
        result = await chatbot_agent.process_message(
            user_id=request.user_id,
            session_id=session_id,
            message_content=request.message.content,
            message_metadata=request.message.metadata or {},
            initial_state={
                "context": {
                    "session_title": request.title or "New Conversation",
                    "patent_analysis": patent_analysis
                }
            }
        )
        
        # Enhance response with patent URLs if patent analysis found results
        enhanced_response = result.get("response")
        patent_urls = []
        if enhanced_response and patent_analysis:
            try:
                enhanced_response = await patent_agent.enhance_chat_response(
                    user_message=request.message.content,
                    base_response=enhanced_response.get("content", str(enhanced_response))
                )
                # Update the response with enhanced content
                if isinstance(result.get("response"), dict):
                    result["response"]["content"] = enhanced_response
                    # Add patent_urls if available from analysis
                    if hasattr(patent_analysis, 'get') and 'patent_urls' in patent_analysis:
                        patent_urls = patent_analysis['patent_urls']
                    elif isinstance(patent_analysis, dict) and 'patent_urls' in patent_analysis:
                        patent_urls = patent_analysis['patent_urls']
                    else:
                        # Extract patent URLs from analysis if available
                        patent_urls = patent_analysis.get('patent_urls', [])
                else:
                    result["response"] = enhanced_response
                    patent_urls = patent_analysis.get('patent_urls', [])
            except Exception as e:
                logger.warning(f"Response enhancement failed: {e}")
        
        # Ensure response is a dict with patent_urls
        if isinstance(result.get("response"), dict):
            if "patent_urls" not in result["response"]:
                result["response"]["patent_urls"] = patent_urls
        else:
            result["response"] = {
                "content": str(result.get("response", "")),
                "patent_urls": patent_urls
            }
        
        return ChatResponse(
            success=result["success"],
            session_id=result["session_id"],
            response=result.get("response"),
            context=result.get("context", {}),
            user_properties=result.get("user_properties", {}),
            total_messages=result.get("total_messages", 0)
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sessions", response_model=Dict[str, str])
async def create_session(request: CreateSessionRequest):
    """Create a new conversation session"""
    
    try:
        session_id = await chatbot_agent.create_new_session(
            user_id=request.user_id,
            title=request.title or "New Conversation"
        )
        
        return {"session_id": session_id}
        
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{session_id}", response_model=SessionInfo)
async def get_session_info(session_id: str):
    """Get session information"""
    
    try:
        summary = await chatbot_agent.get_conversation_summary(session_id)
        
        if not summary:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return SessionInfo(
            session_id=summary["session_id"],
            user_id=summary["user_id"],
            title=summary["title"],
            created_at=summary["created_at"],
            updated_at=summary["updated_at"],
            message_count=summary["message_count"],
            context=summary["context"]
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
        sessions = await memory_manager.get_user_sessions(user_id)
        
        session_infos = []
        for session in sessions:
            session_infos.append(SessionInfo(
                session_id=session.id,
                user_id=session.user_id,
                title=session.title,
                created_at=session.created_at.isoformat(),
                updated_at=session.updated_at.isoformat(),
                message_count=len(session.messages),
                context=session.context or {}
            ))
        
        return session_infos
        
    except Exception as e:
        logger.error(f"Error getting user sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/users/{user_id}/properties")
async def set_user_properties(user_id: str, properties: Dict[str, Any]):
    """Set multiple user properties"""
    
    try:
        from ..memory import UserProperty
        
        for key, value in properties.items():
            # Create user property for each key-value pair
            user_property = UserProperty(
                key=key,
                value=value,
                type="preference",  # Default type
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            await memory_manager.set_user_property(user_property)
        
        return {"success": True, "message": f"Properties set successfully"}
        
    except Exception as e:
        logger.error(f"Error setting user properties: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}/properties/{key}")
async def get_user_property(user_id: str, key: str):
    """Get a specific user property"""
    
    try:
        property_data = await memory_manager.get_user_property(user_id, key)
        
        if not property_data:
            raise HTTPException(status_code=404, detail="Property not found")
        
        return property_data.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user property: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}/properties")
async def get_user_properties(user_id: str):
    """Get all user properties"""
    
    try:
        properties = await memory_manager.get_user_properties(user_id)
        
        return [prop.to_dict() for prop in properties]
        
    except Exception as e:
        logger.error(f"Error getting user properties: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a conversation session"""
    
    try:
        # This would need to be implemented in the memory backend
        # For now, return success
        return {"success": True, "message": "Session deleted"}
        
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/context/sample")
async def get_sample_context():
    """Get sample context for testing"""
    
    try:
        sample_context = {
            "sample_conversation": [
                {
                    "role": "user",
                    "content": "I'm interested in AI patents related to machine learning",
                    "timestamp": datetime.utcnow().isoformat()
                },
                {
                    "role": "assistant", 
                    "content": "I can help you find AI patents related to machine learning. Let me search for relevant patents.",
                    "timestamp": datetime.utcnow().isoformat()
                }
            ],
            "sample_user_properties": {
                "technical_interest": "Artificial Intelligence",
                "expertise_level": "intermediate",
                "preferred_depth": "detailed"
            },
            "sample_patent_context": {
                "query": "machine learning AI patents",
                "results_count": 10,
                "domains": ["artificial intelligence", "software"]
            }
        }
        
        return sample_context
        
    except Exception as e:
        logger.error(f"Error getting sample context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/patents/analyze")
async def analyze_patent_text(request: ChatMessage):
    """Analyze text for patent content and generate URLs"""
    
    try:
        if not patent_agent:
            raise HTTPException(status_code=500, detail="Patent agent not initialized")
        
        result = await patent_agent.analyze_patent_text(request.content)
        
        return {
            "success": True,
            "analysis": result
        }
        
    except Exception as e:
        logger.error(f"Error analyzing patent text: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/patents/intelligence")
async def get_patent_intelligence(patent_ids: List[str]):
    """Get comprehensive patent intelligence for given patent IDs"""
    
    try:
        if not patent_agent:
            raise HTTPException(status_code=500, detail="Patent agent not initialized")
        
        result = await patent_agent.get_patent_intelligence(patent_ids)
        
        return {
            "success": True,
            "intelligence": result
        }
        
    except Exception as e:
        logger.error(f"Error getting patent intelligence: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/enhance")
async def enhance_chat_response(request: ChatRequest):
    """Enhance chat response with patent intelligence"""
    
    try:
        if not patent_agent:
            raise HTTPException(status_code=500, detail="Patent agent not initialized")
        
        # Get original response first
        session_id = request.session_id or str(uuid.uuid4())
        original_result = await chatbot_agent.process_message(
            user_id=request.user_id,
            session_id=session_id,
            message_content=request.message.content,
            message_metadata=request.message.metadata or {},
            initial_state={"context": {"session_title": request.title or "New Conversation"}}
        )
        
        # Enhance response with patent intelligence
        enhanced_response = await patent_agent.enhance_chat_response(
            user_message=request.message.content,
            base_response=original_result.get("response", {}).get("content", str(original_result.get("response")))
        )
        
        return {
            "success": True,
            "original_response": original_result.get("response"),
            "enhanced_response": enhanced_response,
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"Error enhancing chat response: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)