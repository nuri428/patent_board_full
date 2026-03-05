# [Plan] Webpage - Patent Board 프론트엔드 페이지 구성

> **작성일**: 2026-03-04
> **상태**: Do (기존 구현 기준 역방향 정리)
> **버전**: v1.0

---

## 1. Feature 개요

| 항목 | 내용 |
|------|------|
| Feature Name | webpage |
| 유형 | Frontend SPA (React + Vite) |
| 목적 | AI 특허 분석 플랫폼의 모든 웹 페이지 및 레이아웃 구성 |
| 대상 사용자 | 특허 분석가, 연구원, 관리자 |

### 한 줄 요약

> React Router 기반 SPA로 인증 상태에 따라 랜딩/로그인 화면과 보호된 내부 분석 도구 페이지를 제공하는 프론트엔드 전체 구조

---

## 2. 배경 및 목표

### 배경
- Patent Board 플랫폼은 FastAPI 백엔드와 분리된 React SPA로 구성
- 인증된 사용자와 미인증 사용자의 접근 경로를 명확히 분리 필요
- 챗봇, 특허 검색, 그래프 분석, 보고서 등 다양한 기능을 하나의 SPA에서 제공
- Tailwind CSS 기반 프리미엄 디자인 시스템 (`premium-card`, `premium-button-primary`, `glass-morphism`)

### 목표
- **P0**: 인증 라우팅 분기 (랜딩/로그인 ↔ 보호된 내부 페이지)
- **P0**: 모든 내부 페이지에서 공통 레이아웃 (사이드바 + 헤더) 제공
- **P1**: 각 페이지별 API 연동 및 상태 관리
- **P2**: 실시간 알림 시스템 (NotificationsContext + Toast)

---

## 3. 범위 (Scope)

### 포함 (In Scope)

#### 페이지 목록

| 경로 | 컴포넌트 | 접근 권한 | 설명 |
|------|----------|-----------|------|
| `/` | `LandingPage` | 미인증 | 서비스 소개 랜딩 페이지 |
| `/login` | `Login` | 미인증 | 로그인 폼 |
| `/chat` | `Chat` (default) | 인증 필요 | AI 챗봇 (기본 진입점) |
| `/dashboard` | `Dashboard` | 인증 필요 | 통계 대시보드 |
| `/search` | `PatentSearch` | 인증 필요 | 특허 검색 (키워드/필터) |
| `/graph` | `GraphAnalysis` | 인증 필요 | Neo4j 그래프 시각화 |
| `/analysis` | `AnalysisWorkbench` | 인증 필요 | 시맨틱/네트워크 분석 워크벤치 |
| `/reports` | `Reports` | 인증 필요 | 보고서 목록/생성 |
| `/settings` | `Settings` | 인증 필요 | 사용자 설정 |
| `/admin` | `Admin` | admin 역할 | 관리자 패널 |

#### 공통 레이아웃 컴포넌트

| 컴포넌트 | 역할 |
|----------|------|
| `ProtectedLayout` | 인증 필요 라우트의 공통 래퍼 (Sidebar + Header + Outlet) |
| `Sidebar` | 좌측 내비게이션 (로고, 메뉴, 로그아웃) |
| `Header` | 상단 헤더 (페이지 제목, 알림 아이콘) |

#### 전역 Context

| Context | 역할 |
|---------|------|
| `AuthContext` | JWT 인증 상태, user 객체, login/logout |
| `NotificationsContext` | 알림 목록, 읽음 상태 |
| `ChatbotContext` | 챗봇 세션, 메시지 상태 |

#### 알림 시스템

- `NotificationCenter`: 벨 아이콘 클릭 시 드롭다운 알림 목록
- `ToastContainer` / `Toast`: 전역 토스트 메시지 (top-right, 5초)

### 제외 (Out of Scope)
- 백엔드 API 구현 (FastAPI)
- 모바일 앱
- SSR / Next.js 전환

---

## 4. 기술 스택

| 분류 | 기술 |
|------|------|
| 프레임워크 | React 18 + Vite |
| 라우팅 | React Router v6 |
| 스타일링 | Tailwind CSS + 커스텀 CSS (`premium-*`, `glass-morphism`) |
| 애니메이션 | Framer Motion |
| 아이콘 | Lucide React |
| HTTP 클라이언트 | Axios |
| 상태관리 | React Context API |
| E2E 테스트 | Playwright |

---

## 5. 페이지별 주요 기능

### LandingPage (`/`)
- Hero 섹션: 서비스 소개 + CTA 버튼
- Features 섹션: 6개 기능 카드 (Chatbot, Graph, Report, Agent, DB, Realtime)
- CTA 섹션: "Create Your Free Account"
- 네비게이션: `#features`, `#how-it-works`, Sign In 링크
- 배경: Framer Motion 애니메이션 blob 효과

