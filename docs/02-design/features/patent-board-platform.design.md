# [Design] Patent Board Platform — IBM Black UI Redesign

> **작성일**: 2026-02-27
> **참조**: `docs/01-plan/features/patent-board-platform.plan.md`
> **상태**: Design Phase

---

## 1. 디자인 방향

### 핵심 컨셉

**IBM Carbon Design System × Black Data Dashboard**

| 항목 | 현재 (As-Is) | 목표 (To-Be) |
|------|------------|------------|
| 테마 | Light (흰 배경) | **Dark Black** (`#161616` 기반) |
| 색상 계열 | Indigo-Purple | **IBM Blue** (`#0f62fe`) + Data accent |
| 폰트 | 'Outfit' | **IBM Plex Sans** + **IBM Plex Mono** (코드/수치) |
| 레이아웃 | 직관적 카드 | **정보 밀도 높은 데이터 그리드** |
| 분위기 | 프리미엄 SaaS | **엔터프라이즈 분석 플랫폼** |

### 레퍼런스 컨셉

- IBM Carbon Design System — Gray 100 (다크) 팔레트
- Bloomberg Terminal — 데이터 밀도, 모노스페이스 수치
- AWS QuickSight Dark — 분석 대시보드 레이아웃

---

## 2. 디자인 시스템 정의

### 2.1 색상 팔레트 (CSS Variables)

```css
/* IBM Carbon Gray 100 기반 다크 팔레트 */
:root {
  /* 배경 계층 */
  --ibm-bg-base:     #161616;   /* 최상위 배경 (Gray 100) */
  --ibm-bg-layer-1:  #262626;   /* 카드, 패널 */
  --ibm-bg-layer-2:  #393939;   /* 입력, 드롭다운 */
  --ibm-bg-hover:    #474747;   /* 호버 상태 */

  /* 텍스트 */
  --ibm-text-primary:   #f4f4f4;  /* 주요 텍스트 */
  --ibm-text-secondary: #c6c6c6;  /* 보조 텍스트 */
  --ibm-text-placeholder: #6f6f6f; /* 플레이스홀더 */
  --ibm-text-disabled:  #525252;  /* 비활성 */

  /* 브랜드 / 인터랙션 */
  --ibm-blue:       #0f62fe;   /* Primary action */
  --ibm-blue-hover: #0353e9;   /* Hover */
  --ibm-blue-light: #4589ff;   /* Link, accent */

  /* 데이터 시각화 (순서대로 사용) */
  --data-1: #6929c4;   /* Purple — 시맨틱 */
  --data-2: #1192e8;   /* Cyan — 네트워크 */
  --data-3: #005d5d;   /* Teal — 기술 매핑 */
  --data-4: #9f1853;   /* Magenta — 경쟁사 */
  --data-5: #fa4d56;   /* Red — 위험/경고 */
  --data-6: #570408;   /* Dark Red */
  --data-7: #198038;   /* Green — 성공 */
  --data-8: #002d9c;   /* Dark Blue */
  --data-9: #ee538b;   /* Pink */
  --data-10: #b28600;  /* Gold */

  /* 상태 */
  --status-success:  #24a148;
  --status-warning:  #f1c21b;
  --status-error:    #da1e28;
  --status-info:     #0043ce;

  /* 테두리 / 구분선 */
  --ibm-border:       #393939;
  --ibm-border-strong: #525252;
  --ibm-border-focus: #0f62fe;

  /* 코드 / 수치 (IBM Plex Mono) */
  --mono-positive:  #42be65;   /* 증가 수치 */
  --mono-negative:  #fa4d56;   /* 감소 수치 */
  --mono-neutral:   #78a9ff;   /* 기준 수치 */
}
```

### 2.2 타이포그래피

```css
/* 폰트 패밀리 */
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

body {
  font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* 수치, 코드, 특허번호 */
.mono {
  font-family: 'IBM Plex Mono', 'Courier New', monospace;
  font-size: 0.875rem;
  letter-spacing: 0.02em;
}

/* 스케일 */
--text-xs:   0.75rem;    /* 12px — 레이블, 배지 */
--text-sm:   0.875rem;   /* 14px — 보조 텍스트, 모노 수치 */
--text-base: 1rem;       /* 16px — 기본 */
--text-lg:   1.125rem;   /* 18px — 섹션 제목 */
--text-xl:   1.25rem;    /* 20px — 페이지 부제목 */
--text-2xl:  1.5rem;     /* 24px — 페이지 제목 */
--text-3xl:  2rem;       /* 32px — Hero 수치 */
```

