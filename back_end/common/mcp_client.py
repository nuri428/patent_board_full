"""
MCP (Model Context Protocol) Client for LangGraph Integration
Provides unified interface to patent databases and analysis tools
"""

from typing import Dict, List, Any, Optional, Union
import httpx
import json
from pydantic import BaseModel, Field


class MCPClient:
    """MCP client for LangGraph integration with patent tools"""

    def __init__(
        self, base_url: str = "http://localhost:8082", api_key: str = "test-api-key"
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

    async def __aenter__(self):
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.__aexit__(exc_type, exc_val, exc_tb)

    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to MCP server"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            **kwargs.pop("headers", {}),
        }

        try:
            response = await self.client.request(
                method=method, url=endpoint, headers=headers, **kwargs
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise Exception(
                f"MCP API Error {e.response.status_code}: {e.response.text}"
            )
        except Exception as e:
            raise Exception(f"MCP Request Failed: {str(e)}")

    async def extract_patent_ids(self, text: str) -> Dict[str, Any]:
        """Extract patent identifiers from text"""
        payload = {"text": text}
        return await self._request("POST", "/tools/extract_patent_ids", json=payload)

    async def generate_patent_urls(
        self, patent_ids: List[str], country: str, sources: List[str] = None
    ) -> Dict[str, Any]:
        """Generate patent database URLs"""
        payload = {
            "patent_ids": patent_ids,
            "country": country,
            "sources": sources or ["google"],
        }
        return await self._request("POST", "/tools/generate_patent_urls", json=payload)

    async def analyze_patent_text(
        self, text: str, include_sources: List[str] = None
    ) -> Dict[str, Any]:
        """Comprehensive patent text analysis"""
        payload = {
            "text": text,
            "include_sources": include_sources or ["google", "uspto", "kipris", "wipo"],
        }
        return await self._request("POST", "/tools/analyze_patent_text", json=payload)

    async def get_patent_details(
        self, patent_id: str, patent_type: str = "auto"
    ) -> Dict[str, Any]:
        """Get detailed patent information"""
        if patent_type == "auto":
            # Auto-detect type based on patent ID
            if patent_id.startswith("US"):
                patent_type = "foreign"
            elif patent_id.startswith("KR"):
                patent_type = "kr"
            else:
                patent_type = "foreign"

        payload = {"patent_id": patent_id, "type": patent_type}
        return await self._request("POST", "/tools/get_patent_details", json=payload)

    async def search_kr_patents(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search Korean patents"""
        payload = {"query": query, "limit": limit}
        return await self._request("POST", "/tools/search_kr_patents", json=payload)

    async def search_foreign_patents(
        self, query: str, country: str = "US", limit: int = 10
    ) -> Dict[str, Any]:
        """Search foreign patents"""
        payload = {"query": query, "country_code": country, "limit": limit}
        return await self._request(
            "POST", "/tools/search_foreign_patents", json=payload
        )

    async def semantic_search(
        self, query: str, limit: int = 10, similarity_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """Semantic search patent sections"""
        payload = {
            "query": query,
            "limit": limit,
            "similarity_threshold": similarity_threshold,
        }
        return await self._request("POST", "/tools/semantic_search", json=payload)

    async def search_patents(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Unified patent search (wrapper around semantic_search)"""
        return await self.semantic_search(query, limit=limit)

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available MCP tools"""
        return await self._request("POST", "/tools/list")

    async def health_check(self) -> Dict[str, Any]:
        """Check MCP server health"""
        return await self._request("GET", "/health")


# Global MCP client instance
mcp_client = MCPClient()


async def get_mcp_client() -> MCPClient:
    """Get global MCP client instance"""
    global mcp_client

    # Perform health check if not done before (basic check)
    try:
        # We don't want to block everything if it fails on startup
        # but we can try to check if it's alive
        pass
    except Exception:
        pass

    return mcp_client


async def close_mcp_client():
    """Close global MCP client"""
    global mcp_client

    if mcp_client:
        await mcp_client.client.aclose()


# Pydantic models for request/response
class PatentAnalysisRequest(BaseModel):
    """Request model for patent analysis"""

    text: str = Field(..., description="Text to analyze for patent content")
    include_sources: Optional[List[str]] = Field(
        None, description="URL sources to include"
    )


class PatentUrlRequest(BaseModel):
    """Request model for URL generation"""

    patent_ids: List[str] = Field(..., description="List of patent identifiers")
    country: str = Field(..., description="Country code (US, KR, WIPO)")
    sources: Optional[List[str]] = Field(None, description="URL sources to generate")


class PatentIntelligenceRequest(BaseModel):
    """Request model for patent intelligence"""

    patent_ids: List[str] = Field(..., description="Patent IDs to analyze")


class EnhancedChatRequest(BaseModel):
    """Request model for enhanced chat responses"""

    user_id: str = Field(..., description="User identifier")
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Session ID")
    title: Optional[str] = Field(None, description="Conversation title")
