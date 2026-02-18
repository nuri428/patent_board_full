# Patent Board Full Stack - Agent Setup & Documentation

## 1. 📋 프로젝트 설명 (Project Description)
본 프로젝트는 AI 기반 특리 분석 플랫폼으로, 다중 데이터베이스(MariaDB + Neo4j + OpenSearch)와 LangGraph 에이전트 워크플로우를 통합하여 복합적인 특 허 데이터 분석 및 리포트 생성을 지원합니다.

- **핵심 목표**: 대규모 특허 데이터의 정규 검색 및 시맨틱/그래프 분석 자동화.
- **주요 기능**: 시맨틱 검색, 그래프 기반 관계 분석, 다중 에이전트 채팅, 자동 리포트 생성(PDF/CSV).

## 2. 💻 설치 및 개발 환경 (Setup & Dev Environment)
- **런타임**: Python 3.12+, Node.js 20+
- **패키지 매니저**: `uv` (Fast Python package manager), `npm`
- **주요 환경 설정**:
  1. 저장소 클론: `git clone <repo-url>`
  2. 가상환경: `python -m venv .venv` && `source .venv/bin/activate`
  3. 의존성 설치: `uv sync` && `cd front_end && npm install`
  4. 환경 변수: `.env.example`을 `.env`로 복사 후 API 키 설정.

## 3. 🚀 빌드/테스트/런 명령어 (Commands)
### 애플리케이션 실행
- **전체 서비스**: `./start.sh` (Backend + Frontend + MCP)
- **Backend (FastAPI)**: `cd back_end && uv run uvicorn app.main:app --reload`
- **Chatbot Server**: `cd back_end/chatbot && uv run uvicorn main:app --reload --port 8003`
- **Frontend (React)**: `cd front_end && npm run dev`
- **MCP Server**: `cd mcp && uv run uvicorn mcp_server:mcp_app --reload`

### 테스트 및 품질 관리
- **Backend Tests**: `uv run pytest tests/`
- **Frontend Tests**: `cd front_end && npm test`
- **Lint/Format**: `uv run black .` / `uv run isort .` / `uv run mypy .`

## 4. 📏 코드 스타일 & 컨벤션 (Conventions)
- **비동기 패턴**: 모든 DB 작업 및 외부 API 호출은 `async/await`를 기본으로 함.
- **API 버전 관리**: 모든 REST 엔드포인트는 `/api/v1/` 접두사를 사용.
- **데이터 모델**: 요청/응답 스키마는 Pydantic (`app/schemas/`)을 사용하며, 공통 응답 포맷(`StandardResponse`) 준수.
- **오류 처리**: 전역 예외 처리기에서 JSON 형태의 일관된 오류 메시지 반환.
- **DB 접근**: SQLAlchemy는 비동기 드라이버(`aiomysql`)를 사용.

## 5. 🏗️ 기술 스택 & 주요 폴더 구조 (Stack & Structure)
### 기술 스택
- **Backend**: FastAPI, LangGraph, OpenAI SDK
- **Databases**: MariaDB (정형 데이터), Neo4j (그래프), OpenSearch (시맨틱), Redis (캐시)
- **Frontend**: React 19, Tailwind CSS, Vite

### 폴더 구조
```
patent_board_full/
├── back_end/app/           # FastAPI 백엔드 (API, CRUD, Models, Schemas)
├── back_end/chatbot/       # 독립 챗봇 서비스 (LangGraph)
├── back_end/common/        # 백엔드 공통 로직 (MCP Client 등)
├── front_end/src/          # React 프론트엔드 (Components, Pages, Hooks)
├── mcp/                    # Model Context Protocol 서비스 (Patent DB Interface)
├── shared/                 # 공통 유틸리티 및 스키마
├── scripts/                # DB 초기화 및 마이그레이션 도구
└── docs/                   # 문서 및 작업 로그
```

## 6. 🤖 기대 행동 & 역할 정의 (Role Definition)
### AI 에이전트의 역할
- **Architecture Holder**: 다중 DB와 MCP 연동 패턴, 그리고 `back_end/chatbot/`에 위치한 단독 챗봇 서버의 SSE 스트리밍 프로토콜을 유지해야 함.
- **Code Integrity**: 모든 변경 사항은 타입 힌트를 포함하고 테스트로 검증되어야 함.
- **Documentation**: 중요한 로직 변경 시 `docs/` 및 `AGENTS.md`를 최신화해야 함.

## 7. 🚫 금지 규칙 (Prohibited Rules / Anti-Patterns)
- **동기 DB 호출 금지**: `async` 컨텍스트 내에서 동기식 DB 드라이버나 차단(blocking) 코드를 호출하지 말 것.
- **프론트엔드 직접 접근 금지**: 프론트엔드에서 데이터베이스에 직접 쿼리하지 말 것 (반드시 API 경유).
- **CORS 설정**: 하드코딩된 오리진 대신 환경 변수 설정을 활용할 것.
- **예외 누락**: 빈 `except:` 블록을 사용하지 말고 상세한 로깅을 남길 것.

## 8. 📚 참조 문서 링크 & 단서 (References)
- **환경 설정 상세**: [ENVIRONMENT_SETUP.md](file:///home/nuri/dev/git/patent_board_full/ENVIRONMENT_SETUP.md)
- **README**: [README.md](file:///home/nuri/dev/git/patent_board_full/README.md)
- **API 문서**: 서버 실행 후 `http://localhost:8001/docs` (Swagger UI)
- **MCP 상세 사양**: [mcp/README.md](file:///home/nuri/dev/git/patent_board_full/mcp/README.md) 만약 존재한다면 참조.

---
**이 문서는 프로젝트 내 모든 AI 에이전트 및 개발자를 위한 핵심 가이드라인입니다.**