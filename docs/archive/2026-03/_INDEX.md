# Archive Index — 2026-03

> 아카이브 날짜: 2026-03-05

## 완료된 Feature 목록

| Feature | Match Rate | 완료일 | 경로 |
|---------|:----------:|--------|------|
| frontend-phase2 | 95% | 2026-03-05 | `./frontend-phase2/` |
| frontend-phase3 | 93% | 2026-03-05 | `./frontend-phase3/` |
| tgip-code-fixes | 97% | 2026-03-05 | `./tgip-code-fixes/` |
| tgip-minor-fixes | 100% | 2026-03-06 | `./tgip-minor-fixes/` |
| tgip-store-refactor | 100% | 2026-03-06 | `./tgip-store-refactor/` |
| tgip-final-fix | 100% | 2026-03-06 | `./tgip-final-fix/` |
| tgip-w1-fix | 100% | 2026-03-06 | `./tgip-w1-fix/` |

## frontend-phase2

- **내용**: TGIP 멀티뷰 완성 (TPI/FSS/WSD) + FastAPI TGIP API 연동
- **구현 파일**: 15개 (신규 12개 + 수정 3개)
- **Match Rate**: 95% (60개 항목 중 54개 완전 구현)
- **빌드**: 성공 (1,097 KB)

### 아카이브 파일

- `frontend-phase2.plan.md` — Plan 문서
- `frontend-phase2.design.md` — Design 문서
- `frontend-phase2.analysis.md` — Gap Analysis (95%)
- `frontend-phase2.report.md` — 완료 보고서

## frontend-phase3

- **내용**: TGIP 완성도 향상 — 번들 최적화·TGIPLanding·뷰 전환·Library·PDF 내보내기·기술 부채
- **구현 파일**: 12개 (신규 3개 + 수정 9개)
- **Match Rate**: 93% (44개 항목 중 39개 완전 구현)
- **빌드**: 성공 (메인 번들 1,097 KB → 447 KB, 경고 해소)

### 아카이브 파일

- `frontend-phase3.plan.md` — Plan 문서
- `frontend-phase3.design.md` — Design 문서
- `frontend-phase3.analysis.md` — Gap Analysis (93%)
- `frontend-phase3.report.md` — 완료 보고서

## tgip-code-fixes

- **내용**: 코드 리뷰(78/100) Critical 3건 + Major 4건 수정 — PDFExporter 에러처리·메모리·DEV/PROD 분기·Library ErrorState·상수 중앙화·useEffect 정리·ref 연결 보장
- **구현 파일**: 6개 (신규 1개 + 수정 5개)
- **Match Rate**: 97%
- **빌드**: 성공 (경고 0개 유지)

### 아카이브 파일

- `tgip-code-fixes.plan.md` — Plan 문서
- `tgip-code-fixes.design.md` — Design 문서
- `tgip-code-fixes.analysis.md` — Gap Analysis (97%)
- `tgip-code-fixes.report.md` — 완료 보고서

## tgip-minor-fixes

- **내용**: AbortController 정리, exportError 상태 + amber 배너 (alert() 제거)
- **구현 파일**: 7개 (신규 2개 + 수정 5개)
- **Match Rate**: 100%
- **빌드**: 성공

### 아카이브 파일

- `tgip-minor-fixes.plan.md` — Plan 문서
- `tgip-minor-fixes.design.md` — Design 문서
- `tgip-minor-fixes.analysis.md` — Gap Analysis (100%)
- `tgip-minor-fixes.report.md` — 완료 보고서

## tgip-store-refactor

- **내용**: INITIAL_RESULTS/INITIAL_EVIDENCE 상수화, useCallback 적용, API fallback 안전 처리
- **구현 파일**: 3개 (수정 3개)
- **Match Rate**: 100% (17/17)
- **빌드**: 성공

### 아카이브 파일

- `tgip-store-refactor.plan.md` — Plan 문서
- `tgip-store-refactor.design.md` — Design 문서
- `tgip-store-refactor.analysis.md` — Gap Analysis (100%)
- `tgip-store-refactor.report.md` — 완료 보고서

## tgip-final-fix

- **내용**: DEV fallback error: null, ObservationCanvas IIFE 제거, Library run_id fallback
- **구현 파일**: 3개 (수정 3개)
- **Match Rate**: 100% (7/7)
- **빌드**: 성공

### 아카이브 파일

- `tgip-final-fix.plan.md` — Plan 문서
- `tgip-final-fix.design.md` — Design 문서
- `tgip-final-fix.analysis.md` — Gap Analysis (100%)
- `tgip-final-fix.report.md` — 완료 보고서

## tgip-w1-fix

- **내용**: DEV fallback dynamic import에 inner try-catch 추가 — unhandled rejection 방지
- **구현 파일**: 1개 (수정 1개)
- **Match Rate**: 100% (5/5)
- **빌드**: 성공

### 아카이브 파일

- `tgip-w1-fix.plan.md` — Plan 문서
- `tgip-w1-fix.design.md` — Design 문서
- `tgip-w1-fix.analysis.md` — Gap Analysis (100%)
- `tgip-w1-fix.report.md` — 완료 보고서
