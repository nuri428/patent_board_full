from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from sqlalchemy import or_, select
import json
from datetime import date

# Local Imports
from auth.security import verify_api_key
from database import get_patent_db
from db.models import (
    KRPatent,
    ForeignPatent,
)
from db.graph import GraphDatabase


# --- Input Schemas ---
class KRPatentSearchInput(BaseModel):
    query: str = Field(..., description="Search query for Title or Abstract")
    year_start: Optional[int] = Field(
        None, description="Filter by application year start"
    )
    year_end: Optional[int] = Field(None, description="Filter by application year end")
    limit: int = Field(20, le=100)


class ForeignPatentSearchInput(BaseModel):
    query: Optional[str] = Field(
        None, description="Search query for Invention Name or Abstract"
    )
    ipc_code: Optional[str] = Field(
        None, description="Filter by IPC code (e.g., 'G06F')"
    )
    applicant: Optional[str] = Field(
        None, description="Filter by Applicant/Corporation Name"
    )
    inventor: Optional[str] = Field(None, description="Filter by Inventor Name")
    country_code: str = Field("US", description="Country code (default: US)")
    limit: int = Field(20, le=100)


class PatentDetailsInput(BaseModel):
    patent_id: str = Field(
        ...,
        description="Patent ID (Application Number for KR, Document Number for Foreign)",
    )
    type: str = Field(..., description="Patent type: 'kr' or 'foreign'")


class GraphCompetitorInput(BaseModel):
    company_name: str = Field(..., description="Target company name")


class GraphProblemInput(BaseModel):
    keyword: str = Field(..., description="Problem keyword")


class GraphClusterInput(BaseModel):
    keyword: str = Field(..., description="Technology keyword")


class GraphPathInput(BaseModel):
    start_entity: str = Field(..., description="Start entity name")
    end_entity: str = Field(..., description="End entity name")


# --- Response Schemas ---
class ResponseMetadata(BaseModel):
    engine: str = "KIPRIS/MariaDB"
    is_raw: bool = True
    confidence: Optional[str] = None
    total_count: Optional[int] = None


class StandardResponse(BaseModel):
    status: str = "success"
    data: Any
    metadata: ResponseMetadata


def wrap_response(
    data: Any,
    engine: str = "KIPRIS",
    confidence: Optional[str] = None,
    total: Optional[int] = None,
) -> StandardResponse:
    return StandardResponse(
        data=data,
        metadata=ResponseMetadata(
            engine=engine,
            confidence=confidence,
            total_count=total or (len(data) if isinstance(data, list) else None),
        ),
    )


# --- MCP Tool Logic ---

mcp_app = FastAPI(title="Patent MCP Server", version="1.0.0")

# Enable CORS for Frontend
mcp_app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3300",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@mcp_app.get("/health")
async def mcp_health():
    return {"status": "healthy"}


@mcp_app.post("/tools/list")
async def list_tools(key: Any = Depends(verify_api_key)):
    """List available tools with detailed descriptions for Agents"""
    return [
        {
            "name": "search_kr_patents",
            "description": "Search Korean domestic patents by title or abstract. Returns high-resolution metadata.",
        },
        {
            "name": "search_foreign_patents",
            "description": "Search foreign patents (default US) by keyword, country, or corporation.",
        },
        {
            "name": "get_patent_details",
            "description": "Get full raw JSON details of a specific patent by its ID.",
        },
        {
            "name": "graph_get_competitors",
            "description": "Identify competitors for a company based on the Knowledge Graph's COMPETES_WITH relationships.",
        },
        {
            "name": "graph_search_by_problem_solution",
            "description": "Find specific technical problems and their solutions/patents via KG paths.",
        },
        {
            "name": "graph_get_tech_cluster",
            "description": "Group patents into technology clusters based on KG BELONGS_TO relationships.",
        },
        {
            "name": "graph_find_path",
            "description": "Trace paths between any two entities (Corporations, Inventors) in the KG.",
        },
    ]


@mcp_app.post("/tools/graph_get_competitors", response_model=StandardResponse)
async def graph_get_competitors(
    input: GraphCompetitorInput, key: Any = Depends(verify_api_key)
):
    """Analyze competitors for a company using the knowledge graph"""
    results = await GraphDatabase.get_competitors(input.company_name)
    if not results:
        raise HTTPException(status_code=404, detail="No competitors found")
    return wrap_response(results, engine="Neo4j-KG")


@mcp_app.post(
    "/tools/graph_search_by_problem_solution", response_model=StandardResponse
)
async def graph_search_by_problem_solution(
    input: GraphProblemInput, key: Any = Depends(verify_api_key)
):
    """Find patents and solutions for a specific problem keyword"""
    results = await GraphDatabase.search_by_problem_solution(input.keyword)
    if not results:
        raise HTTPException(status_code=404, detail="No solutions found")
    return wrap_response(results, engine="Neo4j-KG")


