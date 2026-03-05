# [Plan] frontend-phase2 — TGIP 멀티뷰 완성 + 백엔드 API 연동

> **작성일**: 2026-03-05
> **상태**: Plan
> **버전**: v1.0
> **연속성**: `frontend` (Phase 1) → **`frontend-phase2`** (Phase 2) → `frontend-phase3` (예정)
> **참고**: `docs/01-plan/features/frontend.plan.md` § 11 (MVP Phase 2)

---

## 1. Feature 개요

| 항목 | 내용 |
|------|------|
| Feature Name | frontend-phase2 |
| 제품명 | TGIP — Technology Geo-Intelligence Platform |
| 유형 | React SPA (Vite + React Router) + FastAPI 백엔드 |
| 목적 | Phase 1(RTS 뷰 + Overview + 뼈대)에서 TPI/FSS/WSD 3개 뷰를 실제 시각화로 완성하고, FastAPI TGIP 엔드포인트를 구현하여 Mock 의존성을 제거 |
| Phase 1 상태 | ✅ 완료 (Match Rate 93%) |

### 한 줄 요약

> Phase 1에서 Placeholder("coming in Phase 2")로 남겨둔 TPI/FSS/WSD 뷰를 실제 시각화로 구현하고, FastAPI에 TGIP API를 추가하여 전체 멀티뷰 워크스페이스를 동작 가능하게 만든다.

---

## 2. 현재 상태 (Phase 1 완료 기준)

### 완료된 것

| 컴포넌트/파일 | 상태 |
|--------------|------|
| `RTSView.jsx` + 4개 서브컴포넌트 | ✅ 완전 구현 |
| `TGIPOverview.jsx`, `TGIPFeatures.jsx`, `TGIPDemo.jsx`, `TGIPDocs.jsx`, `TGIPAbout.jsx` | ✅ 완전 구현 |
| `TGIPWorkspace.jsx`, `ObservationCanvas.jsx`, `SidebarViewSelector.jsx` | ✅ 완전 구현 |
| `EvidenceDrawer.jsx`, `RunController.jsx`, `TGIPHeader.jsx` | ✅ 완전 구현 |
| `tgipStore.js` (Zustand), `api/tgip.js` (Axios) | ✅ 완전 구현 |
| `framer-motion`, `@xyflow/react` | ✅ 이미 설치됨 |

### Phase 2 진입 시 Placeholder 상태

| 파일 | 현재 상태 |
|------|----------|
| `TPIView.jsx` | Placeholder — "coming in Phase 2" |
| `FSSView.jsx` | Placeholder — "coming in Phase 2" |
| `WSDView.jsx` | Placeholder — "coming in Phase 2" |
| `SidebarViewSelector.jsx` | TPI/FSS/WSD `available: false` (disabled) |
| `back_end/app/api/v1/endpoints/tgip.py` | 미존재 |
| `pages/tgip/RunDetail.jsx` | 미존재 |

---

## 3. 범위 정의 (Scope)

### In Scope — Phase 2

#### 3.1 TPIView 구현 (전파 뷰)

| 컴포넌트 | 라이브러리 | 설명 |
|---------|-----------|------|
| `PropagationGraph.jsx` | `@xyflow/react` (설치됨) | 의미 전파 노드-엣지 그래프 |
| `IndustryFlowDiagram.jsx` | Chart.js Bar (horizontal) | 산업별 흐름 — Sankey 근사 |
| `BurstTimeline.jsx` | Chart.js Line | 연도별 버스트 포인트 |
| `TPIView.jsx` | 위 3개 조합 | TPI 뷰 컨테이너 |

#### 3.2 FSSView 구현 (전략 압력 뷰)

| 컴포넌트 | 라이브러리 | 설명 |
|---------|-----------|------|
| `GlobalCoverageMap.jsx` | `react-simple-maps` (신규 설치) | 국가별 특허 커버리지 맵 |
| `FamilyExpansionMeter.jsx` | Tailwind CSS (진행바) | 패밀리 확장 지표 |
| `AssigneePressureTable.jsx` | HTML/Tailwind | 출원인 리더보드 테이블 |
| `FSSView.jsx` | 위 3개 조합 | FSS 뷰 컨테이너 |

#### 3.3 WSDView 구현 (기회 필드 뷰)

| 컴포넌트 | 라이브러리 | 설명 |
|---------|-----------|------|
| `ProblemSolutionHeatmap.jsx` | CSS 그리드 (Chart.js Matrix 검토) | 문제×솔루션 밀도 히트맵 |
| `GapCandidatesList.jsx` | HTML/Tailwind | 갭 후보 목록 (갭 스코어 + 신뢰도) |
| `CrossIndustryAnalogPanel.jsx` | HTML/Tailwind | 교차산업 유추 패널 |
| `WSDView.jsx` | 위 3개 조합 | WSD 뷰 컨테이너 |

#### 3.4 RunDetail 페이지

| 항목 | 내용 |
|------|------|
| 경로 | `/app/runs/:run_id` |
| 파일 | `pages/tgip/RunDetail.jsx` |
| App.jsx | 라우트 추가 |
| 섹션 | Summary / Metrics 카드(RTS/TPI/FSS/WSD) / Evidence 번들 / Logs / Download |

