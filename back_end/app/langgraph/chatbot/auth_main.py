"""
LangGraph Chatbot API Service with Authentication
Context-aware patent analysis chatbot with long-term memory and MCP integration.
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime
import asyncio
import logging
import jwt
from jwt import PyJWTError

# Import our modules
from ..memory import MemoryManager, SQLMemoryBackend, RedisMemoryBackend
from ..agents import ChatbotAgent, ContextEngineering
from ..agents.patent_agent import PatentAgent
from ..mcp_client import get_mcp_client, MCPClient
from ..models.database import PropertyType
from ..auth import get_current_user, require_permission, is_authenticated
from app.core.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JWT Security
security = HTTPBearer()


async def validate_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """
    Validate JWT token and return user_id.

    Args:
        credentials: HTTP Bearer token credentials

    Returns:
        int: User ID from validated token

    Raises:
        HTTPException: 401 if token is invalid, expired, or missing
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        return int(user_id)
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )


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

class AuthResponse(BaseModel):
    authenticated: bool
    user_id: str
    mode: str
    permissions: List[str]

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
    """Health check endpoint - public"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "langgraph-chatbot"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_message(request: ChatRequest, current_user_id: int = Depends(validate_jwt_token)):
    """Process a chat message with patent intelligence integration - requires JWT authentication"""

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

        # Process the message with enhanced context - use authenticated user_id
        result = await chatbot_agent.process_message(
            user_id=str(current_user_id),
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
async def create_session(request: CreateSessionRequest, current_user_id: int = Depends(validate_jwt_token)):
    """Create a new conversation session - requires JWT authentication"""

    try:
        session_id = await chatbot_agent.create_new_session(
            user_id=str(current_user_id),
            title=request.title or "New Conversation"
        )

        return {"session_id": session_id}

    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{session_id}", response_model=SessionInfo)
async def get_session_info(session_id: str, user: dict = Depends(get_current_user)):
    """Get session information - requires authentication"""
    
    try:
        summary = await chatbot_agent.get_conversation_summary(session_id)
        
        if not summary:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Verify user owns the session
        if summary["user_id"] != user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied to this session")
        
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
async def get_user_sessions(user_id: str, current_user: dict = Depends(get_current_user)):
    """Get all sessions for a user - requires authentication and ownership verification"""
    
    # Verify user owns the requested sessions
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied to this user's sessions")
    
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
async def set_user_properties(user_id: str, properties: Dict[str, Any], current_user: dict = Depends(get_current_user)):
    """Set multiple user properties - requires authentication and ownership verification"""
    
    # Verify user owns the requested properties
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied to this user's properties")
    
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
async def get_user_property(user_id: str, key: str, current_user: dict = Depends(get_current_user)):
    """Get a specific user property - requires authentication and ownership verification"""
    
    # Verify user owns the requested property
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied to this user's properties")
    
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
async def get_user_properties(user_id: str, current_user: dict = Depends(get_current_user)):
    """Get all user properties - requires authentication and ownership verification"""
    
    # Verify user owns the requested properties
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied to this user's properties")
    
    try:
        properties = await memory_manager.get_user_properties(user_id)
        
        return [prop.to_dict() for prop in properties]
        
    except Exception as e:
        logger.error(f"Error getting user properties: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/auth/userinfo")
async def get_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information - requires authentication"""
    return {
        "user_id": current_user["user_id"],
        "permissions": current_user["permissions"]
    }

@app.get("/auth/status")
async def get_auth_status(request: Request):
    """Check authentication status - public endpoint"""
    try:
        authenticated = is_authenticated(request)
        if authenticated:
            # Get user info if authenticated
            user = await get_current_user(request)
            return {
                "authenticated": True,
                "user_id": user["user_id"],
                "mode": "full",
                "permissions": user["permissions"]
            }
        else:
            return {
                "authenticated": False,
                "user_id": None,
                "mode": "limited",
                "permissions": []
            }
    except Exception as e:
        logger.error(f"Error checking auth status: {e}")
        return {
            "authenticated": False,
            "user_id": None,
            "mode": "limited",
            "permissions": []
        }

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a session - requires authentication and ownership verification"""
    
    try:
        # Verify session exists and user owns it
        summary = await chatbot_agent.get_conversation_summary(session_id)
        if not summary:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if summary["user_id"] != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied to this session")
        
        # Delete the session
        await chatbot_agent.delete_session(session_id)
        
        return {"success": True, "message": "Session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/users/{user_id}/properties/{key}")
async def delete_user_property(user_id: str, key: str, current_user: dict = Depends(get_current_user)):
    """Delete a specific user property - requires authentication and ownership verification"""
    
    # Verify user owns the property
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied to this user's properties")
    
    try:
        await memory_manager.delete_user_property(user_id, key)
        
        return {"success": True, "message": f"Property '{key}' deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting user property: {e}")
        raise HTTPException(status_code=500, detail=str(e))