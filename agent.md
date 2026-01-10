# Patent Board Full Stack - Agent Setup & Documentation

## 🤖 Agent-Specific Instructions

This document provides comprehensive setup instructions and operational guidelines for the Patent Board full-stack application with MCP (Model Context Protocol) integration.

## 📋 Current Project Status

### ✅ Completed Components
- **FastAPI Backend**: Modern async REST API with modular structure
- **Database Layer**: MariaDB + Neo4j integration with async connection management
- **MCP Integration**: FastAPI-MCP server exposing patent database operations
- **LangGraph Integration**: Multi-agent report generation system
- **Frontend**: Bootstrap 5 + vanilla JavaScript with responsive design
- **Authentication**: JWT-based security with token management

### 🔧 Technology Stack
```
Backend: FastAPI (Python 3.12+)
Databases: MariaDB (structured) + Neo4j (graph)
AI Framework: LangGraph + OpenAI integration
MCP Protocol: fastapi-mcp package
Frontend: Bootstrap 5 + vanilla JavaScript
Package Manager: uv (fast Python package manager)
```

## 🚀 Quick Start Guide

### 1. Environment Setup
```bash
# Clone repository
git clone <repository-url>
cd patent_board_full

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv sync

# Setup environment
cp .env.example .env
# Edit .env with your actual configuration values
```

### 2. Start Application
```bash
# Start all services
./start.sh
```

Access points:
- **Web Interface**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs
- **MCP Server**: http://localhost:8001/mcp/
- **Health Check**: http://localhost:8001/health

### 3. MCP Client Configuration (Claude Desktop)
```json
{
  "mcpServers": {
    "patent-board": {
      "command": "uvicorn",
      "args": ["app:app", "--host", "0.0.0.0", "--port", "8001"],
      "env": {
        "AUTH_TOKEN": "patent-mcp-token"
      }
    }
  }
}
```

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│              AI Agent (Claude Desktop)        │
│                     ↕ MCP Protocol           │
│                     ↕ HTTP Request            │
├─────────────────────────────────────────────┤
│                FastAPI Application           │
│  ┌─────────────┬─────────────┐    │
│  │   MCP       │   Web API  │    │
│  │   Server    │   Routes    │    │
│  └─────────────┴─────────────┘    │
│  ┌─────────────┬─────────────┐    │
│  │    LangGraph │  Frontend  │    │
│  │   Reports   │  Interface │    │
│  └─────────────┴─────────────┘    │
├─────────────────────────────────────────────┤
│          Database Layer (Async)            │
│  ┌─────────────┬─────────────┐    │
│  │   MariaDB   │   Neo4j    │    │
│  │ (Structured) │  (Graph)    │    │
│  └─────────────┴─────────────┘    │
└─────────────────────────────────────────────┘
```

## 📁 Key Features & Endpoints

### MCP Server Tools
- `POST /mcp/tools/list` - List available patent tools
- `POST /mcp/tools/search_patents` - Search patents by query
- `POST /mcp/tools/get_patent` - Get patent details by ID
- `POST /mcp/tools/analyze_patents` - Analyze patent trends

### REST API Endpoints
- `GET /api/v1/patents/` - List patents with pagination
- `POST /api/v1/patents/search` - Advanced patent search
- `GET /api/v1/patents/{patent_id}` - Get patent details
- `POST /api/v1/chat/ask` - AI-powered patent chat
- `POST /api/v1/reports/generate` - Generate analysis reports
- `GET /api/v1/reports/` - List generated reports

### Frontend Pages
- `/` - Dashboard with statistics and quick actions
- `/patents` - Advanced search interface with filters
- `/chat` - AI chat interface with history
- `/reports` - Report generation and management

## 🔍 MCP Implementation Details

### Server Configuration
```python
# File: app/mcp_server.py
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel

class PatentSearchInput(BaseModel):
    query: str

mcp_app = FastAPI(title="Patent MCP Server")

@mcp_app.post("/tools/search_patents")
async def search_patents(input: PatentSearchInput):
    """Search patents via MCP interface"""
    return {"patents": [...]}
    
