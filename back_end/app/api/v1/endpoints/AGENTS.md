# API Endpoints - FastAPI REST Layer

**OVERVIEW**: FastAPI REST endpoints providing patent search, chat, and report generation APIs.

## STRUCTURE
```
back_end/app/api/v1/endpoints/
├── auth.py          # Authentication & user management
├── patents.py        # Patent search and details
├── chat.py          # AI-powered chat interface
├── reports.py       # Report generation workflow
├── analytics.py     # Usage analytics
└── [9 other files]  # Admin, export, notifications, etc.
```

## WHERE TO LOOK
| Task | File | Notes |
|------|------|-------|
| User auth | `auth.py` | JWT tokens, session management |
| Patent search | `patents.py` | KR/US patent queries |
| AI chat | `chat.py` | LangGraph integration |
| Report generation | `reports.py` | Multi-agent workflow |

## CONVENTIONS
- **Authentication**: JWT for web UI, API keys for MCP
- **Response format**: Standardized JSON with `data` + `metadata`
- **Validation**: All endpoints use Pydantic schemas
- **Error handling**: Global exception handler at app level
- **Rate limiting**: Implemented via middleware

## ANTI-PATTERNS
- No synchronous database calls in async endpoints
- No bare except clauses - always log exceptions
- No hardcoded CORS origins in production
- No direct database access - always via CRUD layer