from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, and_, desc

from shared.database import get_mariadb_db, get_neo4j_db
from back_end.app.crud import get_patent_crud
from back_end.app.schemas import Patent, PatentSearchRequest
import json
import time

# MCP Server with real database integration
class MCPTool(BaseModel):
    name: str
    description: str
    input_schema: Optional[Dict[str, Any]] = None

class PatentSearchInput(BaseModel):
    query: str
    query_type: Optional[str] = "keyword"
    limit: Optional[int] = 25
    filters: Optional[Dict[str, Any]] = None

class PatentGetInput(BaseModel):
    patent_id: Optional[int] = None
    patent_number: Optional[str] = None

class PatentAnalysisInput(BaseModel):
    topic: str
    analysis_type: Optional[str] = "comprehensive"  # technical, market, comprehensive

mcp_app = FastAPI(title="Patent MCP Server", version="1.0.0")

@mcp_app.post("/tools/list", response_model=list[MCPTool])
async def list_tools():
    """List available MCP tools"""
    return [
        MCPTool(
            name="search_patents", 
            description="Search patents by query with advanced filtering",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "query_type": {"type": "string", "enum": ["keyword", "semantic", "graph"], "default": "keyword"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 25},
                    "filters": {"type": "object", "description": "Search filters"}
                }
            }
        ),
        MCPTool(
            name="get_patent", 
            description="Get patent details by ID or patent number",
            input_schema={
                "type": "object",
                "properties": {
                    "patent_id": {"type": "integer", "description": "Patent database ID"},
                    "patent_number": {"type": "string", "description": "Patent number"}
                },
                "oneOf": [
                    {"required": ["patent_id"]},
                    {"required": ["patent_number"]}
                ]
            }
        ),
        MCPTool(
            name="analyze_patents", 
            description="Analyze patent trends and patterns",
            input_schema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Analysis topic"},
                    "analysis_type": {"type": "string", "enum": ["technical", "market", "comprehensive"], "default": "comprehensive"}
                }
            }
        ),
        MCPTool(
            name="get_similar_patents", 
            description="Find patents similar to a given patent",
            input_schema={
                "type": "object",
                "properties": {
                    "patent_id": {"type": "integer", "description": "Reference patent ID"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 10}
                }
            }
        ),
        MCPTool(
            name="graph_search_patents", 
            description="Search patents using Neo4j graph relationships",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Graph query"},
                    "relationship_types": {"type": "array", "items": {"type": "string"}, "description": "Types of relationships to follow"},
                    "depth": {"type": "integer", "minimum": 1, "maximum": 5, "default": 2}
                }
            }
        )
    ]

@mcp_app.post("/tools/search_patents")
async def search_patents(input: PatentSearchInput):
    """Search patents using real database"""
    db: AsyncSession = next(get_mariadb_db())
    try:
        patent_crud = get_patent_crud(db)
        
        # Record start time
        start_time = time.time()
        
        # Perform search
        patents, total_count = await patent_crud.search(
            query=input.query,
            query_type=input.query_type or "keyword",
            filters=input.filters or {},
            limit=input.limit or 25,
            offset=0
        )
        
        execution_time_ms = int((time.time() - start_time) * 1000)
        
        # Convert to dictionary format for MCP response
        patent_results = []
        for patent in patents:
            patent_dict = {
                "patent_id": patent.id,
                "patent_number": patent.patent_number,
                "title": patent.title,
                "abstract": patent.abstract,
                "assignee": patent.assignee,
                "filing_date": patent.filing_date.isoformat() if patent.filing_date else None,
                "publication_date": patent.publication_date.isoformat() if patent.publication_date else None,
                "status": patent.status,
                "patent_type": patent.patent_type,
                "classification": patent.classification,
                "keywords": json.loads(patent.keywords) if patent.keywords else [],
                "inventors": json.loads(patent.inventors) if patent.inventors else [],
                "relevance_score": 0.85  # Placeholder - would be calculated by semantic search
            }
            patent_results.append(patent_dict)
        
        return {
            "patents": patent_results,
            "total_count": total_count,
            "query": input.query,
            "query_type": input.query_type or "keyword",
            "execution_time_ms": execution_time_ms,
            "filters_applied": input.filters or {}
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database search failed: {str(e)}"
        )
    finally:
        await db.close()