#### 3.5 FastAPI TGIP 백엔드

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/api/v1/tgip/analysis` | POST | 분석 실행 (기술 ID 받아 run_id + 결과 반환) |
| `/api/v1/tgip/runs/{run_id}` | GET | 실행 상세 조회 |
| `/api/v1/tgip/technologies` | GET | 기술 검색 (`?q=keyword`) |
| `/api/v1/tgip/library` | GET | 저장된 실행 목록 |

> **전략**: Phase 2에서는 Mock 데이터를 반환하는 FastAPI 엔드포인트를 구현하여 프론트엔드 연동을 검증. 실제 DB 연산은 Phase 3에서 진행.

#### 3.6 SidebarViewSelector 업데이트

- TPI / FSS / WSD: `available: false` → `available: true`
- coverage % 지표: 실제 `results[viewId]` 데이터 기반으로 연동

#### 3.7 Mock 데이터 확장 (tgipStore.js)

- `MOCK_RESULTS.TPI`, `MOCK_RESULTS.FSS`, `MOCK_RESULTS.WSD` 추가
- 각 뷰 시각화에 필요한 데이터 구조 정의

### Out of Scope — Phase 3으로 이관

- TGIPLanding 페이지 (`/` 루트 리브랜딩)
- PDF 내보내기
- Library 페이지 (`/app/library`)
- Compare Mode 토글
- 성능 최적화 (번들 크기 / lazy loading)
- 실제 DB 연동 (Neo4j, OpenSearch, MariaDB TGIP 데이터)

---

## 4. 구현 우선순위

```
1순위: tgipStore Mock 데이터 확장 (TPI/FSS/WSD 구조 정의)
  → 모든 뷰 컴포넌트가 이 데이터 구조에 의존

2순위: FastAPI TGIP 엔드포인트 (Mock 응답)
  → 프론트엔드 실제 API 연동 경로 확보

3순위: WSDView (히트맵 + 갭 리스트)
  → 시각적 임팩트 최고, 사용자 관심도 높음

4순위: TPIView (전파 그래프 + 타임라인)
  → @xyflow/react 이미 설치됨, 구현 난도 중

5순위: FSSView (커버리지 맵 + 리더보드)
  → react-simple-maps 신규 설치 필요

6순위: RunDetail 페이지
  → 추적성 확보, 나머지 완료 후 연결

7순위: SidebarViewSelector 활성화
  → 마지막 단계: available: true로 전환
