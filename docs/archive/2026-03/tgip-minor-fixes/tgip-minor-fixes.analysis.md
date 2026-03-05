# tgip-minor-fixes Analysis Report

> **Analysis Type**: Gap Analysis (Design vs Implementation)
>
> **Project**: Patent Board - TGIP Frontend
> **Analyst**: gap-detector
> **Date**: 2026-03-05
> **Design Doc**: [tgip-minor-fixes.design.md](../02-design/features/tgip-minor-fixes.design.md)

---

## 1. Analysis Overview

### 1.1 Analysis Purpose

코드 리뷰(91/100) 에서 도출된 Minor 이슈 5건(m1~m5)의 설계 대비 구현 일치율을 검증한다.

### 1.2 Analysis Scope

- **Design Document**: `docs/02-design/features/tgip-minor-fixes.design.md`
- **Implementation Files**: 7개 파일 (신규 1, 수정 6)
- **Analysis Date**: 2026-03-05

---

## 2. Gap Analysis (Design vs Implementation)

### 2.1 m1: Mock 데이터 분리 (tgipMockData.js + tgipStore.js)

| 항목 | Design 요구사항 | 실제 구현 | Status |
|------|----------------|-----------|--------|
| `src/mocks/tgipMockData.js` 신규 생성 | MOCK_EVIDENCE + MOCK_RESULTS export | MOCK_EVIDENCE + MOCK_RESULTS export | ✅ Match |
| Mock 데이터 내용 유지 | "현행 그대로 이동" | 동일 데이터 구조 및 값 확인 | ✅ Match |
| tgipStore.js 상단 mock 블록 제거 | 인라인 mock 데이터 삭제 | 인라인 mock 데이터 없음 (91줄) | ✅ Match |
| catch 블록 내 dynamic import | `await import('../mocks/tgipMockData.js')` | `await import('../mocks/tgipMockData.js')` (line 71) | ✅ Match |
| DEV 조건부 분기 | `import.meta.env.DEV` 체크 | `import.meta.env.DEV` 체크 (line 69) | ✅ Match |
| 프로덕션 에러 처리 | `console.error` + error state 설정 | `console.error` + error state (lines 82-86) | ✅ Match |
| tgipStore.js < 100줄 | 검증 기준 | 91줄 | ✅ Match |
| 파일 상단 주석 | 명시 없음 | DEV 전용 안내 주석 포함 (line 1-2) | ✅ 추가 개선 |

**m1 Match Rate: 100% (7/7 항목 일치)**

---

### 2.2 m2: Library.jsx AbortController cleanup + tgip.js 수정

| 항목 | Design 요구사항 | 실제 구현 | Status |
|------|----------------|-----------|--------|
| `getLibrary(options = {})` 시그니처 | options 매개변수 추가 | `getLibrary: (options = {})` (tgip.js line 13) | ✅ Match |
| options를 axios에 전달 | `axiosInstance.get('/tgip/library', options)` | 동일 (tgip.js line 14) | ✅ Match |
| AbortController 생성 | `new AbortController()` | `new AbortController()` (Library.jsx line 68) | ✅ Match |
| signal 전달 | `{ signal: controller.signal }` | `{ signal: controller.signal }` (line 72) | ✅ Match |
| CanceledError 체크 | `err.name !== 'CanceledError'` | `err.name !== 'CanceledError'` (line 75) | ✅ Match |
| cleanup return | `return () => controller.abort()` | `return () => controller.abort()` (line 82) | ✅ Match |

**m2 Match Rate: 100% (6/6 항목 일치)**

---

### 2.3 m3: PDFExporter.jsx Magic Number 상수화

| 항목 | Design 요구사항 | 실제 구현 | Status |
|------|----------------|-----------|--------|
| 상수 이름 | `HIGH_RES_AREA_THRESHOLD` | `HIGH_RES_AREA_THRESHOLD` (line 13) | ✅ Match |
| 상수 값 | `1_000_000` | `1_000_000` | ✅ Match |
| 선언 위치 | `exportToPDF` 함수 내부 상단 | 함수 내부, try 블록 안 상단 (line 13) | ✅ Match |
| 주석 | "1,000,000 px2... 초과 시 메모리 절약을 위해 scale=1" | "1,000,000 px2(약 1000x1000) 초과 시 고해상도 렌더링 생략" (line 12) | ✅ Match |
| scale 로직 | `area > HIGH_RES_AREA_THRESHOLD ? 1 : 2` | `area > HIGH_RES_AREA_THRESHOLD ? 1 : 2` (line 16) | ✅ Match |

