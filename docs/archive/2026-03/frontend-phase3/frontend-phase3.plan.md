# [Plan] frontend-phase3 — TGIP 완성도 (랜딩·라이브러리·PDF·성능·트랜지션)

> **작성일**: 2026-03-05
> **상태**: Plan
> **버전**: v1.0
> **연속성**: `frontend` (Phase 1) → `frontend-phase2` (Phase 2, 완료) → **`frontend-phase3`** (Phase 3)
> **참고**: `memory/tgip-todo.md` § Phase 3, `docs/archive/2026-03/_INDEX.md`

---

## 1. Feature 개요

| 항목 | 내용 |
|------|------|
| Feature Name | frontend-phase3 |
| 제품명 | TGIP — Technology Geo-Intelligence Platform |
| 유형 | React SPA + 성능 최적화 |
| 목적 | Phase 1·2에서 남긴 기술 부채와 완성도 항목을 해소하여 TGIP를 프로덕션 수준으로 완성 |
| Phase 2 상태 | ✅ 완료 (Match Rate 95%, 아카이브됨) |

### 한 줄 요약

> `/` 루트를 TGIP 랜딩으로 교체하고, 번들 최적화·뷰 전환 애니메이션·Library 페이지·PDF 내보내기를 구현하여 TGIP의 완성도를 높인다.

---

## 2. 현재 상태 (Phase 2 완료 기준)

### 완료된 것

| 항목 | 상태 |
|------|------|
| RTSView, TPIView, FSSView, WSDView (4개 뷰) | ✅ |
| FastAPI TGIP 엔드포인트 4개 | ✅ |
| RunDetail 페이지 (`/app/runs/:run_id`) | ✅ |
| SidebarViewSelector 4개 뷰 활성화 | ✅ |
| `framer-motion` 설치됨 | ✅ (미활용) |

### Phase 3 진입 시 미해결 항목

| 항목 | 위치 | 영향 |
|------|------|------|
| TGIPLanding 미구현 | `/` 루트 | 기존 Patent Board LandingPage가 그대로 노출 |
| 번들 크기 경고 | 빌드 결과 | 1,097 KB (권장 500 KB 초과) |
| framer-motion 미활용 | ObservationCanvas | 뷰 전환 UX 낮음 |
| loadingView 미활용 | tgipStore.js | 뷰별 로딩 상태 표시 없음 |
| Library 페이지 없음 | `/app/library` | 저장된 실행 목록 접근 불가 |
| Export 버튼 disabled | TGIPHeader | PDF 내보내기 불가 |

---

## 3. 범위 정의 (Scope)

### In Scope — Phase 3

#### 3.1 성능 최적화 (최우선 — 빌드 경고 해소)

| 항목 | 내용 |
|------|------|
| Dynamic import (lazy loading) | 각 뷰 컴포넌트(`RTSView`, `TPIView`, `FSSView`, `WSDView`) lazy 처리 |
| Vite manualChunks | `vite.config.js`에 청크 분리 설정 추가 |
| 목표 번들 크기 | 메인 청크 500 KB 이하 (현재 1,097 KB) |
| Suspense fallback | 뷰 로딩 중 스피너 컴포넌트 |

**적용 파일**: `vite.config.js`, `ObservationCanvas.jsx`

#### 3.2 TGIPLanding 페이지

| 항목 | 내용 |
|------|------|
| 경로 | `/` (루트) — 기존 LandingPage 대체 |
| 파일 | `pages/tgip/TGIPLanding.jsx` |
| 섹션 구성 | Hero + 4-View 요약 카드 + CTA ("Open Workspace") |
| App.jsx 변경 | 미인증 시 `/` → `TGIPLanding` (기존 `LandingPage` 대체) |

> **주의**: 기존 Patent Board `/login`, `/chat` 등 라우트는 유지해야 함. 인증 후 `/chat`으로 이동하는 기존 플로우 보존.

#### 3.3 뷰 전환 트랜지션

| 항목 | 내용 |
|------|------|
| 라이브러리 | `framer-motion` (이미 설치됨) |
| 적용 위치 | `ObservationCanvas.jsx` — 뷰 전환 시 fade/slide |
| 애니메이션 | 현재 뷰 exit(fade-out) → 다음 뷰 enter(fade-in) |
| 성능 고려 | `AnimatePresence` + `motion.div`, GPU 가속 사용 |

#### 3.4 Library 페이지

