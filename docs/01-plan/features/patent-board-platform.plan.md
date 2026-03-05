# [Plan] Patent Board Platform

> **작성일**: 2026-02-27
> **상태**: Completed (구현 완료 기준 역방향 정리)
> **버전**: v1.0

---

## 1. Feature 개요

| 항목 | 내용 |
|------|------|
| Feature Name | patent-board-platform |
| 유형 | Enterprise Fullstack Platform |
| 목적 | AI 기반 특허 분석 및 인사이트 도출 플랫폼 구축 |
| 대상 사용자 | 특허 분석가, 연구원, 관리자 |

### 한 줄 요약

> 멀티 DB(MariaDB·Neo4j·OpenSearch)와 LangGraph 멀티에이전트를 결합한
> 엔터프라이즈급 특허 분석 플랫폼

---

## 2. 배경 및 목표

### 배경
- 특허 데이터는 MariaDB(구조적), Neo4j(그래프 관계), OpenSearch(시맨틱 검색) 등 이기종 저장소에 분산
- 분석가가 각 DB를 개별 도구로 접근하면 생산성이 낮고 인사이트 연결이 어려움
- GPT-4 기반 AI 어시스턴트로 자연어 질의 → 특허 분석 보고서 자동화 필요

### 목표

| # | 목표 | 측정 기준 |
|---|------|-----------|
| G1 | 단일 UI에서 멀티 DB 통합 검색 | 4탭 분석 워크벤치 제공 |
| G2 | 자연어 기반 AI 챗봇으로 특허 분석 | LangGraph 멀티에이전트 챗봇 |
| G3 | AI 기반 리포트 자동 생성 | 클릭 → 리포트 PDF/Markdown 생성 |
| G4 | 역할 기반 접근 제어(RBAC) | admin / analyst / viewer 역할 |
| G5 | 외부 DB 무침습 연동 | 기존 DB 변경 없이 읽기 전용 연동 |

---

## 3. 기능 요구사항 (FR)

### FR-01 인증 및 권한 관리
- JWT 기반 로그인/로그아웃 (Access Token 1h, Refresh 7d)
- 역할: `admin`, `analyst`, `viewer`
- `/auth/login`, `/auth/register`, `/auth/me`, `/auth/status`

### FR-02 대시보드
- 전체 특허 수, 총 리포트 수, 활성 세션 수 통계 표시
- OpenSearch 집계 기반 실시간 지표
- 최근 리포트 목록 (RecentReports 컴포넌트)

### FR-03 특허 검색
- OpenSearch BM25 전문 검색 (`unified-patents-v1` 인덱스)
- 출원번호 / 제목 / 요약 / 청구항 필드 검색
- 검색 결과 pagination, 상세 보기

### FR-04 그래프 분석
- Neo4j Cypher 기반 특허 관계 그래프 조회
- ReactFlow 기반 인터랙티브 노드-엣지 시각화
- 노드 색상 코딩, 통계 HUD (노드 수, 엣지 수)
- 배치 처리로 대용량 그래프 안정 렌더링

### FR-05 분석 워크벤치 (4탭)
| 탭 | 기능 |
|----|------|
| Semantic Search | 시맨틱(임베딩) 기반 유사 특허 검색 |
| Network Analysis | 특허-발명자-출원인 관계 네트워크 분석 |
| Tech Mapping | 기술 분류별 특허 분포 매핑 |
| Visual Analytics | IPC섹션 분포 Bar / 국가별 분포 Doughnut / 기술 분류 수평 Bar |

### FR-06 AI 챗봇
- LangGraph 멀티에이전트 구조 (context-aware)
- SSE(Server-Sent Events) 스트리밍 응답
- 챗 세션 저장/조회 (MariaDB)
- MCP 도구 연동으로 검색/그래프 쿼리 수행

### FR-07 리포트 생성/관리
- 특허 분석 리포트 LLM 자동 생성
- 리포트 목록 조회, 삭제
- 리포트 버전 이력 관리

### FR-08 관리자 기능
- 전체 통계 조회 (admin 역할 한정)
- LLM 토큰 사용량 모니터링 (LLMUsage 모델)

### FR-09 MCP 서버 통합
- Model Context Protocol(MCP) 서버로 특허 쿼리 도구 통합
- 도구: `semantic_search`, `network_analysis`, `technology_mapping`
- 백엔드 MCP 프록시 → 프론트 단일 API 호출

---

## 4. 비기능 요구사항 (NFR)

| 항목 | 요구사항 |
|------|----------|
| 성능 | Redis 캐시로 반복 DB 쿼리 최소화 |
| 보안 | SQL Injection 방지 (SQLAlchemy ORM), Cypher 파라미터화, JWT 검증 |
| 확장성 | API 버전 `/api/v1/` — 미래 v2 대비 |
| 가용성 | 외부 DB 무침습: 기존 MariaDB/Neo4j/OpenSearch 서비스 변경 없음 |
| 코드품질 | Black/isort/flake8/mypy CI 자동 적용 |
| 테스트 | 백엔드 Pytest, E2E Playwright |

---

## 5. 시스템 아키텍처

