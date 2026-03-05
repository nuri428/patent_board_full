# Plan: tgip-code-fixes

> 코드 리뷰(Score: 78/100)에서 발견된 Critical 3개 + Major 4개 이슈 수정

## 목표

frontend-phase3 코드 리뷰 결과를 기반으로 Critical/Major 이슈를 수정하여
프로덕션 안정성과 UX 품질을 개선한다.

## 배경

- `/bkit:code-review` 결과: 78/100
- Critical 3건 (안정성·신뢰성 위협)
- Major 4건 (사용자 경험·유지보수성 문제)

## 수정 범위

### C1+C2 — PDFExporter.jsx: 에러 처리 및 메모리 안전화

**현 상태**
- `try/catch` 없음 → export 실패 시 silent fail
- `scale: 2 + toDataURL()` → 대용량 DOM에서 메모리 폭주 가능

**목표**
- `try/catch`로 감싸고, 실패 시 토스트/console.error 표시
- canvas scale 조정 로직 (DOM 크기 기반 자동 조절)

**파일**: `front_end/src/components/tgip/shared/PDFExporter.jsx`

---

### C3 — tgipStore.js: 프로덕션 mock 데이터 노출 방지

**현 상태** (lines 185-194)
```js
} catch {
  // 모든 에러에서 무조건 mock fallback
  set({ results: MOCK_RESULTS, evidence: MOCK_EVIDENCE, ... });
}
```

**목표**
- `import.meta.env.DEV`로 분기:
  - DEV: mock fallback 유지 (현행)
  - PROD: `set({ error: '분석 서버에 연결할 수 없습니다.', isRunning: false })`
- Store에 error 상태 이미 있음 (`error: null` 초기화), 활용

**파일**: `front_end/src/store/tgipStore.js`

---

### M1 — Library.jsx: 에러 상태 UI 추가

**현 상태**
```js
.catch(() => setRuns([]))  // 에러 silently 무시, EmptyState 표시
```

**목표**
- `error` state 추가
- `.catch((e) => setError(e))` → ErrorState 컴포넌트 표시 (재시도 버튼 포함)

**파일**: `front_end/src/pages/tgip/Library.jsx`

---

### M2 — DEMO_TECHS 상수 분리

**현 상태**
- `TGIPWorkspace.jsx` 상단에 `const DEMO_TECHS = { ... }` 하드코딩

**목표**
- `front_end/src/constants/tgip.js` 파일 생성 → `DEMO_TECHS` export
- TGIPWorkspace, Library에서 공통 import

**파일**: `front_end/src/constants/tgip.js` (신규), `TGIPWorkspace.jsx`, `Library.jsx`

---

### M3 — TGIPWorkspace useEffect 의존성 정리

**현 상태**
```js
useEffect(() => {
  if (technology_id && (!selectedTechnology || selectedTechnology.id !== technology_id)) {
    setTechnology(tech);
  }
}, [technology_id, selectedTechnology, setTechnology]);
```

**문제**: `selectedTechnology`를 의존성에 포함하면 ESLint 경고 + 불필요한 재실행 가능

**목표**
- `useRef`로 이전 technology_id 추적하여 의존성을 `[technology_id]`만으로 최소화
- 또는 Zustand에서 직접 id 비교하는 `setTechnologyById` 액션 추가

**파일**: `front_end/src/pages/tgip/TGIPWorkspace.jsx`

---

### M4 — ObservationCanvas canvasRef 연결 보장

**현 상태**
- loading/empty 상태의 `<main>`에는 `ref` 미연결
- `canExport`가 false인 경우 사실상 문제 없지만, 구조적 불일치

**목표**
- 모든 렌더 경로의 `<main>` 에 `ref={ref}` 연결
- (선택) `forwardRef` 패턴으로 리팩터링

**파일**: `front_end/src/components/tgip/Workspace/ObservationCanvas.jsx`

---

## 구현 순서

1. **tgip.js (constants)** — `DEMO_TECHS` 상수 파일 생성
2. **tgipStore.js** — C3: DEV/PROD 분기 적용
3. **PDFExporter.jsx** — C1+C2: try/catch + scale 안전화
4. **Library.jsx** — M1: error state + ErrorState UI + M2: constants import
5. **TGIPWorkspace.jsx** — M2: constants import + M3: useEffect 정리
6. **ObservationCanvas.jsx** — M4: ref 연결 보장

## 변경 파일 목록

| 파일 | 신규/수정 | 이유 |
|------|-----------|------|
| `src/constants/tgip.js` | 신규 | DEMO_TECHS 상수 분리 |
| `src/store/tgipStore.js` | 수정 | C3: DEV/PROD mock 분기 |
| `src/components/tgip/shared/PDFExporter.jsx` | 수정 | C1+C2: 에러처리 + 메모리 |
| `src/pages/tgip/Library.jsx` | 수정 | M1: error state, M2: constants |
| `src/pages/tgip/TGIPWorkspace.jsx` | 수정 | M2: constants, M3: useEffect |
| `src/components/tgip/Workspace/ObservationCanvas.jsx` | 수정 | M4: ref 연결 |

## 성공 기준

- [ ] PDFExporter export 실패 시 에러 메시지 표시 (console.error + 선택적 toast)
- [ ] 프로덕션 빌드(`import.meta.env.DEV === false`)에서 API 실패 시 error state 표시
- [ ] Library 에러 시 EmptyState 대신 ErrorState + 재시도 버튼
- [ ] DEMO_TECHS가 constants 파일에서 중앙 관리
- [ ] TGIPWorkspace useEffect ESLint 경고 없음
- [ ] ObservationCanvas 모든 경로에서 ref 연결
- [ ] 빌드 성공 (경고 0개 유지)

## 스코프 제외 (Minor 이슈)

- 하드코딩 URL `/app/tech/solid-state-battery` → YAGNI (실제 기술 목록 API 없음)
- PDFExporter.jsx 파일명 변경 → 영향 범위 크고 기능 변화 없음
- 4-branch view → map 패턴 → 동작 동일, 리팩터링만
- 접근성(aria-label) → 별도 Feature로 관리

## 예상 Match Rate 목표

95% (이번 수정으로 Critical 3개 + Major 4개 → 0개 목표)
