# Design: tgip-code-fixes

> Plan 참조: `docs/01-plan/features/tgip-code-fixes.plan.md`
> 코드 리뷰 결과(78/100) Critical 3건 + Major 4건 수정 설계

---

## Step 1 — `src/constants/tgip.js` 생성 (M2)

DEMO_TECHS를 TGIPWorkspace.jsx에서 분리하여 중앙 상수 모듈로 관리한다.

```js
// src/constants/tgip.js
export const DEMO_TECHS = {
  'solid-state-battery': {
    id: 'solid-state-battery',
    name: 'Solid State Battery',
    description: '전고체 배터리 기술',
    patent_count: 4821,
  },
  'perovskite-solar': {
    id: 'perovskite-solar',
    name: 'Perovskite Solar Cell',
    description: '페로브스카이트 태양전지',
    patent_count: 3204,
  },
};

export const DEFAULT_TECH_PATH = '/app/tech/solid-state-battery';
```

`DEFAULT_TECH_PATH`도 함께 export하여 Library.jsx, EmptyState에서 하드코딩 제거에 사용한다.

---

## Step 2 — `src/store/tgipStore.js` 수정 (C3)

catch 블록에서 DEV/PROD 환경 분기를 적용한다.

**변경 전** (lines 185-194):
```js
} catch {
  const mockRunId = `mock-run-${Date.now()}`;
  set({
    analysisRunId: mockRunId,
    results: MOCK_RESULTS,
    evidence: MOCK_EVIDENCE,
    isRunning: false,
    evidenceDrawerOpen: true,
  });
}
```

**변경 후**:
```js
} catch (err) {
  if (import.meta.env.DEV) {
    // 개발 환경에서만 Mock 데이터로 fallback
    const mockRunId = `mock-run-${Date.now()}`;
    set({
      analysisRunId: mockRunId,
      results: MOCK_RESULTS,
      evidence: MOCK_EVIDENCE,
      isRunning: false,
      evidenceDrawerOpen: true,
    });
  } else {
    // 프로덕션: 에러 상태로 전환
    set({
      isRunning: false,
      error: '분석 서버에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요.',
    });
  }
}
```

에러 상태는 이미 store에 `error: null`로 초기화되어 있으므로 추가 상태 정의 불필요.
RunController.jsx 등 에러 표시 UI는 이미 error prop을 받을 수 있는 구조인지 확인 후
필요 시 간단한 inline 에러 배너를 ObservationCanvas 또는 TGIPWorkspace에서 렌더링.

---

## Step 3 — `src/components/tgip/shared/PDFExporter.jsx` 수정 (C1+C2)

**변경 전**:
```js
export const usePDFExport = () => {
  const exportToPDF = async ({ targetRef, fileName }) => {
    if (!targetRef?.current) return;
    const [{ default: html2canvas }, { jsPDF }] = await Promise.all([...]);
    const canvas = await html2canvas(targetRef.current, {
      scale: 2, useCORS: true, backgroundColor: '#f8fafc', logging: false,
    });
    // ...
    pdf.save(fileName);
  };
  return { exportToPDF };
};
```

**변경 후**:
```js
export const usePDFExport = () => {
  const exportToPDF = async ({ targetRef, fileName, onError }) => {
    if (!targetRef?.current) return;
    try {
      const [{ default: html2canvas }, { jsPDF }] = await Promise.all([
        import('html2canvas'),
        import('jspdf'),
      ]);

      // C2: DOM 크기에 따라 scale 자동 조절 (메모리 안전화)
      const el = targetRef.current;
      const area = el.offsetWidth * el.offsetHeight;
      const scale = area > 1_000_000 ? 1 : 2;  // 1M px 초과 시 scale=1

      const canvas = await html2canvas(el, {
        scale,
        useCORS: true,
        backgroundColor: '#f8fafc',
        logging: false,
      });

      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' });

      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();
      const imgRatio = canvas.height / canvas.width;
      const imgHeight = pageWidth * imgRatio;

      pdf.addImage(imgData, 'PNG', 0, 0, pageWidth, Math.min(imgHeight, pageHeight - 16));
      pdf.setFontSize(7);
      pdf.setTextColor(160);
      pdf.text(
        'This system provides observational signals with evidence. It does not prescribe investment or strategic actions.',
        10,
        pageHeight - 6
      );
      pdf.save(fileName);
    } catch (err) {
      console.error('[PDFExporter] Export failed:', err);
      onError?.(err);  // 콜백 옵션으로 호출자에게 전달
    }
  };

  return { exportToPDF };
};
```

