# Patent Board 프로젝트 코딩 수정 플랜 (FIN)

`docs/fix_list.md`에 명시된 우선순위에 따른 구체적인 코딩 수정 및 통합 계획입니다.

## [P0] AI 핵심 기능 통합

### 1.1 AI 채팅 엔드포인트 실구현
- **대상 파일**: [chat.py](file:///home/nuri/dev/git/patent_board_full/back_end/app/api/v1/endpoints/chat.py)
- **작업 내용**:
    - `chatbot/main.py`의 `chatbot_agent` 및 `context_engineering` 모듈을 임포트하여 `/ask` 엔드포인트와 연결.
    - `crud/chat.py`를 사용하여 실제 세션 및 메시지를 MariaDB에 저장.

### 1.2 자동 리포트 생성 및 비동기 처리
- **대상 파일**: [reports.py](file:///home/nuri/dev/git/patent_board_full/back_end/app/api/v1/endpoints/reports.py)
- **작업 내용**:
    - `langgraph/__init__.py`의 `PatentReportGenerator`를 호출하도록 수정.
    - `FastAPI.BackgroundTasks`를 통해 리포트 생성을 비동기로 수행하고, 결과를 `Report` 모델에 업데이트.

## [P1] 데이터 레이어 및 인증 안정화

### 2.1 인증(Auth) 시스템 완성 및 권한 분리
- **대상 파일**: [auth.py](file:///home/nuri/dev/git/patent_board_full/back_end/app/api/v1/endpoints/auth.py), [deps.py](file:///home/nuri/dev/git/patent_board_full/back_end/app/api/deps.py)
- **작업 내용**:
    - 로그인 시 `hashed_password` 검증 로직을 `passlib`를 사용하여 활성화.
    - 모든 API 엔드포인트에 `get_current_active_user` 의존성을 적용하여 보안 강화.
    - 어드민 전용 엔드포인트에는 기존 `get_current_active_superuser`를 적용하거나 이를 활용한 역할 기반 체크를 강화하여 권한 분리.

### 2.2 MCP 데이터 실데이터 강제 및 DB 튜닝
- **대상 파일**: [mcp.py](file:///home/nuri/dev/git/patent_board_full/back_end/app/api/v1/endpoints/mcp.py)
- **작업 내용**:
    - `mcp.py` 내의 `Backend-Test-Fallback` 하드코딩된 데이터 제거 및 MCP 서버 연결 실패 시 503 에러 반환.
    - Neo4j 벡터 인덱스 및 MariaDB 주요 쿼리 실행 계획을 점검하고 필요한 인덱스 적용.

### 2.3 알림 실데이터 연동 (CRUD 적용)
- **대상 파일**: [notifications.py](file:///home/nuri/dev/git/patent_board_full/back_end/app/api/v1/endpoints/notifications.py)
- **작업 내용**:
    - 현재 하드코딩된 알림 목록을 `Notification` 모델 쿼리로 대체.

### 2.4 문서 및 구조 정합성 최종 확인
- **대상 파일**: `README.md`, `PROJECT_COMPLETION.md`
- **작업 내용**:
    - 변경된 `back_end/app/` 구조와 포트 정보가 문서에 정확히 반영되었는지 최종 검토.

## [P2] 프론트엔드 및 실시간 기능 완성

### 3.1 프론트엔드 인증 및 라우팅 강화
- **대상 파일**: [App.jsx](file:///home/nuri/dev/git/patent_board_full/front_end/src/App.jsx)
- **작업 내용**:
    - `demo_token` 제거 및 실제 JWT 기반 `AuthContext` 연동.
    - 비인증 사용자가 인증 시 챗/대시보드로 적절히 리다이렉트되도록 라우팅 흐름 최적화.

### 3.2 리포트 페이지 및 시맨틱 검색 UI 구현
- **대상 파일**: [Reports.jsx](file:///home/nuri/dev/git/patent_board_full/front_end/src/pages/Reports.jsx) (신규), [PatentSearch.jsx](file:///home/nuri/dev/git/patent_board_full/front_end/src/pages/PatentSearch.jsx)
- **작업 내용**:
    - 리포트 목록/상세 UI 및 시맨틱 검색 옵션 추가. 백엔드 해당 엔드포인트 호출 연동.

### 3.3 WebSocket 기반 실시간 알림 시스템
- **대상 파일**: `NotificationsContext.jsx`, [notifications.py](file:///home/nuri/dev/git/patent_board_full/back_end/app/api/v1/endpoints/notifications.py)
- **작업 내용**:
    - 백엔드: 리포트 생성/챗봇 응답 완료 시점에 `manager.send_personal_message` 트리거 추가 (`BackgroundTasks` 활용).
    - 프런트: WebSocket 구독 로직 및 `framer-motion` 등을 활용한 알림 토스트 UI 구현.

### 3.4 프론트엔드 스타일 및 스택 일관성
- **대상 파일**: `LandingPage.jsx`, `index.css`
- **작업 내용**:
    - Bootstrap 요소를 Tailwind CSS로 완전히 전환하고, 프로젝트 전체의 디자인 톤 매칭.

## [P3] 검증 및 테스트
- **E2E 통합 테스트**: `back_end/tests/test_ai_integration.py`에서 [챗봇 -> 시맨틱 검색 -> 리포트 생성 -> 알림(WebSocket)] 전체 흐름 검증.
- **엔드포인트 헬스체크 자동화**: `back_end/verify_endpoints.py`로 실데이터 엔드포인트 상태 코드·필수 필드를 정기적으로 점검.
- **워크플로 단위 테스트**: `back_end/tests/test_langgraph_workflow.py`를 추가해 LangGraph 리포트 파이프라인 단계별 실패/성공 케이스와 MCP 오류 처리(503 등) 분기 검증.

---
*최종 수정일: 2026-02-03*
