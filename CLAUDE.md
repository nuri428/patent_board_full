# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Patent Board is an AI-powered patent analysis platform with a FastAPI backend, React frontend, and multi-database architecture (MariaDB for structured data, Neo4j for graph relationships, OpenSearch for semantic search, Redis for caching).

## Commands

### Backend (from `back_end/`)
```bash
uv sync                                    # Install dependencies
uv run uvicorn app.main:app --reload       # Start dev server (port 8001)
uv run pytest                              # Run all tests
uv run pytest tests/test_file.py -k name   # Run specific test
uv run black app/ && uv run isort app/     # Format code
uv run flake8 app/                         # Lint
uv run mypy app/                           # Type check
```

### Frontend (from `front_end/`)
```bash
npm install                   # Install dependencies
npm run dev                   # Start dev server (port 3000)
npm run build                 # Production build
npm run lint                  # ESLint
npm run test:e2e              # Playwright E2E tests
npm run test:e2e:ui           # Interactive E2E testing
```

### Docker
```bash
docker-compose up --build     # Start all services (dev)
docker-compose -f docker-compose.prod.yml up -d  # Production
```

## Architecture

### Backend Structure (`back_end/app/`)
- `api/v1/endpoints/` - REST API routes (auth, chat, patents, reports, mcp, admin, analytics)
- `services/` - Business logic layer
- `crud/` - SQLAlchemy async database operations
- `models/` - SQLAlchemy ORM models
- `schemas/` - Pydantic validation schemas
- `langgraph/chatbot/` - Multi-agent context-aware chatbot
- `langgraph/app/` - Multi-agent report generation workflow
- `core/config.py` - Environment-based settings (Pydantic Settings)
- `main.py` - FastAPI app, CORS, health checks, middleware

### Frontend Structure (`front_end/src/`)
- `pages/` - Route pages (Dashboard, Chat, PatentSearch, etc.)
- `components/` - React components organized by feature
- `context/` - React Context (AuthContext)
- `api/` - Axios-based API client modules

### MCP Server (`mcp/`)
- `mcp_server.py` - Model Context Protocol server for unified patent queries
- Provides tools for patent search, graph queries, semantic search across all databases

### Key Patterns
- **Async everywhere**: All database operations use `async with AsyncSessionLocal()`
- **Dependency injection**: FastAPI `Depends()` for sessions, auth
- **Multi-database**: MariaDB (CRUD), Neo4j (Cypher graphs), OpenSearch (embeddings), Redis (cache)
- **MCP tools**: Follow `/tools/{tool_name}` pattern with StandardResponse wrapper
- **API versioning**: All REST endpoints under `/api/v1/`

## Access Points (Development)
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001/api/v1
- API Docs (Swagger): http://localhost:8001/docs
- Health Check: http://localhost:8001/health
- MCP Server: http://localhost:8082

## Anti-Patterns to Avoid
- No synchronous database calls in async context
- No direct frontend database access (always via API)
- No hardcoded CORS origins in production
- No bare except clauses

## CI Pipeline (GitHub Actions)
- Backend: Black formatting, Isort imports, Flake8 linting, Pytest
- Frontend: ESLint, Vite build
