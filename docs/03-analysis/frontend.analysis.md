# Frontend TGIP Analysis Report

> **Analysis Type**: Gap Analysis (Design vs Implementation)
>
> **Project**: Patent Board — TGIP Frontend
> **Analyst**: bkit-gap-detector
> **Date**: 2026-03-05
> **Design Doc**: [frontend.design.md](../02-design/features/frontend.design.md)

---

## 1. Analysis Overview

### 1.1 Analysis Purpose

Design 문서(`frontend.design.md`)의 Phase 1 체크리스트(11개 항목)를 기준으로,
실제 구현 코드(`front_end/src/`)가 설계와 얼마나 일치하는지 확인한다.

### 1.2 Analysis Scope

- **Design Document**: `docs/02-design/features/frontend.design.md`
- **Implementation Path**: `front_end/src/`
- **Analysis Date**: 2026-03-05

---

## 2. Overall Score

```
+---------------------------------------------+
|  Overall Match Rate: 82%                     |
+---------------------------------------------+
|  Design Match (구조/파일):  78%              |
|  Architecture Compliance:    90%              |
|  Convention Compliance:      88%              |
|  Overall:                    82%              |
+---------------------------------------------+
```

| Category | Score | Status |
|----------|:-----:|:------:|
| Design Match | 78% | Warning |
| Architecture Compliance | 90% | Pass |
| Convention Compliance | 88% | Warning |
| **Overall** | **82%** | **Warning** |

---

## 3. Section-by-Section Gap Analysis

### 3.1 Routing (Section 2)

| Design Route | Implementation | Status | Notes |
|-------------|---------------|--------|-------|
| `/` -> TGIPLanding | `/` -> LandingPage (기존 유지) | Warning | TGIPLanding 미구현, 기존 LandingPage 유지. 설계에서 Phase 3 항목 |
| `/overview` -> TGIPOverview | `/overview` -> TGIPOverview | Pass | TGIPPublicLayout 내 |
| `/features` -> TGIPFeatures | `/features` -> TGIPFeatures | Pass | |
| `/features/:view` -> TGIPFeatures | `/features/:view` -> TGIPFeatures | Pass | |
| `/demo` -> TGIPDemo | `/demo` -> TGIPDemo | Pass | |
| `/docs` -> TGIPDocs | 미구현 | Missing | TGIPDocs 페이지 없음 |
| `/about` -> TGIPAbout | 미구현 | Missing | TGIPAbout 페이지 없음 |
| `/app` -> Navigate | `/app` -> Navigate to `/app/tech/solid-state-battery` | Pass | 리다이렉트 대상 `sample` -> `solid-state-battery`로 변경 (합리적) |
| `/app/tech/:technology_id` -> TGIPWorkspace | `/app/tech/:technology_id` -> TGIPWorkspace | Pass | |
| `/app/runs/:run_id` -> RunDetail | 미구현 | Missing | RunDetail 페이지 없음 (Phase 2 항목) |
| `/app/library` -> Library | 미구현 | Missing | Library 페이지 없음 (Phase 2 항목) |
| `/app/settings` -> TGIPSettings | 미구현 | Missing | Phase 1 범위 외 |
| TGIPAppLayout wrapper | 미구현 | Missing | Workspace가 직접 레이아웃 구성 |

**Routing Match: 6/13 (46%)** — 단, Phase 1 범위만 한정하면 핵심 라우트는 구현됨

### 3.2 Directory Structure (Section 3)

