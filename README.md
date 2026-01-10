# Patent Board - Patent Analysis Platform

A comprehensive patent analysis platform built with FastAPI, featuring AI-powered insights, chat interface, and automated report generation.

## 🏗️ Architecture

- **Backend**: FastAPI with async/await patterns
- **Frontend**: Bootstrap 5 with vanilla JavaScript
- **Database**: MariaDB (structured data) + Neo4j (graph relationships)
- **AI Integration**: 
  - **MCP**: Model Context Protocol for data queries
  - **LangGraph**: Multi-agent workflow for report generation
  - **OpenAI**: LLM for natural language processing

## 🚀 Features

### Patent Search & Analysis
- Keyword and semantic search across patent databases
- Advanced filtering by date, status, assignee
- Relationship analysis using Neo4j graph database
- Patent detail views with metadata

### AI-Powered Chat
- Natural language patent queries
- Context-aware responses with source citations
- Chat history persistence
- Configurable response depth

### Automated Report Generation
- Multi-agent analysis workflow using LangGraph
- Technical analysis, market landscape, strategic insights
- Customizable report types and depth
- Export capabilities

## 📋 Project Structure

```
patent_board_full/
├── app/
│   ├── __init__.py              # FastAPI app initialization
│   ├── api/v1/                 # API routes
│   │   ├── api.py              # API router aggregation
│   │   └── endpoints/           # Individual endpoint modules
│   │       ├── auth.py          # Authentication endpoints
│   │       ├── patents.py        # Patent search/details
│   │       ├── chat.py          # AI chat interface
│   │       └── reports.py       # Report generation
│   ├── core/
│   │   └── config.py           # Configuration management
│   ├── db/
│   │   └── __init__.py         # Database connections (MariaDB + Neo4j)
│   ├── crud/
│   │   └── __init__.py         # Database operations
│   ├── models/
│   │   └── __init__.py         # SQLAlchemy models
│   ├── schemas/
│   │   └── __init__.py         # Pydantic schemas
│   ├── mcp/
│   │   └── __init__.py         # MCP client integration
│   ├── langgraph/
│   │   └── __init__.py         # Multi-agent report generation
│   └── web/
│       ├── routes.py             # Web page routes
│       ├── templates/            # HTML templates
│       └── static/              # CSS/JS assets
├── pyproject.toml              # Dependencies and build config
├── .env.example              # Environment variables template
└── start.sh                  # Startup script
```

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.12+
- MariaDB/MySQL
- Neo4j Database
- OpenAI API Key (for AI features)

### Installation

1. **Clone and setup environment**:
   ```bash
   git clone <repository>
   cd patent_board_full
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install uv
   uv sync
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your actual configuration
   ```

4. **Start the application**:
   ```bash
   ./start.sh
   ```

## 🌐 Access Points

- **Web Interface**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

## 🔧 Configuration

### Database Setup

**MariaDB** (structured patent data):
```sql
CREATE DATABASE patent_db;
CREATE USER 'patent_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON patent_db.* TO 'patent_user'@'localhost';
```

**Neo4j** (graph relationships):
```bash
# Start Neo4j
# Create constraints for performance
CREATE CONSTRAINT patent_id IF NOT EXISTS FOR (p:Patent) REQUIRE p.id IS UNIQUE;
```

### Environment Variables

Key `.env` settings:
- `MARIADB_URL`: MariaDB connection string
- `NEO4J_URI`: Neo4j bolt connection
- `OPENAI_API_KEY`: OpenAI API key for AI features
- `MCP_SERVER_URL`: MCP server endpoint

## 🤖 AI Integration Details

### MCP (Model Context Protocol)
- Provides unified interface to patent databases
- Supports multiple query types: search, get, graph_search, semantic_search
- Abstracts complex Neo4j Cypher queries
- Handles both MariaDB and Neo4j data sources

### LangGraph Workflow
```
Input Topic → Patent Collection → Data Analysis → Summary Generation → 
Section Creation → Report Compilation → Final Report
```

Multi-agent system with specialized roles:
- **Collector**: Gathers relevant patents via MCP
- **Analyzer**: Performs technical and market analysis
- **Summarizer**: Creates executive summaries
- **Section Writer**: Generates detailed report sections
- **Compiler**: Assembles final report document

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User authentication
- `POST /api/v1/auth/register` - User registration

### Patents
- `GET /api/v1/patents/` - List patents
- `GET /api/v1/patents/{id}` - Get patent details
- `POST /api/v1/patents/search` - Search patents

### Chat
- `POST /api/v1/chat/ask` - Send chat message
- `GET /api/v1/chat/history` - Get chat history

### Reports
- `POST /api/v1/reports/generate` - Generate new report
- `GET /api/v1/reports/` - List reports
- `GET /api/v1/reports/{id}` - Get report details

## 🧪 Development

### Running Tests
```bash
uv run pytest
```

### Code Quality
```bash
uv run black app/          # Format code
uv run isort app/          # Sort imports
uv run mypy app/           # Type checking
```

## 📝 Usage Examples

### Patent Search
```python
# Via API
import requests

response = requests.post(
    "http://localhost:8001/api/v1/patents/search",
    json={
        "query": "machine learning",
        "type": "semantic",
        "limit": 25
    }
)
```

### Report Generation
```python
# Generate comprehensive analysis
response = requests.post(
    "http://localhost:8001/api/v1/reports/generate",
    json={
        "topic": "Artificial Intelligence in Healthcare",
        "report_type": "comprehensive",
        "patent_ids": ["US12345", "US67890"]
    }
)
```

## 🚀 Deployment

### Docker (Recommended)
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install uv && uv sync
EXPOSE 8001
CMD ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0"]
```

### Production Considerations
- Use HTTPS with SSL certificates
- Configure CORS for production domains
- Set up database connection pooling
- Implement rate limiting
- Use production-grade secret management

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and test thoroughly
4. Commit changes: `git commit -m 'Add amazing feature'`
5. Push to branch: `git push origin feature/amazing-feature`
6. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Technologies Used

- **FastAPI** - Modern Python web framework
- **MariaDB** - Structured data storage
- **Neo4j** - Graph database for relationships
- **LangGraph** - Multi-agent AI workflows
- **MCP** - Model Context Protocol
- **Bootstrap 5** - Modern UI framework
- **uv** - Fast Python package manager

Built with ❤️ for patent professionals and researchers.