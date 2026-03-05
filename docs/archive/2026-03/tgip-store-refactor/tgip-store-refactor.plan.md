# Plan: tgip-store-refactor

## Overview
코드 리뷰(82/100)에서 식별된 Major 3건을 해결하는 리팩토링.
Critical 없음 — 기능 변경 없이 코드 품질과 안정성 개선.

## Problem Statement

### M1: API 응답 방어적 처리 미흡 (Confidence 92%)
- 파일: `front_end/src/store/tgipStore.js:60`
- `const { run_id, results, evidence } = response.data` — 서버가 예상 스키마를 벗어난 응답 반환 시 하위 컴포넌트에서 런타임 에러 발생 가능
- `results.RTS`, `evidence.representativePatents` 등에 직접 접근하는 코드가 여럿 존재

### M2: 초기 상태 객체 리터럴 중복 (Confidence 95%)
- 파일: `front_end/src/store/tgipStore.js:27-31, 41-50`
- `setTechnology`와 `reset` 액션에서 `results`, `evidence` 초기값이 각각 별도 하드코딩
- 필드 추가 시 두 곳 모두 수정 필요 → 불일치 버그 위험

### M3: usePDFExport 구조 문제 (Confidence 85%)
- 파일: `front_end/src/components/tgip/shared/PDFExporter.jsx`
- `usePDFExport` hook 내부에서 React hook 미사용 → 매 렌더마다 새 `exportToPDF` 함수 참조 생성
- hook 네이밍 규약 미준수 (use- prefix이지만 실제 hook이 아님)

## Scope

### In Scope
- M1: `tgipStore.js` destructuring에 fallback 기본값 추가
- M2: `INITIAL_RESULTS`, `INITIAL_EVIDENCE` 상수 추출 후 재사용
- M3: `usePDFExport` → `useCallback`으로 감싸거나 일반 함수로 export

### Out of Scope
- Minor 이슈 (m1~m9) — 별도 사이클에서 처리
- 뷰 컴포넌트(RTSView, TPIView 등) 내부 로직
- 기능(Feature) 추가

## Success Criteria
- `tgipStore.js`: `INITIAL_RESULTS`, `INITIAL_EVIDENCE` 상수 사용
- `tgipStore.js`: `response.data` destructuring에 기본값 보장
- `PDFExporter.jsx`: hook 규약 준수 또는 일반 함수로 변경
- 빌드 성공, 0 warnings
- 기존 동작 변경 없음

## Files to Modify
1. `front_end/src/store/tgipStore.js`
2. `front_end/src/components/tgip/shared/PDFExporter.jsx`

## Priority
- M2 (초기 상태 중복): 가장 간단, 즉시 DRY 개선
- M1 (API 응답 방어): 런타임 안정성, 중요도 높음
- M3 (usePDFExport): hook 규약 준수

## Notes
- `tgipStore.js`는 Zustand store — React lifecycle 외부에서 실행되므로 `useCallback` 불가
- M3의 경우 `PDFExporter.jsx`만 수정, `TGIPWorkspace.jsx` import 방식은 유지 가능

---
Created: 2026-03-05
Feature: tgip-store-refactor
Phase: Plan