**m3 Match Rate: 100% (5/5 항목 일치)**

---

### 2.4 m4: ObservationCanvas.jsx VIEW_COMPONENTS 레지스트리

| 항목 | Design 요구사항 | 실제 구현 | Status |
|------|----------------|-----------|--------|
| VIEW_COMPONENTS 객체 선언 | 파일 상단, lazy import 아래 | lines 10-15, lazy import 직후 | ✅ Match |
| 4개 뷰 등록 | RTS, TPI, FSS, WSD | RTS, TPI, FSS, WSD (lines 11-14) | ✅ Match |
| JSX에서 ViewComponent 패턴 | `VIEW_COMPONENTS[selectedView]` | `VIEW_COMPONENTS[selectedView]` (line 84) | ✅ Match |
| Suspense fallback | `<ViewLoader />` | `<ViewLoader />` (line 82) | ✅ Match |
| 조건부 렌더링 | `ViewComponent && <ViewComponent data={results[selectedView]} />` | `ViewComponent ? <ViewComponent data={results[selectedView]} /> : null` (line 85) | ✅ Match |
| 4-branch if 체인 제거 | 개별 조건부 렌더링 제거 | 개별 조건부 렌더링 없음 | ✅ Match |

**참고 사항**: 구현에서는 `&&` 대신 삼항 연산자(`? :`)를 사용했으나 동작이 동일하므로 일치로 판정.

또한, Design에서는 `ViewComponent`를 JSX 밖에서 선언하는 패턴을 제시했지만, 구현에서는 IIFE `(() => { ... })()` 패턴으로 `<Suspense>` 내부에서 선언하고 있다. 이는 AnimatePresence의 key 전환과 함께 사용하기 위한 합리적 변형이며, 기능적으로 동일하다.

**m4 Match Rate: 100% (6/6 항목 일치)**

---

### 2.5 m5: TGIPWorkspace.jsx alert() 제거 + exportError 배너

| 항목 | Design 요구사항 | 실제 구현 | Status |
|------|----------------|-----------|--------|
| `exportError` state 선언 | `useState(null)` | `useState(null)` (line 18) | ✅ Match |
| onError에서 setExportError | 에러 메시지 설정 | 동일 메시지 (line 28) | ✅ Match |
| 4초 자동 해제 | `setTimeout(() => setExportError(null), 4000)` | `setTimeout(() => setExportError(null), 4000)` (line 29) | ✅ Match |
| alert() 완전 제거 | 코드에 alert() 없음 | alert() 없음 | ✅ Match |
| amber 색상 배너 | `bg-amber-50 border-amber-200 text-amber-700` | `bg-amber-50 border-amber-200 text-amber-700` (line 56) | ✅ Match |
| 닫기 버튼 (X) | `<button onClick={() => setExportError(null)}` 포함 | **닫기 버튼 없음** | ⚠️ Gap |
| flex 레이아웃 | `flex items-center justify-between` | flex 미적용 | ⚠️ Gap |

**m5 Match Rate: 71% (5/7 항목 일치, 2건 미구현)**

---

## 3. Match Rate Summary

```
+-----------------------------------------------+
|  Overall Match Rate: 94% (29/31 items)        |
+-----------------------------------------------+
|  m1 Mock 분리:          100% (7/7)   ✅       |
|  m2 AbortController:    100% (6/6)   ✅       |
|  m3 상수화:             100% (5/5)   ✅       |
|  m4 VIEW_COMPONENTS:    100% (6/6)   ✅       |
|  m5 alert 제거:          71% (5/7)   ⚠️       |
+-----------------------------------------------+
```

---

## 4. Differences Found

### 4.1 Missing Features (Design O, Implementation X)

| # | 항목 | Design 위치 | 구현 파일 | 설명 |
|---|------|------------|----------|------|
| 1 | exportError 닫기 버튼 | design.md line 228 | TGIPWorkspace.jsx line 55-58 | Design에 명시된 `<button onClick={() => setExportError(null)}>` 닫기 버튼이 구현에 누락 |
| 2 | exportError 배너 flex 레이아웃 | design.md line 226 | TGIPWorkspace.jsx line 56 | `flex items-center justify-between` 클래스 미적용 |

