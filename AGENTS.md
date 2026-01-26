# Patent Board - Project Knowledge Base

**Generated**: 2026-01-25
**Architecture**: FastAPI + React + Multi-Database Patent Analysis Platform

## OVERVIEW
Patent analysis platform with AI-powered insights, chat interface, and automated report generation. Integrates MariaDB (structured patent data) + Neo4j (graph relationships) + LangGraph (multi-agent workflows).

## STRUCTURE
```
patent_board_full/
├── back_end/app/           # FastAPI backend (13 subdirs)
├── front_end/src/          # React + Vite frontend  
├── mcp/                    # Model Context Protocol server
├── shared/                 # Common schemas and utilities
└── scripts/                # Database/setup utilities
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| API endpoints | `back_end/app/api/v1/endpoints/` | REST endpoints, 13 files |
| Database operations | `back_end/app/crud/` | SQLAlchemy async patterns |
| Data schemas | `back_end/app/schemas/` | Pydantic models |
| MCP integration | `mcp/mcp_server.py` | Patent database queries |
| React components | `front_end/src/components/` | Modern React with hooks |
| Legacy UI | `back_end/app/templates/` + `static/js/` | Bootstrap 5 + vanilla JS |

## CODE MAP
| Symbol | Type | Location | Role |
|--------|------|----------|------|
| FastAPI app | Class | `back_end/app/main.py` | Main application entry |
| api_router | Module | `back_end/app/api/v1/api.py` | Route aggregation |
| GraphDatabase | Class | `mcp/db/graph.py` | Neo4j operations |
| KRPatent/ForeignPatent | Models | `mcp/db/models.py` | Patent data models |

## CONVENTIONS
- **Async/await**: All database operations use async patterns
- **API versioning**: `/api/v1/` prefix for all REST endpoints  
- **CORS**: Multiple localhost origins allowed (3000, 3300, 8001, 8080)
- **Error handling**: Global exception handler returns JSON responses
- **MCP tools**: Follow `/tools/{tool_name}` pattern with StandardResponse wrapper

## ANTI-PATTERNS (THIS PROJECT)
- No synchronous database calls in async context
- No direct frontend database access (always via API)
- No hardcoded CORS origins in production
- No bare except clauses in error handling

## UNIQUE STYLES
- **Dual database**: MariaDB for structured patents + Neo4j for relationships
- **MCP protocol**: Unified interface for patent queries across databases
- **Multi-agent AI**: LangGraph workflows for report generation
- **Mixed frontend**: Modern React (new) + legacy Bootstrap (existing)

## COMMANDS
```bash
# Backend (FastAPI)
cd back_end && uv run uvicorn app.main:app --reload

# Frontend (React)  
cd front_end && npm run dev

# MCP Server
cd mcp && uv run uvicorn mcp_server:mcp_app --reload

# Database setup
./scripts/init_db.py
```

## NOTES
- **Health checks**: Available at `/health` for both main app and MCP server
- **API docs**: Swagger UI at `/docs` when running backend
- **Authentication**: API key based for MCP, session-based for web UI
- **Data sources**: Korean patents (KIPRIS) + Foreign patents (USPTO default)