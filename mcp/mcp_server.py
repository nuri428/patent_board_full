from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

# Simple MCP Server without fastapi-mcp dependency
class MCPTool(BaseModel):
    name: str
    description: str

class PatentSearchInput(BaseModel):
    query: str

mcp_app = FastAPI(title="Patent MCP Server", version="1.0.0")

@mcp_app.post("/tools/list", response_model=list[MCPTool])
async def list_tools():
    """List available MCP tools"""
    return [
        MCPTool(name="search_patents", description="Search patents by query"),
        MCPTool(name="get_patent", description="Get patent details by ID"),
        MCPTool(name="analyze_patents", description="Analyze patent trends")
    ]

@mcp_app.post("/tools/search_patents")
async def search_patents(input: PatentSearchInput):
    """Search patents"""
    return {
        "patents": [
            {
                "patent_id": f"MOCK-{input.query.upper()}001",
                "title": f"Mock Patent: {input.query}",
                "abstract": f"This is a mock abstract about {input.query}"
            }
        ]
    }

@mcp_app.get("/health")
async def mcp_health():
    return {"status": "healthy"}

def get_mcp_app():
    return mcp_app