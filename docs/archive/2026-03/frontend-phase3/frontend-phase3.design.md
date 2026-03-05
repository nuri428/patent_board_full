# [Design] frontend-phase3 — TGIP 완성도 (성능·랜딩·트랜지션·Library·PDF)

> **작성일**: 2026-03-05
> **상태**: Design
> **버전**: v1.0
> **연속성**: frontend-phase2 (완료, 95%) → **frontend-phase3** (현재)

---

## 1. 현재 파일 상태 (Phase 3 진입 기준)

### 수정 대상 파일

| 파일 | 현재 상태 | Phase 3 변경 |
|------|-----------|--------------|
| `vite.config.js` | `plugins: [react()]` 만 존재, manualChunks 없음 | `build.rollupOptions.output.manualChunks` 추가 |
| `ObservationCanvas.jsx` | 4개 뷰 static import, framer-motion 미사용 | lazy import + AnimatePresence 전환 |
| `TGIPHeader.jsx` | Download 버튼 `disabled`, Library 링크 없음 | Export 버튼 활성화, Library 링크 추가 |
| `App.jsx` | 루트 `/` → `LandingPage` (미인증), Library 라우트 없음 | 루트 → `TGIPLanding`, `/app/library` 라우트 추가 |

### 신규 생성 파일

| 파일 | 역할 |
|------|------|
| `pages/tgip/TGIPLanding.jsx` | TGIP 랜딩 페이지 (Hero + 카드 + CTA) |
| `pages/tgip/Library.jsx` | 저장된 실행 목록 페이지 |
| `components/tgip/shared/PDFExporter.jsx` | PDF 내보내기 커스텀 훅 |

---

## 2. Step 1 — 성능 최적화

### 2.1 vite.config.js 변경 설계

**파일**: `front_end/vite.config.js`

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const apiProxyTarget = process.env.VITE_API_PROXY_TARGET || 'http://localhost:8005';

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'chart-vendor': ['chart.js', 'react-chartjs-2'],
          'flow-vendor': ['@xyflow/react'],
          'map-vendor': ['react-simple-maps'],
          'motion-vendor': ['framer-motion'],
        },
      },
    },
  },
  server: {
    // (기존 server 설정 그대로 유지)
  },
})
```

> **주의**: `tgip-views` 청크는 lazy() 사용 시 Rollup이 자동으로 분리하므로 manualChunks에 명시 불필요.
> `react-simple-maps`는 D3 의존성 포함으로 ~300 KB 예상 → 별도 청크 필수.

### 2.2 ObservationCanvas.jsx — lazy loading 설계

**파일**: `front_end/src/components/tgip/Workspace/ObservationCanvas.jsx`

변경 전 (static import):
```javascript
import RTSView from '../views/RTSView/RTSView';
import TPIView from '../views/TPIView/TPIView';
import FSSView from '../views/FSSView/FSSView';
import WSDView from '../views/WSDView/WSDView';
```

변경 후 (lazy import):
```javascript
import { lazy, Suspense } from 'react';

const RTSView = lazy(() => import('../views/RTSView/RTSView'));
const TPIView = lazy(() => import('../views/TPIView/TPIView'));
const FSSView = lazy(() => import('../views/FSSView/FSSView'));
const WSDView = lazy(() => import('../views/WSDView/WSDView'));
```

`Suspense` fallback 컴포넌트 (뷰 전환 중 표시):
```jsx
const ViewLoader = () => (
  <div className="flex items-center justify-center h-full text-slate-400">
    <div className="w-8 h-8 border-2 border-violet-200 border-t-violet-500 rounded-full animate-spin" />
  </div>
);
```

뷰 렌더링 영역을 `<Suspense fallback={<ViewLoader />}>` 로 감쌈.

---

## 3. Step 2 — 뷰 전환 트랜지션

### 3.1 AnimatePresence + motion.div 설계

**파일**: `front_end/src/components/tgip/Workspace/ObservationCanvas.jsx` (Step 1과 동일 파일)

`framer-motion`은 이미 설치됨 (`package.json` 확인됨). import 추가:
```javascript
import { AnimatePresence, motion } from 'framer-motion';
```

뷰 컴포넌트를 `AnimatePresence mode="wait"` 로 감싸고, `motion.div`로 개별 뷰를 래핑:

```jsx
const viewVariants = {
  initial: { opacity: 0, y: 6 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.18 } },
  exit:    { opacity: 0, y: -6, transition: { duration: 0.12 } },
};