### 4.2 Added Features (Design X, Implementation O)

| # | 항목 | 구현 위치 | 설명 |
|---|------|----------|------|
| - | 해당 없음 | - | Design 범위 밖 추가 구현 없음 |

### 4.3 Changed Features (Design != Implementation)

| # | 항목 | Design | Implementation | Impact |
|---|------|--------|----------------|--------|
| 1 | ViewComponent 조건부 렌더링 문법 | `&&` 연산자 | 삼항 연산자 `? :` | Low (동작 동일) |
| 2 | ViewComponent 선언 위치 | JSX 외부 | IIFE 내부 | Low (동작 동일) |

---

## 5. Overall Score

```
+-----------------------------------------------+
|  Overall Score: 94/100                        |
+-----------------------------------------------+
|  Design Match:        94%                     |
|  Architecture:        N/A (리팩터링 건)       |
|  Convention:          98%                     |
+-----------------------------------------------+
```

| Category | Score | Status |
|----------|:-----:|:------:|
| Design Match | 94% | ✅ |
| Convention Compliance | 98% | ✅ |
| **Overall** | **94%** | ✅ |

---

## 6. Convention Compliance

### 6.1 Naming Convention

| Category | Convention | Compliance | Violations |
|----------|-----------|:----------:|------------|
| Components | PascalCase | 100% | - |
| Functions | camelCase | 100% | - |
| Constants | UPPER_SNAKE_CASE | 100% | `HIGH_RES_AREA_THRESHOLD`, `VIEW_COMPONENTS`, `MOCK_EVIDENCE`, `MOCK_RESULTS` |
| Files (component) | PascalCase.jsx | 100% | - |
| Files (utility) | camelCase.js | 100% | `tgipMockData.js`, `tgipStore.js` |
| Folders | kebab-case 또는 PascalCase | 100% | - |

### 6.2 Import Order

모든 수정 파일에서 import 순서 준수 확인:
- [x] 외부 라이브러리 (react, zustand, framer-motion)
- [x] 내부 절대 경로 imports
- [x] 상대 경로 imports
- [x] 스타일 없음 (해당 없음)

---

## 7. Verification Criteria Check

Design 문서 하단 "검증 기준" 대비 확인:

| 검증 항목 | 기준 | 결과 | Status |
|-----------|------|------|--------|
| m1: tgipStore.js 줄수 | < 100줄 | 91줄 | ✅ |
| m1: mocks 파일 존재 | `mocks/tgipMockData.js` 존재 | 존재 (119줄) | ✅ |
| m2: AbortController | unmount 시 abort 호출 | cleanup return 확인 | ✅ |
| m3: 상수 선언 | HIGH_RES_AREA_THRESHOLD 존재 | PDFExporter.jsx line 13 | ✅ |
| m4: VIEW_COMPONENTS | 레지스트리 + ViewComponent 패턴 | ObservationCanvas.jsx lines 10-15, 84-85 | ✅ |
| m5: alert 제거 | 코드에 alert() 없음 | alert() 없음 | ✅ |
| m5: exportError 배너 | 배너 렌더링 | 배너 존재 (닫기 버튼 누락) | ⚠️ |

---

## 8. Recommended Actions

### 8.1 Immediate (Gap 해소)

| Priority | Item | File | Description |
|----------|------|------|-------------|
| ⚠️ 1 | 닫기 버튼 추가 | `src/pages/tgip/TGIPWorkspace.jsx:55-58` | exportError 배너에 Design 명세대로 닫기(X) 버튼 추가 |
| ⚠️ 2 | flex 레이아웃 적용 | `src/pages/tgip/TGIPWorkspace.jsx:56` | `flex items-center justify-between` 클래스 추가 |

### 8.2 참고 (의도적 변경)

| Item | File | Notes |
|------|------|-------|
| ViewComponent 삼항 연산자 | ObservationCanvas.jsx | `&&` 대신 삼항 사용 - 동작 동일, 문서 업데이트 불필요 |

---

## 9. Next Steps

- [ ] m5 배너 닫기 버튼 + flex 레이아웃 추가 (2건)
- [ ] 수정 후 재검증으로 100% 달성
- [ ] `npm run build` 경고 0개 확인
- [ ] Completion report 작성 (`tgip-minor-fixes.report.md`)

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 0.1 | 2026-03-05 | Initial gap analysis | gap-detector |