### 2.3 공통 컴포넌트 클래스 (Tailwind 확장)

```css
/* 다크 카드 */
.data-card {
  @apply bg-[#262626] border border-[#393939] rounded-none;
  /* Carbon은 기본적으로 직각 모서리 */
}

/* 데이터 테이블 헤더 */
.data-table-header {
  @apply bg-[#393939] text-[#c6c6c6] text-xs uppercase tracking-widest
         px-4 py-3 font-medium border-b border-[#525252];
}

/* 데이터 테이블 행 */
.data-table-row {
  @apply bg-[#262626] border-b border-[#393939]
         hover:bg-[#353535] transition-colors duration-100;
}

/* IBM 기본 버튼 */
.ibm-btn-primary {
  @apply bg-[#0f62fe] hover:bg-[#0353e9] text-white
         text-sm font-medium px-4 py-2 rounded-none
         transition-colors duration-100 focus:outline-none
         focus:ring-2 focus:ring-[#0f62fe] focus:ring-offset-2
         focus:ring-offset-[#161616];
}

/* Ghost 버튼 */
.ibm-btn-ghost {
  @apply text-[#0f62fe] hover:bg-[#393939]
         text-sm font-medium px-4 py-2 rounded-none;
}

/* 태그/배지 */
.data-tag {
  @apply inline-flex items-center gap-1 px-2 py-0.5
         text-xs font-mono rounded-none;
}

/* 수치 강조 */
.metric-value {
  @apply font-mono text-3xl font-light text-[#f4f4f4] tracking-tight;
}

.metric-delta-pos {
  @apply font-mono text-xs text-[#42be65]; /* +증가 */
}
.metric-delta-neg {
  @apply font-mono text-xs text-[#fa4d56]; /* -감소 */
}
```

### 2.4 그리드 시스템

Carbon 16-column grid 기반:

```
┌────────────────────────────────────────────────────┐
│  Sidebar (col: 1–2)  │  Content (col: 3–16)        │
│  w-16 collapsed      │  flex-1                     │
│  w-64 expanded       │                             │
└────────────────────────────────────────────────────┘
```

---

## 3. 레이아웃 설계

### 3.1 글로벌 레이아웃 (ProtectedLayout)

```
┌──────────────────────────────────────────────────────────────┐
│ TOP NAV BAR (h-12, bg:#161616, border-b:#393939)             │
│  ├─ [≡] Logo: PATENT BOARD     [Search] [Notif] [User]       │
└──────────────────────────────────────────────────────────────┘
┌─────────────┬────────────────────────────────────────────────┐
│ SIDEBAR     │  MAIN CONTENT                                  │
│ (collapsed: │  bg: #161616                                   │
│  w-16       │                                                │
│  expanded:  │  ┌── PAGE HEADER (bg:#262626, border-b)───┐   │
│  w-56)      │  │  Breadcrumb > Page Title       [Actions] │  │
│             │  └──────────────────────────────────────────┘  │
│ bg:#262626  │                                                │
│ border-r    │  ┌── CONTENT AREA ─────────────────────────┐  │
│ :#393939    │  │  p-6                                     │  │
│             │  │                                          │  │
│ Nav Items:  │  └──────────────────────────────────────────┘  │
│  Icon only  │                                                │
│  (collapse) │                                                │
└─────────────┴────────────────────────────────────────────────┘
```

**변경 사항**:
- 현재 `h-20` 헤더 → `h-12` 압축형 Top Nav (IBM 스타일)
- 사이드바: 아이콘 전용 collapse 모드 추가
- 사이드바 배경: `white` → `#262626`
- 활성 Nav Item: `bg-blue-50 text-blue-600` → `bg-[#0f62fe] text-white border-l-4 border-[#ffffff]`

### 3.2 Top Nav Bar 상세