// 렌더링 영역
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
```

**설계 원칙**:
- `mode="wait"`: exit 완료 후 enter 시작 (겹침 없음)
- `key={selectedView}`: 뷰 변경 시 AnimatePresence가 exit/enter 트리거
- `y` 이동: 6px (미세한 슬라이드) — 무거운 애니메이션 지양
- GPU 가속: `transform: translateY` 사용 (opacity + transform = compositor layer)

---

## 4. Step 3 — TGIPLanding 페이지

### 4.1 파일 경로 및 구조

**파일**: `front_end/src/pages/tgip/TGIPLanding.jsx`

### 4.2 섹션 구성

```
┌──────────────────────────────────────────────┐
│ Hero Section                                  │
│  배경: 짙은 slate 그라데이션 (slate-950 → slate-800) │
│  H1: "Observe Technology. Not Prescribe."     │
│  부제: "TGIP analyzes patent signals..."      │
│  CTA: [Open Workspace →]  [Learn More]        │
└──────────────────────────────────────────────┘
│ 4-View Cards (2×2 그리드, max-w-5xl centered) │
│  RTS: violet  | TPI: cyan                    │
│  FSS: red     | WSD: emerald                 │
│  각 카드: 뷰 이름 + 한 줄 설명 + 아이콘       │
└──────────────────────────────────────────────┘
│ Trust Section                                 │
│  3개 원칙 카드: Evidence-Based / Non-Prescriptive / Transparent │
└──────────────────────────────────────────────┘
│ CTA Footer                                    │
│  [Try the Workspace] [View Docs]              │
└──────────────────────────────────────────────┘
```

### 4.3 컴포넌트 스펙

```jsx
// Hero: 다크 배경, 중앙 정렬, 풀 뷰포트 높이 (min-h-screen)
<section className="min-h-screen bg-gradient-to-br from-slate-950 to-slate-800 flex flex-col items-center justify-center text-white">

// 4-View 카드: 각 카드는 뷰 색상 테마 적용
const VIEW_CARDS = [
  { id: 'RTS', name: 'RTS', title: 'Structural Maturity', desc: '...', color: 'border-violet-500 bg-violet-50', icon: '🔬' },
  { id: 'TPI', name: 'TPI', title: 'Propagation Dynamics', desc: '...', color: 'border-cyan-500 bg-cyan-50', icon: '🌐' },
  { id: 'FSS', name: 'FSS', title: 'Strategic Pressure', desc: '...', color: 'border-red-500 bg-red-50', icon: '🗺️' },
  { id: 'WSD', name: 'WSD', title: 'Opportunity Field', desc: '...', color: 'border-emerald-500 bg-emerald-50', icon: '💡' },
];
```

### 4.4 App.jsx 변경 — 루트 교체

```jsx
// 변경 전 (미인증 분기)
<Route path="/" element={<LandingPage />} />

