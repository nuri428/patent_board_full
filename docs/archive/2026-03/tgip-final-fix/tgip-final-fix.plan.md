# Plan: tgip-final-fix

## Overview
코드 리뷰(93/100) 잔여 이슈 처리. Major 1건 + Minor 2건 선별 수정.
Critical 없음, 기능 변경 없음.

## Problem Statement

### M1: DEV fallback `error: null` 누락 (Confidence 92%)
- 파일: `front_end/src/store/tgipStore.js:76`
- DEV mock fallback의 `set()` 호출에 `error: null`이 없음
- API 에러 발생 → mock fallback 시 이전 error 상태가 잔존 → 에러 배너와 mock 결과 동시 표시 가능
- **1줄 추가**로 해결

### m1: ObservationCanvas IIFE 패턴 (Confidence 90%)
- 파일: `front_end/src/components/tgip/Workspace/ObservationCanvas.jsx:83-86`
- `{(() => { const ViewComponent = ...; return ...; })()}` — 불필요한 IIFE
- `VIEW_COMPONENTS[selectedView]`를 JSX 직전 변수로 추출하면 가독성 향상

### m4: RunCard optional chaining 불일치 (Confidence 78%)
- 파일: `front_end/src/pages/tgip/Library.jsx:43-46`
- `run.technology_id?.replace()` 는 null-safe
- `run.run_id` (46행, key), `run.created_at` (50행) 는 optional chaining 없음
- run 객체 필드 누락 시 에러 가능

## Out of Scope
- m2 (비ASCII URL 처리) — 현재 DEMO_TECHS가 영문이므로 실용적 영향 없음
- m3 (canvas toDataURL 메모리) — Confidence 72%, 현재 스케일에서 문제 없음
- 기능 추가, 뷰 컴포넌트

## Success Criteria
- `tgipStore.js:76` DEV fallback에 `error: null` 포함
- `ObservationCanvas.jsx` IIFE → 변수 추출 패턴
- `Library.jsx` RunCard `run.run_id` / `run.created_at` fallback 처리
- 빌드 성공, 0 warnings

## Files to Modify
1. `front_end/src/store/tgipStore.js` (M1)
2. `front_end/src/components/tgip/Workspace/ObservationCanvas.jsx` (m1)
3. `front_end/src/pages/tgip/Library.jsx` (m4)

## Priority
1. M1 — 버그성, 즉시 수정
2. m1 — 가독성, 간단
3. m4 — 방어적 코딩, 간단

---
Created: 2026-03-05
Feature: tgip-final-fix
Phase: Plan
