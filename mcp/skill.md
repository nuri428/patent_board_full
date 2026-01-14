# Antigravity Skill: FastAPI-MCP Secure Server

## 1. Context & Purpose
- 이 프로젝트는 `fastapi-mcp` 프레임워크를 사용하여 AI 에이전트 전용 데이터 통로를 구축함.
- **핵심 목표**: 사용자의 요청에 대해 Auth DB에서 인증을 거친 후, RDB와 GraphDB의 데이터를 조합(Hybrid)하여 응답함.

## 2. Authentication Logic (Security First)
- **Auth DB**: 서비스 데이터와 분리된 별도 DB(SQLite 또는 Redis 권장)를 사용.
- **Process**:
  1. 클라이언트 요청 시 Header에서 `X-API-Key` 추출.
  2. `auth.py`의 `verify_api_key` 함수가 Auth DB에서 키 유효성 확인.
  3. 인증 실패 시 즉시 MCP Error(401) 반환.
- **Antigravity Rule**: 새로운 Tool을 생성할 때 반드시 FastAPI의 `Depends(verify_api_key)`를 적용할 것.

## 3. Database & Hybrid Query Strategy (with .env)
- **접속 정보 관리**: 모든 데이터베이스(RDB, GraphDB, Auth DB)의 접속 주소, 계정, 비밀번호는 절대 코드에 노출하지 않는다.
- **참조 위치**: 프로젝트 루트(`.`)에 위치한 `.env` 파일의 설정값을 최우선으로 참고한다.
- **하이브리드 로직**: 
  - `.env`에 정의된 `DATABASE_URL`과 `NEO4J_URI`를 사용하여 엔진을 초기화한다.
  - 두 DB의 연동 쿼리 작성 시, 환경 변수에서 로드된 정보를 바탕으로 싱글톤(Singleton) 연결 객체를 사용한다.

## 4. Environment Variables Configuration (.env)
안티그래비티 에이전트는 아래 규칙에 따라 환경 변수를 로드하는 코드를 작성해야 한다.

- **필수 라이브러리**: `python-dotenv` 또는 `pydantic-settings`를 사용한다. (FastAPI 프로젝트이므로 `pydantic-settings` 권장)
- **변수명 규칙**:
  - `MARIADB_URL`: 인증 전용 DB 접속 정보(mariadb)
  - `PATENTDB_URL`: RDB(mariadb) 접속 정보
  - `NEO4J_URI`: Neo4j 접속 주소
  - `NEO4J_USER` / `NEO4J_PASSWORD`: Neo4j 인증 정보
  - `MCP_API_KEY`: 서버 보안을 위한 마스터 키 (필요 시)
- **구현 방식**: `config/` 폴더 내에 `settings.py`를 생성하여 환경 변수를 객체화하고, 프로젝트 전체에서 이 객체를 참조하도록 설계한다.

## 5. Implementation Rules (for Agent)
- **Framework**: 반드시 `fastapi_mcp` 라이브러리를 사용하며, `mcp.mount()`를 통해 SSE 엔드포인트를 노출함.
- **Async Only**: 모든 DB 및 외부 통신은 비동기(`async/await`)로 작성.
- **Naming**: Tool 이름은 `get_patent_network`, `check_auth_status`와 같이 기능을 명시적으로 표현.