from typing import Dict, Any, List, Optional
import httpx
from config.settings import settings


def create_patent_mcp_server():
    """Create MCP server for patent database operations"""
    try:
        from fastapi import FastAPI, Depends, HTTPException
        from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
        from pydantic import BaseModel, Field
        from fastapi_mcp import FastApiMCP

        class PatentSearchRequest(BaseModel):
            query: str = Field(..., description="Search query string")
            limit: int = Field(50, ge=1, le=200)

        security = HTTPBearer()

        async def verify_token(
            credentials: HTTPAuthorizationCredentials = Depends(security),
        ):
            if credentials.credentials != "patent-mcp-token":
                raise HTTPException(
                    status_code=401, detail="Invalid authentication token"
                )
            return credentials.credentials

        app = FastAPI(
            title="Patent Database MCP Server",
            description="MCP server exposing patent database operations as tools",
            version="1.0.0",
        )

        @app.post("/tools/search_patents", operation_id="search_patents")
        async def search_patents(
            request: PatentSearchRequest, token: str = Depends(verify_token)
        ):
            """Search patents via MCP interface"""
            try:
                return {
                    "success": True,
                    "patents": [
                        {
                            "patent_id": "US12345678",
                            "title": f"Search results for: {request.query}",
                            "abstract": f"This is a mock result for query: {request.query}",
                        }
                    ],
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        return FastApiMCP(app)
    except ImportError as e:
        print(f"Warning: fastapi-mcp not available: {e}")
        return None


class MCPClient:
    def __init__(self):
        self.base_url = settings.MCP_SERVER_URL
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

    async def close(self):
        await self.client.aclose()

    async def query_patent_database(
        self, query_type: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query patent database via MCP server

        query_type: 'search', 'get', 'graph_search'
        params: query parameters
        """
        if params is None:
            params = {}

        query_params = params.copy()  # Create mutable copy
        endpoint = f"/mcp/patent/{query_type}"

        try:
            response = await self.client.post(endpoint, json=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP Error: {e.response.status_code}", "details": str(e)}
        except Exception as e:
            return {"error": f"Query failed: {str(e)}"}

    async def search_patents(
        self, query: str, limit: int = 10, database: str = "both"
    ) -> List[Dict[str, Any]]:
        """Search patents across MariaDB and Neo4j"""
        params = {"query": query, "limit": limit, "database": database}

        result = await self.query_patent_database("search", params)
        return result.get("patents", [])

    async def get_patent_details(
        self, patent_id: str, database: str = "both"
    ) -> Dict[str, Any]:
        """Get detailed patent information"""
        params = {"patent_id": patent_id, "database": database}

        return await self.query_patent_database("get", params)

    async def graph_search(
        self, entity_type: str, entity_name: str, relationship_depth: int = 2
    ) -> List[Dict[str, Any]]:
        """Search patent relationships in Neo4j"""
        params = {
            "entity_type": entity_type,  # 'patent', 'inventor', 'assignee'
            "entity_name": entity_name,
            "depth": relationship_depth,
        }

        result = await self.query_patent_database("graph_search", params)
        return result.get("relationships", [])

    async def semantic_search(
        self, query: str, vector_threshold: float = 0.7, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Semantic search using Neo4j vector index"""
        params = {"query": query, "threshold": vector_threshold, "limit": limit}

        result = await self.query_patent_database("semantic_search", params)
        return result.get("similar_patents", [])


# Global MCP client instance
mcp_client = MCPClient()
