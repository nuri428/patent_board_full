# Patent Board TODO

> 마지막 갱신: 2026-02-26 (세션 2 완료)
> 기준: 코드베이스 실제 구현 상태와 문서(docs/, imp_plan/, chatbot_configuration_analysis.md) 비교

---

## 완료된 항목

### 기능 구현
- [x] AnalysisWorkbench API path migration to new MCP routes
- [x] AnalysisWorkbench unit test expectation alignment
- [x] **LLM 설정 외부화** — `config.py`에 `OPENAI_MODEL`, `OPENAI_TEMPERATURE`, `OPENAI_MAX_TOKENS` 등 환경변수화 완료
- [x] **시스템 프롬프트 외부화** — `CHATBOT_SYSTEM_PROMPT_TEMPLATE` 설정으로 분리 완료
- [x] **Context Engineering 설정 외부화** — `CONTEXT_ENGINEERING_PATENT_KEYWORDS`, `TECHNOLOGY_DOMAINS` 설정화 완료
- [x] **AnalysisWorkbench.jsx** — Semantic Search / Network Matrix / Tech Mapping / Visual Analytics 4탭 구현
- [x] **mcp_service.py** — MCP 서버 HTTP 클라이언트 (`semantic_search`, `network_analysis`, `technology_mapping`) 구현
- [x] **MCP 프록시 엔드포인트** — `mcp.py`에 semantic-search, network-analysis, tech-mapping 엔드포인트 추가
- [x] **GraphVisualizer.jsx** — ReactFlow 기반 그래프 시각화 (배치 처리, 노드 색상 코딩, 통계 HUD) 구현
- [x] **App.jsx 라우팅** — `/analysis` 라우트 등록 완료

### 인증 및 보안
- [x] Playwright E2E port stabilization (`3301`, `strictPort`)
- [x] Vite proxy target split for local vs docker (`VITE_API_PROXY_TARGET`)
- [x] MCP API-key verification restored to DB-backed validation (removed permissive bypass)
- [x] Secret handling tightened in backend/MCP config and utility scripts (env-first placeholders)
- [x] Neo4j patent search query safety improvements (parameterization and relationship allowlist)
- [x] MCP schema contract alignment (`test_mcp_schemas.py` + endpoint compatibility)
- [x] Backend test baseline recovered to green (`50 passed`)
- [x] P0 - Unify chatbot auth dependency (JWT vs demo token map)
- [x] P0 - Fix `/auth/status` coroutine/auth call bugs in chatbot service
- [x] P0 - Fix SSE auth flow mismatch (`front_end` vs `back_end/chatbot`)
- [x] P0 - Fix API client factory contract mismatch
- [x] P1 - Remove duplicated chatbot API surface and unify modules
- [x] P1 - Resolve Python type errors in chatbot service modules
- [x] P1 - Fix authenticated SSE user identity source mismatch
- [x] P1 - Add auth/ownership validation to notifications WebSocket endpoint
- [x] P1 - Protect admin statistics endpoint with auth/role checks
- [x] P1 - Validate custom export date filters to avoid 500 errors
- [x] P2 - Remove silent exception swallow in patent country statistics parsing
- [x] E2E failure root-cause validation and test hardening
- [x] Phase 3 evidence files refreshed under `.sisyphus/evidence/`

---

## 미완료 항목

### P0 — 인프라 (미완료)

> **중요**: MariaDB, OpenSearch, Neo4j는 외부에 이미 운영 중인 서비스에 접속하는 구조.
> Docker로 직접 띄우지 않음. `.env`의 접속 정보만 올바르면 됨.

- [x] **Docker Compose 포트 통일** — 개발 4만번대(48001/48080/48082/48003/46379), 운영 5만번대(58001/58080/58082/58003) 정리 완료
- [ ] **Playwright Firefox 의존성 설치** — `libgtk-3-0` 호스트 패키지 필요, E2E 전체 실행 차단 중
- [ ] **외부 DB 접속 정보 확인** — `.env`의 `MARIADB_URL`, `PATENTDB_URL`, `NEO4J_URI`, `OPENSEARCH_URL` 값이 실제 외부 서비스를 가리키는지 검증 (`/health/detailed` 응답으로 확인)
- [ ] **E2E 전체 실행** — 접속 정상화 후 skip 없는 Playwright 전체 통과 확인

---

### P1 — 기능 완성

- [x] **OpenSearch 직접 통합**
  - `back_end/app/services/opensearch_service.py` — httpx 기반 BM25 전문검색 + 집계 통계 구현
  - `config.py`에 `OPENSEARCH_URL/HOST/PORT/USER/PASSWORD/USE_SSL` 설정 추가
  - `.env`에 OpenSearch 접속 정보 추가

- [x] **Visual Analytics 탭 구현** (`front_end/src/components/AnalysisWorkbench/VisualAnalyticsTab.jsx`)
  - `react-chartjs-2` 기반 Bar / Doughnut 차트
  - 시맨틱 검색: IPC 섹션 분포 + 국가별 분포
  - 네트워크 분석: 노드 타입 분포 + 노드/엣지 수 카드
  - 기술 매핑: 상위 10개 기술 분류 수평 바 차트

---

### P2 — 코드 품질 개선 (완료)

- [x] **FastAPI deprecated lifecycle hooks 마이그레이션** (`back_end/app/langgraph/chatbot/main.py`)
  - `@app.on_event` → `asynccontextmanager lifespan` 으로 교체

- [x] **naive UTC 타임스탬프 교체** — 프로젝트 전체
  - `datetime.utcnow()` → `datetime.now(timezone.utc)` 전파 완료
  - 대상 파일: back_end 12개, mcp 2개, shared 1개, test 1개

- [x] **Reports 페이지 axios 클라이언트 교체** (`front_end/src/pages/Reports.jsx`)
  - raw `fetch` 3곳 → 공통 axios 인스턴스 통일

- [x] **Dashboard CTA / RecentReports 라우팅 수정**
  - `Dashboard.jsx`: 하드코딩 `totalPatents:12503`, `credits:500` 제거, `/analytics/overview` API 호출로 대체
  - `RecentReports.jsx`: dead route `/reports/new` → `/reports`

- [x] **MCP 클라이언트 dead 코드 제거** (`back_end/app/langgraph/mcp_client.py`)
  - no-op `try/except pass` 블록 제거

---

### P0 — 인프라 (미완료)