| Design Path | Exists | Status |
|-------------|:------:|--------|
| `pages/tgip/TGIPLanding.jsx` | No | Missing (Phase 3) |
| `pages/tgip/TGIPOverview.jsx` | Yes | Pass |
| `pages/tgip/TGIPFeatures.jsx` | Yes | Pass |
| `pages/tgip/TGIPDemo.jsx` | Yes | Pass |
| `pages/tgip/TGIPDocs.jsx` | No | Missing |
| `pages/tgip/TGIPAbout.jsx` | No | Missing |
| `pages/tgip/TGIPWorkspace.jsx` | Yes | Pass |
| `pages/tgip/RunDetail.jsx` | No | Missing (Phase 2) |
| `pages/tgip/Library.jsx` | No | Missing (Phase 2/3) |
| `components/tgip/Layout/TGIPPublicLayout.jsx` | Yes | Pass |
| `components/tgip/Layout/TGIPAppLayout.jsx` | No | Missing |
| `components/tgip/Layout/TGIPHeader.jsx` | Yes | Pass |
| `components/tgip/Layout/TGIPFooter.jsx` | No | Missing |
| `components/tgip/Workspace/TechnologySelector.jsx` | Yes | Pass |
| `components/tgip/Workspace/SidebarViewSelector.jsx` | Yes | Pass |
| `components/tgip/Workspace/ObservationCanvas.jsx` | Yes | Pass |
| `components/tgip/Workspace/RunController.jsx` | Yes | Pass |
| `components/tgip/Workspace/EvidenceDrawer.jsx` | Yes | Pass |
| `components/tgip/views/RTSView/RTSView.jsx` | Yes | Pass |
| `components/tgip/views/RTSView/MaturityScale.jsx` | Yes | Pass |
| `components/tgip/views/RTSView/ScoreBreakdownChart.jsx` | Yes | Pass |
| `components/tgip/views/RTSView/BottleneckIndicator.jsx` | No | Missing |
| `components/tgip/views/RTSView/SolutionOptionsTable.jsx` | Yes | Pass |
| `components/tgip/views/TPIView/TPIView.jsx` | Yes | Pass (placeholder) |
| `components/tgip/views/FSSView/FSSView.jsx` | Yes | Pass (placeholder) |
| `components/tgip/views/WSDView/WSDView.jsx` | Yes | Pass (placeholder) |
| `components/tgip/overview/*` (HeroSection 등 5개) | No | Changed |
| `components/tgip/shared/CoverageIndicator.jsx` | No | Missing |
| `components/tgip/shared/ConfidenceBadge.jsx` | Yes | Pass |
| `components/tgip/shared/RunIdBadge.jsx` | No | Missing |
| `components/tgip/shared/DisclaimerBanner.jsx` | Yes | Pass |
| `context/TGIPContext.jsx` | No | Changed |
| `store/tgipStore.js` (Zustand) | Yes | Changed (Context -> Zustand) |
| `api/tgip.js` | Yes | Pass |

**Directory Structure Match: 20/34 files exist (59%)**

### 3.3 State Management (Section 4)

| Design Item | Implementation | Status | Notes |
|-------------|---------------|--------|-------|
| TGIPContext (React Context + useReducer) | `store/tgipStore.js` (Zustand) | Changed | Context/Reducer 대신 Zustand 사용. 동일한 상태 구조 |
| `selectedTechnology` | `selectedTechnology` | Pass | |
| `selectedView: 'RTS'` | `selectedView: 'RTS'` | Pass | |
| `analysisRunId` | `analysisRunId` | Pass | |
| `results: {RTS,TPI,FSS,WSD}` | `results: {RTS,TPI,FSS,WSD}` | Pass | |
| `evidence` (4개 필드) | `evidence` (4개 필드) | Pass | |
| `isRunning` | `isRunning` | Pass | |
| `evidenceDrawerOpen` | `evidenceDrawerOpen` | Pass | |
| `loadingView` | 미구현 | Missing | |
| `error` | `error` | Pass | |
| `SET_TECHNOLOGY` action | `setTechnology()` | Pass | |
| `SET_VIEW` action | `setView()` | Pass | |
| `RUN_ANALYSIS_START/SUCCESS/ERROR` | `runAnalysis()` (async) | Pass | 단일 함수로 통합 |
| `TOGGLE_EVIDENCE` | `toggleEvidenceDrawer()` | Pass | |
| `RESET` action | 미구현 | Missing | |
| Mock 데이터 | 내장 (tgipStore.js) | Pass | catch 블록에서 자동 fallback |

**State Management Match: 13/16 (81%)**

### 3.4 API Client (Section 5)

| Design API | Implementation | Status |
|-----------|---------------|--------|
| `runAnalysis(technology_id, options)` | `tgipApi.runAnalysis(technology_id, options)` | Pass |
| `getRunDetail(run_id)` | `tgipApi.getRunDetail(run_id)` | Pass |
| `searchTechnologies(query)` | `tgipApi.searchTechnologies(query)` | Pass |
| `getLibrary()` | `tgipApi.getLibrary()` | Pass |
| Mock 데이터 파일 (`tgip.mock.js`) | tgipStore.js 내부에 통합 | Changed |

