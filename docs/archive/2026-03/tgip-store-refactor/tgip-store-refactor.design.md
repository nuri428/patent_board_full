# Design: tgip-store-refactor

## Overview
코드 리뷰(82/100) Major 3건 해결. 수정 파일 2개, 기능 변경 없음.

---

## Step 1: INITIAL_RESULTS / INITIAL_EVIDENCE 상수 추출 (M2)

**파일**: `front_end/src/store/tgipStore.js`

**목적**: `setTechnology`와 `reset`에서 중복된 초기값 리터럴을 파일 상단 상수로 추출.

**변경 전**:
```js
// setTechnology 내부
results: { RTS: null, TPI: null, FSS: null, WSD: null },
evidence: { representativePatents: [], ipcSignatures: [], abstractSnippets: [], confidenceScores: {} },

// reset 내부 (동일 리터럴 반복)
results: { RTS: null, TPI: null, FSS: null, WSD: null },
evidence: { representativePatents: [], ipcSignatures: [], abstractSnippets: [], confidenceScores: {} },
```

**변경 후**: `import { create }` 바로 아래에 상수 추가
```js
import { create } from 'zustand';

const INITIAL_RESULTS = { RTS: null, TPI: null, FSS: null, WSD: null };
const INITIAL_EVIDENCE = {
  representativePatents: [],
  ipcSignatures: [],
  abstractSnippets: [],
  confidenceScores: {},
};
```

- `setTechnology`에서: `results: { ...INITIAL_RESULTS }, evidence: { ...INITIAL_EVIDENCE },`
- `reset`에서: 동일하게 spread 사용
- 초기 상태(store 선언부)에서도 동일하게 사용

> **주의**: spread(`{ ...INITIAL_RESULTS }`) 필수 — 참조 공유 방지 (각 set 호출마다 새 객체)

---

## Step 2: API 응답 방어적 처리 (M1)

**파일**: `front_end/src/store/tgipStore.js`

**목적**: `response.data` destructuring 시 서버 응답이 예상 스키마를 벗어날 경우 fallback 보장.

**변경 전**:
```js
const { run_id, results, evidence } = response.data;
set({
  analysisRunId: run_id,
  results,
  evidence,
  isRunning: false,
  evidenceDrawerOpen: true,
});
```

**변경 후**:
```js
const { run_id, results = { ...INITIAL_RESULTS }, evidence = { ...INITIAL_EVIDENCE } } = response.data ?? {};
set({
  analysisRunId: run_id ?? null,
  results,
  evidence,
  isRunning: false,
  evidenceDrawerOpen: true,
});
```

- `response.data ?? {}`: data 자체가 null/undefined인 경우 방어
- `results = { ...INITIAL_RESULTS }`: results 누락 시 안전한 초기값 (4개 뷰 키 보장)
- `evidence = { ...INITIAL_EVIDENCE }`: evidence 누락 시 빈 배열/객체 보장
- `run_id ?? null`: run_id 누락 방어 (선택적, 하지만 일관성)

---

## Step 3: usePDFExport → useCallback으로 안정화 (M3)

**파일**: `front_end/src/components/tgip/shared/PDFExporter.jsx`

**목적**: 매 렌더마다 새 함수 참조 생성 방지. hook 네이밍 규약 준수.

**현재 구조**:
```js
export const usePDFExport = () => {
  const exportToPDF = async ({ targetRef, fileName, onError }) => {
    // ... 구현
  };
  return { exportToPDF };
};
```

**변경 후**:
```js
import { useCallback } from 'react';

export const usePDFExport = () => {
  const exportToPDF = useCallback(async ({ targetRef, fileName, onError }) => {
    // ... 구현 (변경 없음)
  }, []); // 의존성 없음 — 함수 본체가 외부 상태에 의존하지 않음

  return { exportToPDF };
};
```

- `useCallback` import 추가
- `exportToPDF` 함수를 `useCallback`으로 감싸기
- 의존성 배열 `[]` — 함수 본체가 React 상태/props에 의존하지 않음
- 함수 본체(html2canvas, jsPDF 로직) 변경 없음
- `TGIPWorkspace.jsx` 변경 불필요 (import/사용 방식 동일)

---

## 구현 순서

1. `tgipStore.js` Step 1 (M2: 상수 추출)
2. `tgipStore.js` Step 2 (M1: API 응답 fallback)
3. `PDFExporter.jsx` Step 3 (M3: useCallback)
4. 빌드 검증

## 파일 목록

| 파일 | 변경 유형 | Step |
|------|---------|------|
| `front_end/src/store/tgipStore.js` | 수정 | Step 1, 2 |
| `front_end/src/components/tgip/shared/PDFExporter.jsx` | 수정 | Step 3 |

---
Created: 2026-03-05
Feature: tgip-store-refactor
Phase: Design
