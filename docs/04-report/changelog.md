# TGIP Project Changelog

> **프로젝트**: Patent Board / TGIP (Technology Geo-Intelligence Platform)
> **형식**: [Semantic Versioning](https://semver.org/lang/ko/) 따름

---

## [2.0.1-refactor] - 2026-03-05

### Overview
tgip-store-refactor PDCA 사이클 완료. 코드 리뷰(82/100) Major 3건 해결 → 코드 품질 및 안정성 개선.

- **Match Rate**: 100% (17/17 항목 완료)
- **기간**: 2026-03-05 (1일, 기존 Phase 2 구현 후 검증)
- **상태**: ✅ Complete
- **영향 범위**: 리팩터링 전용 (기능 변경 0건)

### Added

- `INITIAL_RESULTS` 상수: `tgipStore.js`에 결과값 초기 상태 중앙화
- `INITIAL_EVIDENCE` 상수: 증거 데이터 초기 상태 중앙화
- `useCallback` 최적화: `usePDFExport` hook에 메모이제이션 추가

### Fixed

- **M1** (API 응답 방어): `response.data ?? {}` + fallback 기본값으로 서버 응답 스키마 벗어남 방어
  - `results = { ...INITIAL_RESULTS }` destructuring fallback
  - `evidence = { ...INITIAL_EVIDENCE }` destructuring fallback
  - `run_id ?? null` nullish coalescing
- **M2** (중복 제거): 초기 상태 객체 리터럴 중복 제거 → 6개소에서 상수 재사용 (DRY 원칙)
- **M3** (Hook 규약): React hook 네이밍 규약 완전 준수 + 함수 참조 안정화

### Changed

- `setTechnology` 액션: `INITIAL_RESULTS`, `INITIAL_EVIDENCE` 상수 사용
- `reset` 액션: `INITIAL_RESULTS`, `INITIAL_EVIDENCE` 상수 사용
- 초기 상태 선언: spread 문법 사용 (참조 공유 방지)

### Quality Metrics

- **Design Match Rate**: 100% (17/17 항목 완료, 0/17 미구현)
- **Architecture Compliance**: 100%
- **Convention Compliance**: 100%
- **Breaking Changes**: 0건 (완전 호환)

### Documentation

- ✅ Plan: `docs/01-plan/features/tgip-store-refactor.plan.md`
- ✅ Design: `docs/02-design/features/tgip-store-refactor.design.md`
- ✅ Analysis: `docs/03-analysis/tgip-store-refactor.analysis.md` (100% Match)
- ✅ Report: `docs/04-report/features/tgip-store-refactor.report.md`

---

## [2.0.0-phase2] - 2026-03-05

### Overview
frontend-phase2 PDCA 사이클 완료. TGIP 멀티뷰(TPI/FSS/WSD) 완성 + FastAPI 백엔드 API 연동.

- **Match Rate**: 95% (54/60 항목 완료, 6/60 경미 변경)
- **기간**: 2026-02-28 ~ 2026-03-05 (6일)
- **상태**: ✅ Complete

### Added

#### 프론트엔드 컴포넌트 (12개 신규 파일)

**TPIView 구현**
- `PropagationGraph.jsx` (99 lines): @xyflow/react 기반 의미 전파 노드-엣지 그래프
  - 방사형 레이아웃 (core: center, RADIUS=180)
  - 노드 크기 가변 (size*2)
  - 엣지 가중치 시각화 (strokeWidth: weight*5)
- `BurstTimeline.jsx` (94 lines): Chart.js Line 듀얼 Y축
  - 왼쪽 Y축: 특허 건수 (count, 파란색 #38bdf8)
  - 오른쪽 Y축: 버스트 스코어×100 (burstScore, 주황색 #f97316, 대시)
- `IndustryFlowDiagram.jsx` (65 lines): Chart.js 가로 Bar
  - indexAxis: 'y' (가로 바)
  - 조건부 색상: score >= 0.7 (#38bdf8), 0.5-0.7 (#60a5fa), < 0.5 (#cbd5e1)
- `TPIView.jsx` (46 lines): 컨테이너 컴포넌트

**FSSView 구현**
- `GlobalCoverageMap.jsx` (89 lines): react-simple-maps 기반 세계 지도
  - ComposableMap + Geographies (world-atlas CDN)
  - ISO2 → numeric ID 변환 매핑 추가 (KR→410, US→840 등)
  - intensity → violet 색상 (rgba(124,58,237,alpha))
  - projectionConfig.scale=147
  - 하단 커버리지 요약 바 추가 (UX 개선)
- `FamilyExpansionMeter.jsx` (45 lines): Tailwind 진행바
  - FES/GCR/MIV 지표 (violet/cyan/emerald)
  - averageFamilySize 별도 표시
- `AssigneePressureTable.jsx` (43 lines): HTML/Tailwind 리더보드
  - 순위 | 출원인명 | 패밀리 수 | GCR 점수
  - GCR 색상 배지 (>= 0.88: violet, >= 0.75: cyan, else: slate)
- `FSSView.jsx` (39 lines): 컨테이너 컴포넌트

**WSDView 구현**
- `ProblemSolutionHeatmap.jsx` (84 lines): CSS 그리드
  - 문제(행) × 솔루션(열) 4×3 매트릭스
  - 셀 색상: rgba(124,58,237,value)
  - 호버 시 툴팁 (값 + 레이블)
  - 하단 범례 추가 (Low-High 색상)
- `GapCandidatesList.jsx` (55 lines): 갭 후보 카드 목록
  - 갭 스코어 배지 (>= 0.8: emerald, >= 0.6: cyan)
  - 신뢰도 진행바
- `CrossIndustryAnalogPanel.jsx` (33 lines): 교차산업 유추 패널
  - 화살표 형태 레이아웃 (sourceIndustry → targetProblem → analogy)
- `WSDView.jsx` (45 lines): 컨테이너 컴포넌트

**RunDetail 페이지**
- `pages/tgip/RunDetail.jsx` (221 lines): /app/runs/:run_id 페이지
  - Summary Card (기술명, Run ID, 생성일시)
  - Metrics Grid 2×2 (RTS/TPI/FSS/WSD 주요 지표)
  - Evidence Bundle (대표 특허 + IPC 시그니처, 접힘 가능)
  - JSON 다운로드 버튼
  - PDF 내보내기 (Phase 3 예정, disabled)
  - 하단 면책 고지

**라우팅 및 Store 확장**
- `App.jsx`: /app/runs/:run_id 라우트 추가 (TGIPAppLayout 내부)
- `SidebarViewSelector.jsx`: TPI/FSS/WSD available: true로 활성화, "soon" 배지 제거
- `tgipStore.js`: MOCK_RESULTS.TPI/FSS/WSD 데이터 추가 (Mock 데이터)
- `api/tgip.js`: tgipApi 메서드 4개 추가 (runAnalysis, getRunDetail, searchTechnologies, getLibrary)

#### 백엔드 API (2개 신규 파일)

**Pydantic 스키마**
- `back_end/app/schemas/tgip.py` (130 lines):
  - TGIPAnalysisRequest: technology_id, views[]
  - EvidenceBundle: representativePatents, ipcSignatures, abstractSnippets, confidenceScores
  - TGIPAnalysisResponse: run_id, technology_id, results{}, evidence, created_at
  - TGIPRunResponse: TGIPAnalysisResponse + metadata
  - TechnologySearchResult: id, name, patentCount, description
  - TGIPLibraryItem: run_id, technology_id, technology_name, created_at, views_computed[]

**FastAPI 엔드포인트**
- `back_end/app/api/v1/endpoints/tgip.py` (320 lines):
  - POST `/api/v1/tgip/analysis`: 분석 실행 (Mock 응답, run_id 자동 생성)
  - GET `/api/v1/tgip/runs/{run_id}`: 실행 상세 조회 (fallback Mock 제공)
  - GET `/api/v1/tgip/technologies?q=keyword`: 기술 검색 (5개 샘플 데이터)
  - GET `/api/v1/tgip/library`: 실행 히스토리 (in-memory store)
  - Mock 데이터: RTS/TPI/FSS/WSD 모두 포함 (Design 문서와 동일 구조)

**라우터 등록**
- `back_end/app/api/v1/api.py`:
  - `from app.api.v1.endpoints import tgip` 추가
  - `api_router.include_router(tgip.router, prefix="/tgip", tags=["tgip"])` 추가

#### 신규 의존성

- `react-simple-maps` ^3.0.0: 세계 지도 시각화

### Changed

#### 시각적 개선 사항

- **PropagationGraph 엣지 두께**: Design weight×4 → Implementation weight×5 (가시성 향상)
- **IndustryFlowDiagram 색상**: 단일 색상 → 3단계 조건부 색상 (가독성 향상)
  - score >= 0.7: #38bdf8 (blue)
  - 0.5 <= score < 0.7: #60a5fa (light blue)
  - score < 0.5: #cbd5e1 (slate)
- **AssigneePressureTable GCR 임계값**: Design 0.85/0.7 → Implementation 0.88/0.75 (미세 조정)

#### Store 및 API 확장

- `tgipStore.js`: MOCK_RESULTS 객체 확장 (RTS 기존 유지 + TPI/FSS/WSD 추가)
- `SidebarViewSelector.jsx`: TPI/FSS/WSD available 플래그 false → true
- `App.jsx`: Routing 구조 확장 (/app/runs/:run_id 추가)
- `api/tgip.js`: API 메서드 4개 신규 추가

### Fixed

- **react-simple-maps 국가 ID 호환성**: ISO2 코드 → numeric ID 변환 매핑 추가
  - world-atlas (CDN 지리 데이터)는 ISO3 코드 대신 numeric ID(3자리) 사용
  - 한국(KR)→410, 미국(US)→840 등 ISO2_TO_NUMERIC 매핑 테이블 추가
- **ProblemSolutionHeatmap 히트맵 범례**: Low-High 색상 범례 추가 (가독성)
- **GlobalCoverageMap 커버리지 요약**: 지도 하단에 국가별 색상 요약 바 추가
- **RunDetail 면책 고지**: 법적 표준 준수 (하단 disclaimer 추가)

### Build & Performance

- **프론트엔드 빌드**: ✅ 성공
  - Duration: 3.09초
  - Bundle Size: 1,097 KB
  - Warning: 1건 (번들 크기 > 500KB 경고)
    - 원인: 3개 차트 라이브러리 + 지도 라이브러리
    - 계획: Phase 3에서 Code Splitting + lazy loading으로 개선 (목표 < 500KB)

### Quality Metrics

- **Design Match Rate**: 95% (54/60 항목 완료, 6/60 경미 변경, 0/60 미구현)
  - 경미 변경 사항: 모두 기능적 영향 무함 (시각적 조정 또는 기술적 개선)
- **Architecture Compliance**: 98%
- **Convention Compliance**: 100%
- **E2E 검증**: 100% (Mock 렌더링, API 응답, Routing, Evidence 일관성)

### Documentation

- ✅ Plan 문서: `docs/01-plan/features/frontend-phase2.plan.md`
- ✅ Design 문서: `docs/02-design/features/frontend-phase2.design.md`
- ✅ Analysis 문서: `docs/03-analysis/frontend-phase2.analysis.md` (95% Match)
- ✅ Completion Report: `docs/04-report/frontend-phase2.report.md`

---

## [1.0.0-phase1] - 2026-03-02 (Previous Release)

### Overview
TGIP Phase 1 완료. 기본 프론트엔드 구조 및 RTSView 구현.

- **Match Rate**: 93%
- **상태**: ✅ Complete

### Added

#### Phase 1 컴포넌트

- **RTSView**: Technology Readiness Status 뷰 (4개 서브컴포넌트)
- **TGIP 랜딩 페이지**: Overview, Features, Demo, Docs, About
- **Workspace 구조**: ObservationCanvas + SidebarViewSelector + EvidenceDrawer + RunController
- **Zustand Store**: MOCK_RESULTS (RTS 데이터)
- **API 클라이언트**: tgipApi (기초 구조)
- **신규 라이브러리**: @xyflow/react, framer-motion, chart.js, react-chartjs-2

---

## Notes

### Design vs Implementation Alignment

| Category | Phase 1 | Phase 2 |
|----------|---------|---------|
| Match Rate | 93% | **95%** |
| Minor Changes | 5% | 10% |
| Missing Items | 2% | 0% |

Phase 2에서 완전성 향상: 미구현 항목 0 달성, 모든 기능 완료.

### Next Phase (Phase 3)

**예정 작업**:
- TGIPLanding 페이지 (SEO 최적화)
- PDF 내보내기 기능
- Library 페이지 (/app/library)
- Compare Mode
- 번들 크기 최적화 (target: < 500KB)
- 실제 DB 연동 (Neo4j/OpenSearch/MariaDB)

**예상 시작**: 2026-03-10
**예상 기간**: 10~14일
