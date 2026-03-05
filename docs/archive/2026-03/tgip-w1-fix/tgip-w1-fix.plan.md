# Plan: tgip-w1-fix

## Feature Overview
- **Feature Name**: tgip-w1-fix
- **Priority**: Minor (Warning W1 from code review)
- **Complexity**: Low (단일 파일, 단일 함수 수정)

## Problem Statement

`tgipStore.js`의 `runAnalysis` 함수에서 DEV 환경 fallback 처리 시, dynamic import 자체가 실패하는 경우를 처리하지 않는다.

```js
// 현재 코드 (취약)
} catch (err) {
  if (import.meta.env.DEV) {
    const { MOCK_RESULTS, MOCK_EVIDENCE } = await import('../mocks/tgipMockData.js');
    set({ ... });
  } else {
    set({ isRunning: false, error: '...' });
  }
}
```

`import('../mocks/tgipMockData.js')`가 실패하면:
- outer catch에서 이미 처리 중이므로 inner error가 catch되지 않음
- Unhandled Promise Rejection 발생
- UI가 `isRunning: true` 상태에서 멈춤 (spinner stuck)

## Goal

- W1 경고 해소 (code review 94/100 → 95/100 목표)
- DEV fallback 실패 시에도 UI가 안전하게 복구되도록 보장

## Scope

### In Scope
- `front_end/src/store/tgipStore.js` — inner try-catch 추가

### Out of Scope
- W2 (toDataURL → toBlob): 별도 작업
- W3 (conditional ref): 설계 의도 있음, 생략
- Mock 데이터 내용 변경 없음

## Implementation Plan

### Step 1: `tgipStore.js` DEV fallback에 inner try-catch 추가

**수정 전:**
```js
} catch (err) {
  if (import.meta.env.DEV) {
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
    console.error('[tgipStore] Analysis failed:', err);
    set({ isRunning: false, error: '분석 서버에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요.' });
  }
}
```

**수정 후:**
```js
} catch (err) {
  if (import.meta.env.DEV) {
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
    console.error('[tgipStore] Analysis failed:', err);
    set({ isRunning: false, error: '분석 서버에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요.' });
  }
}
```

## Acceptance Criteria
- [ ] DEV fallback의 dynamic import가 inner try-catch로 감싸짐
- [ ] importErr 발생 시 `isRunning: false, error: null`로 안전 복구
- [ ] `console.warn`으로 문제 가시화
- [ ] 빌드 성공
- [ ] 기존 기능(mock 데이터 로드) 정상 동작 유지

## Files to Modify
| File | Change |
|------|--------|
| `front_end/src/store/tgipStore.js` | DEV fallback에 inner try-catch 추가 |