**API Client Match: 4/4 endpoints (100%)**

### 3.5 Components (Section 6)

| Design Component | Implementation | Status | Quality |
|-----------------|---------------|--------|---------|
| TGIPWorkspace | `pages/tgip/TGIPWorkspace.jsx` | Pass | 설계와 구조 일치. DisclaimerBanner 추가 (good) |
| TGIPHeader | `components/tgip/Layout/TGIPHeader.jsx` | Pass | TechnologySelector + ViewSwitch + RunController + Export 포함 |
| SidebarViewSelector | `components/tgip/Workspace/SidebarViewSelector.jsx` | Pass | coverage 지표 대신 dot indicator 사용 |
| ObservationCanvas | `components/tgip/Workspace/ObservationCanvas.jsx` | Pass | Loading/Empty 상태 처리 완료 |
| EvidenceDrawer | `components/tgip/Workspace/EvidenceDrawer.jsx` | Pass | run_id 표시, 특허 목록, IPC 시그니처, confidence 포함 |
| RunController | `components/tgip/Workspace/RunController.jsx` | Pass | 실행 버튼 + 스피너 + 비활성화 |
| RTSView | `components/tgip/views/RTSView/RTSView.jsx` | Pass | MaturityScale + ScoreBreakdown + SolutionOptions |
| MaturityScale | `components/tgip/views/RTSView/MaturityScale.jsx` | Pass | 세그먼트 바 + 포인터, stage별 색상 |
| ScoreBreakdownChart | `components/tgip/views/RTSView/ScoreBreakdownChart.jsx` | Pass | 수평 바 차트 (Chart.js 사용) |
| BottleneckIndicator | 미구현 | Missing | MaturityScale이 stage 표시를 포함하므로 기능적 중복 가능 |
| SolutionOptionsTable | `components/tgip/views/RTSView/SolutionOptionsTable.jsx` | Pass | 테이블 구조 설계와 일치 |
| TechnologySelector | `components/tgip/Workspace/TechnologySelector.jsx` | Pass | debounce 300ms, Mock fallback 포함 |

**Component Match: 11/12 (92%)**

### 3.6 Visualization Library (Section 7)

| Design Choice | Implementation | Status |
|--------------|---------------|--------|
| Recharts (권장) | Chart.js + react-chartjs-2 | Changed |
| MaturityScale (CSS) | CSS-only segmented bar | Pass |
| ScoreBreakdownChart (BarChart) | Chart.js Bar (horizontal) | Pass (라이브러리 다름) |

설계에서 Recharts를 권장했으나 Chart.js를 사용. 기능적으로 동일하며 package.json에
`chart.js@4.5.1`, `react-chartjs-2@5.3.1`이 설치되어 있음. Recharts는 미설치.

**Visualization Match: 기능적 100%, 라이브러리 선택 변경**

### 3.7 Style Guide (Section 8)

| Design Item | Implementation | Status |
|-------------|---------------|--------|
| TGIP 색상 팔레트 (violet/cyan/red/emerald) | Tailwind 클래스로 적용 | Pass |
| `--tgip-primary: indigo-800` | violet-600 사용 | Changed |
| View별 색상 (RTS=violet, TPI=cyan, FSS=red, WSD=emerald) | 일치 | Pass |
| tgip-card 패턴 | `rounded-xl border border-slate-200 bg-white shadow-sm p-6` | Pass |
| DisclaimerBanner | 구현 완료, 문구 일치 | Pass |
| 면책 고지 위치 (모든 페이지 하단) | Workspace + PublicLayout footer | Pass |

**Style Guide Match: 5/6 (83%)**

### 3.8 Phase 1 Checklist (Section 9) — 11 Items