**TGIPWorkspace.jsx의 handleExport도 수정**:
```js
const handleExport = () => {
  const fileName = `tgip-${selectedTechnology?.id || 'unknown'}-${selectedView}-${analysisRunId || 'draft'}.pdf`;
  exportToPDF({
    targetRef: canvasRef,
    fileName,
    onError: () => alert('PDF 내보내기에 실패했습니다. 다시 시도해 주세요.'),
  });
};
```

> 토스트 라이브러리가 없으므로 `alert()`로 최소 피드백 제공. 별도 toast 시스템 추가는 YAGNI.

---

## Step 4 — `src/pages/tgip/Library.jsx` 수정 (M1 + M2)

**M2**: `DEFAULT_TECH_PATH` import로 하드코딩 제거
**M1**: error state + ErrorState 컴포넌트 추가

```jsx
import { DEFAULT_TECH_PATH } from '../../constants/tgip';

// 추가 state
const [error, setError] = useState(null);

// useEffect 변경
useEffect(() => {
  tgipApi.getLibrary()
    .then((res) => setRuns(res.data?.runs || []))
    .catch((err) => {
      console.error('[Library] Failed to load runs:', err);
      setError(err);
    })
    .finally(() => setLoading(false));
}, []);
```

**ErrorState 컴포넌트** (Library.jsx 내 정의):
```jsx
const ErrorState = ({ onRetry }) => (
  <div className="text-center py-20 text-slate-400">
    <div className="text-4xl mb-4">⚠️</div>
    <p className="text-lg font-medium text-slate-600">불러오기 실패</p>
    <p className="text-sm mt-1 mb-6">분석 기록을 가져올 수 없습니다.</p>
    <button
      onClick={onRetry}
      className="inline-block px-6 py-2 bg-violet-600 text-white rounded-lg text-sm font-semibold hover:bg-violet-700 transition-colors"
    >
      다시 시도
    </button>
  </div>
);
```

**렌더 조건 변경**:
```jsx
{loading ? (
  <LoadingSpinner />
) : error ? (
  <ErrorState onRetry={() => { setError(null); setLoading(true); /* retrigger */ }} />
) : runs.length === 0 ? (
  <EmptyState />
) : (
  <RunList runs={runs} />
)}
```

**재시도 구현**: `retryCount` state를 추가하여 useEffect 의존성에 포함, 재시도 시 increment.

```jsx
const [retryCount, setRetryCount] = useState(0);

useEffect(() => {
  setLoading(true);
  setError(null);
  tgipApi.getLibrary()
    .then((res) => setRuns(res.data?.runs || []))
    .catch((err) => { console.error(...); setError(err); })
    .finally(() => setLoading(false));
}, [retryCount]);

// ErrorState onRetry
<ErrorState onRetry={() => setRetryCount((c) => c + 1)} />
```

**EmptyState의 하드코딩 URL도 수정**:
```jsx
<Link to={DEFAULT_TECH_PATH} ...>Open Workspace →</Link>
```

---

## Step 5 — `src/pages/tgip/TGIPWorkspace.jsx` 수정 (M2 + M3)

**M2**: DEMO_TECHS import
```js
import { DEMO_TECHS } from '../../constants/tgip';
// const DEMO_TECHS = { ... } 줄 삭제
```

**M3**: useEffect 의존성 최소화

현재 코드:
```js
useEffect(() => {
  if (technology_id && (!selectedTechnology || selectedTechnology.id !== technology_id)) {
    const tech = DEMO_TECHS[technology_id] ?? { ... };
    setTechnology(tech);
  }
}, [technology_id, selectedTechnology, setTechnology]);
```

문제: `selectedTechnology`가 의존성에 있어 setTechnology 호출 후 재실행됨
(조건 분기로 infinite loop는 방지되나 ESLint 경고 + 불필요한 effect 재평가)

