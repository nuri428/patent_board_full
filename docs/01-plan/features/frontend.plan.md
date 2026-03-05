# [Plan] Frontend - TGIP 프론트엔드 전체 페이지 기획

> **작성일**: 2026-03-05
> **상태**: Plan
> **버전**: v1.0
> **참고 문서**: `tgip_front_plan.txt`

---

## 1. Feature 개요

| 항목 | 내용 |
|------|------|
| Feature Name | frontend |
| 제품명 | TGIP — Technology Geo-Intelligence Platform |
| 유형 | React SPA (Vite + React Router) |
| 목적 | 기술 생태계를 4가지 관찰 시점(RTS/TPI/FSS/WSD)으로 분석하는 멀티뷰 관찰 시스템 |
| 대상 사용자 | 특허 분석가, 기술 전략 연구원, 산업 분석 전문가 |

### 한 줄 요약

> "하나의 기술 오브젝트를 네 가지 관찰 시점으로 분석한다" — 의사결정 중립 원칙을 지키며 증거 기반 신호만 제공하는 멀티뷰 워크스페이스

---

## 2. 제품 정체성 (Product Identity)

### 핵심 UX 원칙

- **One Technology Object → Multiple View Points**
- RTS/TPI/FSS/WSD는 "답"이 아니라 "근거 있는 관찰"이다
- 추천/처방 없음 — 관찰 신호와 근거만 제공

### Non-goals (명시적 제외)

- "권장 의사결정" 출력 없음
- 투자/전략 처방 없음
- 모든 UI 카피에서 "best", "recommend", "should", "invest" 등 표현 금지

---

## 3. 정보 아키텍처 (IA)

### 공개 페이지 (로그인 불필요)

| 경로 | 페이지명 | 내용 |
|------|----------|------|
| `/` | Landing | 짧고 시각적인 랜딩 |
| `/overview` | TGIP Overview | 개념 + 파이프라인 + 4가지 뷰 설명 |
| `/features` | Feature Detail | RTS/TPI/FSS/WSD 상세 (의미/산출물/근거) |
| `/demo` | Demo | 샘플 보고서 / 샘플 뷰 미리보기 |
| `/docs` | Documentation | API/Schema/Glossary 허브 |
| `/about` | About | 소개 / 연락처 |

### 앱 페이지 (로그인 선택적, 처음엔 오픈 가능)

| 경로 | 페이지명 | 내용 |
|------|----------|------|
| `/app` | App Shell | 기술 셀렉터 + 뷰 전환 |
| `/app/tech/:id` | Technology Workspace | 핵심 관찰 UI (RTS/TPI/FSS/WSD 캔버스) |
| `/app/runs/:run_id` | Analysis Run Detail | 추적성 / 근거 / 로그 |
| `/app/library` | Library | 저장된 기술 / 실행 / 보고서 내보내기 |
| `/app/settings` | Settings | 모델 범위, 언어, 내보내기 설정 |

### MVP 권장 순서

1. `/overview` + `/app/tech/:id` (RTS 뷰) + `/app/runs/:run_id`
2. 나머지는 "coming soon" 처리 가능

---

## 4. Overview 페이지 구조 (`/overview`)

### 섹션 구성 (위→아래)

| # | 섹션명 | 내용 |
|---|--------|------|
| A | Hero | 제목 + 설명 + "Open Demo" CTA |
| B | Multi-View Concept | 하나의 오브젝트, 4가지 시점 다이어그램 |
| C | Technology Landscape Concept | 지리적 풍경 메타포 설명 |
| D | Feature Production Pipeline | 6단계 파이프라인 스텝퍼 |
| E | Outputs as Views | RTS/TPI/FSS/WSD 4카드 (핵심 질문 + 산출물 + 근거) |
| F | Trust / Safety | 비추천 철학 + 증거 필수 원칙 + 면책 고지 |
| G | CTA Footer | "Try the Workspace" + "Read Feature Specs" |