@mcp_app.post("/tools/graph_get_tech_cluster", response_model=StandardResponse)
async def graph_get_tech_cluster(
    input: GraphClusterInput, key: Any = Depends(verify_api_key)
):
    """Identify technology clusters and major patents by keyword"""
    results = await GraphDatabase.get_tech_cluster(input.keyword)
    if not results:
        raise HTTPException(status_code=404, detail="No clusters found")
    return wrap_response(results, engine="Neo4j-KG")


@mcp_app.post("/tools/graph_find_path", response_model=StandardResponse)
async def graph_find_path(input: GraphPathInput, key: Any = Depends(verify_api_key)):
    """Find the shortest path between two entities"""
    results = await GraphDatabase.find_path(input.start_entity, input.end_entity)
    if not results:
        raise HTTPException(status_code=404, detail="No path found")
    return wrap_response(results, engine="Neo4j-KG")


@mcp_app.post("/tools/search_kr_patents", response_model=StandardResponse)
async def search_kr_patents(
    input: KRPatentSearchInput, key: Any = Depends(verify_api_key)
):
    """Search Domestic (Korean) Patents using MariaDB"""
    async for session in get_patent_db():
        try:
            stmt = select(KRPatent)
            if input.query:
                stmt = stmt.where(
                    or_(
                        KRPatent.title.like(f"%{input.query}%"),
                        KRPatent.abstract.like(f"%{input.query}%"),
                    )
                )
            if input.year_start:
                stmt = stmt.where(
                    KRPatent.applicate_date >= date(input.year_start, 1, 1)
                )
            if input.year_end:
                stmt = stmt.where(
                    KRPatent.applicate_date <= date(input.year_end, 12, 31)
                )
            stmt = stmt.limit(input.limit)
            result = await session.execute(stmt)
            patents = result.scalars().all()
            response = [
                {
                    "id": p.application_number,
                    "title": p.title,
                    "abstract": p.abstract[:500] + "..." if p.abstract else None,
                    "date": p.applicate_date.isoformat() if p.applicate_date else None,
                    "status": p.patent_status,
                }
                for p in patents
            ]
            return wrap_response(response, engine="KIPRIS-MariaDB")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"KR Search failed: {str(e)}")


@mcp_app.post("/tools/search_foreign_patents", response_model=StandardResponse)
async def search_foreign_patents(
    input: ForeignPatentSearchInput, key: Any = Depends(verify_api_key)
):
    """Search Foreign (US) Patents using MariaDB"""
    async for session in get_patent_db():
        try:
            stmt = select(ForeignPatent).where(
                ForeignPatent.country_code == input.country_code
            )
            if input.query:
                stmt = stmt.where(
                    or_(
                        ForeignPatent.invention_name.like(f"%{input.query}%"),
                        ForeignPatent.abstract.like(f"%{input.query}%"),
                    )
                )
            stmt = stmt.limit(input.limit)
            result = await session.execute(stmt)
            patents = result.scalars().all()
            response = [
                {
                    "id": p.document_number,
                    "title": p.invention_name,
                    "date": p.application_date.isoformat()
                    if p.application_date
                    else None,
                    "country": p.country_code,
                }
                for p in patents
            ]
            return wrap_response(response, engine="USPTO-MariaDB")
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Foreign Search failed: {str(e)}"
            )


@mcp_app.post("/tools/get_patent_details", response_model=StandardResponse)
async def get_patent_details(
    input: PatentDetailsInput, key: Any = Depends(verify_api_key)
):
    """Get full details of a patent including parsed JSON data"""
    async for session in get_patent_db():
        try:
            if input.type.lower() == "kr":
                stmt = select(KRPatent).where(
                    KRPatent.application_number == input.patent_id
                )
            else:
                stmt = select(ForeignPatent).where(
                    ForeignPatent.document_number == input.patent_id
                )
            res = await session.execute(stmt)
            patent = res.scalar_one_or_none()
            if not patent:
                raise HTTPException(status_code=404, detail="Patent not found")
            raw_info = {}
            if patent.raw_data:
                try:
                    raw_info = json.loads(patent.raw_data)
                except json.JSONDecodeError:
                    raw_info = {"error": "Failed to parse raw data"}
            base_info = {
                "id": input.patent_id,
                "type": input.type,
                "raw_details": raw_info,
            }
            return wrap_response(base_info, engine="Patent-Master-DB")
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Details fetch failed: {str(e)}"
            )


# Create the MCP Interface
def create_mcp_server():
    from fastapi_mcp import FastApiMCP

    return FastApiMCP(mcp_app)
