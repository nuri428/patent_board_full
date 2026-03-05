# [Design] Frontend - TGIP 프론트엔드 상세 설계

> **작성일**: 2026-03-05
> **상태**: Design
> **버전**: v1.0
> **참고 Plan**: `docs/01-plan/features/frontend.plan.md`

---

## 1. 설계 개요

### 현재 구조 vs 목표 구조

| 항목 | 현재 (Patent Board) | 목표 (TGIP 통합) |
|------|---------------------|-----------------|
| 랜딩 | `/` → `LandingPage` | `/` → TGIP Landing |
| 앱 진입 | `/chat` (로그인 후) | `/app/tech/:id` (Workspace) |
| 분석 | `AnalysisWorkbench` | `ObservationCanvas` (RTS/TPI/FSS/WSD) |
| 공개 페이지 | 없음 | `/overview`, `/features`, `/demo`, `/docs` |

### 통합 전략

기존 Patent Board 라우트를 유지하면서 TGIP 라우트를 **추가**한다.
- 기존 인증 시스템(AuthContext) 그대로 사용
- TGIP 앱 페이지는 선택적 로그인 (공개 접근 허용)
- 공개 페이지(`/overview`, `/features`)는 완전 공개

---

## 2. 라우팅 설계

### 2.1 전체 라우트 맵

```
/                           → TGIPLanding (공개)
/overview                   → TGIPOverview (공개)
/features                   → TGIPFeatures (공개)
/features/rts               → TGIPFeatures (RTS 탭)
/features/tpi               → TGIPFeatures (TPI 탭)
/features/fss               → TGIPFeatures (FSS 탭)
/features/wsd               → TGIPFeatures (WSD 탭)
/demo                       → TGIPDemo (공개)
/docs                       → TGIPDocs (공개)
/about                      → TGIPAbout (공개)

/app                        → AppShell (기술 선택 → /app/tech/:id 리다이렉트)
/app/tech/:technology_id    → TGIPWorkspace (메인 분석 UI)
/app/runs/:run_id           → RunDetail (분석 실행 상세)
/app/library                → Library (저장된 기술/실행)
/app/settings               → TGIPSettings

-- 기존 Patent Board 라우트 (유지) --
/login                      → Login
/chat                       → ChatPage (인증 필요)
/dashboard                  → Dashboard (인증 필요)
/search                     → PatentSearch (인증 필요)
/graph                      → GraphAnalysis (인증 필요)
/analysis                   → AnalysisWorkbench (인증 필요)
/reports                    → Reports (인증 필요)
/settings                   → Settings (인증 필요)
/admin                      → Admin (인증 필요)
```

### 2.2 App.jsx 수정 계획

```jsx
// 추가할 import
import TGIPLanding from './pages/tgip/TGIPLanding';
import TGIPOverview from './pages/tgip/TGIPOverview';
import TGIPFeatures from './pages/tgip/TGIPFeatures';
import TGIPDemo from './pages/tgip/TGIPDemo';
import TGIPWorkspace from './pages/tgip/TGIPWorkspace';
import RunDetail from './pages/tgip/RunDetail';
import Library from './pages/tgip/Library';
import TGIPPublicLayout from './components/tgip/Layout/TGIPPublicLayout';
import TGIPAppLayout from './components/tgip/Layout/TGIPAppLayout';

// 라우트 구조 (공개 라우트 그룹 추가)
<Route element={<TGIPPublicLayout />}>
  <Route path="/overview" element={<TGIPOverview />} />
  <Route path="/features" element={<TGIPFeatures />} />
  <Route path="/features/:view" element={<TGIPFeatures />} />
  <Route path="/demo" element={<TGIPDemo />} />
  <Route path="/docs" element={<TGIPDocs />} />
  <Route path="/about" element={<TGIPAbout />} />
</Route>
<Route element={<TGIPAppLayout />}>
  <Route path="/app" element={<Navigate to="/app/tech/sample" replace />} />
  <Route path="/app/tech/:technology_id" element={<TGIPWorkspace />} />
  <Route path="/app/runs/:run_id" element={<RunDetail />} />
  <Route path="/app/library" element={<Library />} />
</Route>
```

---

## 3. 디렉토리 구조