### Feature Production Pipeline 6단계

| 단계 | 이름 | 설명 |
|------|------|------|
| 1 | Data Ingestion | KR(KIPRIS)/US(Google Patents) 특허 수집 및 정규화 |
| 2 | Semantic Indexing | OpenSearch 키워드 인덱스 + 벡터 임베딩 |
| 3 | Knowledge Graph | Neo4j 노드(Patent/Applicant/IPC/Tech/Problem/Solution) |
| 4 | Feature Extraction | Problem-Solution 쌍, 기술 시그니처, 신뢰도 |
| 5 | Metrics Computation | RTS/TPI/FSS/WSD 지표 계산 |
| 6 | Reporting & Evidence | analysis_run_id + 증거 패키지 + 면책 고지 |

---

## 5. Feature 상세 페이지 (`/features`)

### 레이아웃

- 좌측 네비: RTS / TPI / FSS / WSD
- 우측: 개념 → 산출물 → 근거 → 엣지케이스 → 용어집

### 5.1 RTS (구조 성숙도 뷰)

| 항목 | 내용 |
|------|------|
| 핵심 질문 | "이 기술은 성숙도 어디에 있고, 왜 아직인가?" |
| 주요 산출물 | rts_score(0~1), stage(Critical Bottleneck/Bottleneck/Closure), 컴포넌트 점수 |
| 증거 패키지 | 대표 특허(≤5), IPC/CPC 시그니처, 섹션별 스니펫, 신뢰도/커버리지 |
| UI 위젯 | 성숙도 스케일 바, Why-Not-Yet 컴포넌트 바, 옵션 비교 테이블 |

### 5.2 TPI (전파 뷰)

| 항목 | 내용 |
|------|------|
| 핵심 질문 | "어디로 퍼지고, 얼마나 빠르며, 어디서 수렴하는가?" |
| 주요 산출물 | semantic_propagation score, industry_flow matrix, burst timeline, hidden lineage |
| 증거 패키지 | 상위 의미 유사 특허 + 유사도, 인용, 산업 매핑 |
| UI 위젯 | Sankey-like 플로우 맵, 타임라인 버스트 차트, 리니지 스트립 |

### 5.3 FSS (전략 압력 뷰)

| 항목 | 내용 |
|------|------|
| 핵심 질문 | "출원인이 글로벌로 얼마나 강하게 방어하는가?" |
| 주요 산출물 | FES, GCR, MIV, SCI, TLT, 패밀리 크기, 국가 커버리지 |
| 증거 패키지 | 패밀리 멤버 목록, 법적 상태 코드, 국가 커버리지 |
| UI 위젯 | 국가 커버리지 맵, 패밀리 확장 미터, 출원인 리더보드 |

### 5.4 WSD (기회 필드 뷰)

| 항목 | 내용 |
|------|------|
| 핵심 질문 | "해결 안 된 문제 영역과 시도되지 않은 조합은 어디인가?" |
| 주요 산출물 | 문제 클러스터/밀도, 솔루션 클러스터/밀도, 갭 후보, 교차산업 유추 |
| 증거 패키지 | 클러스터별 지지 특허, 추출 신뢰도/누락 지표 |
| UI 위젯 | 문제×솔루션 히트맵, 갭 리스트(갭 스코어+신뢰도), 유추 이전 패널 |

---

## 6. TGIP Workspace (`/app/tech/:id`)

### 레이아웃 구조

```
+------------------------------------------------------------+
| Header                                                     |
| Technology Selector | View Switch | Run Analysis | Export  |
+------------------------------------------------------------+

+----------------------+-------------------------------------+
| View Selector        | Observation Canvas                  |
|                      |                                     |
| RTS  [coverage%]     | 뷰별 시각화                          |
| TPI  [coverage%]     |                                     |
| FSS  [coverage%]     | Charts / Graphs / Maps              |
| WSD  [coverage%]     |                                     |
+----------------------+-------------------------------------+

+------------------------------------------------------------+
| Evidence Drawer (상시 접근 가능)                            |
| Analysis Run ID | Patents | IPC Signatures | Snippets      |
+------------------------------------------------------------+
```