```
[React 프론트] ←HTTP→ [FastAPI 백엔드 :8001]
                              ↓
                    ┌─────────────────────┐
                    │     서비스 레이어      │
                    ├─────────────────────┤
                    │ MariaDB (pa_system)  │  ← 사용자, 세션, 리포트
                    │ MariaDB (patent_db)  │  ← 특허 캐시
                    │ Redis               │  ← 캐시
                    └─────────────────────┘
                              ↓ HTTP
                    [MCP 서버 :8082]
                              ↓
                    ┌─────────────────────┐
                    │ Neo4j (patentsKg)   │  ← 그래프 관계
                    │ OpenSearch          │  ← 시맨틱/BM25
                    └─────────────────────┘

[LangGraph Chatbot :8001/chatbot]
    ↓ SSE 스트리밍
[React 챗 페이지]
```

### 포트 체계

| 서비스 | 개발(4만번대) | 운영(5만번대) |
|--------|-------------|-------------|
| FastAPI 백엔드 | 48001 | 58001 |
| React 프론트 | 48080 | 58080 |
| MCP 서버 | 48082 | 58082 |
| Redis | 46379 | 내부만 |

---

## 6. 기술 스택

### 백엔드
| 레이어 | 기술 |
|--------|------|
| 프레임워크 | FastAPI (Python 3.12) |
| ORM | SQLAlchemy 2.0 (async) |
| 패키지 관리 | uv |
| AI 오케스트레이션 | LangGraph |
| LLM | OpenAI GPT-4 (환경변수 교체 가능) |
| MCP | fastapi-mcp |

### 프론트엔드
| 레이어 | 기술 |
|--------|------|
| 프레임워크 | React 18 + Vite |
| 라우팅 | React Router v6 |
| 상태관리 | React Context (AuthContext) |
| HTTP 클라이언트 | Axios (공통 인스턴스, JWT 자동 첨부) |
| 차트 | react-chartjs-2 (Bar, Doughnut) |
| 그래프 시각화 | ReactFlow |

### 인프라
| 항목 | 기술 |
|------|------|
| 컨테이너 | Docker Compose (dev/prod 분리) |
| 캐시 | Redis |
| CI/CD | GitHub Actions (Black·isort·flake8·mypy·pytest·ESLint·Vite build) |

---

## 7. 데이터 모델 (주요 엔티티)

| 모델 | 테이블 | 역할 |
|------|--------|------|
| User | users | 사용자 (role: admin/analyst/viewer) |
| Report | reports | AI 생성 특허 분석 리포트 |
| ReportPatent | report_patents | 리포트 ↔ 특허 M:N |
| ChatSession | chat_sessions | 챗봇 대화 세션 |
| ChatMessage | chat_messages | 메시지 이력 |
| Patent | patents | MCP에서 캐시한 특허 데이터 |
| LLMUsage | llm_usages | GPT 토큰 사용량 추적 |
| SearchQuery | search_queries | 검색 이력 |
| Workspace | workspaces | 분석 워크스페이스 |
| PromptTemplate | prompt_templates | 커스텀 프롬프트 |

---

## 8. 우선순위 및 구현 상태

| 우선순위 | 기능 | 상태 |
|----------|------|------|
| P0 | JWT 인증, 사용자 RBAC | ✅ 완료 |
| P0 | FastAPI 백엔드 기반 구축 | ✅ 완료 |
| P0 | Docker Compose dev/prod | ✅ 완료 |
| P1 | LangGraph 멀티에이전트 챗봇 | ✅ 완료 |
| P1 | 분석 워크벤치 4탭 | ✅ 완료 |
| P1 | OpenSearch BM25 서비스 | ✅ 완료 |
| P1 | MCP 서버 + 백엔드 프록시 | ✅ 완료 |
| P1 | 그래프 시각화 (ReactFlow) | ✅ 완료 |
| P2 | 리포트 생성/버전 관리 | ✅ 완료 |
| P2 | Visual Analytics 차트 | ✅ 완료 |
| P2 | 코드 품질 (timezone, lifecycle) | ✅ 완료 |
| P3 | Playwright E2E 전체 통과 | 🔄 진행 중 |
| P3 | 외부 DB 실서버 접속 검증 | 🔄 진행 중 |

---

## 9. 제약사항 및 의존성

- **외부 DB 무침습**: MariaDB(192.168.0.10:3306), Neo4j(192.168.0.10:7688), OpenSearch(192.168.0.10:9200) — Docker 미사용, `.env`로만 관리
- **LLM 비용**: OpenAI API 사용량에 따른 비용 발생 → LLMUsage로 추적
- **SSE 스트리밍**: 챗봇 응답은 SSE로 전달 — WebSocket 미사용
- **MCP 버전**: Model Context Protocol 기반 도구 — fastapi-mcp 라이브러리 의존

---

## 10. 잔존 과제 (Known Issues)

| 항목 | 설명 | 우선순위 |
|------|------|----------|
| Playwright Firefox | `libgtk-3-0` 호스트 패키지 미설치 → E2E 전체 실행 차단 | P0 |
| 외부 DB 접속 검증 | `.env` 값이 실제 외부 서비스를 가리키는지 `/health/detailed`로 확인 필요 | P0 |
| E2E 전체 통과 | 접속 정상화 후 skip 없는 Playwright 전체 통과 확인 | P0 |

---

*이 문서는 현재 구현 상태를 기반으로 역방향(retrospective)으로 작성된 기획 문서입니다.*
