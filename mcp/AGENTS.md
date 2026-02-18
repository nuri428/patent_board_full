# Patent Board MCP Server - Developer & Agent Guide

## 1. 📋 프로젝트 설명 (Project Description)
본 섹션은 Model Context Protocol (MCP)을 구현한 서버 프로젝트입니다. LLM 에이전트(예: Claude)가 특허 데이터베이스, 그래프 엔진, 시맨틱 검색 엔진에 직접 접근할 수 있도록 표준화된 도구(Tools) 인터페이스를 제공합니다.

## 2. 💻 설치 및 개발 환경 (Setup & Dev Environment)
- **런타임**: Python 3.12+
- **패키지 매니저**: `uv`
- **핵심 기술**: FastAPI, FastApiMCP
- **초기화**: `uv sync`를 통해 환경을 구축합니다.

## 3. 🚀 빌드/테스트/런 명령어 (Commands)
- **실행**: `uv run uvicorn mcp_server:mcp_app --host 0.0.0.0 --port 8001`
- **테스트**: `uv run pytest tests/`
- **도구 목록 확인**: `curl -X POST http://localhost:8001/tools/list`

## 4. 📏 코드 스타일 & 컨벤션 (Conventions)
- **도구 정의**: `@mcp_app.post("/tools/{name}")` 데코레이터를 사용하여 기능을 노출합니다.
- **입출력 규격**: 모든 도구는 Pydantic 모델을 통해 입력을 검증하고 `StandardResponse` 형식으로 응답합니다.
- **비동기 처리**: 성능을 위해 모든 DB 쿼리 및 네트워크 호출은 비동기 방식으로 구현합니다.

## 5. 🏗️ 기술 스택 & 주요 폴더 구조 (Stack & Structure)
### 기술 스택
- **Core**: FastAPI, FastApiMCP
- **Graph**: Neo4j (GDS 포함)
- **Search**: OpenSearch (Vectors)
- **Model Interface**: Pydantic

### 폴더 구조
- `db/`: Neo4j 및 MariaDB 접근 로직
- `auth/`: API Key 인증 처리
- `services/`: 핵심 분석 로직 (V2 기술 매퍼 등)
- `mcp_server.py`: 메인 엔트리포인트 및 도구 정의

## 6. 🤖 기대 행동 & 역할 정의 (Role Definition)
- **Self-Documenting**: 각 도구의 Docstring을 상세히 작성하여 LLM이 올바르게 이해하고 호출할 수 있도록 합니다.
- **Error Transparency**: 오류 발생 시 상세한 에러 메시지를 반환하여 에러 원인을 추적 가능하게 합니다.
- **Tracing**: 모든 분석 작업은 `analysis_run_id`를 통해 추적 가능하게 관리해야 합니다.

## 7. 🚫 금지 규칙 (Prohibited Rules)
- **인증 우회 금지**: API Key 검증을 거치지 않는 공개 도구 생성을 금지합니다.
- **과도한 데이터 반환 금지**: 한 번의 호출로 시스템 리소스를 과다 소모하는 대량 데이터 반환을 지양합니다.
- **비표준 응답 금지**: 반드시 약속된 JSON 스바르를 준수해야 합니다.

## 8. 📚 참조 문서 링크 & 단서 (References)
- **전체 가이드**: [../AGENTS.md](file:///home/nuri/dev/git/patent_board_full/AGENTS.md)
- **MCP 명세**: [https://modelcontextprotocol.io/](https://modelcontextprotocol.io/)