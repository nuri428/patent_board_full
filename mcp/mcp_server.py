from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from sqlalchemy import or_, select
import json
from datetime import date

# Local Imports
from auth.security import verify_api_key
from database import get_patent_db, get_opensearch_client
from db.models import (
    KRPatent,
    ForeignPatent,
)
from db.models import AnalysisRun
from db.graph import GraphDatabase
from services.embedding_service import EmbeddingService
from config.settings import settings
from tools.patent_identifier import (
    PatentIdentifierTool, 
    PatentUrlGenerator,
    PatentIdentifier,
    PatentUrl
)


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


class IndexPatentSectionInput(BaseModel):
    analysis_run_id: str = Field(..., description="Analysis run identifier")
    patent_id: str = Field(..., description="Patent ID")
    section_type: str = Field(..., description="Section type")
    section_content: str = Field(..., description="Section content")
    ipc_codes: List[str] = Field(default=[], description="IPC codes")
    cpc_codes: List[str] = Field(default=[], description="CPC codes")


class PatentSectionSearchInput(BaseModel):
    query: str = Field(..., description="Search query")
    section_types: List[str] = Field(default=[], description="Section types to search")
    limit: int = Field(20, le=100)
    analysis_run_id: Optional[str] = Field(None, description="Filter by analysis run")


class SemanticSearchInput(BaseModel):
    query: str = Field(..., description="Query for semantic search")
    limit: int = Field(10, le=50)
    similarity_threshold: float = Field(0.7, ge=0.0, le=1.0)
    analysis_run_id: Optional[str] = Field(None, description="Filter by analysis run")


class NetworkAnalysisInput(BaseModel):
    node_types: Optional[List[str]] = Field(
        default=["Corporation", "Technology", "Patent"],
        description="Node types to analyze",
    )
    include_centrality: bool = Field(True, description="Include centrality metrics")
    include_communities: bool = Field(True, description="Include community analysis")
    include_link_prediction: bool = Field(True, description="Include link prediction")


class TechnologyMappingInput(BaseModel):
    patent_id: str = Field(..., description="Patent application number")
    technology_id: str = Field(..., description="Technology ID")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    method: str = Field(..., description="Classification method")
    analysis_run_id: str = Field(..., description="Analysis run ID")
    is_partial: bool = Field(False, description="Partial classification")
    applied_config_version: str = Field("2.1.0", description="Config version applied")
    synergy_bonus_applied: bool = Field(False, description="Synergy bonus applied")
    negative_keywords_matched: List[str] = Field(
        default=[], description="Negative keywords matched"
    )
    confidence_before_cap: Optional[float] = Field(
        None, description="Confidence before cap"
    )


class TechnologyMappingFilterInput(BaseModel):
    analysis_run_id: Optional[str] = Field(None, description="Filter by analysis run")
    patent_id: Optional[str] = Field(None, description="Filter by patent ID")
    technology_id: Optional[str] = Field(None, description="Filter by technology ID")
    confidence_threshold: float = Field(
        0.0, ge=0.0, le=1.0, description="Minimum confidence threshold"
    )


# Patent Identifier Tools Input/Output Schemas
class PatentExtractionInput(BaseModel):
    text: str = Field(..., description="Text to extract patent identifiers from")


class PatentUrlGenerationInput(BaseModel):
    patent_ids: List[str] = Field(..., description="List of patent identifiers")
    country: str = Field(..., description="Country code (US, KR, WIPO)")
    sources: Optional[List[str]] = Field(None, description="URL sources to generate (default: ['google'])")


class PatentAnalysisInput(BaseModel):
    text: str = Field(..., description="Text to analyze for patent identifiers and generate URLs")
    include_sources: Optional[List[str]] = Field(None, description="URL sources to include (default: ['google'])")


# Patent Tools Response Schemas
class PatentExtractionResponse(BaseModel):
    found: List[Dict] = Field(default_factory=list, description="Found patent identifiers")
    raw_text: str = Field(..., description="Original input text")
    has_patents: bool = Field(False, description="Whether any patents were found")


class PatentUrlResponse(BaseModel):
    urls: List[Dict] = Field(default_factory=list, description="Generated URLs")
    errors: List[str] = Field(default_factory=list, description="Errors encountered")