```
┌──────────────────────────────────────────────────────────┐
│ [≡] PATENT BOARD    [  Search patents...  ]  [🔔] [PA▾] │
│  w-16→w-56 toggle   flex-1 max-w-sm              user   │
└──────────────────────────────────────────────────────────┘
bg: #262626
height: 48px (h-12)
border-bottom: 1px solid #393939
```

### 3.3 Sidebar 상세

```
[collapse 상태: w-16]        [expand 상태: w-56]
┌──────┐                    ┌────────────────────┐
│ 📊   │                    │ 📊 Dashboard        │
│ 📄   │                    │ 📄 Reports          │
│ 💬   │                    │ 💬 Chat             │
│ 🔍   │                    │ 🔍 Patent Search    │
│ 🕸   │                    │ 🕸 Graph Analysis   │
│ 🧪   │                    │ 🧪 Workbench        │
│ ─    │                    │ ─────────────────── │
│ ⚙   │                    │ ⚙  Settings         │
│ 🛡   │                    │ 🛡  Admin           │
└──────┘                    └────────────────────┘

Active state:
  bg: #0f62fe
  text: white
  left-border: 3px solid white

Hover state:
  bg: #353535
```

---

## 4. 페이지별 상세 설계

### 4.1 Dashboard (현재 → 변경)

#### As-Is (현재)
- 흰 배경 카드 3개 + 그라디언트 버튼
- "Recent Investigations" 테이블
- "Pro Upgrade" 다크 패널

#### To-Be (변경)

```
┌── DASHBOARD ──────────────────────────────────────────────┐
│ PAGE HEADER                                                │
│  Patent Intelligence Dashboard          [+ New Analysis]  │
│  Last updated: 2026-02-27 09:12 KST                       │
├───────────────────────────────────────────────────────────┤
│ METRICS ROW (4개 KPI 카드)                                  │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │
│ │ 12,503  │ │   847   │ │  1,204  │ │  98.2%  │          │
│ │ Patents │ │ Reports │ │Sessions │ │Accuracy │          │
│ │ ▲ +2.3% │ │ ▲ +12  │ │ ▼ -3   │ │  ──     │          │
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘          │
├────────────────────────────┬──────────────────────────────┤
│ RECENT ACTIVITY (col 8)    │ QUICK STATS (col 4)          │
│                            │                              │
│ ┌─ Data Table ───────────┐ │ ┌─ IPC Distribution ──────┐ │
│ │# │ ID │ Title │ Status │ │ │ H: ████████ 42%         │ │
│ │1 │ KR │ ...   │ DONE   │ │ │ G: ██████   31%         │ │
│ │2 │ US │ ...   │ PROC.  │ │ │ A: ████     18%         │ │
│ │  │    │       │        │ │ │ B: ██        9%         │ │
│ └────────────────────────┘ │ └─────────────────────────┘ │
│                            │                              │
│ ┌─ Timeline Chart ───────┐ │ ┌─ Top Assignees ─────────┐ │
│ │ 특허 출원 트렌드 (12M)   │ │ │ Samsung  ████████ 1,203 │ │
│ │ ─────────────────────  │ │ │ LG       ██████   892  │ │
│ │ 2025     2026          │ │ │ Hyundai  ████     543  │ │
│ └────────────────────────┘ │ └─────────────────────────┘ │
└────────────────────────────┴──────────────────────────────┘
```

**변경 상세**:
| 요소 | 현재 | 변경 |
|------|------|------|
| 배경 | `bg-gray-50` | `bg-[#161616]` |
| KPI 카드 | 흰 카드, 색상 아이콘 | 다크 카드, 수치 모노 폰트 |
| 수치 | `text-3xl font-bold text-gray-800` | `font-mono text-3xl font-light text-[#f4f4f4]` |
| 델타 | `text-green-500` / `text-red-500` | `--mono-positive` / `--mono-negative` |
| 테이블 헤더 | — | `data-table-header` 클래스 적용 |
| "Pro Upgrade" 패널 | 제거 대상 | 제거 후 Quick Stats로 교체 |

---

### 4.2 Patent Search

#### As-Is
- 흰 패널, Explorer/Analyst 토글 모드
- 파란색/보라색 버튼 모드 전환

#### To-Be

