# Design: tgip-final-fix

## Overview
코드 리뷰(93/100) 잔여 이슈 3건. 수정 파일 3개, 총 ~6줄 변경.

---

## Step 1: DEV fallback `error: null` 추가 (M1)

**파일**: `front_end/src/store/tgipStore.js:76`

**변경 전** (line 76-82):
```js
set({
  analysisRunId: mockRunId,
  results: MOCK_RESULTS,
  evidence: MOCK_EVIDENCE,
  isRunning: false,
  evidenceDrawerOpen: true,
});
```

**변경 후**:
```js
set({
  analysisRunId: mockRunId,
  results: MOCK_RESULTS,
  evidence: MOCK_EVIDENCE,
  isRunning: false,
  evidenceDrawerOpen: true,
  error: null,
});
```

- `error: null` 1줄 추가
- API 에러 후 mock fallback 시 이전 error 상태 초기화 보장

---

## Step 2: ObservationCanvas IIFE 제거 (m1)

**파일**: `front_end/src/components/tgip/Workspace/ObservationCanvas.jsx`

**변경 전** (line 82-87):
```jsx
<Suspense fallback={<ViewLoader />}>
  {(() => {
    const ViewComponent = VIEW_COMPONENTS[selectedView];
    return ViewComponent ? <ViewComponent data={results[selectedView]} /> : null;
  })()}
</Suspense>
```

**변경 후**:
```jsx
<Suspense fallback={<ViewLoader />}>
  {VIEW_COMPONENTS[selectedView]
    ? <VIEW_COMPONENTS[selectedView] data={results[selectedView]} />
    : null}
</Suspense>
```

> **주의**: JSX에서 `<obj[key] />` 형태는 유효하지 않음 — 변수 추출 필요:

**실제 적용 패턴** — `ObservationCanvas` 컴포넌트 함수 본문 상단에서 추출:
```jsx
const ObservationCanvas = ({ canvasRef }) => {
  const { selectedView, results, isRunning, selectedTechnology } = useTGIPStore();
  const innerRef = useRef(null);
  const ref = canvasRef || innerRef;
  const ViewComponent = VIEW_COMPONENTS[selectedView];  // ← 추가

  const hasAnyResult = Object.values(results).some(Boolean);

  return (
    // ...
    <Suspense fallback={<ViewLoader />}>
      {ViewComponent ? <ViewComponent data={results[selectedView]} /> : null}
    </Suspense>
    // ...
  );
};
```

- IIFE 완전 제거
- `ViewComponent`를 컴포넌트 본문 상단에서 한 번만 선언
- JSX 내부에서 `{ViewComponent ? <ViewComponent .../> : null}` 직접 사용

---

## Step 3: RunCard optional chaining 일관화 (m4)

**파일**: `front_end/src/pages/tgip/Library.jsx`

**변경 전**:
```jsx
<p className="text-xs text-slate-400 mt-0.5 font-mono truncate">
  {run.run_id}
</p>
// ...
<span className="text-sm text-slate-500">{formatDate(run.created_at)}</span>
// ...
to={`/app/runs/${run.run_id}`}
```

**변경 후**:
```jsx
<p className="text-xs text-slate-400 mt-0.5 font-mono truncate">
  {run.run_id ?? '—'}
</p>
// ...
<span className="text-sm text-slate-500">{formatDate(run.created_at)}</span>
// (created_at은 이미 formatDate에서 null 처리 → 변경 불필요)
// ...
to={`/app/runs/${run.run_id ?? ''}`}
```

> **참고**: `formatDate()`는 이미 `if (!iso) return '—'` 로 null 처리함 → `run.created_at`은 변경 불필요.
> `run.run_id`의 표시(46행)와 Link href(52행)에만 fallback 추가.

---

## 구현 순서

1. `tgipStore.js` Step 1 (M1: 1줄 추가)
2. `ObservationCanvas.jsx` Step 2 (m1: IIFE 제거)
3. `Library.jsx` Step 3 (m4: run_id fallback)
4. 빌드 검증

## 파일 목록

| 파일 | 변경 유형 | Step |
|------|---------|------|
| `front_end/src/store/tgipStore.js` | 수정 (1줄) | Step 1 |
| `front_end/src/components/tgip/Workspace/ObservationCanvas.jsx` | 수정 | Step 2 |
| `front_end/src/pages/tgip/Library.jsx` | 수정 | Step 3 |

---
Created: 2026-03-05
Feature: tgip-final-fix
Phase: Design