```
front_end/src/
├── pages/
│   ├── tgip/                         # TGIP 전용 페이지
│   │   ├── TGIPLanding.jsx           # / 랜딩
│   │   ├── TGIPOverview.jsx          # /overview
│   │   ├── TGIPFeatures.jsx          # /features
│   │   ├── TGIPDemo.jsx              # /demo
│   │   ├── TGIPDocs.jsx              # /docs
│   │   ├── TGIPAbout.jsx             # /about
│   │   ├── TGIPWorkspace.jsx         # /app/tech/:id (핵심)
│   │   ├── RunDetail.jsx             # /app/runs/:run_id
│   │   └── Library.jsx               # /app/library
│   └── (기존 페이지들 유지)
│
├── components/
│   ├── tgip/                         # TGIP 전용 컴포넌트
│   │   ├── Layout/
│   │   │   ├── TGIPPublicLayout.jsx  # 공개 페이지 레이아웃
│   │   │   ├── TGIPAppLayout.jsx     # 앱 레이아웃 (헤더+사이드바+드로어)
│   │   │   ├── TGIPHeader.jsx        # 기술 셀렉터 + 버튼
│   │   │   └── TGIPFooter.jsx        # 면책 고지
│   │   ├── Workspace/
│   │   │   ├── TechnologySelector.jsx
│   │   │   ├── SidebarViewSelector.jsx
│   │   │   ├── ObservationCanvas.jsx
│   │   │   ├── RunController.jsx
│   │   │   └── EvidenceDrawer.jsx
│   │   ├── views/
│   │   │   ├── RTSView/
│   │   │   │   ├── RTSView.jsx
│   │   │   │   ├── MaturityScale.jsx
│   │   │   │   ├── ScoreBreakdownChart.jsx
│   │   │   │   ├── BottleneckIndicator.jsx
│   │   │   │   └── SolutionOptionsTable.jsx
│   │   │   ├── TPIView/
│   │   │   │   ├── TPIView.jsx
│   │   │   │   ├── PropagationGraph.jsx
│   │   │   │   ├── IndustryFlowDiagram.jsx
│   │   │   │   └── BurstTimeline.jsx
│   │   │   ├── FSSView/
│   │   │   │   ├── FSSView.jsx
│   │   │   │   ├── FamilyExpansionMeter.jsx
│   │   │   │   ├── GlobalCoverageMap.jsx
│   │   │   │   └── AssigneePressureTable.jsx
│   │   │   └── WSDView/
│   │   │       ├── WSDView.jsx
│   │   │       ├── ProblemSolutionHeatmap.jsx
│   │   │       ├── GapCandidatesList.jsx
│   │   │       └── CrossIndustryAnalogPanel.jsx
│   │   ├── overview/
│   │   │   ├── HeroSection.jsx
│   │   │   ├── MultiViewConcept.jsx
│   │   │   ├── PipelineStepper.jsx
│   │   │   ├── ViewCards.jsx
│   │   │   └── TrustSection.jsx
│   │   └── shared/
│   │       ├── CoverageIndicator.jsx
│   │       ├── ConfidenceBadge.jsx
│   │       ├── RunIdBadge.jsx
│   │       └── DisclaimerBanner.jsx
│   └── (기존 컴포넌트 유지)
│
├── context/
│   └── TGIPContext.jsx               # TGIP 전역 상태
│
└── api/
    └── tgip.js                       # TGIP API 클라이언트
```

---

## 4. 상태 관리 설계

### 4.1 TGIPContext

```jsx
// src/context/TGIPContext.jsx

const TGIPContext = createContext();

const initialState = {
  // Global
  selectedTechnology: null,       // { id, name, description }
  selectedView: 'RTS',            // 'RTS' | 'TPI' | 'FSS' | 'WSD'
  analysisRunId: null,            // string

  // Analysis Results
  results: {
    RTS: null,                    // RTSResult | null
    TPI: null,
    FSS: null,
    WSD: null,
  },

  // Evidence
  evidence: {
    representativePatents: [],
    ipcSignatures: [],
    abstractSnippets: [],
    confidenceScores: {},
  },

  // UI State
  isRunning: false,               // 분석 실행 중
  evidenceDrawerOpen: false,      // 드로어 열림 여부
  loadingView: null,              // 로딩 중인 뷰
  error: null,
};

// Actions
const tgipReducer = (state, action) => {
  switch (action.type) {
    case 'SET_TECHNOLOGY':       // 기술 선택
    case 'SET_VIEW':             // 뷰 전환 (재계산 없음)
    case 'RUN_ANALYSIS_START':   // 분석 시작
    case 'RUN_ANALYSIS_SUCCESS': // 결과 + run_id 수신
    case 'RUN_ANALYSIS_ERROR':   // 오류
    case 'TOGGLE_EVIDENCE':      // 드로어 토글
    case 'RESET':                // 초기화
  }
};
```

