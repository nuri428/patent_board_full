# [Design] frontend-phase2 — TGIP 멀티뷰 완성 + 백엔드 API 연동

> **작성일**: 2026-03-05
> **상태**: Design
> **버전**: v1.0
> **참고 Plan**: `docs/01-plan/features/frontend-phase2.plan.md`

---

## 1. 아키텍처 개요

### 변경 영향 범위

```
back_end/
└── app/
    ├── api/v1/
    │   ├── api.py               ← TGIP 라우터 추가
    │   └── endpoints/
    │       └── tgip.py          ← 신규 생성
    └── schemas/
        └── tgip.py              ← 신규 생성 (Pydantic 스키마)

front_end/src/
├── store/
│   └── tgipStore.js            ← MOCK_RESULTS.TPI/FSS/WSD 추가
├── components/tgip/views/
│   ├── TPIView/
│   │   ├── PropagationGraph.jsx  ← 신규
│   │   ├── BurstTimeline.jsx     ← 신규
│   │   ├── IndustryFlowDiagram.jsx ← 신규
│   │   └── TPIView.jsx           ← 교체 (Placeholder → 실제 구현)
│   ├── FSSView/
│   │   ├── GlobalCoverageMap.jsx ← 신규
│   │   ├── FamilyExpansionMeter.jsx ← 신규
│   │   ├── AssigneePressureTable.jsx ← 신규
│   │   └── FSSView.jsx           ← 교체
│   └── WSDView/
│       ├── ProblemSolutionHeatmap.jsx ← 신규
│       ├── GapCandidatesList.jsx ← 신규
│       ├── CrossIndustryAnalogPanel.jsx ← 신규
│       └── WSDView.jsx           ← 교체
├── Workspace/
│   └── SidebarViewSelector.jsx  ← available: true 수정
└── pages/tgip/
    └── RunDetail.jsx             ← 신규

App.jsx                           ← /app/runs/:run_id 라우트 추가
```

---

## 2. 백엔드 설계

### 2.1 신규 파일: `back_end/app/schemas/tgip.py`

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# --- Request ---
class TGIPAnalysisRequest(BaseModel):
    technology_id: str
    views: list[str] = ["RTS", "TPI", "FSS", "WSD"]

# --- Response 서브타입 ---
class RTSResult(BaseModel):
    score: float
    stage: str
    components: dict[str, float]
    solutionOptions: list[dict] = []

class PropagationNode(BaseModel):
    id: str
    label: str
    size: int = 20

class PropagationEdge(BaseModel):
    source: str
    target: str
    weight: float

class TPIResult(BaseModel):
    semanticPropagationScore: float
    propagationGraph: dict  # nodes + edges
    industryFlow: list[dict]
    burstTimeline: list[dict]

class FSSResult(BaseModel):
    familyMetrics: dict[str, float]
    countryCoverage: list[dict]
    assigneeLeaderboard: list[dict]

class WSDResult(BaseModel):
    problemClusters: list[dict]
    solutionClusters: list[dict]
    heatmapMatrix: list[list[float]]
    gapCandidates: list[dict]
    crossIndustryAnalogs: list[dict]

class EvidenceBundle(BaseModel):
    representativePatents: list[dict]
    ipcSignatures: list[str]
    abstractSnippets: list[str] = []
    confidenceScores: dict[str, float]

class TGIPAnalysisResponse(BaseModel):
    run_id: str
    technology_id: str
    results: dict  # {"RTS": RTSResult, "TPI": TPIResult, ...}
    evidence: EvidenceBundle
    created_at: datetime

class TGIPRunResponse(TGIPAnalysisResponse):
    metadata: dict = {}

class TechnologySearchResult(BaseModel):
    id: str
    name: str
    patentCount: int
    description: str = ""

class TGIPLibraryItem(BaseModel):
    run_id: str
    technology_id: str
    technology_name: str
    created_at: datetime
    views_computed: list[str]