@mcp_app.post("/tools/get_patent")
async def get_patent(input: PatentGetInput):
    """Get patent details by ID or patent number"""
    db: AsyncSession = next(get_mariadb_db())
    try:
        patent_crud = get_patent_crud(db)
        
        # Get patent by ID or number
        if input.patent_id:
            patent = await patent_crud.get(input.patent_id)
        elif input.patent_number:
            patent = await patent_crud.get_by_number(input.patent_number)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either patent_id or patent_number must be provided"
            )
        
        if not patent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patent not found"
            )
        
        # Get similar patents
        similar_patents = await patent_crud.get_similar_patents(patent.id, limit=5)
        
        # Convert to MCP format
        patent_dict = {
            "patent_id": patent.id,
            "patent_number": patent.patent_number,
            "title": patent.title,
            "abstract": patent.abstract,
            "description": patent.description,
            "assignee": patent.assignee,
            "inventors": json.loads(patent.inventors) if patent.inventors else [],
            "filing_date": patent.filing_date.isoformat() if patent.filing_date else None,
            "publication_date": patent.publication_date.isoformat() if patent.publication_date else None,
            "grant_date": patent.grant_date.isoformat() if patent.grant_date else None,
            "status": patent.status,
            "patent_type": patent.patent_type,
            "classification": patent.classification,
            "claims": json.loads(patent.claims) if patent.claims else [],
            "citations": json.loads(patent.citations) if patent.citations else [],
            "keywords": json.loads(patent.keywords) if patent.keywords else [],
            "similar_patents": [
                {
                    "patent_id": sim.id,
                    "patent_number": sim.patent_number,
                    "title": sim.title,
                    "similarity_score": 0.75  # Placeholder
                }
                for sim in similar_patents
            ]
        }
        
        return patent_dict
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    finally:
        await db.close()

@mcp_app.post("/tools/analyze_patents")
async def analyze_patents(input: PatentAnalysisInput):
    """Analyze patent trends and patterns"""
    db: AsyncSession = next(get_mariadb_db())
    try:
        patent_crud = get_patent_crud(db)
        
        # Search for relevant patents
        patents, total_count = await patent_crud.search(
            query=input.topic,
            query_type="keyword",
            filters={},
            limit=100,
            offset=0
        )
        
        # Basic analysis based on search results
        analysis = {
            "topic": input.topic,
            "analysis_type": input.analysis_type or "comprehensive",
            "total_patents_found": total_count,
            "sample_patents": [
                {
                    "patent_id": patent.id,
                    "patent_number": patent.patent_number,
                    "title": patent.title,
                    "assignee": patent.assignee,
                    "filing_date": patent.filing_date.isoformat() if patent.filing_date else None
                }
                for patent in patents[:10]  # Return sample of 10 patents
            ],
            "insights": {
                "top_assignees": _extract_top_assignees(patents),
                "filing_trend": _analyze_filing_trends(patents),
                "technology_areas": _extract_technology_areas(patents),
                "summary": f"Found {total_count} patents related to {input.topic}"
            }
        }
        
        return analysis
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )
    finally:
        await db.close()

@mcp_app.post("/tools/get_similar_patents")
async def get_similar_patents_mcp(input: PatentGetInput):
    """Get patents similar to a given patent"""
    if not input.patent_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="patent_id is required"
        )
    
    db: AsyncSession = next(get_mariadb_db())
    try:
        patent_crud = get_patent_crud(db)
        
        similar_patents = await patent_crud.get_similar_patents(
            input.patent_id, 
            limit=10
        )
        
        results = [
            {
                "patent_id": patent.id,
                "patent_number": patent.patent_number,
                "title": patent.title,
                "abstract": patent.abstract,
                "similarity_score": 0.8,  # Placeholder - would be calculated by semantic analysis
                "classification": patent.classification,
                "filing_date": patent.filing_date.isoformat() if patent.filing_date else None
            }
            for patent in similar_patents
        ]
        
        return {
            "reference_patent_id": input.patent_id,
            "similar_patents": results,
            "total_found": len(results)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Similarity search failed: {str(e)}"
        )
    finally:
        await db.close()