class AnalysisRunResultsInput(BaseModel):
    analysis_run_id: str = Field(..., description="Analysis run ID")
    include_opensearch: bool = Field(True, description="Include OpenSearch results")
    include_neo4j: bool = Field(True, description="Include Neo4j results")
    include_tech_mappings: bool = Field(True, description="Include technology mappings")
    limit: int = Field(100, le=500, description="Results limit per source")


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
        {
            "name": "run_network_analysis",
            "description": "Run comprehensive GDS-based network analysis including centrality metrics, community detection, and link prediction.",
        },
        {
            "name": "create_technology_mapping",
            "description": "Create V2 technology mapping for patents with confidence scores and method tracking.",
        },
        {
            "name": "get_technology_mappings",
            "description": "Retrieve technology mappings with filtering options by analysis run, patent, or technology.",
        },
        {
            "name": "get_analysis_run_results",
            "description": "Get comprehensive results for a specific analysis run including OpenSearch and Neo4j data.",
        },
        {
            "name": "extract_patent_ids",
            "description": "Extract patent identifiers from text using regex patterns for US, KR, and WIPO patents.",
        },
        {
            "name": "generate_patent_urls",
            "description": "Generate official database URLs for patent identifiers from Google Patents, USPTO, KIPRIS.",
        },
        {
            "name": "analyze_patent_text",
            "description": "Comprehensive patent text analysis - extract IDs and generate authoritative URLs.",
        },
    ]


@mcp_app.post("/tools/graph_get_competitors", response_model=StandardResponse)
async def graph_get_competitors(
    input: GraphCompetitorInput, key: Any = Depends(verify_api_key)
):
    """Analyze competitors for a company using the knowledge graph"""
    results = await GraphDatabase.get_competitors(input.company_name)
    # Return empty list instead of 404 to prevent client-side error handling from treating it as a system failure
    return wrap_response(results, engine="Neo4j-KG")


@mcp_app.post(
    "/tools/graph_search_by_problem_solution", response_model=StandardResponse
)
async def graph_search_by_problem_solution(
    input: GraphProblemInput, key: Any = Depends(verify_api_key)
):
    """Find patents and solutions for a specific problem keyword"""
    results = await GraphDatabase.search_by_problem_solution(input.keyword)
    return wrap_response(results, engine="Neo4j-KG")


@mcp_app.post("/tools/graph_get_tech_cluster", response_model=StandardResponse)
async def graph_get_tech_cluster(
    input: GraphClusterInput, key: Any = Depends(verify_api_key)
):
    """Identify technology clusters and major patents by keyword"""
    results = await GraphDatabase.get_tech_cluster(input.keyword)
    return wrap_response(results, engine="Neo4j-KG")


@mcp_app.post("/tools/graph_find_path", response_model=StandardResponse)
async def graph_find_path(input: GraphPathInput, key: Any = Depends(verify_api_key)):
    """Find the shortest path between two entities"""
    results = await GraphDatabase.find_path(input.start_entity, input.end_entity)
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
                    "abstract": p.abstract[:500] + "..."
                    if p.abstract is not None
                    else None,
                    "date": p.applicate_date.isoformat()
                    if p.applicate_date is not None
                    else None,
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
                    if p.application_date is not None
                    else None
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