### 뷰 전환 규칙

- 뷰 전환 시 기본적으로 재계산하지 않음 (최신 analysis_run_id 재사용)
- "Run Analysis" 버튼 클릭 시만 재계산 → 새 run_id 생성

### Evidence Drawer 규칙 (필수)

모든 신호에는 반드시 근거가 있어야 함:

| 항목 | 내용 |
|------|------|
| Patent ID | 특허 고유 ID |
| Title | 특허 제목 |
| Abstract Snippet | 초록 스니펫 |
| IPC/CPC Signature | 분류 코드 |
| Confidence Score | 신뢰도 점수 |
| Analysis Run ID | 추적용 실행 ID |

> **불변 규칙**: 캔버스는 근거 항목 없이 어떤 주장도 표시해서는 안 됨

---

## 7. React 컴포넌트 아키텍처

```
App
 ├── Layout
 │    ├── Header
 │    │    ├── TechnologySelector (검색)
 │    │    ├── RunAnalysisButton
 │    │    └── ExportButton
 │    ├── SidebarViewSelector
 │    │    ├── ViewTab (RTS/TPI/FSS/WSD)
 │    │    └── CoverageIndicator
 │    └── EvidenceDrawer (하단 토글)
 │
 ├── ObservationCanvas
 │    ├── RTSView
 │    │    ├── MaturityScale
 │    │    ├── ScoreBreakdownChart
 │    │    ├── BottleneckIndicator
 │    │    └── SolutionOptionsTable
 │    ├── TPIView
 │    │    ├── PropagationGraph
 │    │    ├── IndustryFlowDiagram
 │    │    └── BurstTimeline
 │    ├── FSSView
 │    │    ├── FamilyExpansionMeter
 │    │    ├── GlobalCoverageMap
 │    │    └── AssigneePressureTable
 │    └── WSDView
 │         ├── ProblemSolutionHeatmap
 │         ├── GapCandidatesList
 │         └── CrossIndustryAnalogPanel
 │
 └── RunController
      ├── RunAnalysisButton
      └── RunStatusIndicator
```

---

## 8. 상태 관리 모델

### Global State

| 상태 | 타입 | 설명 |
|------|------|------|
| selectedTechnology | string | 선택된 기술 ID |
| selectedView | enum(RTS/TPI/FSS/WSD) | 현재 뷰 |
| analysisRunId | string | 현재 분석 실행 ID |

### Technology Data State

| 상태 | 설명 |
|------|------|
| technologyMetadata | 기술 메타데이터 |
| patentCount | 특허 수 |
| technologyCluster | 기술 클러스터 |

### Analysis Result State

```
RTS: { score, stage, components }
TPI: { propagationGraph, burstTimeline }
FSS: { familyMetrics, coverageMap }
WSD: { problemSolutionDensity, gapCandidates }
```

### Evidence State

```
{ representativePatents, ipcSignatures, abstractSnippets, confidenceScores }
```

### 상태 흐름

```
기술 선택 → Run Analysis → Backend → analysis_run_id
  → 결과 번들 로드 → 뷰 전환 시 시각화 렌더링
```

---

## 9. Run Detail 페이지 (`/app/runs/:run_id`)

| 섹션 | 내용 |
|------|------|
| Summary | 대상 기술 + 범위 + 파라미터 |
| Metrics | RTS/TPI/FSS/WSD JSON + 사람이 읽기 좋은 카드 |
| Evidence | 확장 가능한 근거 번들 |
| Logs | 추출 커버리지, 누락 필드 수 (선택) |
| Download | 보고서 PDF / raw JSON |

