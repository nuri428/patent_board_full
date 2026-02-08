# MCP Server - Model Context Protocol

**OVERVIEW**: FastAPI-based MCP server providing unified patent database access, Neo4j graph queries, and comprehensive analysis results tracking.

## STRUCTURE
```
mcp/
├── mcp_server.py          # Main MCP FastAPI app with 14 tools
├── db/
│   ├── models.py         # SQLAlchemy models + AnalysisRun tracking
│   ├── graph.py          # Neo4j operations + GDS analysis
│   └── __init__.py
├── auth/
│   ├── security.py       # API key authentication
│   └── models.py
├── config/
│   └── settings.py       # Configuration management
└── scripts/              # Database utilities
```

## WHERE TO LOOK
| Task | File | Notes |
|------|------|-------|
| MCP tools | `mcp_server.py` | 14 endpoints including search, analysis, tracking |
| Graph queries | `db/graph.py` | Neo4j + GDS network analysis |
| Auth security | `auth/security.py` | API key verification |
| Data models | `db/models.py` | KRPatent/ForeignPatent/AnalysisRun |
| Analysis tracking | `models.py` | AnalysisRun entity for result tracing |

## CORE CAPABILITIES

### Patent Search & Retrieval
- `search_kr_patents` - Korean patent search with filters
- `search_foreign_patents` - Foreign patent search  
- `get_patent_details` - Full patent metadata retrieval

### Graph Analysis (Neo4j)
- `graph_get_competitors` - Competitor analysis via COMPETES_WITH
- `graph_search_by_problem_solution` - Problem-solution path finding
- `graph_get_tech_cluster` - Technology clustering via BELONGS_TO
- `graph_find_path` - Entity relationship path tracing

### Advanced Network Analysis (GDS)
- `run_network_analysis` - Centrality, communities, link prediction
  - Degree/betweenness centrality metrics
  - Community detection (edge-based clustering)
  - Potential collaboration prediction

### Technology V2 Mapper
- `create_technology_mapping` - Patent-technology classification with:
  - Confidence scoring (0.0-1.0)
  - Method tracking (IPC_MAPPING, KEYWORD_MATCHING, etc.)
  - Policy versioning (applied_config_version)
  - Negative keyword handling
  - Synergy bonus tracking
- `get_technology_mappings` - Filtered retrieval by run/patent/tech

### OpenSearch Integration
- `index_patent_sections` - Section-level indexing with BGE-M3 embeddings
- `search_patent_sections` - Hybrid (text + semantic) search
- `semantic_search` - Pure vector similarity search

### Analysis Tracking
- `create_analysis_run` - Analysis execution management
- `get_analysis_run_results` - Comprehensive results:
  - AnalysisRun metadata
  - OpenSearch sections by run
  - Technology mappings by run
  - Network analysis results
  - Error handling per component

## CONVENTIONS
- **Tool pattern**: `/tools/{tool_name}` with StandardResponse wrapper
- **Authentication**: API key via `verify_api_key` dependency
- **Response format**: `data` + `metadata` with engine info
- **Analysis tracking**: All results traced to `analysis_run_id`
- **Error handling**: HTTPException with 404/500 codes
- **Async patterns**: All DB operations use async/await

## ANTI-PATTERNS
- No synchronous database access
- No bypassing API key authentication
- No raw SQL - use SQLAlchemy ORM
- No hard-coded CORS origins
- No analysis results without `analysis_run_id` tracking