@mcp_app.post("/tools/index_patent_sections", response_model=StandardResponse)
async def index_patent_sections(
    input: IndexPatentSectionInput, key: Any = Depends(verify_api_key)
):
    try:
        opensearch = await get_opensearch_client()
        embedding_service = EmbeddingService()

        embeddings = await embedding_service.encode_text(input.section_content)

        index_name = settings.OPENSEARCH_PATENT_INDEX
        doc = {
            "application_number": input.patent_id,
            "section_type": input.section_type,
            "section_content": input.section_content,
            "embedding": embeddings["dense_vector"],
            "sparse_vector": embeddings["sparse_vector"],
            "ipc_codes": input.ipc_codes,
            "cpc_codes": input.cpc_codes,
            "analysis_run_id": input.analysis_run_id,
            "indexed_at": str(date.today()),
        }

        await opensearch.index(
            index=index_name, body=doc, id=f"{input.patent_id}_{input.section_type}"
        )

        return wrap_response(
            {"indexed": True, "doc_id": f"{input.patent_id}_{input.section_type}"},
            engine="OpenSearch-BGE-M3",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")


@mcp_app.post("/tools/search_patent_sections", response_model=StandardResponse)
async def search_patent_sections(
    input: PatentSectionSearchInput, key: Any = Depends(verify_api_key)
):
    try:
        opensearch = await get_opensearch_client()
        embedding_service = EmbeddingService()

        query_embeddings = await embedding_service.encode_text(input.query)

        search_body = {
            "size": input.limit,
            "query": {
                "bool": {
                    "should": [
                        {
                            "multi_match": {
                                "query": input.query,
                                "fields": ["section_content^2", "section_type"],
                            }
                        },
                        {
                            "knn": {
                                "embedding": {
                                    "vector": query_embeddings["dense_vector"],
                                    "k": input.limit,
                                }
                            }
                        },
                    ]
                }
            },
        }

        if input.section_types:
            search_body["query"]["bool"]["filter"] = [
                {"terms": {"section_type": input.section_types}}
            ]

        if input.analysis_run_id:
            search_body["query"]["bool"]["filter"] = search_body["query"]["bool"].get(
                "filter", []
            )
            search_body["query"]["bool"]["filter"].append(
                {"term": {"analysis_run_id": input.analysis_run_id}}
            )

        response = await opensearch.search(
            index=settings.OPENSEARCH_PATENT_INDEX, body=search_body
        )

        hits = response["hits"]["hits"]
        results = []
        for hit in hits:
            results.append(
                {"id": hit["_id"], "score": hit["_score"], "source": hit["_source"]}
            )

        return wrap_response(results, engine="OpenSearch-Hybrid", total=len(results))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@mcp_app.post("/tools/semantic_search", response_model=StandardResponse)
async def semantic_search(
    input: SemanticSearchInput, key: Any = Depends(verify_api_key)
):
    try:
        opensearch = await get_opensearch_client()
        embedding_service = EmbeddingService()

        query_embeddings = await embedding_service.encode_text(input.query)
        
        # Debug logging
        print(f"[DEBUG] Query: {input.query}")
        print(f"[DEBUG] Embedding length: {len(query_embeddings['dense_vector'])}")
        print(f"[DEBUG] Embedding sample (first 5): {query_embeddings['dense_vector'][:5]}")

        # Use script_score with knn_score function for nmslib index
        search_body = {
            "size": input.limit,
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "knn_score",
                        "lang": "knn",
                        "params": {
                            "field": "embedding",
                            "query_value": query_embeddings["dense_vector"],
                            "space_type": "cosinesimil"
                        }
                    }
                }
            }
        }
        
        # Apply min_score filter if specified
        if input.similarity_threshold > 0:
            search_body["min_score"] = input.similarity_threshold

        if input.analysis_run_id:
            # Wrap match_all in bool query to add filter
            search_body["query"]["script_score"]["query"] = {
                "bool": {
                    "must": {"match_all": {}},
                    "filter": {"term": {"analysis_run_id": input.analysis_run_id}}
                }
            }

        print(f"[DEBUG] Search body: {json.dumps(search_body, indent=2, default=str)[:500]}")
        
        response = await opensearch.search(
            index=settings.OPENSEARCH_PATENT_INDEX, body=search_body
        )
        
        print(f"[DEBUG] Response total hits: {response.get('hits', {}).get('total', {})}")
        print(f"[DEBUG] Response hits count: {len(response.get('hits', {}).get('hits', []))}")

        hits = response["hits"]["hits"]
        results = []
        for hit in hits:
            results.append(
                {"id": hit["_id"], "score": hit["_score"], "source": hit["_source"]}
            )

        return wrap_response(results, engine="OpenSearch-Semantic", total=len(results))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Semantic search failed: {str(e)}")


@mcp_app.post("/tools/get_analysis_results", response_model=StandardResponse)
async def get_analysis_results(
    analysis_run_id: str, key: Any = Depends(verify_api_key)
):
    try:
        from db.analysis_models import AnalysisRun

        async for session in get_patent_db():
            stmt = select(AnalysisRun).where(AnalysisRun.id == analysis_run_id)
            result = await session.execute(stmt)
            analysis_run = result.scalar_one_or_none()

            if not analysis_run:
                raise HTTPException(status_code=404, detail="Analysis run not found")

            return wrap_response(analysis_run.to_dict(), engine="Analysis-Tracker")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get analysis results: {str(e)}"
        )