| 항목 | 내용 |
|------|------|
| 경로 | `/app/library` |
| 파일 | `pages/tgip/Library.jsx` |
| 내용 | 저장된 실행 목록 (run_id + 기술명 + 날짜), 실행 상세 링크 |
| API | `GET /api/v1/tgip/library` (Phase 2에서 구현됨) |
| App.jsx | `/app/library` 라우트 추가 |
| TGIPHeader | Library 링크 버튼 추가 |

#### 3.5 PDF 내보내기

| 항목 | 내용 |
|------|------|
| 라이브러리 | `html2canvas` + `jspdf` (신규 설치) |
| 트리거 | TGIPHeader의 Export 버튼 활성화 |
| 대상 | 현재 선택된 뷰의 ObservationCanvas 캡처 |
| 파일명 | `tgip-{technology_id}-{view}-{run_id}.pdf` |
| 면책 고지 포함 | "This system provides observational signals with evidence." |

#### 3.6 기술 부채 해소

| 항목 | 파일 | 내용 |
|------|------|------|
| loadingView 활용 | `ObservationCanvas.jsx` | `loadingView` 상태로 뷰별 스켈레톤 표시 |
| DisclaimerBanner 위치 | 뷰 컴포넌트들 | 각 뷰 하단에 DisclaimerBanner 추가 |

### Out of Scope — 나중으로 이관

- Compare Mode (두 기술 동시 관찰) — 복잡도 높음, 별도 Feature로 분리
- 실제 DB 연동 (Neo4j, OpenSearch TGIP 데이터) — 별도 백엔드 Feature로 분리
- Settings 페이지 (`/app/settings`) — 낮은 우선순위

---

## 4. 구현 우선순위

```
1순위: 성능 최적화 (vite.config.js + lazy loading)
  → 빌드 경고 해소, 초기 로딩 속도 개선

2순위: 뷰 전환 트랜지션 (framer-motion)
  → 이미 설치됨, ObservationCanvas 수정만 필요

3순위: TGIPLanding (랜딩 리브랜딩)
  → 외부 접속 시 TGIP 아이덴티티 노출

4순위: Library 페이지
  → API 이미 구현됨, UI 추가만 필요

5순위: PDF 내보내기
  → 신규 라이브러리 설치 필요

6순위: 기술 부채 해소 (loadingView, DisclaimerBanner)
  → 마지막 정리
```

---

## 5. 성능 최적화 전략

### 5.1 Dynamic Import 패턴

```javascript
// ObservationCanvas.jsx
import { lazy, Suspense } from 'react';

const RTSView = lazy(() => import('../views/RTSView/RTSView'));
const TPIView = lazy(() => import('../views/TPIView/TPIView'));
const FSSView = lazy(() => import('../views/FSSView/FSSView'));
const WSDView = lazy(() => import('../views/WSDView/WSDView'));
```

### 5.2 Vite manualChunks 설정

```javascript
// vite.config.js
build: {
  rollupOptions: {
    output: {
      manualChunks: {
        'react-vendor': ['react', 'react-dom', 'react-router-dom'],
        'chart-vendor': ['chart.js', 'react-chartjs-2'],
        'flow-vendor': ['@xyflow/react'],
        'map-vendor': ['react-simple-maps'],
        'motion-vendor': ['framer-motion'],
        'tgip-views': [
          './src/components/tgip/views/RTSView/RTSView',
          './src/components/tgip/views/TPIView/TPIView',
          './src/components/tgip/views/FSSView/FSSView',
          './src/components/tgip/views/WSDView/WSDView',
        ],
      },
    },
  },
}
```

**예상 결과**: 메인 청크 ~200 KB, 뷰 청크 ~100 KB 각각, 지도 청크 ~300 KB

---

## 6. TGIPLanding 섹션 구성

```
+----------------------------------------------------------+
| Hero                                                       |
|  "Observe Technology. Not Prescribe."                      |
|  부제 + [Open Workspace →]                                 |
+----------------------------------------------------------+
| 4-View Summary Cards (2×2 그리드)                          |
|  RTS: 구조 성숙도  |  TPI: 전파 동력학                      |
|  FSS: 전략 압력   |  WSD: 기회 필드                        |
+----------------------------------------------------------+
| Trust Section                                              |
|  증거 기반 · 비추천 원칙 · 면책 고지                          |
+----------------------------------------------------------+
| CTA Footer                                                 |
|  [Try the Workspace] [Read Docs]                           |
+----------------------------------------------------------+
```

---

## 7. Library 페이지 구성