```
┌── PATENT SEARCH ──────────────────────────────────────────┐
│ PAGE HEADER                                                │
│  Patent Search                   [Mode: ○ BM25  ○ Semantic]│
├───────────────────────────────────────────────────────────┤
│ SEARCH PANEL (bg:#262626, p-4)                             │
│  ┌─────────────────────────────────────┐ [Search]         │
│  │ 🔍  Search patents, inventors...    │ ibm-btn-primary  │
│  └─────────────────────────────────────┘                  │
│  Filters: [IPC Class ▾] [Country ▾] [Date Range ▾]        │
├───────────────────────────────────────────────────────────┤
│ RESULTS (data-table)                                       │
│ ┌──┬──────────────┬────────────────────────┬───────────┐  │
│ │  │ App No.      │ Title                  │ Assignee  │  │
│ │  │ KR10-2024-..│ 무선통신 시스템의 제어방법│ 삼성전자  │  │
│ │  │ US17/123456  │ Method for wireless... │ Samsung   │  │
│ └──┴──────────────┴────────────────────────┴───────────┘  │
│ Showing 1-20 of 1,204 results                  [<] 1 [>]  │
└───────────────────────────────────────────────────────────┘
```

**변경 상세**:
| 요소 | 현재 | 변경 |
|------|------|------|
| 모드 토글 | Explorer/Analyst 탭 | BM25/Semantic 라디오 버튼 |
| 검색 입력 | `backdrop-blur-xl, opacity-80` | `bg-[#393939] border border-[#525252]` |
| 결과 표시 | 흰 카드 목록 | `data-table` 스타일 테이블 |
| 특허번호 | 일반 텍스트 | `font-mono text-[#78a9ff]` |
| Confidence HUD | purple-50 bg | `bg-[#262626]` 인라인 배지 |

---

### 4.3 Analysis Workbench (4탭)

#### As-Is
- 흰 배경 탭 컨테이너
- 각 탭에 색상 아이콘 (indigo/emerald/purple/amber)

#### To-Be

```
┌── ANALYSIS WORKBENCH ──────────────────────────────────────┐
│ ┌──────────────┬─────────────────┬───────────┬──────────┐  │
│ │ Semantic     │ Network Matrix  │Tech Map   │ Visual   │  │
│ │ Search       │                 │           │Analytics │  │
│ │ ●active      │                 │           │          │  │
│ └──────────────┴─────────────────┴───────────┴──────────┘  │
│ tab border-bottom: 2px solid #0f62fe (active)              │
│ tab color: #c6c6c6 (inactive) / #f4f4f4 (active)           │
├───────────────────────────────────────────────────────────┤
│ [Semantic Search Tab]                                      │
│  Query ─────────────────────────────────── [Search]       │
│                                                           │
│  ┌─ Results ─────────────────────────────────────────┐   │
│  │ Confidence: ██████████░░ 0.87   Patent: KR...     │   │
│  │ Confidence: █████████░░░ 0.81   Patent: US...     │   │
│  └───────────────────────────────────────────────────┘   │
│                                                           │
│ [Visual Analytics Tab]                                    │
│  ┌── IPC Section Distribution ──┐ ┌── Country ─────────┐ │
│  │  H ████████████████   42%   │ │   🇰🇷 KR  ████ 58%  │ │
│  │  G ████████████       31%   │ │   🇺🇸 US  ███  28%  │ │
│  │  A ██████             18%   │ │   🇨🇳 CN  ██   14%  │ │
│  └──────────────────────────────┘ └────────────────────┘ │
└───────────────────────────────────────────────────────────┘
```

**탭 스타일 변경**:
```css
/* 현재: rounded 탭 버튼 */
/* 변경: Carbon 스타일 언더라인 탭 */
.tab-item {
  border-bottom: 2px solid transparent;
  color: var(--ibm-text-secondary);
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
}
.tab-item.active {
  border-bottom-color: var(--ibm-blue);
  color: var(--ibm-text-primary);
}
```

**차트 색상 변경**:
```javascript
// 현재: 밝은 pastel 팔레트
// 변경: IBM 데이터 시각화 팔레트
const IBM_DATA_COLORS = [
  '#6929c4', // Purple
  '#1192e8', // Cyan
  '#005d5d', // Teal
  '#9f1853', // Magenta
  '#fa4d56', // Red
  '#570408', // Dark Red
  '#198038', // Green
  '#002d9c', // Dark Blue
  '#ee538b', // Pink
  '#b28600', // Gold
]
```

