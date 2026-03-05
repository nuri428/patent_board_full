# Design: tgip-minor-fixes

> Plan 참조: `docs/01-plan/features/tgip-minor-fixes.plan.md`
> 코드 리뷰(91/100) Minor 5건 수정 설계

---

## Step 1 — `src/mocks/tgipMockData.js` 생성 + `tgipStore.js` 수정 (m1)

### 1-a. `src/mocks/tgipMockData.js` 신규

`tgipStore.js`의 MOCK_EVIDENCE, MOCK_RESULTS를 외부 파일로 분리.

```js
// src/mocks/tgipMockData.js
export const MOCK_EVIDENCE = { ... };  // 현행 그대로 이동
export const MOCK_RESULTS = { ... };   // 현행 그대로 이동
```

### 1-b. `tgipStore.js` 수정

파일 상단 mock 데이터 블록 제거, 조건부 import로 교체.

**변경 전** (lines 1-118):
```js
import { create } from 'zustand';

const MOCK_EVIDENCE = { ... };  // 24줄
const MOCK_RESULTS = { ... };   // 94줄
```

**변경 후**:
```js
import { create } from 'zustand';

// Mock 데이터: DEV 환경에서만 사용 (프로덕션 번들 제외)
let MOCK_EVIDENCE = null;
let MOCK_RESULTS = null;
if (import.meta.env.DEV) {
  const mocks = await import('../mocks/tgipMockData.js');
  MOCK_EVIDENCE = mocks.MOCK_EVIDENCE;
  MOCK_RESULTS = mocks.MOCK_RESULTS;
}
```

> **주의**: Zustand store 파일은 모듈 최상위에서 `await`를 사용할 수 없음(ESM top-level await는 Vite에서 지원하나 store 파일의 패턴에 따라 다름).
> 안전한 대안: 정적 조건부 import 대신 catch 블록 내부에서만 dynamic import 유지.

**실제 구현 방안**: catch 블록 내부에서 dynamic import (현행 패턴 유지하되 파일 분리만 적용):

```js
import { create } from 'zustand';
// store 파일 상단에는 import 선언 없음 — catch 블록에서만 참조

// ...store 정의...
    } catch (err) {
      if (import.meta.env.DEV) {
        const { MOCK_EVIDENCE, MOCK_RESULTS } = await import('../mocks/tgipMockData.js');
        const mockRunId = `mock-run-${Date.now()}`;
        set({ analysisRunId: mockRunId, results: MOCK_RESULTS, evidence: MOCK_EVIDENCE,
              isRunning: false, evidenceDrawerOpen: true });
      } else {
        console.error('[tgipStore] Analysis failed:', err);
        set({ isRunning: false, error: '분석 서버에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요.' });
      }
    }
```

이렇게 하면 `runAnalysis`가 `async` 함수이므로 내부 `await import()`가 유효하고,
프로덕션 번들에서 `tgipMockData.js`는 DEV 조건으로 인해 tree-shake된다.

---

## Step 2 — `src/components/tgip/shared/PDFExporter.jsx` 수정 (m3)

Magic number `1_000_000`을 명명된 상수로 추출.

**변경 전**:
```js
const scale = area > 1_000_000 ? 1 : 2;
```

**변경 후**:
```js
// 1,000,000 px²(약 1000×1000) 초과 시 메모리 절약을 위해 scale=1 사용
const HIGH_RES_AREA_THRESHOLD = 1_000_000;
const scale = area > HIGH_RES_AREA_THRESHOLD ? 1 : 2;
```

상수는 `exportToPDF` 함수 내부 상단에 선언 (파일 스코프에 둘 만큼 재사용되지 않음).

---

## Step 3 — `src/api/tgip.js` 수정 (m2 선행 작업)

AbortController signal을 전달하려면 `getLibrary`가 options를 받아야 함.
axios는 config 객체의 `signal` 필드를 네이티브 지원 (axios 0.22+).

**변경 전**:
```js
getLibrary: () =>
  axiosInstance.get('/tgip/library'),
```

**변경 후**:
```js
getLibrary: (options = {}) =>
  axiosInstance.get('/tgip/library', options),
```

---

## Step 4 — `src/pages/tgip/Library.jsx` 수정 (m2)

useEffect에 AbortController cleanup 추가.

**변경 전**:
```js
useEffect(() => {
  setLoading(true);
  setError(null);
  tgipApi.getLibrary()
    .then((res) => setRuns(res.data?.runs || []))
    .catch((err) => { console.error(...); setError(err); })
    .finally(() => setLoading(false));
}, [retryCount]);
```

