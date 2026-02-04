# Patent Board 프로젝트 통합 수정 및 개선 리스트 (Refined)

코드베이스 분석을 통해 확인된 구체적인 기술 부채와 구현 누락 사항을 정리했습니다.

## 1. AI 핵심 기능 통합 (P0 – 가장 시급)
- **AI 채팅 서비스 실데이터 연결**: 
    - `back_end/app/api/v1/endpoints/chat.py`의 placeholder를 `back_end/app/langgraph/chatbot/main.py`의 실시간 로직으로 대체.
- **자동 리포트 생성 기능 활성화**:
    - `back_end/app/api/v1/endpoints/reports.py`의 `/generate`를 `back_end/app/langgraph/__init__.py`의 `PatentReportGenerator`와 연결.
    - 리포트 생성 상태를 `Report` 모델에 저장하고 비동기 처리 적용.

## 2. 시스템 설정 및 인프라 정합성 (P1)
- **설정 값 통일**: `config.py`, `mcp_client.py`, `.env.example` 간에 서로 다른 `MCP_SERVER_URL` (8000, 8081, 8082) 통일.
- **누락된 설정 추가**: `.env.example`에는 있으나 `app/core/config.py`의 `Settings` 클래스에서 누락된 `ELASTICSEARCH_URL` (또는 `OPENSEARCH_URL`) 필드 추가 및 검증 로직 구현.
- **데이터베이스 마이그레이션**: Alembic을 초기화하여 모델 변경 사항이 MariaDB/Neo4j에 체계적으로 반영되도록 구성.

## 3. 실데이터 기반 데이터 레이어 (P1)
- **MCP Fallback 제거**: `app/api/v1/endpoints/mcp.py`의 `Backend-Test-Fallback` 하드코딩된 데이터를 실제 데이터베이스 조회 결과로 대체.
- **알림 시스템 실체화**: `app/api/v1/endpoints/notifications.py`의 하드코딩된 알림 목록을 `Notification` 테이블(또는 관련 모델) 조회로 변경.

## 4. 프론트엔드 현대화 및 인증 강화 (P2)
- **기술 스택 문서 동기화**: `README.md` 등의 "Bootstrap/Vanilla JS" 설명을 실제 스택인 "React + Vite + Tailwind"로 현행화.
- **실제 인증 플로우 적용**: `front_end/src/App.jsx`의 `demo_token` 방식을 백엔드 JWT와 연동된 정식 로그인 로직으로 교체.
- **라우팅 최적화**: LandingPage에서 로그인 여부에 따라 자동으로 Dashboard/Chat으로 리다이렉트되는 로직 강화.

## 5. 테스트 및 가시성 (P3)
- **핵심 워크플로 테스트**: LangGraph의 리포트 생성 체인과 MCP 프록시 엔드포인트에 대한 통합 테스트(Integration Test) 우선 작성.
- **진행도 현행화**: 챗봇 30%, 리포트 20%로 표기된 수치를 실제 구현된 LangGraph 로직 수준을 반영하여 재조정 (현재 약 60% 수준이나 연결이 안 된 상태).

---
*최종 수정일: 2026-02-03*