```

### 2.2 신규 파일: `back_end/app/api/v1/endpoints/tgip.py`

```python
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Query

from app.schemas.tgip import (
    TGIPAnalysisRequest,
    TGIPAnalysisResponse,
    TGIPRunResponse,
)

router = APIRouter()

# --- Mock 데이터 (Phase 2 전략: Mock 응답으로 API 구조 확립) ---
def _build_mock_response(technology_id: str, run_id: str) -> dict:
    return {
        "run_id": run_id,
        "technology_id": technology_id,
        "results": {
            "RTS": {
                "score": 0.72,
                "stage": "Bottleneck",
                "components": {
                    "patent_volume": 0.85,
                    "growth": 0.60,
                    "classification_conf": 0.78,
                    "citation_percentile": 0.65,
                },
                "solutionOptions": [
                    {"approach": "황화물계 전해질", "patents": 1243, "coverage": 0.82, "evidence": "H01M 10/0562"},
                    {"approach": "산화물계 전해질", "patents": 876, "coverage": 0.71, "evidence": "H01M 10/052"},
                ],
            },
            "TPI": {
                "semanticPropagationScore": 0.78,
                "propagationGraph": {
                    "nodes": [
                        {"id": "core", "label": technology_id.replace("-", " ").title(), "size": 40},
                        {"id": "ev", "label": "Electric Vehicle", "size": 30},
                        {"id": "consumer", "label": "Consumer Electronics", "size": 22},
                        {"id": "grid", "label": "Grid Storage", "size": 18},
                    ],
                    "edges": [
                        {"source": "core", "target": "ev", "weight": 0.85},
                        {"source": "core", "target": "consumer", "weight": 0.71},
                        {"source": "core", "target": "grid", "weight": 0.58},
                    ],
                },
                "industryFlow": [
                    {"industry": "Automotive EV", "score": 0.85, "patents": 412},
                    {"industry": "Consumer Electronics", "score": 0.71, "patents": 287},
                    {"industry": "Grid Storage", "score": 0.58, "patents": 163},
                    {"industry": "Aerospace", "score": 0.34, "patents": 89},
                ],
                "burstTimeline": [
                    {"year": 2017, "count": 187, "burstScore": 0.2},
                    {"year": 2018, "count": 234, "burstScore": 0.3},
                    {"year": 2019, "count": 312, "burstScore": 0.4},
                    {"year": 2020, "count": 445, "burstScore": 0.55},
                    {"year": 2021, "count": 623, "burstScore": 0.72},
                    {"year": 2022, "count": 891, "burstScore": 0.90},
                    {"year": 2023, "count": 1043, "burstScore": 0.95},
                ],
            },
            "FSS": {
                "familyMetrics": {"FES": 0.82, "GCR": 0.74, "MIV": 0.68, "averageFamilySize": 4.3},
                "countryCoverage": [
                    {"iso": "KR", "count": 1243, "intensity": 1.0},
                    {"iso": "US", "count": 876, "intensity": 0.71},
                    {"iso": "CN", "count": 734, "intensity": 0.59},
                    {"iso": "JP", "count": 512, "intensity": 0.41},
                    {"iso": "DE", "count": 289, "intensity": 0.23},
                ],
                "assigneeLeaderboard": [
                    {"name": "Samsung SDI", "familyCount": 234, "gcr": 0.91},
                    {"name": "LG Energy Solution", "familyCount": 198, "gcr": 0.87},
                    {"name": "CATL", "familyCount": 176, "gcr": 0.82},
                    {"name": "Panasonic", "familyCount": 145, "gcr": 0.79},
                    {"name": "SK Innovation", "familyCount": 112, "gcr": 0.73},
                ],
            },
            "WSD": {
                "problemClusters": [
                    {"id": "dendrite", "label": "Dendrite Growth", "density": 0.87, "patents": 312},
                    {"id": "interface", "label": "Interface Resistance", "density": 0.74, "patents": 267},
                    {"id": "thermal", "label": "Thermal Stability", "density": 0.61, "patents": 198},
                    {"id": "scalability", "label": "Manufacturing Scale", "density": 0.45, "patents": 134},
                ],
                "solutionClusters": [
                    {"id": "coating", "label": "Interface Coating", "density": 0.72, "patents": 198},
                    {"id": "composite", "label": "Composite Electrolyte", "density": 0.65, "patents": 176},
                    {"id": "pressure", "label": "Stack Pressure Control", "density": 0.48, "patents": 112},
                ],
                "heatmapMatrix": [
                    [0.9, 0.3, 0.1],
                    [0.7, 0.8, 0.2],
                    [0.2, 0.4, 0.6],
                    [0.1, 0.1, 0.9],
                ],
                "gapCandidates": [
                    {"id": "gap-1", "problem": "Thermal Stability at High Temperature", "solution": "Cross-industry Ceramic Tech", "gapScore": 0.83, "confidence": 0.71},
                    {"id": "gap-2", "problem": "Manufacturing Scale", "solution": "Roll-to-Roll Process", "gapScore": 0.76, "confidence": 0.65},
                    {"id": "gap-3", "problem": "Dendrite Growth", "solution": "Liquid Metal Interface", "gapScore": 0.68, "confidence": 0.59},
                ],
                "crossIndustryAnalogs": [
                    {"sourceIndustry": "Aerospace", "targetProblem": "Thermal Electrolyte", "analogy": "Ceramic Insulator Tech", "similarity": 0.76},
                    {"sourceIndustry": "Fuel Cell", "targetProblem": "Interface Resistance", "analogy": "MEA Fabrication", "similarity": 0.68},
                ],
            },
        },
        "evidence": {
            "representativePatents": [
                {
                    "id": "KR1020230045231",
                    "title": "고체 전해질 기반 리튬 이온 배터리 및 제조 방법",
                    "abstractSnippet": "전해질 층의 두께를 최소화하여 이온 전도도를 개선하고, 계면 저항을 감소시키는 고체 전해질 구조",
                    "ipc": ["H01M 10/0562", "H01M 10/052"],
                    "confidence": 0.91,
                },
                {
                    "id": "KR1020220098712",
                    "title": "황화물계 고체 전해질 합성 방법",
                    "abstractSnippet": "황화물계 고체 전해질의 고이온 전도성을 달성하기 위한 합성 방법",
                    "ipc": ["H01M 10/0562", "C01B 17/20"],
                    "confidence": 0.87,
                },
            ],
            "ipcSignatures": ["H01M 10/05", "H01M 4/13", "C01B 17/00"],
            "abstractSnippets": [],
            "confidenceScores": {"overall": 0.89, "coverage": 0.73},
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


# In-memory store (Phase 2 임시 — Phase 3에서 DB로 교체)
_run_store: dict[str, dict] = {}


@router.post("/analysis")
async def run_analysis(request: TGIPAnalysisRequest):
    run_id = f"tgip-run-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
    data = _build_mock_response(request.technology_id, run_id)
    _run_store[run_id] = data
    return data


@router.get("/runs/{run_id}")
async def get_run_detail(run_id: str):
    if run_id in _run_store:
        return {**_run_store[run_id], "metadata": {"executionTime": "2.4s", "patentsAnalyzed": 4821}}
    # run_id를 모를 경우 Mock fallback
    data = _build_mock_response("unknown-technology", run_id)
    return {**data, "metadata": {"executionTime": "2.4s", "patentsAnalyzed": 4821}}


@router.get("/technologies")
async def search_technologies(q: str = Query(default="", min_length=0)):
    all_techs = [
        {"id": "solid-state-battery", "name": "Solid State Battery", "patentCount": 4821, "description": "전고체 배터리 기술"},
        {"id": "perovskite-solar", "name": "Perovskite Solar Cell", "patentCount": 3412, "description": "페로브스카이트 태양전지"},
        {"id": "carbon-nanotube", "name": "Carbon Nanotube", "patentCount": 6789, "description": "탄소나노튜브 소재"},
        {"id": "quantum-computing", "name": "Quantum Computing", "patentCount": 2891, "description": "양자 컴퓨팅"},
        {"id": "gene-editing-crispr", "name": "CRISPR Gene Editing", "patentCount": 5124, "description": "CRISPR 유전자 편집"},
    ]
    if q:
        q_lower = q.lower()
        results = [t for t in all_techs if q_lower in t["name"].lower() or q_lower in t["description"].lower()]
    else:
        results = all_techs
    return {"results": results, "total": len(results)}


@router.get("/library")
async def get_library():
    runs = [
        {
            "run_id": run_id,
            "technology_id": data["technology_id"],
            "technology_name": data["technology_id"].replace("-", " ").title(),
            "created_at": data["created_at"],
            "views_computed": ["RTS", "TPI", "FSS", "WSD"],
        }
        for run_id, data in _run_store.items()
    ]
    return {"runs": runs, "total": len(runs)}
```

### 2.3 수정 파일: `back_end/app/api/v1/api.py`

```python
# 추가 라인 (기존 imports에 추가)
from app.api.v1.endpoints import tgip  # ← 추가

# 추가 라인 (기존 include_router 목록에 추가)
api_router.include_router(tgip.router, prefix="/tgip", tags=["tgip"])
```

---

## 3. 프론트엔드 — Store 설계

### 3.1 `tgipStore.js` — Mock 데이터 확장

```javascript
// MOCK_RESULTS 확장 (기존 RTS 아래에 TPI/FSS/WSD 추가)
const MOCK_RESULTS = {
  RTS: { /* 기존 유지 */ },
  TPI: {
    semanticPropagationScore: 0.78,
    propagationGraph: {
      nodes: [
        { id: 'core', label: 'Solid State Battery', size: 40 },
        { id: 'ev', label: 'Electric Vehicle', size: 30 },
        { id: 'consumer', label: 'Consumer Electronics', size: 22 },
        { id: 'grid', label: 'Grid Storage', size: 18 },
      ],
      edges: [
        { id: 'e1', source: 'core', target: 'ev', weight: 0.85 },
        { id: 'e2', source: 'core', target: 'consumer', weight: 0.71 },
        { id: 'e3', source: 'core', target: 'grid', weight: 0.58 },
      ],
    },
    industryFlow: [
      { industry: 'Automotive EV', score: 0.85, patents: 412 },
      { industry: 'Consumer Electronics', score: 0.71, patents: 287 },
      { industry: 'Grid Storage', score: 0.58, patents: 163 },
      { industry: 'Aerospace', score: 0.34, patents: 89 },
    ],
    burstTimeline: [
      { year: 2017, count: 187, burstScore: 0.2 },
      { year: 2018, count: 234, burstScore: 0.3 },
      { year: 2019, count: 312, burstScore: 0.4 },
      { year: 2020, count: 445, burstScore: 0.55 },
      { year: 2021, count: 623, burstScore: 0.72 },
      { year: 2022, count: 891, burstScore: 0.90 },
      { year: 2023, count: 1043, burstScore: 0.95 },
    ],
  },
  FSS: {
    familyMetrics: { FES: 0.82, GCR: 0.74, MIV: 0.68, averageFamilySize: 4.3 },
    countryCoverage: [
      { iso: 'KR', count: 1243, intensity: 1.0 },
      { iso: 'US', count: 876, intensity: 0.71 },
      { iso: 'CN', count: 734, intensity: 0.59 },
      { iso: 'JP', count: 512, intensity: 0.41 },
      { iso: 'DE', count: 289, intensity: 0.23 },
    ],
    assigneeLeaderboard: [
      { name: 'Samsung SDI', familyCount: 234, gcr: 0.91 },
      { name: 'LG Energy Solution', familyCount: 198, gcr: 0.87 },
      { name: 'CATL', familyCount: 176, gcr: 0.82 },
      { name: 'Panasonic', familyCount: 145, gcr: 0.79 },
      { name: 'SK Innovation', familyCount: 112, gcr: 0.73 },
    ],
  },
  WSD: {
    problemClusters: [
      { id: 'dendrite', label: 'Dendrite Growth', density: 0.87, patents: 312 },
      { id: 'interface', label: 'Interface Resistance', density: 0.74, patents: 267 },
      { id: 'thermal', label: 'Thermal Stability', density: 0.61, patents: 198 },
      { id: 'scalability', label: 'Manufacturing Scale', density: 0.45, patents: 134 },
    ],
    solutionClusters: [
      { id: 'coating', label: 'Interface Coating', density: 0.72, patents: 198 },
      { id: 'composite', label: 'Composite Electrolyte', density: 0.65, patents: 176 },
      { id: 'pressure', label: 'Stack Pressure Control', density: 0.48, patents: 112 },
    ],
    heatmapMatrix: [
      [0.9, 0.3, 0.1],
      [0.7, 0.8, 0.2],
      [0.2, 0.4, 0.6],
      [0.1, 0.1, 0.9],
    ],
    gapCandidates: [
      { id: 'gap-1', problem: 'Thermal Stability at High Temperature', solution: 'Cross-industry Ceramic Tech', gapScore: 0.83, confidence: 0.71 },
      { id: 'gap-2', problem: 'Manufacturing Scale', solution: 'Roll-to-Roll Process', gapScore: 0.76, confidence: 0.65 },
      { id: 'gap-3', problem: 'Dendrite Growth', solution: 'Liquid Metal Interface', gapScore: 0.68, confidence: 0.59 },
    ],
    crossIndustryAnalogs: [
      { sourceIndustry: 'Aerospace', targetProblem: 'Thermal Electrolyte', analogy: 'Ceramic Insulator Tech', similarity: 0.76 },
      { sourceIndustry: 'Fuel Cell', targetProblem: 'Interface Resistance', analogy: 'MEA Fabrication', similarity: 0.68 },
    ],
  },
};
```

---

## 4. TPIView 설계

### 4.1 파일 구조

```
front_end/src/components/tgip/views/TPIView/
├── PropagationGraph.jsx    (@xyflow/react 노드-엣지 그래프)
├── BurstTimeline.jsx       (Chart.js Line)
├── IndustryFlowDiagram.jsx (Chart.js 가로 Bar)
└── TPIView.jsx             (컨테이너)
```

### 4.2 PropagationGraph.jsx

**라이브러리**: `@xyflow/react` (이미 설치됨)

```jsx
import ReactFlow, { Background, Controls } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

// nodes: data.propagationGraph.nodes → { id, position, data: { label } }
// edges: data.propagationGraph.edges → { id, source, target, label: weight }
// 노드 크기: node.size 기반 스타일 (style.width = size*2, style.height = size*2)
// 레이아웃: 수동 position (core: center, 나머지 방사형 배치)
```

**포지셔닝 로직**:
- `core` 노드: `{ x: 250, y: 200 }`
- 나머지 노드: 균등 각도로 방사형 배치 (`r=180`)
- 엣지 두께: `strokeWidth: weight * 4`

### 4.3 BurstTimeline.jsx

**라이브러리**: Chart.js Line

```jsx
// data.burstTimeline → 연도별 특허 건수 + 버스트 스코어
// Dataset 1 (왼쪽 Y축): count (bar-style line, fill: true, color: #38bdf8)
// Dataset 2 (오른쪽 Y축): burstScore * 100 (line, color: #f97316, dashed)
// X축: year
// 버스트 임계선: annotation 플러그인 없이 데이터로 처리
```

### 4.4 IndustryFlowDiagram.jsx

**라이브러리**: Chart.js 가로 Bar

```jsx
// data.industryFlow → industry별 score + patents
// indexAxis: 'y'
// 2개 데이터셋: score(0~1 → %) / patents(우측 별도 표시)
// 색상: score 막대 = #38bdf8, patents = 우측 표시만
```

### 4.5 TPIView.jsx 구조

```jsx
const TPIView = ({ data }) => {
  if (!data) return <EmptyState viewName="TPI" description="..." />;
  return (
    <div className="space-y-8">
      {/* 헤더 */}
      <h2>TPI — Propagation View</h2>
      <p className="text-sm text-slate-500">Semantic Propagation Score: {(data.semanticPropagationScore * 100).toFixed(0)}%</p>

      {/* 전파 그래프 */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm" style={{ height: 360 }}>
        <PropagationGraph nodes={data.propagationGraph.nodes} edges={data.propagationGraph.edges} />
      </div>

      {/* 버스트 타임라인 */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <BurstTimeline timeline={data.burstTimeline} />
      </div>

      {/* 산업 플로우 */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <IndustryFlowDiagram flow={data.industryFlow} />
      </div>
    </div>
  );
};
```

---

## 5. FSSView 설계

### 5.1 파일 구조

```
front_end/src/components/tgip/views/FSSView/
├── GlobalCoverageMap.jsx      (react-simple-maps)
├── FamilyExpansionMeter.jsx   (Tailwind CSS 진행바)
├── AssigneePressureTable.jsx  (HTML/Tailwind 테이블)
└── FSSView.jsx                (컨테이너)
```

### 5.2 GlobalCoverageMap.jsx

**라이브러리**: `react-simple-maps` (`npm install react-simple-maps`)

```jsx
import { ComposableMap, Geographies, Geography } from 'react-simple-maps';

const GEO_URL = 'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json';

// countryCoverage 배열에서 iso → intensity 매핑
// intensity → fill 색상 (0: #f1f5f9 → 1.0: #7c3aed)
// 툴팁: 국가명 + 특허 건수
// 크기: width=800, height=400, projectionConfig.scale=147
```

**색상 스케일**: `intensity` → `rgba(124, 58, 237, intensity)` (violet 계열)

### 5.3 FamilyExpansionMeter.jsx

지표 4개(FES/GCR/MIV/averageFamilySize)를 진행바 형태로 표시:

```jsx
// { FES: 0.82, GCR: 0.74, MIV: 0.68, averageFamilySize: 4.3 }
// FES/GCR/MIV: 0~1 → 퍼센트 진행바 (violet/cyan/emerald)
// averageFamilySize: 0~10 → 별도 표시
```

### 5.4 AssigneePressureTable.jsx

```jsx
// assigneeLeaderboard → 순위 | 출원인명 | 패밀리 수 | GCR 점수
// GCR 값에 따라 색상 배지 (> 0.85: violet, > 0.7: cyan, else: slate)
// 상위 5개 표시
```

### 5.5 FSSView.jsx 구조

```jsx
const FSSView = ({ data }) => {
  if (!data) return <EmptyState viewName="FSS" description="..." />;
  return (
    <div className="space-y-8">
      <h2>FSS — Strategic Pressure View</h2>

      {/* 지표 4개 */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <FamilyExpansionMeter metrics={data.familyMetrics} />
      </div>

      {/* 세계 지도 */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <GlobalCoverageMap coverage={data.countryCoverage} />
      </div>

      {/* 출원인 리더보드 */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <AssigneePressureTable leaderboard={data.assigneeLeaderboard} />
      </div>
    </div>
  );
};
```

---

## 6. WSDView 설계

### 6.1 파일 구조

```
front_end/src/components/tgip/views/WSDView/
├── ProblemSolutionHeatmap.jsx  (CSS 그리드)
├── GapCandidatesList.jsx       (HTML/Tailwind 카드 리스트)
├── CrossIndustryAnalogPanel.jsx (HTML/Tailwind 패널)
└── WSDView.jsx                 (컨테이너)
```

### 6.2 ProblemSolutionHeatmap.jsx

**접근**: CSS 그리드 (Chart.js Matrix 대신 직접 구현 — 의존성 최소화)

```jsx
// heatmapMatrix[i][j] = problem_i × solution_j 밀도
// 행: problemClusters, 열: solutionClusters
// 각 셀: 0~1 → 배경색 (0: #f8fafc → 1: #7c3aed)
// 셀 크기: 60×60px, gap: 4px
// 툴팁: 호버 시 값 + 레이블 표시
```

**색상 계산**: `background: rgba(124, 58, 237, ${value})`

### 6.3 GapCandidatesList.jsx

```jsx
// gapCandidates → 카드 목록
// 각 카드: 갭 스코어 배지 | 문제 영역 | 솔루션 후보 | 신뢰도
// 갭 스코어 > 0.8: emerald badge, > 0.6: cyan badge, else: slate badge
// 신뢰도: 진행바 표시
```

### 6.4 CrossIndustryAnalogPanel.jsx

```jsx
// crossIndustryAnalogs → 유추 이전 패널
// 각 항목: 출처 산업 → 대상 문제 → 유추 기술 | 유사도
// 화살표 형태 레이아웃 (→ 기호 사용)
```

### 6.5 WSDView.jsx 구조

```jsx
const WSDView = ({ data }) => {
  if (!data) return <EmptyState viewName="WSD" description="..." />;
  return (
    <div className="space-y-8">
      <h2>WSD — Opportunity Field View</h2>

      {/* 히트맵 */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <ProblemSolutionHeatmap
          matrix={data.heatmapMatrix}
          problems={data.problemClusters}
          solutions={data.solutionClusters}
        />
      </div>

      {/* 갭 후보 리스트 */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <GapCandidatesList candidates={data.gapCandidates} />
      </div>

      {/* 교차산업 유추 */}
      {data.crossIndustryAnalogs?.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <CrossIndustryAnalogPanel analogs={data.crossIndustryAnalogs} />
        </div>
      )}
    </div>
  );
};
```

---

## 7. RunDetail 페이지 설계

### 7.1 파일: `front_end/src/pages/tgip/RunDetail.jsx`

```jsx
// useParams: run_id
// useEffect: tgipApi.getRunDetail(run_id) 호출 → state 저장
// 로딩/에러 처리 포함
```

**섹션 레이아웃**:

```
+-------------------------------------------------------------+
| ← Back to Workspace         Analysis Run Detail            |
+-------------------------------------------------------------+
| [Summary Card]                                              |
|  Technology: xxx | Run ID: tgip-run-... | Date: 2026-03-05  |
+-------------------------------------------------------------+
| [Metrics Grid — 2×2]                                        |
|  RTS: score + stage  |  TPI: propagation score             |
|  FSS: GCR + FES      |  WSD: gap candidates count          |
+-------------------------------------------------------------+
| [Evidence Bundle — 접힘 가능]                               |
|  대표 특허 목록 | IPC 시그니처 | 신뢰도                       |
+-------------------------------------------------------------+
| [Download]                                                  |
|  [JSON 다운로드]  [← Phase 3: PDF 내보내기]                 |
+-------------------------------------------------------------+
```

### 7.2 App.jsx 라우트 추가

```jsx
// 기존 TGIPAppLayout 내부에 추가:
import RunDetail from './pages/tgip/RunDetail';

<Route element={<TGIPAppLayout />}>
  <Route path="/app/tech/:technology_id" element={<TGIPWorkspace />} />
  <Route path="/app/runs/:run_id" element={<RunDetail />} />   {/* ← 추가 */}
</Route>
```

---

## 8. SidebarViewSelector 수정 설계

### 수정 내용

```jsx
// 기존: available: false → 변경: available: true (TPI, FSS, WSD 모두)
const VIEWS = [
  { id: 'RTS', ..., available: true },
  { id: 'TPI', ..., available: true },  // ← false → true
  { id: 'FSS', ..., available: true },  // ← false → true
  { id: 'WSD', ..., available: true },  // ← false → true
];

// "soon" 배지 제거:
// {!v.available && <span className="text-xs text-slate-400 ml-auto">soon</span>}
// → 이 줄 삭제
```

---

## 9. 공통 EmptyState 패턴

모든 뷰(TPI/FSS/WSD)는 동일한 EmptyState 패턴을 사용:

```jsx
// RTSView와 동일한 UI 패턴
const EmptyState = ({ viewName, description }) => (
  <div className="flex flex-col items-center justify-center h-64 text-slate-400">
    <p className="text-lg font-medium">{viewName} — No Data</p>
    <p className="text-sm mt-1">{description}</p>
  </div>
);
```

---

## 10. 신규 설치 의존성

| 패키지 | 명령 | 용도 |
|--------|------|------|
| `react-simple-maps` | `npm install react-simple-maps` | FSSView 세계 지도 |

> 나머지(`@xyflow/react`, `chart.js`, `react-chartjs-2`, `framer-motion`)는 이미 설치됨.

---

## 11. 구현 순서 (상세)

### Step 1 — tgipStore.js Mock 확장
- `MOCK_RESULTS.TPI`, `MOCK_RESULTS.FSS`, `MOCK_RESULTS.WSD` 추가

### Step 2 — 백엔드 구현
1. `back_end/app/schemas/tgip.py` 생성
2. `back_end/app/api/v1/endpoints/tgip.py` 생성
3. `back_end/app/api/v1/api.py` — import + include_router 추가

### Step 3 — WSDView (우선)
1. `ProblemSolutionHeatmap.jsx`
2. `GapCandidatesList.jsx`
3. `CrossIndustryAnalogPanel.jsx`
4. `WSDView.jsx` 교체

### Step 4 — TPIView
1. `PropagationGraph.jsx`
2. `BurstTimeline.jsx`
3. `IndustryFlowDiagram.jsx`
4. `TPIView.jsx` 교체

### Step 5 — FSSView
1. `npm install react-simple-maps`
2. `GlobalCoverageMap.jsx`
3. `FamilyExpansionMeter.jsx`
4. `AssigneePressureTable.jsx`
5. `FSSView.jsx` 교체

### Step 6 — RunDetail + 라우팅
1. `RunDetail.jsx` 구현
2. `App.jsx` 라우트 추가

### Step 7 — 통합 마무리
1. `SidebarViewSelector.jsx` — `available: true`로 수정
2. E2E 검증: Mock → FastAPI API 연동 확인
3. (선택) `framer-motion` 뷰 전환 애니메이션

---

## 12. 검증 기준 (Gap Analysis 기준)

| 항목 | 검증 방법 |
|------|----------|
| TPIView 렌더링 | Mock 데이터로 PropagationGraph + BurstTimeline 화면 표시 |
| FSSView 렌더링 | GlobalCoverageMap 국가 5개 색상 표시 |
| WSDView 렌더링 | 히트맵 4×3 그리드 + 갭 후보 3개 카드 |
| FastAPI 응답 | `POST /api/v1/tgip/analysis` → 200 + run_id |
| RunDetail | `/app/runs/{run_id}` → Summary + Metrics 표시 |
| SidebarViewSelector | TPI/FSS/WSD 클릭 → 해당 뷰 렌더링 |
| EvidenceDrawer 연동 | 3개 신규 뷰에서도 EvidenceDrawer 내용 표시 |
| Mock Fallback 제거 | runAnalysis() 성공 시 MOCK_RESULTS 미사용 |
