"""Multi-modal chat endpoint for processing up to two queries per request."""

from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime
from typing import Any, cast

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.crud.chat import get_chat_crud
from app.crud.crud_confidence_score import get_confidence_score_crud
from app.models import ChatSession, User
from app.schemas.chat import ChatMessageCreate, ChatSessionCreate
from app.services.confidence_calculator import ConfidenceCalculator
from shared.database import get_db

router = APIRouter(prefix="/multi-modal", tags=["chat", "multi-modal"])
logger = logging.getLogger(__name__)

LANGGRAPH_CHATBOT_URL = "http://localhost:8001"


class MultiModalRequest(BaseModel):
    """Request model for multi-modal chat processing."""

    queries: list[str] = Field(
        ...,
        min_length=1,
        max_length=2,
        description="List of query strings to process (1-2 queries)",
    )
    session_id: str | None = Field(
        default=None,
        description="Optional existing chat session ID",
    )
    patent_context: list[str] = Field(
        default_factory=list,
        description="Optional patent context shared across queries",
    )
    search_depth: str = Field(
        default="standard",
        description="Search depth for chatbot processing",
    )


class IndividualQueryResult(BaseModel):
    """Result details for an individual query in a multi-modal request."""

    query: str = Field(..., description="Original query text")
    response: str = Field(..., description="Generated response text")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score for this query")
    confidence_level: str = Field(..., description="Confidence level label for this query")
    sources: list[dict[str, Any]] = Field(default_factory=list, description="Sources used in response generation")
    patent_references: list[str] = Field(default_factory=list, description="Patent references extracted for this query")
    processing_time_ms: int = Field(..., ge=0, description="Processing time for this query in milliseconds")
    success: bool = Field(..., description="Whether processing was successful")
    error: str | None = Field(default=None, description="Error detail when query processing fails")


class MultiModalResponse(BaseModel):
    """Response model for multi-modal chat processing."""

    session_id: str = Field(..., description="Chat session UUID")
    consolidated_answer: str = Field(..., description="Consolidated answer from all query responses")
    combined_confidence_score: float = Field(..., ge=0.0, le=1.0, description="Aggregate confidence score")
    individual_results: list[IndividualQueryResult] = Field(
        default_factory=list,
        description="Per-query processing results and metadata",
    )
    query_count: int = Field(..., ge=1, le=2, description="Number of processed queries")
    total_processing_time_ms: int = Field(..., ge=0, description="Total processing time in milliseconds")
    timestamp: datetime = Field(..., description="Response timestamp")