### 4.2 상태 흐름

```
기술 선택 (TechnologySelector)
  → SET_TECHNOLOGY
  → 기존 run_id 있으면 결과 로드
  → 없으면 빈 상태 표시

Run Analysis 클릭 (RunController)
  → RUN_ANALYSIS_START (isRunning = true)
  → POST /api/v1/tgip/analysis
  → RUN_ANALYSIS_SUCCESS (results + evidence + run_id)
  → isRunning = false

뷰 전환 (SidebarViewSelector)
  → SET_VIEW (selectedView 변경만, 재계산 없음)
  → ObservationCanvas가 해당 뷰 렌더링
```

---

## 5. API 연동 설계

### 5.1 API 엔드포인트 (백엔드 연동 필요)

```
POST /api/v1/tgip/analysis
  Request:  { technology_id, scope?, time_window? }
  Response: { run_id, results: {RTS, TPI, FSS, WSD}, evidence }

GET  /api/v1/tgip/runs/:run_id
  Response: { run_id, technology_id, results, evidence, logs, created_at }

GET  /api/v1/tgip/technologies?q=:query
  Response: [{ id, name, description, patent_count }]

GET  /api/v1/tgip/library
  Response: [{ technology_id, name, last_run_id, last_run_at }]
```

### 5.2 API 클라이언트 (`src/api/tgip.js`)

```js
import axiosInstance from './axios';

export const tgipApi = {
  // 분석 실행
  runAnalysis: (technology_id, options = {}) =>
    axiosInstance.post('/tgip/analysis', { technology_id, ...options }),

  // 실행 상세 조회
  getRunDetail: (run_id) =>
    axiosInstance.get(`/tgip/runs/${run_id}`),

  // 기술 검색
  searchTechnologies: (query) =>
    axiosInstance.get('/tgip/technologies', { params: { q: query } }),

  // 라이브러리
  getLibrary: () =>
    axiosInstance.get('/tgip/library'),
};
```

### 5.3 Mock 데이터 (MVP Phase 1 용)

백엔드 API 미완성 시 Mock 데이터를 사용한다:

```js
// src/api/tgip.mock.js
export const MOCK_RTS_RESULT = {
  score: 0.72,
  stage: 'Bottleneck',
  components: {
    patent_volume: 0.85,
    growth: 0.60,
    classification_conf: 0.78,
    citation_percentile: 0.65,
  },
};

export const MOCK_EVIDENCE = {
  representativePatents: [
    {
      id: 'KR1020230012345',
      title: '고체 전해질 기반 리튬 이온 배터리',
      abstract_snippet: '...',
      ipc: ['H01M 10/0562', 'H01M 10/052'],
      confidence: 0.91,
    },
  ],
  ipcSignatures: ['H01M 10/05', 'H01M 4/13'],
  confidenceScores: { overall: 0.87, coverage: 0.73 },
};
```

---

## 6. 컴포넌트 상세 설계

### 6.1 TGIPWorkspace (핵심 페이지)

```jsx
// pages/tgip/TGIPWorkspace.jsx
// 경로: /app/tech/:technology_id

const TGIPWorkspace = () => {
  const { technology_id } = useParams();
  const { state, dispatch } = useTGIP();

  // technology_id 변경 시 기술 로드
  useEffect(() => {
    if (technology_id && technology_id !== 'sample') {
      loadTechnology(technology_id);
    }
  }, [technology_id]);

  return (
    <div className="tgip-workspace h-screen flex flex-col">
      <TGIPHeader />
      <div className="flex flex-1 overflow-hidden">
        <SidebarViewSelector />
        <ObservationCanvas />
      </div>
      <EvidenceDrawer />
    </div>
  );
};
```

### 6.2 TGIPHeader

```
+------------------------------------------------------------+
| [TGIP]  [🔍 Technology Selector      ▼] [RTS▾] [▶ Run] [⬇]|
+------------------------------------------------------------+
```