@mcp_app.post("/tools/graph_search_patents")
async def graph_search_patents(input: PatentAnalysisInput):
    """Search patents using Neo4j graph relationships"""
    try:
        neo4j_db = get_neo4j_db()
        session = neo4j_db.get_session()
        
        # Build Cypher query based on input
        cypher_query = """
        MATCH (p:Patent)
        WHERE p.title CONTAINS $query OR p.abstract CONTAINS $query
        RETURN p
        LIMIT $limit
        """
        
        result = session.run(
            cypher_query,
            query=input.topic,
            limit=50
        )
        
        patents = []
        for record in result:
            node = record["p"]
            patents.append({
                "patent_id": node.get("id"),
                "patent_number": node.get("patent_number"),
                "title": node.get("title"),
                "abstract": node.get("abstract"),
                "labels": list(node.labels)
            })
        
        session.close()
        
        return {
            "query": input.topic,
            "patents": patents,
            "total_found": len(patents),
            "search_type": "graph"
        }
    
    except Exception as e:
        # Fallback to MariaDB if Neo4j fails
        db: AsyncSession = next(get_mariadb_db())
        try:
            patent_crud = get_patent_crud(db)
            patents, _ = await patent_crud.search(
                query=input.topic,
                query_type="keyword",
                limit=50,
                offset=0
            )
            
            results = [
                {
                    "patent_id": patent.id,
                    "patent_number": patent.patent_number,
                    "title": patent.title,
                    "abstract": patent.abstract,
                    "labels": ["Patent"]
                }
                for patent in patents
            ]
            
            return {
                "query": input.topic,
                "patents": results,
                "total_found": len(results),
                "search_type": "fallback_keyword"
            }
        
        finally:
            await db.close()

@mcp_app.get("/health")
async def mcp_health():
    """Health check for MCP server"""
    try:
        # Test database connections
        db: AsyncSession = next(get_mariadb_db())
        await db.execute("SELECT 1")
        await db.close()
        
        neo4j_db = get_neo4j_db()
        session = neo4j_db.get_session()
        session.run("RETURN 1")
        session.close()
        
        return {
            "status": "healthy",
            "database": {
                "mariadb": "connected",
                "neo4j": "connected"
            },
            "timestamp": time.time()
        }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }

def _extract_top_assignees(patents, limit=5):
    """Extract top assignees from patent list"""
    assignee_counts = {}
    for patent in patents:
        if patent.assignee:
            assignee_counts[patent.assignee] = assignee_counts.get(patent.assignee, 0) + 1
    
    return sorted(assignee_counts.items(), key=lambda x: x[1], reverse=True)[:limit]

def _analyze_filing_trends(patents):
    """Analyze filing date trends"""
    if not patents:
        return {}
    
    years = {}
    for patent in patents:
        if patent.filing_date:
            year = patent.filing_date.year
            years[year] = years.get(year, 0) + 1
    
    return {
        "yearly_counts": years,
        "trend": "increasing" if len(years) > 1 and sorted(years.values())[-1] > sorted(years.values())[0] else "stable"
    }

def _extract_technology_areas(patents):
    """Extract technology areas from classifications"""
    areas = {}
    for patent in patents:
        if patent.classification:
            # Extract main class from CPC classification
            main_class = patent.classification.split('/')[0] if '/' in patent.classification else patent.classification
            areas[main_class] = areas.get(main_class, 0) + 1
    
    return dict(sorted(areas.items(), key=lambda x: x[1], reverse=True)[:10])

def get_mcp_app():
    return mcp_app