---

### 4.4 Chat (/chat)

#### As-Is
- 흰 사이드바 + 흰 메인 영역
- indigo 사용자 메시지 버블
- glass-morphism 헤더

#### To-Be

```
┌── CHAT ──────────────────────────────────────────────────┐
│ SIDEBAR (w-56, bg:#262626)  │ MAIN (bg:#161616)           │
│                             │                             │
│ ┌─ Sessions ─────────────┐ │ ┌─ Header ─────────────────┐│
│ │ + New Session          │ │ │  AI Patent Analyst  [⋯]  ││
│ │ ─────────────────────  │ │ │  Context: 12 patents     ││
│ │ ● Session 1 (active)   │ │ └─────────────────────────┘│
│ │   2026-02-27 09:12     │ │                             │
│ │   Session 2            │ │ ┌─ Messages ───────────────┐│
│ │   2026-02-26           │ │ │                           ││
│ │   Session 3            │ │ │  [User]                   ││
│ └────────────────────────┘ │ │  ┌──────────────────────┐││
│                             │ │  │ 삼성전자 무선통신    │││
│                             │ │  │ 특허 분석해줘        │││
│                             │ │  └──────────────────────┘││
│                             │ │   bg:#0f62fe text:white  ││
│                             │ │                           ││
│                             │ │  [AI]                     ││
│                             │ │  ┌──────────────────────┐││
│                             │ │  │ 분석 결과:            │││
│                             │ │  │ • 총 특허: 1,203건    │││
│                             │ │  │ • 주요 IPC: H04W...  │││
│                             │ │  └──────────────────────┘││
│                             │ │   bg:#262626 border      ││
│                             │ └─────────────────────────┘│
│                             │ ┌─ Input ──────────────────┐│
│                             │ │[특허에 대해 질문하세요...] ││
│                             │ │                   [Send→]││
│                             │ └─────────────────────────┘│
└─────────────────────────────┴─────────────────────────────┘
```

**메시지 스타일 변경**:
```css
/* 사용자 메시지 */
.user-message {
  background: #0f62fe;      /* IBM Blue (현재: indigo-600) */
  color: white;
  border-radius: 0;         /* 직각 (현재: rounded-2xl) */
}

/* AI 메시지 */
.ai-message {
  background: #262626;      /* 현재: white */
  color: #f4f4f4;
  border: 1px solid #393939;
  border-radius: 0;
}

/* AI 응답 내 수치 강조 */
.ai-message .number {
  font-family: 'IBM Plex Mono', monospace;
  color: #78a9ff;
}
```

**세션 목록 스타일**:
```css
/* 활성 세션 (현재: bg-primary-light 보라) */
.session-active {
  background: #393939;
  border-left: 3px solid #0f62fe;
  color: #f4f4f4;
}
```

---

### 4.5 Graph Analysis (/graph)

#### As-Is
- 흰 배경 ReactFlow 캔버스
- 분석 모드 컬러 배지

#### To-Be