**변경 후**:
```js
useEffect(() => {
  const controller = new AbortController();
  setLoading(true);
  setError(null);

  tgipApi.getLibrary({ signal: controller.signal })
    .then((res) => setRuns(res.data?.runs || []))
    .catch((err) => {
      if (err.name !== 'CanceledError') {
        console.error('[Library] Failed to load runs:', err);
        setError(err);
      }
    })
    .finally(() => setLoading(false));

  return () => controller.abort();
}, [retryCount]);
```

`CanceledError` 체크: abort 시 axios가 던지는 에러를 error state로 처리하지 않음.

---

## Step 5 — `src/components/tgip/Workspace/ObservationCanvas.jsx` 수정 (m4)

4-branch if 체인을 VIEW_COMPONENTS 레지스트리 패턴으로 교체.

**변경 전**:
```jsx
{selectedView === 'RTS' && <RTSView data={results.RTS} />}
{selectedView === 'TPI' && <TPIView data={results.TPI} />}
{selectedView === 'FSS' && <FSSView data={results.FSS} />}
{selectedView === 'WSD' && <WSDView data={results.WSD} />}
```

**변경 후**:
```js
// 파일 상단 (lazy import 바로 아래)
const VIEW_COMPONENTS = {
  RTS: RTSView,
  TPI: TPIView,
  FSS: FSSView,
  WSD: WSDView,
};
```

```jsx
// JSX 내부
const ViewComponent = VIEW_COMPONENTS[selectedView];
// ...
<Suspense fallback={<ViewLoader />}>
  {ViewComponent && <ViewComponent data={results[selectedView]} />}
</Suspense>
```

새 view 추가 시 `VIEW_COMPONENTS`에 1줄만 추가하면 됨.

---

## Step 6 — `src/pages/tgip/TGIPWorkspace.jsx` 수정 (m5)

`alert()` 제거 → `exportError` state + 자동 해제 배너.

**변경 전**:
```js
const handleExport = () => {
  const fileName = ...;
  exportToPDF({
    targetRef: canvasRef,
    fileName,
    onError: () => alert('PDF 내보내기에 실패했습니다. 다시 시도해 주세요.'),
  });
};
```

**변경 후**:
```js
const [exportError, setExportError] = useState(null);

const handleExport = () => {
  const fileName = ...;
  exportToPDF({
    targetRef: canvasRef,
    fileName,
    onError: () => {
      setExportError('PDF 내보내기에 실패했습니다. 다시 시도해 주세요.');
      setTimeout(() => setExportError(null), 4000);  // 4초 후 자동 해제
    },
  });
};
```

**에러 배너 JSX** (기존 error 배너 아래 추가):
```jsx
{exportError && (
  <div className="px-6 py-2 bg-amber-50 border-t border-amber-200 text-sm text-amber-700 flex items-center justify-between">
    <span>{exportError}</span>
    <button onClick={() => setExportError(null)} className="ml-4 text-amber-500 hover:text-amber-700">✕</button>
  </div>
)}
```

amber(노란) 색상으로 API 에러(red)와 구분.

---

## 구현 순서 요약

| 순서 | 파일 | 이슈 | 변경 내용 |
|------|------|------|-----------|
| 1 | `src/mocks/tgipMockData.js` (신규) | m1 | MOCK_EVIDENCE + MOCK_RESULTS 이동 |
| 2 | `src/store/tgipStore.js` | m1 | dynamic import로 교체, 상단 mock 블록 제거 |
| 3 | `src/components/tgip/shared/PDFExporter.jsx` | m3 | HIGH_RES_AREA_THRESHOLD 상수화 |
| 4 | `src/api/tgip.js` | m2 선행 | getLibrary(options) 시그니처 추가 |
| 5 | `src/pages/tgip/Library.jsx` | m2 | AbortController cleanup |
| 6 | `src/components/tgip/Workspace/ObservationCanvas.jsx` | m4 | VIEW_COMPONENTS 레지스트리 |
| 7 | `src/pages/tgip/TGIPWorkspace.jsx` | m5 | exportError state + amber 배너 |

## 검증 기준

| 항목 | 검증 방법 |
|------|-----------|
| m1: mock 분리 | tgipStore.js < 100줄, mocks/tgipMockData.js 파일 존재 |
| m2: cleanup | React DevTools에서 unmount 시 abort 호출 확인 |
| m3: 상수화 | PDFExporter에 HIGH_RES_AREA_THRESHOLD 선언 확인 |
| m4: view map | VIEW_COMPONENTS 레지스트리 + ViewComponent 패턴 사용 |
| m5: alert 제거 | 코드에 alert() 없음, exportError 배너 렌더 |
| 빌드 | `npm run build` 경고 0개 |