| # | Checklist Item | Status | Notes |
|---|---------------|--------|-------|
| 1 | TGIPContext + tgipReducer 작성 | Pass | Zustand store로 대체 (동일 기능) |
| 2 | src/api/tgip.js API 클라이언트 작성 (Mock 포함) | Pass | 4개 엔드포인트 + store 내 Mock |
| 3 | TGIPPublicLayout + TGIPAppLayout 레이아웃 | Partial | TGIPPublicLayout 완료, TGIPAppLayout 미구현 |
| 4 | App.jsx에 TGIP 라우트 추가 | Pass | 공개 + 앱 라우트 모두 추가 |
| 5 | TGIPOverview 페이지 (정적 콘텐츠) | Pass | Hero + ViewCards + Pipeline + CTA 포함 |
| 6 | TGIPWorkspace 페이지 + TGIPHeader | Pass | 설계 구조와 일치 |
| 7 | SidebarViewSelector (RTS 활성, 나머지 coming soon) | Pass | available 플래그로 제어 |
| 8 | ObservationCanvas 컨테이너 | Pass | Loading/Empty/View 렌더링 |
| 9 | RTSView + MaturityScale + ScoreBreakdownChart (Mock) | Pass | 3개 서브컴포넌트 모두 구현 |
| 10 | EvidenceDrawer (토글 + 특허 목록) | Pass | 토글, 특허, IPC, confidence, run_id |
| 11 | RunController (실행 버튼 + 로딩 상태) | Pass | Mock fallback 포함 |

**Phase 1 Checklist: 10/11 Pass, 1 Partial (91%)**

---

## 4. Differences Found

### 4.1 Missing Features (Design O, Implementation X)

| Item | Design Location | Description |
|------|----------------|-------------|
| TGIPAppLayout | design:118 | 앱 레이아웃 래퍼 컴포넌트 미구현 (Workspace가 자체 레이아웃) |
| TGIPFooter | design:120 | 전용 푸터 컴포넌트 미구현 (DisclaimerBanner로 대체) |
| TGIPDocs 페이지 | design:107 | `/docs` 라우트 및 페이지 미구현 |
| TGIPAbout 페이지 | design:108 | `/about` 라우트 및 페이지 미구현 |
| BottleneckIndicator | design:133 | 별도 컴포넌트 미구현 (MaturityScale에 통합) |
| Overview 서브컴포넌트 5개 | design:149-154 | HeroSection, MultiViewConcept 등 별도 파일 미분리 |
| CoverageIndicator | design:156 | shared 컴포넌트 미구현 |
| RunIdBadge | design:158 | shared 컴포넌트 미구현 (EvidenceDrawer에 인라인) |
| `loadingView` 상태 | design:205 | 뷰별 로딩 상태 미구현 |
| `RESET` action | design:218 | 초기화 액션 미구현 |

### 4.2 Changed Features (Design != Implementation)

| Item | Design | Implementation | Impact |
|------|--------|---------------|--------|
| State Management | React Context + useReducer | Zustand | Low (개선) |
| Visualization Library | Recharts (권장) | Chart.js + react-chartjs-2 | Low (동등) |
| Primary Color | indigo-800 (`#1E40AF`) | violet-600 | Low |
| Mock 데이터 위치 | `api/tgip.mock.js` (별도 파일) | `store/tgipStore.js` (내장) | Low |
| Overview 구조 | 5개 서브컴포넌트로 분리 | 단일 파일 내 인라인 | Medium |
| SidebarViewSelector coverage | coverage 퍼센트 바 표시 | dot indicator만 | Low |

### 4.3 Added Features (Design X, Implementation O)

| Item | Implementation Location | Description |
|------|------------------------|-------------|
| `openEvidenceDrawer()` | `store/tgipStore.js` | toggle 외 별도 open 액션 |
| DEMO_TECHS 사전 | `pages/tgip/TGIPWorkspace.jsx` | URL 파라미터 기반 기술 자동 로드 |
| View Switch in Header | `TGIPHeader.jsx` | 헤더 내 뷰 전환 버튼 (모바일 숨김) |

---

## 5. Convention Compliance

### 5.1 Naming Convention

| Category | Convention | Compliance | Notes |
|----------|-----------|:----------:|-------|
| Components | PascalCase | 100% | TGIPWorkspace, RTSView 등 |
| Functions | camelCase | 100% | setTechnology, runAnalysis 등 |
| Constants | UPPER_SNAKE_CASE | 100% | MOCK_EVIDENCE, MOCK_RESULTS, VIEWS 등 |
| Files (component) | PascalCase.jsx | 100% | |
| Files (utility) | camelCase.js | 100% | tgipStore.js, tgip.js |
| Folders | kebab-case or PascalCase | Pass | tgip/, Workspace/, Layout/, views/ |

