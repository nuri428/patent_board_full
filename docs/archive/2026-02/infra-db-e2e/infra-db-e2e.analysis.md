# Gap Analysis: infra-db-e2e

- **Feature**: 인프라 안정화 (DB 접속 검증 + Docker Compose + E2E 테스트)
- **Date**: 2026-02-27
- **Analyzed by**: 직접 grep 검증
- **Match Rate**: 100% (18/18)

---

## 분석 범위

이전 세션에서 수행한 3가지 목표에 대한 설계 vs 구현 갭 분석:

1. **Goal 1**: 외부 DB 접속 검증 (MariaDB, Neo4j, OpenSearch, Redis)
2. **Goal 2**: Docker Compose 전체 서비스 정상화
3. **Goal 3**: Playwright E2E 헤드리스 테스트 12/12 통과

---

## Goal 1: 외부 DB 접속 검증 (7/7 ✅)

| # | 항목 | 파일 | 결과 |
|---|------|------|------|
| 1 | `REDIS_URL=redis://localhost:6379` | `.env` | ✅ |
| 2 | `health_check()` → `/` 루트 엔드포인트 | `opensearch_service.py` | ✅ |
| 3 | `check_redis()` → `aclose()` | `back_end/app/main.py` | ✅ |
| 4 | `check_opensearch()` 함수 추가 | `back_end/app/main.py` | ✅ |
| 5 | `/health/detailed` → `check_opensearch()` 포함 | `back_end/app/main.py` | ✅ |
| 6 | `AsyncSessionLocal = mariadb_session_factory` alias | `shared/database/__init__.py` | ✅ |
| 7 | `result.fetchone()` → `await` 제거 | `back_end/app/main.py` | ✅ |

### 최종 `/health/detailed` 응답
```json
{
  "status": "healthy",
  "services": {
    "mariadb": "healthy",
    "neo4j": "healthy",
    "mcp_server": "healthy",
    "redis": "healthy",
    "opensearch": "healthy"
  }
}
```

---

## Goal 2: Docker Compose 전체 서비스 정상화 (5/5 ✅)

| # | 항목 | 파일 | 결과 |
|---|------|------|------|
| 1 | healthcheck `CMD` → `CMD-SHELL` (3곳) | `docker-compose.yml` | ✅ |
| 2 | backend `REDIS_URL=redis://patent-board-redis:6379` | `docker-compose.yml` | ✅ |
| 3 | MCP multi-stage build | `docker/mcp/Dockerfile` | ✅ |
| 4 | venv → `/opt/mcp-venv` (볼륨 마운트 충돌 방지) | `docker/mcp/Dockerfile` | ✅ |
| 5 | langgraph `uv sync --frozen` + `--no-sync` | `docker/langgraph/Dockerfile` | ✅ |

### 최종 `docker ps` 결과
| 컨테이너 | 포트 | 상태 |
|----------|------|------|
| patent-board-backend | 48001 | ✅ healthy |
| patent-board-mcp | 48082 | ✅ healthy |
| patent-board-langgraph | 48003 | ✅ healthy |
| patent-board-frontend | 48080 | ✅ Up |
| patent-board-redis | 46379 | ✅ healthy |

---

## Goal 3: Playwright E2E 헤드리스 테스트 (6/6 ✅)

| # | 항목 | 파일 | 결과 |
|---|------|------|------|
| 1 | `VITE_API_PROXY_TARGET=http://localhost:48001` | `playwright.config.js` | ✅ |
| 2 | `localhost:8005` → `localhost:48001` 교체 | `patent-board.spec.js` | ✅ |
| 3 | `beforeAll` → `/health` 직접 체크 (기존 `/api/v1/health` 제거) | `patent-board.spec.js` | ✅ |
| 4 | 모달 셀렉터 `[role="dialog"]` → `getByText('Generate New Report')` | `patent-board.spec.js` | ✅ |
| 5 | 입력 셀렉터 `input[name="topic"]` → `input[placeholder*="Machine Learning..."]` | `patent-board.spec.js` | ✅ |
| 6 | Chromium 헤드리스 12/12 통과 (9.2초) | — | ✅ |

### 테스트 그룹별 결과
| 그룹 | 테스트 수 | 결과 |
|------|-----------|------|
| Health Check Integration | 2 | ✅ |
| Authentication Flow | 3 | ✅ |
| Report Generation Flow | 4 | ✅ |
| WebSocket Notification Flow | 2 | ✅ |
| End-to-End User Flow | 1 | ✅ |

---

## 잔여 이슈 (구현 완료 후 발견)

| 이슈 | 심각도 | 비고 |
|------|--------|------|
| Firefox E2E: `libgtk-3-0` 미설치 | Low | 호스트 시스템 패키지 문제, 서비스 영향 없음 |
| WebSocket `/api/v1/notifications/ws/{user_id}` 연결 실패 | Medium | E2E 통과이나 실제 알림 기능 미작동 |
| `admin/statistics` 스키마 확인 필요 | Low | Dashboard.jsx 필드 매핑 검증 필요 |

---

## 결론

**Match Rate: 100% (18/18)**

모든 설계 목표가 구현에 반영되었음이 확인되었습니다.

- 커밋 `2b73e07`: fix(infra): resolve docker compose startup and health check failures
- 커밋 `5842f7f`: test(e2e): fix playwright config and selectors for headless server environment

다음 권장 단계: `/pdca report infra-db-e2e`