Props/구성:
- `TechnologySelector`: 검색 드롭다운, debounce 300ms
- View Switch: 현재 뷰 표시 (드롭다운 or 탭)
- `RunAnalysisButton`: 실행 중엔 스피너 + 비활성화
- Export 버튼 (Phase 3)

### 6.3 SidebarViewSelector

```
+----------------------+
| RTS                  |
| Structural Maturity  |
| ███████░░░ 73%       |  ← coverage 지표
| Last: 2026-03-05     |
|                      |
| TPI                  |
| Propagation          |
| ░░░░░░░░░░ —         |  ← 미실행
|                      |
| FSS     [coming]     |
| WSD     [coming]     |
+----------------------+
```

### 6.4 ObservationCanvas

```jsx
const ObservationCanvas = () => {
  const { state } = useTGIP();
  const { selectedView, results, isRunning } = state;

  if (isRunning) return <AnalysisLoadingScreen />;
  if (!results[selectedView]) return <EmptyViewState view={selectedView} />;

  return (
    <div className="observation-canvas flex-1 overflow-auto p-6">
      {selectedView === 'RTS' && <RTSView data={results.RTS} />}
      {selectedView === 'TPI' && <TPIView data={results.TPI} />}
      {selectedView === 'FSS' && <FSSView data={results.FSS} />}
      {selectedView === 'WSD' && <WSDView data={results.WSD} />}
    </div>
  );
};
```

### 6.5 EvidenceDrawer

```
+------------------------------------------------------------+
| Evidence  [▲ collapse]                  Run ID: abc-123    |
+------------------------------------------------------------+
| Patent: KR1020230012345                                     |
| 고체 전해질 기반 리튬 이온 배터리                              |
| "...전해질 층의 두께를 최소화하여..." [confidence: 91%]       |
| IPC: H01M 10/0562, H01M 10/052                             |
|                                                            |
| [+ 4 more patents]                                         |
+------------------------------------------------------------+
```

구현 규칙:
- `evidence.representativePatents` 비어있으면 드로어 열림 불가
- 캔버스에서 신호 클릭 시 해당 근거로 드로어 스크롤

### 6.6 RTSView 컴포넌트

```jsx
// MaturityScale: 0~1 세그먼트 바
// stage별 색상: Critical Bottleneck(red) / Bottleneck(orange) / Closure(green)

// ScoreBreakdownChart: 4개 컴포넌트 수평 바 차트
// patent_volume / growth / classification_conf / citation_percentile

// BottleneckIndicator: stage 텍스트 + 아이콘

// SolutionOptionsTable: top-k 접근법 테이블
// | Approach | Patents | Coverage | Evidence |
```

### 6.7 Overview 페이지 컴포넌트

```
TGIPOverview
 ├── HeroSection
 │    ├── 제목/설명 텍스트
 │    └── CTA 버튼 (Open Demo, View Features)
 ├── MultiViewConceptSection
 │    ├── 설명 텍스트
 │    └── ViewCards (RTS/TPI/FSS/WSD 4카드)
 ├── LandscapeConceptSection
 │    └── 지리적 풍경 메타포 텍스트
 ├── PipelineSection
 │    └── PipelineStepper (6단계)
 └── CTAFooterSection
      └── CTA 링크들
```

---

## 7. 시각화 라이브러리 선택

| 컴포넌트 | 권장 라이브러리 | 대안 |
|----------|-----------------|------|
| MaturityScale (바) | Recharts ProgressBar | CSS only |
| ScoreBreakdownChart | Recharts BarChart | Nivo |
| BurstTimeline | Recharts LineChart | Chart.js |
| PropagationGraph | react-force-graph | D3.js |
| ProblemSolutionHeatmap | Nivo HeatMap | D3.js |
| GlobalCoverageMap | react-simple-maps | D3 geo |
| IndustryFlowDiagram | Recharts Sankey | D3 Sankey |

**MVP Phase 1 선택**: Recharts (이미 설치 여부 확인 필요, 없으면 설치)

---

## 8. 스타일 가이드 (Tailwind 기반)

### 색상 팔레트

