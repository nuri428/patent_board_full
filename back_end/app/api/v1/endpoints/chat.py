from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, cast
import httpx
import uuid
import logging

from app.api.deps import get_current_active_user
from app.models import User
from shared.database import get_db
from app.crud.chat import get_chat_crud
from app.crud.crud_confidence_score import get_confidence_score_crud
from app.schemas.chat import ChatRequest, ChatResponse, ChatSessionCreate, ChatMessageCreate
from app.services.confidence_calculator import ConfidenceCalculator

router = APIRouter()
logger = logging.getLogger(__name__)

# LangGraph Chatbot Service URL
LANGGRAPH_CHATBOT_URL = "http://localhost:8001"


@router.post("/ask", response_model=ChatResponse)
async def ask_question(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Process a chat message with AI-powered patent analysis.
    Integrates with LangGraph chatbot service for intelligent responses.
    """
    chat_crud = get_chat_crud(db)
    confidence_crud = get_confidence_score_crud(db)
    confidence_calculator = ConfidenceCalculator()
    
    try:
        # Get or create session
        session_uuid = request.session_id or str(uuid.uuid4())
        
        # Check if session exists, if not create it
        session = await chat_crud.get_session_by_uuid(session_uuid)
        if not session and request.session_id:
            # Session ID provided but not found
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chat session {request.session_id} not found"
            )
        
        if not session:
            # Create new session
            session_create = ChatSessionCreate(
                title=request.message[:50] + "..." if len(request.message) > 50 else request.message,
                is_active=True
            )
            session = await chat_crud.create_session(
                user_id=current_user.id,
                session_create=session_create
            )
            # Update session_uuid to match the created session
            session_uuid = session.session_id
        
        # Store user message in database
        user_message = await chat_crud.add_message(
            ChatMessageCreate(
                session_id=session.id,
                message_type="user",
                content=request.message,
                patent_references=request.patent_context or []
            )
        )
        
        # Call LangGraph Chatbot Service
        async with httpx.AsyncClient(timeout=60.0) as client:
            chatbot_request = {
                "user_id": str(current_user.id),
                "message": {
                    "content": request.message,
                    "metadata": {
                        "patent_context": request.patent_context or [],
                        "search_depth": request.search_depth
                    }
                },
                "session_id": session_uuid,
                "title": session.title
            }
            
            try:
                response = await client.post(
                    f"{LANGGRAPH_CHATBOT_URL}/chat",
                    json=chatbot_request
                )
                response.raise_for_status()
                chatbot_result = response.json()
            except httpx.HTTPError as e:
                # If LangGraph service is unavailable, provide fallback response
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"AI chatbot service temporarily unavailable: {str(e)}"
                )
        
        # Extract AI response content
        ai_response_content = ""
        patent_refs = []
        sources = []
        
        if chatbot_result.get("response"):
            response_data = chatbot_result["response"]
            if isinstance(response_data, dict):
                ai_response_content = response_data.get("content", str(response_data))
                patent_refs = response_data.get("patent_urls", [])
                sources = response_data.get("sources", [])
            else:
                ai_response_content = str(response_data)
        
        # Store AI response in database
        ai_message = await chat_crud.add_message(
            ChatMessageCreate(
                session_id=session.id,
                message_type="assistant",
                content=ai_response_content,
                patent_references=patent_refs,
                sources=sources
            )
        )

        try:
            confidence_result = confidence_calculator.calculate_confidence_details(
                response=ai_response_content,
                query=request.message,
                sources_used=sources,
            )
            confidence_value = float(cast(float, confidence_result["confidence_value"]))
            confidence_level = str(cast(str, confidence_result["confidence_level"]))
            source_factors = cast(dict[str, object], confidence_result["source_factors"])
            await confidence_crud.create(
                session_id=session_uuid,
                user_id=current_user.id,
                confidence_value=confidence_value,
                confidence_level=confidence_level,
                source_factors=source_factors,
            )
        except Exception:
            logger.exception(
                "Failed to calculate/store confidence score: session_id=%s user_id=%s",
                session_uuid,
                current_user.id,
            )

        return ChatResponse(
            message_id=ai_message.id,
            session_id=session_uuid,
            content=ai_response_content,
            sources=sources,
            patent_references=patent_refs,
            timestamp=ai_message.timestamp
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat message: {str(e)}"
        )


@router.get("/sessions/{session_id}")
async def get_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get chat session details with message history"""
    chat_crud = get_chat_crud(db)
    
    # Get session from database
    session = await chat_crud.get_session_by_uuid(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat session {session_id} not found"
        )
    
    # Verify user owns this session
    if session.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this chat session"
        )
    
    # Get messages
    messages = await chat_crud.get_session_messages(session.id)
    
    return {
        "session_id": session.session_id,
        "title": session.title,
        "user_id": session.user_id,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "is_active": session.is_active,
        "messages": [
            {
                "id": msg.id,
                "message_type": msg.message_type,
                "content": msg.content,
                "patent_references": msg.patent_references,
                "sources": msg.sources,
                "timestamp": msg.timestamp
            }
            for msg in messages
        ]
    }


@router.get("/history")
async def get_chat_history(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 50,
):
    """Get user's chat session history"""
    chat_crud = get_chat_crud(db)
    
    sessions = await chat_crud.get_user_sessions(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    
    return {
        "sessions": [
            {
                "session_id": session.session_id,
                "title": session.title,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
                "is_active": session.is_active,
                "message_count": len(session.messages) if hasattr(session, 'messages') else 0
            }
            for session in sessions
        ],
        "total": len(sessions),
        "skip": skip,
        "limit": limit
    }


@router.post("/sessions")
async def create_chat_session(
    title: Optional[str] = "New Chat",
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new chat session"""
    chat_crud = get_chat_crud(db)
    
    session_create = ChatSessionCreate(
        title=title,
        is_active=True
    )
    
    session = await chat_crud.create_session(
        user_id=current_user.id,
        session_create=session_create
    )
    
    return {
        "session_id": session.session_id,
        "title": session.title,
        "created_at": session.created_at
    }


@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a chat session"""
    chat_crud = get_chat_crud(db)
    
    # Get session
    session = await chat_crud.get_session_by_uuid(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat session {session_id} not found"
        )
    
    # Verify user owns this session
    if session.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this chat session"
        )
    
    # Delete session
    success = await chat_crud.delete_session(session.id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete chat session"
        )
    
    return {"message": "Chat session deleted successfully"}