return FastApiMCP(mcp_app)
```

### Integration Pattern
1. **Separate Process**: MCP server runs independently
2. **HTTP Communication**: FastAPI app mounts MCP server at `/mcp`
3. **Tool Definition**: Each FastAPI endpoint becomes an MCP tool
4. **Authentication**: Bearer token with `patent-mcp-token`
5. **JSON Schema**: Pydantic models define tool input/output

## 🧪 LangGraph Integration

### Multi-Agent Workflow
```
Patent Analysis Request
        ↓
    [Agent: Collector]
    Gather patents via MCP queries
        ↓
    [Agent: Analyzer] 
    Extract insights using LLM
        ↓
    [Agent: Summarizer]
    Create executive summary
        ↓
    [Agent: Report Writer]
    Generate structured sections
        ↓
    [Agent: Compiler]
    Assemble final report
        ↓
    Comprehensive Patent Report
```

### Agent Configuration
```python
# File: app/langgraph/__init__.py
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

def _build_graph():
    graph = StateGraph(PatentAnalysisState)
    graph.add_node("collect_patents", self._collect_patents)
    graph.add_edge(START, "collect_patents")
    return graph.compile()
```

## 🗄️ Database Schema

### MariaDB Tables
```sql
-- Patents table
CREATE TABLE patents (
    patent_id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    abstract TEXT,
    filing_date DATE,
    status VARCHAR(20) DEFAULT 'pending',
    assignee VARCHAR(255),
    inventors JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reports table  
CREATE TABLE reports (
    id VARCHAR(50) PRIMARY KEY,
    topic VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    patent_ids JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Neo4j Graph Schema
```cypher
-- Patent nodes with properties
CREATE CONSTRAINT patent_id IF NOT EXISTS FOR (p:Patent) REQUIRE p.id IS UNIQUE;
CREATE INDEX patent_title IF NOT EXISTS FOR (p:Patent) ON (p.title);
CREATE INDEX patent_abstract_vector IF NOT EXISTS FOR (p:Patent) OPTIONS {indexConfig: {
  `vector.dimensions`: 1536,
  `vector.similarity_function`: 'cosine'
}};

-- Patent relationships
(p:Patent)-[:ASSIGNED_TO]->(a:Assignee)
(p:Patent)-[:INVENTED_BY]->(i:Inventor)
(p:Patent)-[:CITES]->(p:Patent)
```

## 🔐 Security Configuration

### Authentication Flow
1. **Token Generation**: JWT tokens with expiration
2. **MCP Auth**: Fixed token `patent-mcp-token` for demo
3. **API Security**: Bearer token authentication
4. **CORS Configuration**: Allowed origins list

### Environment Variables
```bash
# Database Configuration
MARIADB_URL=mysql+aiomysql://user:password@localhost/patent_db
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# MCP Configuration
MCP_SERVER_URL=http://localhost:8001
AUTH_TOKEN=patent-mcp-token

# AI Configuration
OPENAI_API_KEY=your-openai-api-key
LANGSMITH_API_KEY=your-langsmith-key

# Application
SECRET_KEY=your-super-secret-key
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8001
```

## 🧪 Development Workflow

### 1. Code Organization
```
app/
├── __init__.py              # Main FastAPI app
├── api/v1/                 # REST API routes
├── web/                    # Frontend pages
├── mcp/                    # MCP integration
├── langgraph/               # AI report generation
├── db/                     # Database connections
├── models/                  # SQLAlchemy models
├── schemas/                 # Pydantic schemas
└── crud/                   # Database operations
```

### 2. Testing Strategy
```bash
# Unit tests
uv run pytest tests/

# Integration tests
uv run pytest tests/integration/

# MCP server tests
curl -X POST http://localhost:8001/mcp/tools/list \
  -H "Authorization: Bearer patent-mcp-token"

# API endpoint tests
curl -X POST http://localhost:8001/api/v1/patents/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "limit": 10}'
```

### 3. Quality Assurance
```bash
# Code formatting
uv run black app/ && uv run isort app/

# Type checking  
uv run mypy app/

# Linting
uv run flake8 app/
```

## 🚀 Deployment Guide

### Development Deployment
```bash
# Using uvicorn with reload
uv run uvicorn app:app --host 0.0.0.0 --port 8001 --reload
```

### Production Deployment
```bash
# Using Gunicorn with multiple workers
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app

# Docker deployment
docker build -t patent-board .
docker run -p 8001:8001 patent-board

# Environment variables for production
export DATABASE_URL=production-db-url
export SECRET_KEY=production-secret
export OPENAI_API_KEY=prod-api-key
```

## 🔧 Troubleshooting

### Common Issues & Solutions

1. **MCP Server Not Responding**
   ```bash
   # Check if MCP server is running
   curl -X POST http://localhost:8001/mcp/tools/list
   
   # Verify token
   curl -X POST http://localhost:8001/mcp/tools/list \
     -H "Authorization: Bearer patent-mcp-token"
   ```

2. **Database Connection Issues**
   ```bash
   # Test MariaDB connection
   uv run python -c "from app.db import get_mariadb_db; print('MariaDB OK')"
   
   # Test Neo4j connection  
   uv run python -c "from app.db import get_neo4j_db; print('Neo4j OK')"
   ```

3. **Frontend Not Loading**
   ```bash
   # Check static files are served
   curl -I http://localhost:8001/static/css/main.css
   
   # Verify templates are accessible
   curl -I http://localhost:8001/
   ```

4. **LangGraph Report Generation Failing**
   ```bash
   # Check OpenAI API key
   echo $OPENAI_API_KEY
   
   # Test LangGraph directly
   uv run python -c "from app.langgraph import report_generator; print('LangGraph OK')"
   ```

## 📊 Performance Optimization

### Database Optimization
- **MariaDB**: Connection pooling, query optimization
- **Neo4j**: Index optimization, query tuning
- **Caching**: Redis for frequent queries

### API Performance
- **Async Operations**: All database operations async
- **Rate Limiting**: Prevent abuse
- **Pagination**: Large dataset handling
- **Response Compression**: gzip for API responses

## 🔄 Monitoring & Logging

### Application Metrics
- Request/response times
- Error rates by endpoint
- Database query performance
- MCP tool usage statistics

### Health Checks
```bash
# Application health
curl http://localhost:8001/health

# MCP server health
curl http://localhost:8001/mcp/health

# Database health
uv run python -c "
from app.db import get_mariadb_db, get_neo4j_db
print('Health check passed')
"
```

## 📚 Additional Resources

### Documentation
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **MCP Specification**: https://modelcontextprotocol.io/
- **LangGraph Guide**: https://langchain-ai.github.io/langgraph/
- **Neo4j Python**: https://neo4j.com/docs/python-manual/current/

### Community & Support
- **FastAPI Discord**: https://discord.gg/VQjSZtVua6UyfBHy
- **Neo4j Community**: https://community.neo4j.com/
- **LangChain Discord**: https://discord.gg/c6dPNZZWAj7p9s

## 🎯 Best Practices

### Code Standards
- **Type Hints**: Full type annotations
- **Error Handling**: Comprehensive try/catch blocks
- **Logging**: Structured logging with levels
- **Documentation**: Docstrings for public interfaces
- **Testing**: Unit and integration test coverage

### Security Standards
- **Input Validation**: Pydantic models everywhere
- **SQL Injection Prevention**: Parameterized queries only
- **Authentication**: Secure token handling
- **CORS**: Proper origin configuration
- **Environment Variables**: Never commit secrets

## 📝 Agent Responsibilities

When working on this project, focus on:

### For Code Changes
1. **Maintain Architecture**: Follow established patterns
2. **Type Safety**: No `any`, `ignore` without justification
3. **Test Thoroughly**: Cover edge cases
4. **Document Changes**: Update relevant documentation

### For MCP Integration
1. **Tool Design**: Clear input/output schemas
2. **Error Handling**: Graceful failure responses
3. **Authentication**: Secure token validation
4. **Performance**: Efficient query patterns

### For Database Work
1. **Connection Management**: Proper async connection handling
2. **Query Optimization**: Efficient SQL/Cypher queries
3. **Data Consistency**: Maintain referential integrity
4. **Migration Safety**: Version control schema changes

### For Frontend Development
1. **Responsive Design**: Mobile-first approach
2. **Accessibility**: WCAG 2.1 compliance
3. **Performance**: Lazy loading, code splitting
4. **User Experience**: Loading states, error feedback

---

**This document serves as the comprehensive guide for maintaining and extending the Patent Board full-stack application with MCP integration.**