@mcp_app.post("/tools/create_analysis_run", response_model=StandardResponse)
async def create_analysis_run(
    analysis_type: str,
    parameters: Dict[str, Any] = {},
    key: Any = Depends(verify_api_key),
):
    try:
        async for session in get_patent_db():
            new_run = AnalysisRun(analysis_type=analysis_type, parameters=parameters)
            session.add(new_run)
            await session.commit()
            await session.refresh(new_run)

            return wrap_response(new_run.to_dict(), engine="Analysis-Tracker")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create analysis run: {str(e)}"
        )


@mcp_app.post("/tools/run_network_analysis", response_model=StandardResponse)
async def run_network_analysis(
    input: NetworkAnalysisInput, key: Any = Depends(verify_api_key)
):
    try:
        results = await GraphDatabase.run_advanced_network_analysis()

        filtered_results = {}
        if input.include_centrality:
            filtered_results["degree_centrality"] = results.get("degree_centrality", [])
            filtered_results["betweenness_centrality"] = results.get(
                "betweenness_centrality", []
            )

        if input.include_communities:
            filtered_results["community_edges"] = results.get("community_edges", [])

        if input.include_link_prediction:
            filtered_results["link_prediction"] = results.get("link_prediction", [])

        return wrap_response(filtered_results, engine="Neo4j-GDS")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Network analysis failed: {str(e)}"
        )


@mcp_app.post("/tools/create_technology_mapping", response_model=StandardResponse)
async def create_technology_mapping(
    input: TechnologyMappingInput, key: Any = Depends(verify_api_key)
):
    try:
        result = await GraphDatabase.create_technology_mapping(
            patent_id=input.patent_id,
            technology_id=input.technology_id,
            confidence=input.confidence,
            method=input.method,
            analysis_run_id=input.analysis_run_id,
            is_partial=input.is_partial,
            applied_config_version=input.applied_config_version,
            synergy_bonus_applied=input.synergy_bonus_applied,
            negative_keywords_matched=input.negative_keywords_matched,
            confidence_before_cap=input.confidence_before_cap,
        )
        return wrap_response(result, engine="Neo4j-V2-Mapper")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Technology mapping failed: {str(e)}"
        )


@mcp_app.post("/tools/get_technology_mappings", response_model=StandardResponse)
async def get_technology_mappings(
    input: TechnologyMappingFilterInput, key: Any = Depends(verify_api_key)
):
    try:
        results = await GraphDatabase.get_technology_mappings(
            analysis_run_id=input.analysis_run_id,
            patent_id=input.patent_id,
            technology_id=input.technology_id,
            confidence_threshold=input.confidence_threshold,
        )
        return wrap_response(results, engine="Neo4j-V2-Mapper", total=len(results))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get technology mappings: {str(e)}"
        )


@mcp_app.post("/tools/get_analysis_run_results", response_model=StandardResponse)
async def get_analysis_run_results(
    input: AnalysisRunResultsInput, key: Any = Depends(verify_api_key)
):
    try:
        comprehensive_results = {
            "analysis_run_id": input.analysis_run_id,
            "metadata": {},
        }

        async for session in get_patent_db():
            stmt = select(AnalysisRun).where(AnalysisRun.id == input.analysis_run_id)
            result = await session.execute(stmt)
            analysis_run = result.scalar_one_or_none()

            if not analysis_run:
                raise HTTPException(status_code=404, detail="Analysis run not found")

            comprehensive_results["metadata"] = analysis_run.to_dict()

        if input.include_opensearch:
            try:
                opensearch = await get_opensearch_client()
                search_body = {
                    "size": input.limit,
                    "query": {"term": {"analysis_run_id": input.analysis_run_id}},
                }

                response = await opensearch.search(
                    index=settings.OPENSEARCH_PATENT_INDEX,
                    body=search_body,
                )

                hits = response["hits"]["hits"]
                opensearch_results = []
                for hit in hits:
                    opensearch_results.append(
                        {
                            "id": hit["_id"],
                            "score": hit["_score"],
                            "source": hit["_source"],
                        }
                    )

                comprehensive_results["opensearch_sections"] = opensearch_results
            except Exception as e:
                comprehensive_results["opensearch_sections"] = []
                comprehensive_results["opensearch_error"] = str(e)

        if input.include_tech_mappings:
            try:
                tech_mappings = await GraphDatabase.get_technology_mappings(
                    analysis_run_id=input.analysis_run_id, confidence_threshold=0.0
                )
                comprehensive_results["technology_mappings"] = tech_mappings[
                    : input.limit
                ]
            except Exception as e:
                comprehensive_results["technology_mappings"] = []
                comprehensive_results["tech_mapping_error"] = str(e)

        if input.include_neo4j:
            try:
                network_results = await GraphDatabase.run_advanced_network_analysis()
                comprehensive_results["network_analysis"] = network_results
            except Exception as e:
                comprehensive_results["network_analysis"] = {}
                comprehensive_results["network_error"] = str(e)

        total_results = len(comprehensive_results.get("opensearch_sections", [])) + len(
            comprehensive_results.get("technology_mappings", [])
        )

        return wrap_response(
            comprehensive_results, engine="Analysis-Hub", total=total_results
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get analysis run results: {str(e)}"
        )