class MultiModalChatService:
    """Service for processing multi-modal chat requests."""

    def __init__(self, db: AsyncSession, current_user: User) -> None:
        """Initialize service with request-scoped dependencies."""
        self.db = db
        self.current_user = current_user
        self.chat_crud = get_chat_crud(db)
        self.confidence_crud = get_confidence_score_crud(db)
        self.confidence_calculator = ConfidenceCalculator()

    async def process(self, request: MultiModalRequest) -> MultiModalResponse:
        """Process one to two queries and return consolidated output."""
        if not 1 <= len(request.queries) <= 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="queries must contain between 1 and 2 items",
            )

        started_at = time.perf_counter()
        session = await self._get_or_create_session(request)
        session_uuid = session.session_id

        logger.info(
            "Starting multi-modal processing: user_id=%s session_id=%s query_count=%s",
            self.current_user.id,
            session_uuid,
            len(request.queries),
        )

        results: list[IndividualQueryResult] = []
        for index, query in enumerate(request.queries, start=1):
            query_result = await self._process_single_query(
                query_index=index,
                query=query,
                session_id=session.id,
                session_uuid=session_uuid,
                session_title=session.title,
                patent_context=request.patent_context,
                search_depth=request.search_depth,
            )
            results.append(query_result)

        consolidated_answer = self._build_consolidated_answer(results)
        combined_confidence_score = self._calculate_combined_confidence(results)
        total_processing_time_ms = int((time.perf_counter() - started_at) * 1000)

        logger.info(
            "Completed multi-modal processing: user_id=%s session_id=%s query_count=%s confidence=%.3f total_ms=%s",
            self.current_user.id,
            session_uuid,
            len(results),
            combined_confidence_score,
            total_processing_time_ms,
        )

        return MultiModalResponse(
            session_id=session_uuid,
            consolidated_answer=consolidated_answer,
            combined_confidence_score=combined_confidence_score,
            individual_results=results,
            query_count=len(results),
            total_processing_time_ms=total_processing_time_ms,
            timestamp=datetime.utcnow(),
        )

    async def _get_or_create_session(self, request: MultiModalRequest) -> ChatSession:
        """Get an existing chat session or create a new one."""
        session_uuid = request.session_id or str(uuid.uuid4())
        session = await self.chat_crud.get_session_by_uuid(session_uuid)

        if not session and request.session_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chat session {request.session_id} not found",
            )

        if not session:
            title_seed = request.queries[0]
            session_create = ChatSessionCreate(
                title=title_seed[:50] + "..." if len(title_seed) > 50 else title_seed,
                is_active=True,
            )
            session = await self.chat_crud.create_session(
                user_id=self.current_user.id,
                session_create=session_create,
            )

        return session

    async def _process_single_query(
        self,
        query_index: int,
        query: str,
        session_id: int,
        session_uuid: str,
        session_title: str | None,
        patent_context: list[str],
        search_depth: str,
    ) -> IndividualQueryResult:
        """Process one query independently and return structured metadata."""
        query_started_at = time.perf_counter()
        logger.info(
            "Processing multi-modal query: user_id=%s session_id=%s query_index=%s",
            self.current_user.id,
            session_uuid,
            query_index,
        )

        try:
            await self.chat_crud.add_message(
                ChatMessageCreate(
                    session_id=session_id,
                    message_type="user",
                    content=query,
                    patent_references=patent_context,
                )
            )

            chatbot_result = await self._call_chatbot(
                query=query,
                session_uuid=session_uuid,
                session_title=session_title,
                patent_context=patent_context,
                search_depth=search_depth,
            )

            response_content, patent_refs, sources = self._extract_chatbot_response(chatbot_result)

            ai_message = await self.chat_crud.add_message(
                ChatMessageCreate(
                    session_id=session_id,
                    message_type="assistant",
                    content=response_content,
                    patent_references=patent_refs,
                    sources=sources,
                )
            )

            confidence_value = 0.0
            confidence_level = "low"
            try:
                confidence_result = self.confidence_calculator.calculate_confidence_details(
                    response=response_content,
                    query=query,
                    sources_used=cast(list[object], sources),
                )
                confidence_value = float(cast(float, confidence_result["confidence_value"]))
                confidence_level = str(cast(str, confidence_result["confidence_level"]))
                source_factors = cast(dict[str, object], confidence_result["source_factors"])
                await self.confidence_crud.create(
                    session_id=session_uuid,
                    user_id=self.current_user.id,
                    confidence_value=confidence_value,
                    confidence_level=confidence_level,
                    source_factors=source_factors,
                )
            except Exception:
                logger.exception(
                    "Failed to calculate/store confidence score in multi-modal flow: user_id=%s session_id=%s query_index=%s",
                    self.current_user.id,
                    session_uuid,
                    query_index,
                )

            processing_time_ms = int((time.perf_counter() - query_started_at) * 1000)
            logger.info(
                "Completed multi-modal query: user_id=%s session_id=%s query_index=%s message_id=%s confidence=%.3f ms=%s",
                self.current_user.id,
                session_uuid,
                query_index,
                ai_message.id,
                confidence_value,
                processing_time_ms,
            )

            return IndividualQueryResult(
                query=query,
                response=response_content,
                confidence_score=confidence_value,
                confidence_level=confidence_level,
                sources=sources,
                patent_references=patent_refs,
                processing_time_ms=processing_time_ms,
                success=True,
                error=None,
            )

        except HTTPException:
            raise
        except Exception as exc:
            processing_time_ms = int((time.perf_counter() - query_started_at) * 1000)
            logger.exception(
                "Multi-modal query failed: user_id=%s session_id=%s query_index=%s ms=%s",
                self.current_user.id,
                session_uuid,
                query_index,
                processing_time_ms,
            )
            return IndividualQueryResult(
                query=query,
                response="",
                confidence_score=0.0,
                confidence_level="low",
                sources=[],
                patent_references=[],
                processing_time_ms=processing_time_ms,
                success=False,
                error=str(exc),
            )

    async def _call_chatbot(
        self,
        query: str,
        session_uuid: str,
        session_title: str | None,
        patent_context: list[str],
        search_depth: str,
    ) -> dict[str, Any]:
        """Call existing LangGraph chatbot workflow for a single query."""
        chatbot_request = {
            "user_id": str(self.current_user.id),
            "message": {
                "content": query,
                "metadata": {
                    "patent_context": patent_context,
                    "search_depth": search_depth,
                },
            },
            "session_id": session_uuid,
            "title": session_title,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{LANGGRAPH_CHATBOT_URL}/chat",
                    json=chatbot_request,
                )
                response.raise_for_status()
                return cast(dict[str, Any], response.json())
            except httpx.HTTPError as exc:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"AI chatbot service temporarily unavailable: {exc}",
                ) from exc

    @staticmethod
    def _extract_chatbot_response(chatbot_result: dict[str, Any]) -> tuple[str, list[str], list[dict[str, Any]]]:
        """Extract response content, patent references, and sources from chatbot payload."""
        response_content = ""
        patent_refs: list[str] = []
        sources: list[dict[str, Any]] = []

        response_data = chatbot_result.get("response")
        if isinstance(response_data, dict):
            response_content = str(response_data.get("content", ""))
            patent_refs_raw = response_data.get("patent_urls", [])
            sources_raw = response_data.get("sources", [])
            if isinstance(patent_refs_raw, list):
                patent_refs = [str(item) for item in patent_refs_raw]
            if isinstance(sources_raw, list):
                sources = [item for item in sources_raw if isinstance(item, dict)]
        elif response_data is not None:
            response_content = str(response_data)

        return response_content, patent_refs, sources

    @staticmethod
    def _build_consolidated_answer(results: list[IndividualQueryResult]) -> str:
        """Build a consolidated answer from all successful query responses."""
        successful = [result for result in results if result.success]
        if not successful:
            return "Unable to generate responses for the provided queries."

        parts: list[str] = []
        for index, item in enumerate(successful, start=1):
            parts.append(f"Query {index}: {item.query}\nAnswer: {item.response}")

        return "\n\n".join(parts)

    @staticmethod
    def _calculate_combined_confidence(results: list[IndividualQueryResult]) -> float:
        """Calculate aggregate confidence score from individual query scores."""
        successful = [result.confidence_score for result in results if result.success]
        if not successful:
            return 0.0
        return round(sum(successful) / len(successful), 4)


@router.post("", response_model=MultiModalResponse)
async def process_multi_modal_queries(
    request: MultiModalRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> MultiModalResponse:
    """
    Process up to two queries in one request and return a consolidated answer.

    This endpoint processes each query independently through the existing chatbot
    workflow and aggregates per-query metadata and confidence scores.
    """
    if not 1 <= len(request.queries) <= 2:
        logger.warning(
            "Invalid multi-modal query count: user_id=%s query_count=%s",
            current_user.id,
            len(request.queries),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="queries must contain between 1 and 2 items",
        )

    service = MultiModalChatService(db=db, current_user=current_user)

    try:
        response = await service.process(request)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(
            "Unhandled multi-modal processing error: user_id=%s",
            current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing multi-modal request: {exc}",
        ) from exc

    if not any(result.success for result in response.individual_results):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process all queries for the multi-modal request",
        )

    return response