```
┌── GRAPH ANALYSIS ─────────────────────────────────────────┐
│ TOOLBAR (bg:#262626, border-b:#393939)                     │
│  Mode: [Competitor▾]  Depth: [2▾]  [Analyze]  [Export]   │
├──────────────────────────────────────────────────────────┤
│ GRAPH CANVAS (bg:#0f0f0f)                                  │
│  • 노드: `bg-[#262626] border-[#393939]`                   │
│  • 활성 노드: `border-[#0f62fe]`                            │
│  • 엣지: `stroke: #525252` → `stroke: #0f62fe` (selected) │
│  • 배경: Dot pattern (#2a2a2a)                              │
├──────────────────────────────────────────────────────────┤
│ HUD (우측 상단, bg:#262626/80, backdrop-blur)               │
│  Nodes: 143  Edges: 89  Clusters: 7                       │
│  [Zoom +] [Zoom -] [Fit]                                  │
└───────────────────────────────────────────────────────────┘
```

**ReactFlow 스타일 변경**:
```javascript
// Node 스타일
style: {
  background: '#262626',
  border: '1px solid #393939',
  color: '#f4f4f4',
  fontSize: '11px',
  fontFamily: 'IBM Plex Mono, monospace',
}

// Edge 스타일
style: {
  stroke: '#525252',
  strokeWidth: 1.5,
}
```

---

### 4.6 Reports

#### As-Is
- 흰 카드 그리드
- 컬러 상태 배지 (yellow/blue/green/red)

#### To-Be

```
┌── REPORTS ────────────────────────────────────────────────┐
│ PAGE HEADER                          [+ Generate Report]  │
├───────────────────────────────────────────────────────────┤
│ STATUS FILTER: [All ●] [Completed] [Processing] [Failed]  │
├───────────────────────────────────────────────────────────┤
│ REPORTS TABLE (data-table)                                 │
│ ┌────┬───────────┬──────────────────┬──────────┬───────┐  │
│ │ #  │ Type      │ Topic            │ Status   │ Date  │  │
│ │ 1  │ ANALYSIS  │ 삼성 무선통신 특허│ ● DONE   │ 02-27 │  │
│ │ 2  │ COMPETITOR│ LG vs Samsung   │ ◌ PROC.  │ 02-27 │  │
│ │ 3  │ TREND     │ H04W IPC trends  │ ○ PEND.  │ 02-26 │  │
│ └────┴───────────┴──────────────────┴──────────┴───────┘  │
│                                                           │
│ 상태 배지:                                                  │
│ DONE: ● (color: --status-success) text-mono              │
│ PROC: ◌ (color: --ibm-blue) text-mono + spinner          │
│ PEND: ○ (color: --ibm-text-placeholder)                  │
│ FAIL: ✕ (color: --status-error)                          │
└───────────────────────────────────────────────────────────┘
```

---

### 4.7 Login

#### As-Is
- `from-indigo-100 to-purple-100` 그라디언트 배경
- 흰 카드 + 상단 파란/보라 border bar

#### To-Be

```
┌── LOGIN ──────────────────────────────────────────────────┐
│ bg: #161616 (전체 화면)                                     │
│                                                           │
│         ┌─────────────────────────┐                       │
│         │ PATENT BOARD            │                       │
│         │ Patent Intelligence     │                       │
│         │ Platform                │                       │
│         │                         │                       │
│         │ Email ─────────────── │                       │
│         │ Password ────────────│                       │
│         │                         │                       │
│         │ [      Sign In       ]  │  ← ibm-btn-primary    │
│         │                         │                       │
│         │ Don't have an account?  │                       │
│         │ Register →              │                       │
│         └─────────────────────────┘                       │
│         bg: #262626, border: #393939                      │
└───────────────────────────────────────────────────────────┘
```

**변경 사항**:
- 그라디언트 배경 → 단색 `#161616`
- 흰 카드 → `bg-[#262626]`
- 상단 gradient border 유지 (→ `#0f62fe` 단색으로 단순화)
- Framer Motion 애니메이션 유지 (fade-in)

---

## 5. 구현 계획

### 5.1 변경 범위

| 파일 | 변경 유형 | 우선순위 |
|------|----------|----------|
| `front_end/index.html` | IBM Plex 폰트 로드 추가 | P0 |
| `front_end/src/index.css` | CSS 변수 전체 교체 + 다크 기반 | P0 |
| `front_end/tailwind.config.js` | IBM 팔레트 색상 추가 | P0 |
| `front_end/src/components/Layout/Sidebar.jsx` | 다크 사이드바 + collapse | P1 |
| `front_end/src/components/Layout/Header.jsx` | Top Nav Bar 압축 | P1 |
| `front_end/src/pages/Dashboard.jsx` | KPI 카드 + 데이터 테이블 | P1 |
| `front_end/src/pages/Chat.jsx` + `Chatbot/` | 메시지 스타일 변경 | P1 |
| `front_end/src/pages/PatentSearch.jsx` | 결과 테이블 형식 | P2 |
| `front_end/src/pages/Reports.jsx` | 테이블 + 상태 배지 | P2 |
| `front_end/src/pages/GraphAnalysis.jsx` | 다크 캔버스 | P2 |
| `front_end/src/components/AnalysisWorkbench/` | 탭 + 차트 색상 | P2 |
| `front_end/src/pages/Login.jsx` | 다크 로그인 | P3 |

### 5.2 구현 순서

```
Phase 1 (토대)
  └─ index.css CSS 변수 교체
  └─ tailwind.config.js IBM 팔레트
  └─ index.html 폰트 변경
         ↓
Phase 2 (레이아웃)
  └─ Sidebar 다크 + collapse
  └─ Header Top Nav
         ↓
Phase 3 (페이지)
  └─ Dashboard → Chat → PatentSearch → Reports
  └─ GraphAnalysis → AnalysisWorkbench
         ↓
Phase 4 (마무리)
  └─ Login
  └─ 차트 색상 일괄 변경
```

### 5.3 유지 사항 (변경 불필요)

- React Router 라우팅 구조 — 그대로 유지
- Axios API 클라이언트 — 변경 없음
- Framer Motion 애니메이션 — 유지 (페이드 효과 활용)
- Chart.js / ReactFlow 라이브러리 — 색상만 변경
- Lucide React 아이콘 — 유지
- AuthContext, ChatbotContext — 변경 없음
- Playwright E2E 테스트 — UI 셀렉터 일부 업데이트 필요

### 5.4 신규 추가 라이브러리

| 라이브러리 | 용도 | 필요 여부 |
|-----------|------|----------|
| `@carbon/react` | Carbon 컴포넌트 | 선택 (필요시) |
| `@carbon/charts-react` | IBM 전용 차트 | 선택 (기존 chart.js 대체 가능) |

> **권고**: IBM Plex 폰트 + CSS 변수 교체만으로 Carbon 분위기를 낼 수 있어 라이브러리 추가 없이 구현 가능. `@carbon/react` 도입은 선택 사항.

---

## 6. 컴포넌트 상세 스펙 (재사용 공통)

### DataCard

```jsx
// 변경 전
<div className="premium-card p-6">
  <h3 className="text-gray-500 text-sm">...</h3>
  <p className="text-3xl font-bold text-gray-800">12,503</p>
</div>

// 변경 후
<div className="bg-[#262626] border border-[#393939] p-4">
  <p className="text-xs text-[#c6c6c6] uppercase tracking-widest mb-1">Total Patents</p>
  <p className="font-mono text-3xl font-light text-[#f4f4f4]">12,503</p>
  <span className="font-mono text-xs text-[#42be65]">▲ +2.3%</span>
</div>
```

### DataTable

```jsx
// 재사용 가능한 IBM 스타일 테이블
<table className="w-full text-sm">
  <thead>
    <tr className="bg-[#393939] text-[#c6c6c6] text-xs uppercase tracking-widest">
      <th className="px-4 py-3 text-left font-medium">App No.</th>
      <th className="px-4 py-3 text-left font-medium">Title</th>
    </tr>
  </thead>
  <tbody>
    <tr className="bg-[#262626] border-b border-[#393939] hover:bg-[#353535]">
      <td className="px-4 py-3 font-mono text-[#78a9ff]">KR10-2024-0012345</td>
      <td className="px-4 py-3 text-[#f4f4f4]">무선통신 시스템...</td>
    </tr>
  </tbody>
</table>
```

### StatusBadge

```jsx
const STATUS_STYLES = {
  completed: 'text-[#24a148] bg-[#042008] border border-[#198038]',
  processing: 'text-[#78a9ff] bg-[#001141] border border-[#0043ce]',
  pending:    'text-[#c6c6c6] bg-[#393939] border border-[#525252]',
  failed:     'text-[#fa4d56] bg-[#2d0709] border border-[#da1e28]',
}

<span className={`font-mono text-xs px-2 py-0.5 ${STATUS_STYLES[status]}`}>
  {status.toUpperCase()}
</span>
```

---

## 7. 접근성 고려사항

| 항목 | 대응 |
|------|------|
| 명암비 | `#f4f4f4` on `#161616` = 15.3:1 (AAA 통과) |
| 포커스 링 | `ring-2 ring-[#0f62fe] ring-offset-[#161616]` |
| 다크 전용 | 라이트 모드 미지원 (시스템 설정 무관, 다크 고정) |
| 키보드 내비게이션 | Tab 순서 유지, focus-visible 스타일 적용 |

---

*이 문서는 기존 구현 코드를 기반으로 IBM Black 테마 적용 방향을 설계한 문서입니다.*
*실제 구현 시 `/pdca do patent-board-ui` 로 진행합니다.*