---

## 10. UI 카피 / 톤 규칙

### 사용해야 할 표현

- "observed", "measured", "signals", "evidence", "indicates"
- "possible interpretations", "ranges", "confidence"

### 사용 금지 표현

- "best", "promising", "should", "recommend", "buy", "invest"

### 기본 면책 고지 (푸터 + 내보내기)

> "This system provides observational signals with evidence. Final decisions remain with the user."

---

## 11. MVP 구현 순서

### Phase 1 — 시각적 신뢰도 (최우선)

- [x] `/overview` 페이지 (개념 + 파이프라인 + 4가지 뷰)
- [x] `/app/tech/:id` (RTS 뷰 + Evidence Drawer)
- [x] `/app/runs/:run_id` (추적성 페이지)

### Phase 2 — 멀티뷰 완성

- [ ] TPI 뷰 추가
- [ ] FSS 뷰 추가
- [ ] WSD 뷰 추가 (히트맵 + 갭 리스트 시작)

### Phase 3 — 완성도

- [ ] Demo 프리셋 (solid-state battery 등)
- [ ] PDF 내보내기
- [ ] Library / 저장된 실행
- [ ] 세밀한 필터 + 성능 최적화

---

## 12. 디자인 원칙 5가지

| # | 원칙 | 설명 |
|---|------|------|
| 1 | Evidence First | 모든 분석 신호에 추적 가능한 근거 필수 |
| 2 | Multi-View Observation | 기술 오브젝트를 여러 시점으로 관찰 |
| 3 | Decision Neutrality | 신호/관찰만 제공, 권고 없음 |
| 4 | Structural Thinking | 구조, 전파, 압력, 기회에 집중 |
| 5 | Consistent Object Identity | 모든 뷰는 동일 기술 오브젝트를 참조 |

---

## 13. Must-Have / Nice-to-Have

### Must-Have

- [ ] Technology Selector (기술 검색)
- [ ] View Switch (RTS/TPI/FSS/WSD)
- [ ] Evidence Drawer (항상 접근 가능)
- [ ] analysis_run_id 표시
- [ ] Coverage/Confidence 지표
- [ ] 처방적 언어 없음 (카피 가이드 준수)

### Nice-to-Have

- [ ] 뷰 전환 시 카메라 같은 부드러운 트랜지션
- [ ] Compare Mode 토글
- [ ] 미리 빌드된 데모
- [ ] 내보내기 + 공유 가능한 실행 링크

---

## 14. 미래 확장 (Future Extensions)

| 기능 | 설명 |
|------|------|
| 3D Technology Terrain View | 기술 클러스터를 고도 필드로 시각화 |
| Time Evolution Mode | 연도별 기술 전파 관찰 |
| Industry Overlay | 교차산업 이전 경로 하이라이트 |
| Scenario Mode | RTS/TPI 파라미터 시뮬레이션 |
| Collaborative Annotation | 분석가 노트 첨부 기능 |

---

## 15. 기술 스택 (현재 프로젝트 기준)

| 항목 | 기술 |
|------|------|
| 프레임워크 | React + Vite |
| 라우팅 | React Router v6 |
| 스타일링 | Tailwind CSS |
| 상태 관리 | React Context (+ 필요 시 Zustand 검토) |
| HTTP | Axios |
| 시각화 | (TBD: Recharts / D3.js / Nivo) |
| 빌드 | Vite |

---

## 16. 성공 지표

| 지표 | 목표 |
|------|------|
| MVP Phase 1 페이지 완성 | Overview + RTS Workspace + Run Detail |
| Evidence Drawer 구현 | 모든 신호에 근거 1개 이상 |
| 처방적 언어 부재 | 카피 리뷰 통과 |
| 뷰 전환 응답 | < 200ms (재계산 없이) |
| 분석 실행 완료 | analysis_run_id 정상 발급 |
