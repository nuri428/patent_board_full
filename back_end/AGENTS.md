# Patent Board Backend - Developer & Agent Guide

## 1. 📋 프로젝트 설명 (Project Description)
본 섹션은 Patent Board의 핵심 비즈니스 로직과 데이터 처리를 담당하는 FastAPI 백엔드 프로젝트입니다. MariaDB, Neo4j, OpenSearch 등 다중 데이터베이스와의 연동을 관리하며, LangGraph를 이용한 AI 에이전트 워크플로우를 제공합니다.

## 2. 💻 설치 및 개발 환경 (Setup & Dev Environment)
- **런타임**: Python 3.12+
- **패키지 매니저**: `uv`
- **주요 서비스 포트**:
  - **API 서버**: 8001 (Main Backend)
  - **챗봇 서버**: 8003 (Chatbot API in `chatbot/`)
- **주요 환경 변수**: `.env` 파일에 DB 연결 문자열 및 OpenAI API 키 설정 필요.
- **초기화**: `uv sync`를 통해 의존성을 설치하고 가상환경을 활성화합니다.

## 3. 🚀 빌드/테스트/런 명령어 (Commands)
- **Main API**: `uv run uvicorn app.main:app --reload --port 8001`
- **Chatbot Server**: `cd chatbot && uv run uvicorn main:app --reload --port 8003`
- **테스트**: `uv run pytest tests/`
- **DB 마이그레이션**: `alembic upgrade head`
- **품질 관리**: `uv run black .`, `uv run isort .`, `uv run mypy .`

## 4. 📏 코드 스타일 & 컨벤션 (Conventions)
- **비동기 필수**: 모든 CRUD 작업 및 외부 API 통신은 `async/await`를 사용합니다.
- **스키마 기반**: 요청 및 응답은 `app/schemas/`의 Pydantic 모델을 엄격히 준수합니다.
- **라우팅**: 기능별로 `app/api/v1/endpoints/`에 모듈화하여 관리합니다.
- **의존성 주입**: `fastapi.Depends`를 사용하여 DB 세션 및 인증을 처리합니다.

## 5. 🏗️ 기술 스택 & 주요 폴더 구조 (Stack & Structure)
### 기술 스택
- **Framework**: FastAPI
- **ORM/Query**: SQLAlchemy (Async), Neo4j Python Driver
- **AI/LLM**: LangGraph, OpenAI, LangChain
- **Others**: Pandas (Export), PyJWT (Auth), OpenSearch-py

### 폴더 구조
- `app/api/`: REST API 엔드포인트 정의
- `app/crud/`: 데이터베이스 생성/읽기/수정/삭제 로직
- `app/models/`: SQLAlchemy DB 모델
- `app/schemas/`: Pydantic 데이터 검증 모델
- `app/agents/`: AI 에이전트 및 리포트 생성기
- `chatbot/`: 독립 챗봇 서비스
- `common/`: 공통 유틸리티 및 MCP 클라이언트

## 6. 🤖 기대 행동 & 역할 정의 (Role Definition)
- **Architecture Holder**: 기존의 다중 DB 구조와 MCP 연동 패턴을 유지해야 합니다. 특히 `chatbot/`에 위치한 단독 챗봇 서버의 SSE(Server-Sent Events) 스트리밍 프로토콜을 이해하고 유지해야 합니다.
- **Code Integrity**: 모든 함수에 타입 힌트를 명시하고 `mypy` 검사를 통과해야 합니다.
- **에이전트 연동**: 새로운 AI 기능을 추가할 때는 `langgraph` 폴더의 기존 패턴을 따릅니다.

## 7. 🚫 금지 규칙 (Prohibited Rules)
- **Raw SQL 사용 지양**: 가급적 SQLAlchemy ORM 또는 Query Builder를 사용하십시오.
- **Blocking 코드 금지**: `time.sleep()` 등 비동기 루프를 방해하는 코드를 사용하지 마십시오.
- **하드코딩 금지**: 모든 설정 정보는 `app/core/config.py` 또는 환경 변수를 통해 관리합니다.

## 8. 📚 참조 문서 링크 & 단서 (References)
- **전체 가이드**: [../AGENTS.md](file:///home/nuri/dev/git/patent_board_full/AGENTS.md)
- **API 문서**: `http://localhost:8001/docs` (로컬 실행 시)
- **데이터베이스 가이드**: `docs/database_schema.md` (존재 시)