// 변경 후
import TGIPLanding from './pages/tgip/TGIPLanding';
// ...
<Route path="/" element={<TGIPLanding />} />
```

> **보존**: `/login`, `/chat`, 인증 후 `/` → `/chat` redirect 플로우 유지.
> `LandingPage` import는 더 이상 사용되지 않으면 제거 (App.jsx에서만 사용됨).

---

## 5. Step 4 — Library 페이지

### 5.1 파일 경로

**파일**: `front_end/src/pages/tgip/Library.jsx`

### 5.2 API 연동

`GET /api/v1/tgip/library` — Phase 2에서 이미 구현됨.

`tgip.js` API 클라이언트에 `getLibrary()` 추가:
```javascript
// front_end/src/api/tgip.js 에 추가
getLibrary: () => api.get('/tgip/library'),
```

### 5.3 컴포넌트 설계

```jsx
const Library = () => {
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    tgipApi.getLibrary()
      .then(res => setRuns(res.data.runs || []))
      .catch(() => setRuns([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-4xl mx-auto p-8">
      <h1>My Analysis Library</h1>
      {loading ? <Spinner /> : runs.length === 0 ? <EmptyState /> : <RunList runs={runs} />}
    </div>
  );
};
```

**RunCard 구조**:
```
┌────────────────────────────────────────────┐
│  기술명 (technology_id)     날짜           │
│  Run ID: mock-run-xxx...    [View →]        │
└────────────────────────────────────────────┘
```

### 5.4 App.jsx — `/app/library` 라우트 추가

```jsx
import Library from './pages/tgip/Library';
// TGIPAppLayout 하위에 추가:
<Route path="/app/library" element={<Library />} />
```

### 5.5 TGIPHeader.jsx — Library 링크 추가

```jsx
import { Link } from 'react-router-dom';
import { BookOpen } from 'lucide-react';

// Export 버튼 앞에 추가:
<Link to="/app/library" className="p-2 rounded-lg text-slate-500 hover:text-slate-700 hover:bg-slate-100 transition-colors" title="Library">
  <BookOpen size={16} />
</Link>
```

---

## 6. Step 5 — PDF 내보내기

### 6.1 의존성 설치

```bash
npm install html2canvas jspdf --legacy-peer-deps
```

### 6.2 PDFExporter.jsx 설계

**파일**: `front_end/src/components/tgip/shared/PDFExporter.jsx`

커스텀 훅 패턴:

```javascript
import html2canvas from 'html2canvas';
import { jsPDF } from 'jspdf';

export const usePDFExport = () => {
  const exportToPDF = async ({ targetRef, fileName }) => {
    if (!targetRef?.current) return;

    const canvas = await html2canvas(targetRef.current, {
      scale: 2,
      useCORS: true,
      backgroundColor: '#f8fafc',
    });

    const imgData = canvas.toDataURL('image/png');
    const pdf = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' });

    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();
    const imgRatio = canvas.height / canvas.width;
    const imgHeight = pageWidth * imgRatio;

    pdf.addImage(imgData, 'PNG', 0, 0, pageWidth, Math.min(imgHeight, pageHeight - 20));

    // 면책 고지
    pdf.setFontSize(8);
    pdf.setTextColor(150);
    pdf.text(
      'This system provides observational signals with evidence. It does not prescribe investment or strategic actions.',
      10,
      pageHeight - 8
    );

    pdf.save(fileName);
  };

  return { exportToPDF };
};
```

### 6.3 TGIPHeader.jsx — Export 버튼 활성화

```jsx
import { useRef } from 'react';
import { usePDFExport } from '../shared/PDFExporter';
import { useTGIPStore } from '../../../store/tgipStore';

const TGIPHeader = () => {
  const { selectedView, selectedTechnology, analysisRunId, results } = useTGIPStore();
  const canvasRef = useRef(null);
  const { exportToPDF } = usePDFExport();

  const hasResult = !!results?.[selectedView];

  const handleExport = () => {
    const fileName = `tgip-${selectedTechnology?.id || 'unknown'}-${selectedView}-${analysisRunId || 'draft'}.pdf`;
    exportToPDF({ targetRef: canvasRef, fileName });
  };

  // Export 버튼:
  <button
    onClick={handleExport}
    disabled={!hasResult}
    className={`p-2 rounded-lg transition-colors ${hasResult ? 'text-slate-600 hover:bg-slate-100' : 'text-slate-300 cursor-not-allowed'}`}
    title="Export to PDF"
  >
    <Download size={16} />
  </button>
};
```

> **구현 메모**: `canvasRef`는 `ObservationCanvas`의 `<main>` 요소에 전달해야 함.
> `TGIPHeader`와 `ObservationCanvas`가 형제 컴포넌트이므로 Zustand store에 `canvasRef`를 저장하거나,
> `TGIPWorkspace.jsx` 에서 ref를 생성 후 두 컴포넌트에 prop으로 전달하는 방식 중 선택.
> → **권장: TGIPWorkspace에서 ref 생성 + prop drilling** (단순, 컴포넌트 수 적음)

---

## 7. Step 6 — 기술 부채 해소

### 7.1 loadingView 활용 (ObservationCanvas.jsx)

`tgipStore.js`에 `loadingView` 상태가 이미 존재하지만 미활용.
현재 `isRunning`이 전체 로딩을 커버하므로 Phase 3에서는 `loadingView` 활용 대신
**기존 `LoadingOverlay`에 현재 처리 중인 뷰 이름 표시**로 단순화:

```jsx
// ObservationCanvas.jsx의 LoadingOverlay 강화
const LoadingOverlay = () => (
  <div className="flex flex-col items-center justify-center h-full gap-4 text-slate-500">
    {/* 기존 스피너 유지 */}
    <div className="text-center">
      <p className="font-medium">Running analysis...</p>
      <p className="text-sm text-slate-400 mt-1">Computing RTS · TPI · FSS · WSD signals</p>
    </div>
  </div>
);
```

> `loadingView` 뷰별 세분화는 백엔드 streaming 구현 후 적용 예정 (Phase 4+).

### 7.2 DisclaimerBanner 위치

각 뷰(RTSView, TPIView, FSSView, WSDView)의 최하단에 `DisclaimerBanner` 추가.

이미 `DisclaimerBanner`가 존재하는지 확인 후 없으면 인라인 구현:

```jsx
// 각 뷰 컴포넌트 최하단
<div className="mt-6 p-3 bg-slate-50 border border-slate-200 rounded-lg">
  <p className="text-xs text-slate-400 text-center">
    This system provides observational signals with evidence. It does not prescribe investment or strategic actions.
  </p>
</div>
```

---

## 8. 변경 파일 상세 요약

### 수정 파일

| 파일 | 변경 내용 | Step |
|------|-----------|------|
| `front_end/vite.config.js` | `build.rollupOptions.output.manualChunks` 5개 청크 추가 | 1 |
| `front_end/src/components/tgip/Workspace/ObservationCanvas.jsx` | lazy import + AnimatePresence + ViewLoader | 1, 2 |
| `front_end/src/components/tgip/Layout/TGIPHeader.jsx` | Export 버튼 활성화 + Library 링크 | 4, 5 |
| `front_end/src/App.jsx` | 루트 → TGIPLanding + `/app/library` 라우트 추가 | 3, 4 |
| `front_end/src/api/tgip.js` | `getLibrary()` 메서드 추가 | 4 |
| `front_end/src/pages/tgip/TGIPWorkspace.jsx` | `canvasRef` 생성 + ObservationCanvas에 전달 | 5 |

### 신규 파일

| 파일 | Step |
|------|------|
| `front_end/src/pages/tgip/TGIPLanding.jsx` | 3 |
| `front_end/src/pages/tgip/Library.jsx` | 4 |
| `front_end/src/components/tgip/shared/PDFExporter.jsx` | 5 |

---

## 9. 구현 순서

```
Step 1: vite.config.js manualChunks
  → ObservationCanvas lazy import + ViewLoader
  → 빌드 확인 (메인 청크 크기 감소 확인)

Step 2: ObservationCanvas AnimatePresence 추가
  → (Step 1과 동일 파일, Step 1 완료 후 바로 추가)

Step 3: TGIPLanding.jsx 신규 생성
  → App.jsx 루트 교체

Step 4: Library.jsx 신규 생성
  → tgip.js getLibrary() 추가
  → App.jsx 라우트 추가
  → TGIPHeader.jsx Library 링크 추가

Step 5: npm install html2canvas jspdf --legacy-peer-deps
  → PDFExporter.jsx 신규 생성
  → TGIPWorkspace.jsx canvasRef 추가
  → ObservationCanvas canvasRef prop 수신
  → TGIPHeader.jsx Export 버튼 활성화

Step 6: 각 뷰 하단 DisclaimerBanner 추가
  (RTSView, TPIView, FSSView, WSDView)
```

---

## 10. 성공 지표 (Design 기준)

| 지표 | 설계 목표 |
|------|-----------|
| 메인 청크 | 500 KB 이하 (현재 1,097 KB) |
| map-vendor 청크 | ~300 KB (react-simple-maps + D3) |
| 뷰 전환 | selectedView 변경 시 fade 0.18s + exit 0.12s |
| TGIPLanding | `LandingPage` 완전 대체, `/login` 유지 |
| Library | `/app/library` 접속 시 실행 목록 또는 빈 상태 |
| PDF | 분석 결과 존재 시 Export 버튼 활성화, 클릭 시 PDF 다운로드 |
| DisclaimerBanner | 4개 뷰 모두 최하단에 면책 고지 표시 |
