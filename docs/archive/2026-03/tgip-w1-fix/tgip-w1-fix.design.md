# Design: tgip-w1-fix

## Overview

`tgipStore.js`의 `runAnalysis` DEV fallback에 inner try-catch를 추가하여 dynamic import 실패 시 unhandled rejection을 방지한다.

## Target File

**`front_end/src/store/tgipStore.js`** — `runAnalysis` async 함수의 outer catch 블록

## Design Specification

### D1: tgipStore.js — DEV fallback inner try-catch

**위치**: `runAnalysis` 함수, outer `catch (err)` 블록 내 DEV 분기

**변경 전 (lines 71-92):**
```js
} catch (err) {
  if (import.meta.env.DEV) {
    // 개발 환경에서만 Mock 데이터로 fallback (프로덕션 번들 제외)
    const { MOCK_RESULTS, MOCK_EVIDENCE } = await import('../mocks/tgipMockData.js');
    const mockRunId = `mock-run-${Date.now()}`;
    set({
      analysisRunId: mockRunId,
      results: MOCK_RESULTS,
      evidence: MOCK_EVIDENCE,
      isRunning: false,
      evidenceDrawerOpen: true,
      error: null,
    });
  } else {
    // 프로덕션: 에러 상태로 전환
    console.error('[tgipStore] Analysis failed:', err);
    set({
      isRunning: false,
      error: '분석 서버에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요.',
    });
  }
}
```

**변경 후:**
```js
} catch (err) {
  if (import.meta.env.DEV) {
    // 개발 환경에서만 Mock 데이터로 fallback (프로덕션 번들 제외)
    try {
      const { MOCK_RESULTS, MOCK_EVIDENCE } = await import('../mocks/tgipMockData.js');
      const mockRunId = `mock-run-${Date.now()}`;
      set({
        analysisRunId: mockRunId,
        results: MOCK_RESULTS,
        evidence: MOCK_EVIDENCE,
        isRunning: false,
        evidenceDrawerOpen: true,
        error: null,
      });
    } catch (importErr) {
      console.warn('[tgipStore] Mock data import failed:', importErr);
      set({ isRunning: false, error: null });
    }
  } else {
    // 프로덕션: 에러 상태로 전환
    console.error('[tgipStore] Analysis failed:', err);
    set({
      isRunning: false,
      error: '분석 서버에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요.',
    });
  }
}
```

### 설계 근거

| 항목 | 결정 |
|------|------|
| importErr 발생 시 error 상태 | `error: null` — DEV 환경이므로 사용자에게 오류 메시지 불필요 |
| console.warn vs console.error | `warn` — 프로덕션 에러가 아닌 DEV 개발 문제 |
| evidenceDrawerOpen 생략 | import 실패 시 results 없으므로 drawer 열지 않음 |
| isRunning: false 보장 | spinner stuck 방지 — 가장 중요한 복구 조건 |

## Verification Criteria (gap-detector 대상)

| ID | 항목 | 확인 방법 |
|----|------|-----------|
| V1 | `import('../mocks/tgipMockData.js')` 호출이 inner try 내부에 있음 | 코드 구조 확인 |
| V2 | inner catch에서 `console.warn('[tgipStore] Mock data import failed:', importErr)` | 로그 문자열 확인 |
| V3 | inner catch에서 `set({ isRunning: false, error: null })` | 상태 복구 확인 |
| V4 | outer catch 구조(DEV/else 분기) 유지 | 회귀 없음 확인 |
| V5 | 빌드 성공 | `npm run build` |