```css
/* TGIP 브랜드 색상 */
--tgip-primary:    #1E40AF  (indigo-800)  /* 주 액션 */
--tgip-accent:     #0891B2  (cyan-600)    /* 강조 */
--tgip-rts:        #7C3AED  (violet-600)  /* RTS 뷰 */
--tgip-tpi:        #0891B2  (cyan-600)    /* TPI 뷰 */
--tgip-fss:        #DC2626  (red-600)     /* FSS 뷰 */
--tgip-wsd:        #059669  (emerald-600) /* WSD 뷰 */
--tgip-surface:    #F8FAFC  (slate-50)    /* 배경 */
--tgip-border:     #E2E8F0  (slate-200)   /* 경계 */
```

### 공통 클래스 패턴

```
tgip-card       → rounded-xl border border-slate-200 bg-white shadow-sm p-6
tgip-badge      → inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
tgip-section    → py-16 px-4 max-w-6xl mx-auto
tgip-view-tab   → 뷰 탭 (활성/비활성 스타일)
```

### 면책 고지 표시

모든 페이지 하단 및 Evidence 드로어:
```
"This system provides observational signals with evidence.
 Final decisions remain with the user."
```

---

## 9. 구현 순서 (Do Phase 체크리스트)

### Phase 1 — 핵심 UI 뼈대 (최우선)

```
[ ] 1. TGIPContext + tgipReducer 작성
[ ] 2. src/api/tgip.js API 클라이언트 작성 (Mock 포함)
[ ] 3. TGIPPublicLayout + TGIPAppLayout 레이아웃 컴포넌트
[ ] 4. App.jsx에 TGIP 라우트 추가
[ ] 5. TGIPOverview 페이지 (정적 콘텐츠)
[ ] 6. TGIPWorkspace 페이지 + TGIPHeader
[ ] 7. SidebarViewSelector (RTS 활성, TPI/FSS/WSD = coming soon)
[ ] 8. ObservationCanvas 컨테이너
[ ] 9. RTSView + MaturityScale + ScoreBreakdownChart (Mock 데이터)
[ ] 10. EvidenceDrawer (토글 + 특허 목록)
[ ] 11. RunController (실행 버튼 + 로딩 상태)
```

### Phase 2 — 멀티뷰 완성

```
[ ] 12. TPIView + PropagationGraph + BurstTimeline
[ ] 13. FSSView + GlobalCoverageMap + AssigneePressureTable
[ ] 14. WSDView + ProblemSolutionHeatmap + GapCandidatesList
[ ] 15. TGIPFeatures 페이지 (RTS/TPI/FSS/WSD 상세)
[ ] 16. RunDetail 페이지
```

### Phase 3 — 완성도

```
[ ] 17. TGIPLanding 랜딩 페이지 (기존 / 교체)
[ ] 18. TGIPDemo 데모 페이지 + 프리셋 기술
[ ] 19. Library 페이지
[ ] 20. PDF 내보내기
[ ] 21. TechnologySelector 실시간 검색 (백엔드 연동)
```

---

## 10. 주요 제약 및 규칙

| 규칙 | 설명 |
|------|------|
| Evidence 필수 | 캔버스에 신호 표시 시 근거 1개 이상 없으면 렌더링 금지 |
| 재계산 없는 뷰 전환 | 뷰 전환 시 API 재호출 없음 (기존 results 사용) |
| 처방 언어 금지 | "recommend", "best", "should" 등 카피 사용 금지 |
| 면책 고지 | 모든 페이지/내보내기에 고지 문구 포함 |
| run_id 표시 | Evidence Drawer에 항상 analysis_run_id 표시 |
| 기존 라우트 유지 | Patent Board 기존 `/chat`, `/dashboard` 등 그대로 동작 |

---

## 11. 의존성 추가 (필요 시)

```bash
# 시각화 (Recharts 미설치 시)
npm install recharts

# 지도 컴포넌트 (Phase 2 FSS)
npm install react-simple-maps

# 그래프 시각화 (Phase 2 TPI)
npm install react-force-graph-2d
```

현재 설치된 주요 패키지 확인 필요: `front_end/package.json`

---

## 12. 테스트 전략

| 수준 | 대상 | 방법 |
|------|------|------|
| 컴포넌트 | RTSView, EvidenceDrawer | Mock 데이터 렌더링 확인 |
| 상태 | TGIPContext reducer | unit test |
| E2E | Workspace 전체 플로우 | Playwright (기존 설정 활용) |
| 증거 규칙 | Evidence 없는 신호 렌더링 방지 | 컴포넌트 테스트 |