```
+----------------------------------------------------------+
| Header: "My Analysis Library"                              |
| (저장된 실행 개수)                                          |
+----------------------------------------------------------+
| Run 목록 (카드 리스트)                                      |
|  기술명 | Run ID | 날짜 | [View →]                          |
+----------------------------------------------------------+
| 빈 상태: "No runs yet. Start by running an analysis."      |
+----------------------------------------------------------+
```

---

## 8. 신규 설치 의존성

| 패키지 | 명령 | 용도 |
|--------|------|------|
| `html2canvas` | `npm install html2canvas --legacy-peer-deps` | DOM → Canvas 변환 |
| `jspdf` | `npm install jspdf --legacy-peer-deps` | Canvas → PDF 변환 |

---

## 9. 변경 파일 목록

### 수정

| 파일 | 변경 내용 |
|------|----------|
| `vite.config.js` | manualChunks 설정 추가 |
| `ObservationCanvas.jsx` | lazy loading + framer-motion 전환 + loadingView 활용 |
| `TGIPHeader.jsx` | Export 버튼 활성화 + Library 링크 추가 |
| `App.jsx` | TGIPLanding 교체 + `/app/library` 라우트 추가 |

### 신규 생성

| 파일 | 내용 |
|------|------|
| `pages/tgip/TGIPLanding.jsx` | TGIP 랜딩 페이지 |
| `pages/tgip/Library.jsx` | 저장된 실행 목록 |
| `components/tgip/shared/PDFExporter.jsx` | PDF 내보내기 훅/유틸 |

---

## 10. 구현 체크리스트

### Step 1 — 성능 최적화

- [ ] `vite.config.js` manualChunks 설정
- [ ] `ObservationCanvas.jsx` lazy import 전환
- [ ] `Suspense` fallback 컴포넌트 추가
- [ ] 빌드 후 청크 크기 확인 (메인 500 KB 이하)

### Step 2 — 뷰 전환 트랜지션

- [ ] `ObservationCanvas.jsx`에 `AnimatePresence` + `motion.div` 적용
- [ ] fade 애니메이션 (opacity: 0→1, duration: 0.2s)

### Step 3 — TGIPLanding

- [ ] `pages/tgip/TGIPLanding.jsx` 구현 (Hero + 4-View 카드 + CTA)
- [ ] `App.jsx`: 미인증 루트 `/` → `TGIPLanding` 교체
- [ ] `/login` 라우트 유지 확인

### Step 4 — Library 페이지

- [ ] `pages/tgip/Library.jsx` 구현
- [ ] `App.jsx`: `/app/library` 라우트 추가
- [ ] `TGIPHeader.jsx`: Library 링크 버튼 추가

### Step 5 — PDF 내보내기

- [ ] `npm install html2canvas jspdf --legacy-peer-deps`
- [ ] `components/tgip/shared/PDFExporter.jsx` 구현
- [ ] `TGIPHeader.jsx`: Export 버튼 활성화

### Step 6 — 기술 부채 해소

- [ ] `ObservationCanvas.jsx`: `loadingView` 상태 활용
- [ ] 각 뷰 하단 `DisclaimerBanner` 추가 (RTSView, TPIView, FSSView, WSDView)

---

## 11. 성공 지표

| 지표 | 목표 |
|------|------|
| 메인 청크 크기 | 500 KB 이하 (현재 1,097 KB) |
| TGIPLanding | `/` 접속 시 TGIP 랜딩 표시 |
| 뷰 전환 애니메이션 | RTS→TPI 전환 시 fade 애니메이션 동작 |
| Library 페이지 | `/app/library` 접속 시 실행 목록 표시 |
| PDF 내보내기 | Export 버튼 클릭 → PDF 다운로드 |
| 빌드 경고 | 청크 크기 경고 해소 |

---

## 12. 기술 부채 잔여 항목 (Phase 3 이후)

| 항목 | 이유 |
|------|------|
| Compare Mode | 구조 복잡, 별도 Feature 필요 |
| 실제 DB 연동 | 백엔드 TGIP 서비스 구현 필요 |
| 세밀한 필터 | Nice-to-Have |

---

## 13. 관련 문서

| 문서 | 경로 |
|------|------|
| 잔여 작업 메모 | `memory/tgip-todo.md` |
| Phase 2 아카이브 | `docs/archive/2026-03/frontend-phase2/` |
| vite.config.js | `front_end/vite.config.js` |
| ObservationCanvas | `front_end/src/components/tgip/Workspace/ObservationCanvas.jsx` |