# --- Patent Identifier Tools Implementation ---

@mcp_app.post("/tools/extract_patent_ids", response_model=StandardResponse)
async def extract_patent_ids(
    input: PatentExtractionInput, key: Any = Depends(verify_api_key)
):
    """Extract patent identifiers from text using regex patterns for US, KR, and WIPO patents."""
    try:
        identifier_tool = PatentIdentifierTool()
        extraction_result = identifier_tool.extract_patent_ids(input.text)
        
        response_data = extraction_result.dict()
        
        return wrap_response(
            response_data, 
            engine="Patent-Identifier-Regex",
            total=len(extraction_result.found)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Patent ID extraction failed: {str(e)}"
        )


@mcp_app.post("/tools/generate_patent_urls", response_model=StandardResponse)
async def generate_patent_urls(
    input: PatentUrlGenerationInput, key: Any = Depends(verify_api_key)
):
    """Generate official database URLs for patent identifiers from Google Patents, USPTO, KIPRIS."""
    try:
        url_generator = PatentUrlGenerator()
        
        # Create PatentIdentifier objects from the provided IDs
        patent_identifiers = []
        for patent_id in input.patent_ids:
            # Simple country detection based on patent ID prefix
            country = input.country
            if country == "auto":
                if patent_id.startswith("US"):
                    country = "US"
                elif patent_id.startswith("KR"):
                    country = "KR"
                elif patent_id.startswith("WO"):
                    country = "WIPO"
                else:
                    country = "GENERIC"
            
            patent_identifiers.append(PatentIdentifier(
                id=patent_id,
                country=country,
                type="unknown",
                raw_text=patent_id
            ))
        
        # Generate URLs
        sources = input.sources or ["google"]
        url_result = url_generator.generate_urls(patent_identifiers, sources)
        
        response_data = url_result.dict()
        
        return wrap_response(
            response_data,
            engine="Patent-URL-Generator",
            total=len(url_result.urls)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"URL generation failed: {str(e)}"
        )


@mcp_app.post("/tools/analyze_patent_text", response_model=StandardResponse)
async def analyze_patent_text(
    input: PatentAnalysisInput, key: Any = Depends(verify_api_key)
):
    """Comprehensive patent text analysis - extract IDs and generate authoritative URLs."""
    try:
        # Use the integrated tool that does both extraction and URL generation
        url_generator = PatentUrlGenerator()
        include_sources = input.include_sources or ["google"]
        
        # Generate complete response (extracts patents + creates URLs)
        complete_response = url_generator.generate_complete_response(
            text=input.text,
            include_sources=include_sources
        )
        
        response_data = {
            "text_analysis": {
                "found_patents": complete_response.get("extracted_patents", []),
                "total_count": complete_response.get("patent_count", 0),
                "has_patents": complete_response.get("has_patents", False)
            },
            "url_generation": {
                "urls": complete_response.get("generated_urls", []),
                "total_urls": len(complete_response.get("generated_urls", [])),
                "errors": complete_response.get("errors", [])
            },
            "summary": complete_response
        }
        
        return wrap_response(
            response_data,
            engine="Patent-Text-Analyzer",
            total=complete_response.get("patent_count", 0)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Patent text analysis failed: {str(e)}"
        )


# Create the MCP Interface
def create_mcp_server():
    from fastapi_mcp import FastApiMCP

    return FastApiMCP(mcp_app)
