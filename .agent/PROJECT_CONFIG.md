# Patent Board - 프로젝트 환경 설정

## 패키지 관리

| 항목 | 도구 |
|------|------|
| Python 패키지 관리 | `uv` |
| Node.js 패키지 관리 | `npm` |
| 컨테이너 관리 | `Docker Compose` |

## 실행 방법

### Python 스크립트 실행
```bash
uv run <script.py>
```

### 백엔드 로컬 실행
```bash
cd back_end
uv run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Docker 환경 실행
```bash
docker-compose up -d
```

## 주요 포트

| 서비스 | 포트 |
|--------|------|
| Backend (FastAPI) | 8001 |
| Frontend (React) | 3300 |
| MCP Server | 8081 |
| Neo4j | 7474 (HTTP), 7687 (Bolt) |
| MariaDB | 3306 |

## 데이터베이스 연결

| 용도 | 환경변수 | 데이터베이스 | 역할 | 상태 |
|------|----------|--------------|------|------|
| 사용자/시스템 | `MARIADB_URL` | MariaDB (`pa_system`) | 사용자 인증, 시스템 설정 | ✅ 연결됨 |
| 특허 데이터 | `PATENTDB_URL` | MariaDB (`patent_db`) | **Patch Data** (상세 데이터) | ✅ 연결됨 |
| 그래프 DB | `NEO4J_URI` | Neo4j | **KAG** (Knowledge Graph RAG) | ✅ 연결됨 |
| 검색 엔진 | `OPENSEARCH_URL` | OpenSearch | **RAG** (Vector Search) | 🔜 예정 |

## 데이터 흐름 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  OpenSearch │      │  patent_db  │      │    Neo4j    │
│   (검색)    │─────▶│ (상세 데이터)│      │  (그래프)   │
│             │ ID   │             │      │             │
└─────────────┘      └─────────────┘      └─────────────┘
```

**검색 흐름 (예정):**
1. OpenSearch에서 키워드 검색 → 특허 ID 목록 반환
2. patent_db에서 ID로 상세 정보 조회
3. Neo4j에서 관련 그래프 데이터 조회

## 필수 환경 변수

`.env` 파일에 다음 항목을 설정하세요:

```env
# Database
MARIADB_URL=mysql+aiomysql://user:password@host/pa_system
PATENTDB_URL=mysql+aiomysql://user:password@host/patent_db
NEO4J_URI=neo4j://host:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Security
SECRET_KEY=your-secret-key

# OpenAI (선택사항)
OPENAI_API_KEY=your-api-key
```