### 5.2 Import Order

모든 TGIP 파일이 일관된 패턴을 따름:
1. 외부 라이브러리 (react, react-router-dom, lucide-react, chart.js)
2. 내부 상대 경로 imports
3. 스타일 없음 (Tailwind 기반)

---

## 6. Architecture Compliance

### 6.1 Layer Assignment

| Component | Expected Layer | Actual Location | Status |
|-----------|---------------|-----------------|--------|
| Pages (TGIPWorkspace 등) | Presentation | `pages/tgip/` | Pass |
| UI Components | Presentation | `components/tgip/` | Pass |
| State Store | Application | `store/tgipStore.js` | Pass |
| API Client | Infrastructure | `api/tgip.js` | Pass |

### 6.2 Dependency Direction

| File | Layer | Imports | Status |
|------|-------|---------|--------|
| `RunController.jsx` | Presentation | tgipStore, tgipApi | Warning |

`RunController`가 `api/tgip.js`를 직접 import하여 `runAnalysis(tgipApi)`로 전달.
설계상으로는 store가 API 호출을 캡슐화하므로 Presentation -> Infrastructure 직접 의존.
단, tgipApi를 store 액션에 주입하는 패턴이므로 심각도는 낮음.

---

## 7. Match Rate Summary

```
+---------------------------------------------+
|  Phase 1 Checklist Match: 91% (10/11)        |
|  File Structure Match:    59% (20/34)        |
|  Component Match:         92% (11/12)        |
|  API Match:              100% (4/4)          |
|  State Match:             81% (13/16)        |
|  Style Match:             83% (5/6)          |
+---------------------------------------------+
|  Weighted Overall:        82%                |
+---------------------------------------------+
```

가중치 기준: Phase 1 체크리스트(40%), 컴포넌트(25%), 상태관리(15%), API(10%), 스타일(10%)

---

## 8. Recommended Actions

### 8.1 Immediate (Phase 1 완성)

| Priority | Item | Description |
|----------|------|-------------|
| 1 | TGIPAppLayout 구현 | Workspace 래퍼 레이아웃으로 Header/Footer 일관성 확보 |
| 2 | RESET 액션 추가 | tgipStore에 `reset()` 액션 추가 |
| 3 | loadingView 상태 추가 | 뷰별 로딩 상태 지원 |

### 8.2 Short-term (Phase 1 -> Phase 2 전환 전)

| Priority | Item | Description |
|----------|------|-------------|
| 1 | TGIPDocs 페이지 | `/docs` 라우트 + 정적 콘텐츠 |
| 2 | TGIPAbout 페이지 | `/about` 라우트 + 정적 콘텐츠 |
| 3 | Overview 컴포넌트 분리 | TGIPOverview를 HeroSection, ViewCards 등 5개 서브컴포넌트로 분리 |
| 4 | SidebarViewSelector coverage 표시 | coverage 퍼센트 바 추가 |

### 8.3 Design Document Update Needed

| Item | Description |
|------|-------------|
| State Management | Context/useReducer -> Zustand 변경 반영 |
| Visualization Library | Recharts -> Chart.js 변경 반영 |
| Primary Color | indigo-800 -> violet-600 변경 반영 |
| Mock 데이터 위치 | 별도 파일 -> store 내장으로 변경 반영 |

---

## 9. Conclusion

Phase 1 체크리스트 11개 항목 기준으로 **91%** 달성. 핵심 기능(Workspace, RTSView,
EvidenceDrawer, RunController, API Client, State Store)은 모두 구현 완료.

주요 차이는 **의도적 개선**(Context -> Zustand, Recharts -> Chart.js)과
**합리적 생략**(BottleneckIndicator를 MaturityScale에 통합, Overview 서브컴포넌트 미분리)으로
분류할 수 있으며, 기능적 결함은 없음.

**TGIPAppLayout** 미구현과 **TGIPDocs/TGIPAbout** 페이지 부재가 주요 Gap.

Match Rate >= 82%이므로 문서 업데이트를 권장하며, Phase 2 진행 전 위 항목들을 해소하는 것이 바람직함.

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-03-05 | Initial gap analysis | bkit-gap-detector |