```

---

## 5. 데이터 구조 정의

### TPI Mock 데이터 구조

```json
{
  "propagationGraph": {
    "nodes": [{ "id": "tech-core", "label": "Solid State Battery", "size": 40 }],
    "edges": [{ "source": "tech-core", "target": "ev-industry", "weight": 0.82 }]
  },
  "industryFlow": [
    { "industry": "Automotive EV", "score": 0.85, "patents": 412 },
    { "industry": "Consumer Electronics", "score": 0.71, "patents": 287 }
  ],
  "burstTimeline": [
    { "year": 2018, "count": 234, "burstScore": 0.3 },
    { "year": 2022, "count": 891, "burstScore": 0.9 }
  ],
  "semanticPropagationScore": 0.78
}
```

### FSS Mock 데이터 구조

```json
{
  "familyMetrics": {
    "FES": 0.82,
    "GCR": 0.74,
    "MIV": 0.68,
    "averageFamilySize": 4.3
  },
  "countryCoverage": [
    { "iso": "KR", "count": 1243, "intensity": 1.0 },
    { "iso": "US", "count": 876, "intensity": 0.71 }
  ],
  "assigneeLeaderboard": [
    { "name": "Samsung SDI", "familyCount": 234, "gcr": 0.91 },
    { "name": "LG Energy Solution", "familyCount": 198, "gcr": 0.87 }
  ]
}
```

### WSD Mock 데이터 구조

```json
{
  "problemClusters": [
    { "id": "dendrite", "label": "덴드라이트 성장", "density": 0.87, "patents": 312 }
  ],
  "solutionClusters": [
    { "id": "coating", "label": "코팅층 최적화", "density": 0.72, "patents": 198 }
  ],
  "heatmapMatrix": [[0.9, 0.3], [0.2, 0.8]],
  "gapCandidates": [
    { "id": "gap-1", "problem": "고온 안정성", "solution": "교차산업 세라믹", "gapScore": 0.83, "confidence": 0.71 }
  ],
  "crossIndustryAnalogs": [
    { "sourceIndustry": "Aerospace", "targetProblem": "고온 전해질", "analogy": "세라믹 절연체 기술", "similarity": 0.76 }
  ]
}
```

---

## 6. 기술 스택 (Phase 2 추가)

| 항목 | 기술 | 메모 |
|------|------|------|
| 그래프 시각화 | `@xyflow/react` | ✅ 이미 설치됨 |
| 세계 지도 | `react-simple-maps` | ⚠️ 신규 설치 필요 (`npm install react-simple-maps`) |
| 차트 | Chart.js (이미 설치됨) | Line, Bar, Matrix |
| 애니메이션 | `framer-motion` | ✅ 이미 설치됨 (뷰 전환) |
| 백엔드 | FastAPI, Pydantic | 기존 구조 따름 |

---

## 7. FastAPI 엔드포인트 설계

### POST `/api/v1/tgip/analysis`

**Request**:
```json
{ "technology_id": "solid-state-battery", "views": ["RTS", "TPI", "FSS", "WSD"] }
```

**Response**:
```json
{
  "run_id": "tgip-run-2026-03-05-abc123",
  "technology_id": "solid-state-battery",
  "results": { "RTS": {...}, "TPI": {...}, "FSS": {...}, "WSD": {...} },
  "evidence": { "representativePatents": [...], "ipcSignatures": [...] },
  "created_at": "2026-03-05T10:00:00Z"
}
```

### GET `/api/v1/tgip/runs/{run_id}`

**Response**: 위와 동일 구조 + `metadata.executionTime`

### GET `/api/v1/tgip/technologies?q=battery`

**Response**:
```json
{
  "results": [
    { "id": "solid-state-battery", "name": "Solid State Battery", "patentCount": 4821 }
  ]
}
```

---

## 8. 구현 순서 (체크리스트)

### Step 1 — 데이터 기반 준비
- [ ] `tgipStore.js`: `MOCK_RESULTS.TPI/FSS/WSD` Mock 데이터 추가
- [ ] FastAPI `back_end/app/api/v1/endpoints/tgip.py` 생성 (Mock 응답)
- [ ] `back_end/app/main.py`에 TGIP 라우터 등록

### Step 2 — WSDView
- [ ] `ProblemSolutionHeatmap.jsx` 구현 (CSS 그리드 기반)
- [ ] `GapCandidatesList.jsx` 구현
- [ ] `CrossIndustryAnalogPanel.jsx` 구현
- [ ] `WSDView.jsx` 조합

### Step 3 — TPIView
- [ ] `PropagationGraph.jsx` (@xyflow/react)
- [ ] `IndustryFlowDiagram.jsx` (Chart.js Bar)
- [ ] `BurstTimeline.jsx` (Chart.js Line)
- [ ] `TPIView.jsx` 조합

### Step 4 — FSSView
- [ ] `npm install react-simple-maps`
- [ ] `GlobalCoverageMap.jsx` 구현
- [ ] `FamilyExpansionMeter.jsx` 구현
- [ ] `AssigneePressureTable.jsx` 구현
- [ ] `FSSView.jsx` 조합

### Step 5 — RunDetail 페이지
- [ ] `pages/tgip/RunDetail.jsx` 구현
- [ ] `App.jsx`에 `/app/runs/:run_id` 라우트 추가

### Step 6 — 연동 완성
- [ ] `SidebarViewSelector.jsx`: TPI/FSS/WSD `available: true`로 변경
- [ ] Mock 의존성 → 실제 FastAPI API 연동 검증
- [ ] `framer-motion` 뷰 전환 애니메이션 (`ObservationCanvas`)

---

## 9. 성공 지표

| 지표 | 목표 |
|------|------|
| 3개 뷰 렌더링 | TPI/FSS/WSD 각각 데이터 있을 때 실제 차트 표시 |
| SidebarViewSelector | TPI/FSS/WSD 클릭 가능 (available: true) |
| FastAPI 엔드포인트 | `POST /api/v1/tgip/analysis` 200 응답 |
| RunDetail 페이지 | `/app/runs/:run_id` 정상 렌더링 |
| Evidence 일관성 | 3개 신규 뷰에서도 EvidenceDrawer 데이터 표시 |
| Mock → API | `tgipApi.runAnalysis()` 실제 FastAPI 응답 사용 |

---

## 10. Must-Have / Nice-to-Have

### Must-Have (Phase 2 완료 기준)

- [ ] TPIView: PropagationGraph + BurstTimeline
- [ ] FSSView: GlobalCoverageMap + AssigneePressureTable
- [ ] WSDView: ProblemSolutionHeatmap + GapCandidatesList
- [ ] RunDetail 페이지 기본 구조
- [ ] FastAPI TGIP 엔드포인트 4개 (Mock 응답)
- [ ] SidebarViewSelector 3개 뷰 활성화

### Nice-to-Have (시간 여유 시)

- [ ] `framer-motion` 뷰 전환 애니메이션
- [ ] `CrossIndustryAnalogPanel.jsx` (WSD 보조)
- [ ] `IndustryFlowDiagram.jsx` (TPI 보조)
- [ ] `FamilyExpansionMeter.jsx` (FSS 보조)

---

## 11. 관련 문서

| 문서 | 경로 |
|------|------|
| Phase 1 Plan | `docs/01-plan/features/frontend.plan.md` |
| 잔여 작업 메모 | `memory/tgip-todo.md` |
| 기존 RTSView 참고 | `front_end/src/components/tgip/views/RTSView/` |
| Zustand Store | `front_end/src/store/tgipStore.js` |
| API 클라이언트 | `front_end/src/api/tgip.js` |