수정 방안 — `useRef`로 이전 ID 추적:
```js
const prevTechIdRef = useRef(null);

useEffect(() => {
  if (technology_id && prevTechIdRef.current !== technology_id) {
    prevTechIdRef.current = technology_id;
    const tech = DEMO_TECHS[technology_id] ?? {
      id: technology_id,
      name: technology_id.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
      description: '',
      patent_count: null,
    };
    setTechnology(tech);
  }
}, [technology_id, setTechnology]);
```

`selectedTechnology`를 의존성에서 제거하고 `prevTechIdRef`로 중복 실행 방지.
`setTechnology`는 Zustand stable ref이므로 ESLint `react-hooks/exhaustive-deps` 통과.

**C3 에러 표시** (PROD에서 store.error 표시):
TGIPWorkspace에서 `error` state를 store에서 읽어 인라인 배너 표시:
```jsx
const { ..., error } = useTGIPStore();
// ...
{error && (
  <div className="px-6 py-2 bg-red-50 border-t border-red-200 text-sm text-red-700">
    {error}
  </div>
)}
```

---

## Step 6 — `src/components/tgip/Workspace/ObservationCanvas.jsx` 수정 (M4)

모든 렌더 경로에 `ref={ref}` 연결.

**변경 전** (loading/empty 상태에 ref 없음):
```jsx
if (isRunning) return (
  <main className="flex-1 overflow-auto bg-slate-50">
    <LoadingOverlay />
  </main>
);

if (!hasAnyResult) return (
  <main className="flex-1 overflow-auto bg-slate-50">
    <EmptyState technology={selectedTechnology} />
  </main>
);

return (
  <main ref={ref} className="flex-1 overflow-auto bg-slate-50 p-6">
    ...
  </main>
);
```

**변경 후** — 단일 `<main>` 렌더 패턴으로 통합:
```jsx
return (
  <main ref={ref} className="flex-1 overflow-auto bg-slate-50">
    {isRunning ? (
      <LoadingOverlay />
    ) : !hasAnyResult ? (
      <EmptyState technology={selectedTechnology} />
    ) : (
      <div className="p-6 h-full">
        <AnimatePresence mode="wait">
          <motion.div
            key={selectedView}
            variants={viewVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            className="h-full"
          >
            <Suspense fallback={<ViewLoader />}>
              {selectedView === 'RTS' && <RTSView data={results.RTS} />}
              {selectedView === 'TPI' && <TPIView data={results.TPI} />}
              {selectedView === 'FSS' && <FSSView data={results.FSS} />}
              {selectedView === 'WSD' && <WSDView data={results.WSD} />}
            </Suspense>
          </motion.div>
        </AnimatePresence>
      </div>
    )}
  </main>
);
```

`innerRef` 및 `const ref = canvasRef || innerRef` 패턴 제거 (항상 prop으로 받으므로).
`innerRef` fallback은 유지하되 불필요한 경우 제거 검토.

---

## 구현 순서 요약

| 순서 | 파일 | 이슈 | 변경 내용 |
|------|------|------|-----------|
| 1 | `constants/tgip.js` (신규) | M2 | DEMO_TECHS, DEFAULT_TECH_PATH export |
| 2 | `store/tgipStore.js` | C3 | DEV/PROD 분기 |
| 3 | `components/tgip/shared/PDFExporter.jsx` | C1+C2 | try/catch + scale 안전화 |
| 4 | `pages/tgip/Library.jsx` | M1+M2 | ErrorState + retryCount + DEFAULT_TECH_PATH |
| 5 | `pages/tgip/TGIPWorkspace.jsx` | M2+M3+C3 | constants import + useRef 패턴 + error 배너 |
| 6 | `components/tgip/Workspace/ObservationCanvas.jsx` | M4 | 단일 main 패턴 |

## 검증 기준

| 항목 | 검증 방법 |
|------|-----------|
| C1: PDF 에러 피드백 | export 중 강제 에러 → alert 확인 |
| C2: scale 조절 | 대용량 DOM에서 scale=1 적용 확인 |
| C3: PROD mock 차단 | `import.meta.env.DEV=false` 환경에서 error state 표시 |
| M1: Library 에러 UI | API 실패 시 ErrorState + 재시도 버튼 |
| M2: 상수 중앙화 | constants/tgip.js에서 DEMO_TECHS 참조 |
| M3: ESLint 경고 없음 | `npm run lint` 통과 |
| M4: ref 연결 | loading/empty 상태에서도 main에 ref 연결 |
| 빌드 | `npm run build` 경고 0개 |