### Login (`/login`)
- 이메일/비밀번호 폼
- JWT 토큰 발급 → `AuthContext` 저장
- 로그인 성공 시 `/chat` 리다이렉트

### Dashboard (`/dashboard`)
- 통계 카드 3개: Active Reports, Analyzed Patents, AI Credits
- 최근 조사 목록 (`RecentReports`)
- 사이드 패널: Pro Callout, Omni-Search 빠른 검색
- 데이터 출처: `/api/v1/reports/`, `/api/v1/analytics/overview`, `/api/v1/admin/statistics` (admin)

### Chat (`/chat`) — 기본 진입점
- 인증 사용자: 전체 `Chatbot` 컴포넌트 (분할 레이아웃)
- 미인증: `LimitedChat` → 로그인 유도
- `ChatbotContext`로 세션/메시지 상태 관리

### PatentSearch (`/search`)
- 검색 파라미터: title, abstract, assignee, ipc, inventor, status, country, filing_date
- Analyst Mode 토글 (고급 필터)
- MCP API 연동 (`patentMcpAPI`)
- 페이지네이션, 특허 상세 보기

### GraphAnalysis (`/graph`)
- Neo4j 그래프 데이터 시각화
- 노드-엣지 네트워크 인터랙션

### AnalysisWorkbench (`/analysis`)
- 탭 구성: SemanticSearch, NetworkAnalysis, TechMapping, VisualAnalytics
- `GraphVisualizer` 컴포넌트 포함

### Reports (`/reports`)
- 보고서 목록, 생성, LangGraph 멀티에이전트 실행

### Settings (`/settings`)
- 사용자 프로파일 설정

### Admin (`/admin`)
- `user?.role === 'admin'`인 경우에만 사이드바에 노출
- 시스템 통계, 사용자 관리

---

## 6. 라우팅 구조

```
App
├── AuthProvider
│   └── NotificationsProvider
│       ├── AppContent (Router)
│       │   ├── 인증됨
│       │   │   ├── / → /chat (redirect)
│       │   │   └── ProtectedLayout
│       │   │       ├── /chat
│       │   │       ├── /dashboard
│       │   │       ├── /search
│       │   │       ├── /graph
│       │   │       ├── /analysis
│       │   │       ├── /settings
│       │   │       ├── /reports
│       │   │       └── /admin
│       │   └── 미인증
│       │       ├── / → LandingPage
│       │       ├── /login → Login
│       │       └── * → / (redirect)
│       └── ToastContainer (전역)
```

---

## 7. 디자인 시스템

### 커스텀 CSS 클래스

| 클래스 | 용도 |
|--------|------|
| `premium-card` | 둥근 모서리 + 그림자 카드 컨테이너 |
| `premium-button-primary` | 인디고 계열 주요 버튼 |
| `glass-morphism` | 반투명 유리 효과 (Navbar 등) |

### 색상 팔레트
- Primary: `indigo-600` / `indigo-50`
- Secondary: `violet-600`
- Neutral: `slate-900` (텍스트), `slate-50` (배경)
- Success: `emerald-600`
- Warning: `amber-600`

---

## 8. API 연동 패턴

```js
// api/axios.js - 기본 Axios 인스턴스
import api from '../api/axios';

// 인증 헤더 자동 첨부 (Interceptor)
// Base URL: /api/v1 (Nginx proxy → FastAPI :8001)

// MCP API 별도 인스턴스
import { patentMcpAPI } from '../api/mcp';
// Base URL: /mcp-api (Nginx proxy → MCP Server :8082)
```

---

## 9. 완료 기준 (Definition of Done)

- [ ] 모든 10개 페이지 라우트 정상 동작
- [ ] 인증/미인증 라우팅 분기 정확
- [ ] 사이드바 네비게이션 active 상태 표시
- [ ] 알림 시스템 (Toast + NotificationCenter) 동작
- [ ] Playwright E2E 테스트 통과
- [ ] Vite 빌드 오류 없음

---

## 10. 의존성 (Dependencies)

| 의존성 | 설명 |
|--------|------|
| 백엔드 API | FastAPI `:8001` - 인증, 보고서, 분석, 관리자 |
| MCP 서버 | `:8082` - 특허 검색 MCP 도구 |
| Nginx | 리버스 프록시 (`:80` → 각 서비스) |
| MariaDB / Neo4j / OpenSearch | 외부 운영 DB (192.168.0.10) |

---

_역방향 작성: 기존 구현 코드 기반으로 Plan 문서 정리 (2026-03-04)_
