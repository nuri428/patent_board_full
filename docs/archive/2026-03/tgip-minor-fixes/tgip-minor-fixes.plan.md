# Plan: tgip-minor-fixes

> 코드 리뷰(91/100) Minor 5건 수정

## 목표

tgip-code-fixes 이후 재검토에서 발견된 Minor 이슈 5건을 수정하여
코드 품질을 91/100 → 97+ 수준으로 끌어올린다.

## 배경

- `tgip-code-fixes` 완료 후 재검토 점수: 91/100
- Critical 0건, Major 0건, Minor 5건
- 모두 배포 무관이나 가독성·안정성·확장성 개선 가치 있음

## 수정 범위

### m1 — `tgipStore.js`: Mock 데이터 별도 파일 분리

**현 상태**: Mock 데이터(MOCK_EVIDENCE, MOCK_RESULTS)가 store 파일에 118줄 인라인
**목표**: `src/mocks/tgipMockData.js` 신규 파일로 분리
- DEV 환경에서만 import하여 프로덕션 번들에서 tree-shake
- `tgipStore.js` 가독성 향상 (실제 로직만 90줄 수준)

**파일**:
- `front_end/src/mocks/tgipMockData.js` (신규)
- `front_end/src/store/tgipStore.js` (수정)

---

### m2 — `Library.jsx`: useEffect cleanup (AbortController)

**현 상태**: API 호출에 cleanup 없음 → 빠른 unmount 시 state 업데이트 경고 가능
**목표**: AbortController를 사용하여 컴포넌트 unmount 시 진행 중인 fetch 취소

```js
useEffect(() => {
  const controller = new AbortController();
  // API 호출 시 signal 전달
  return () => controller.abort();
}, [retryCount]);
```

> tgip.js getLibrary()가 AbortController signal을 지원하지 않을 경우,
> unmount flag 패턴(isMounted ref)으로 대체.

**파일**: `front_end/src/pages/tgip/Library.jsx`

---

### m3 — `PDFExporter.jsx`: Magic number 상수화

**현 상태**: `area > 1_000_000` 이 인라인 숫자
**목표**: 명명된 상수로 추출하여 의도를 명확히 함

```js
const HIGH_RES_AREA_THRESHOLD = 1_000_000; // 1M px 초과 시 scale=1
```

**파일**: `front_end/src/components/tgip/shared/PDFExporter.jsx`

---

### m4 — `ObservationCanvas.jsx`: view map 패턴으로 전환

**현 상태**: 4개 view를 if 체인으로 렌더링
```jsx
{selectedView === 'RTS' && <RTSView data={results.RTS} />}
{selectedView === 'TPI' && <TPIView data={results.TPI} />}
{selectedView === 'FSS' && <FSSView data={results.FSS} />}
{selectedView === 'WSD' && <WSDView data={results.WSD} />}
```

**목표**: view 컴포넌트 레지스트리 패턴으로 전환
```js
const VIEW_COMPONENTS = { RTS: RTSView, TPI: TPIView, FSS: FSSView, WSD: WSDView };
const ViewComponent = VIEW_COMPONENTS[selectedView];
// <ViewComponent data={results[selectedView]} />
```
새 view 추가 시 레지스트리 1줄만 추가하면 됨.

**파일**: `front_end/src/components/tgip/Workspace/ObservationCanvas.jsx`

---

### m5 — `TGIPWorkspace.jsx`: `alert()` → 인라인 에러 상태

**현 상태**: PDF export 실패 시 `alert()` 사용
**목표**: store의 error state 패턴을 재사용하여 인라인 에러 표시

- `exportError` state 추가 (TGIPWorkspace 내부)
- `onError: (err) => setExportError('PDF 내보내기에 실패했습니다.')` 로 변경
- TGIPHeader 아래에 조건부 에러 배너 표시 (3초 후 자동 해제 또는 닫기 버튼)

**파일**: `front_end/src/pages/tgip/TGIPWorkspace.jsx`

---

## 구현 순서

| 순서 | 파일 | 이슈 | 복잡도 |
|------|------|------|--------|
| 1 | `mocks/tgipMockData.js` (신규) | m1 | Low |
| 2 | `store/tgipStore.js` | m1 | Low |
| 3 | `components/tgip/shared/PDFExporter.jsx` | m3 | Low |
| 4 | `pages/tgip/Library.jsx` | m2 | Medium |
| 5 | `components/tgip/Workspace/ObservationCanvas.jsx` | m4 | Low |
| 6 | `pages/tgip/TGIPWorkspace.jsx` | m5 | Low |

## 스코프 제외

- toast 라이브러리 도입 (YAGNI — 단일 에러 메시지에 과함)
- tgipStore 전체 구독 최적화 (Zustand 특성상 selector 분리가 필요하나 현 규모에서 성능 영향 미미)

## 성공 기준

- [ ] tgipStore.js 실제 로직 파일 길이 90줄 내외
- [ ] Library useEffect에 cleanup 함수 포함
- [ ] PDFExporter에 `HIGH_RES_AREA_THRESHOLD` 상수 사용
- [ ] ObservationCanvas에 VIEW_COMPONENTS 레지스트리 패턴 적용
- [ ] TGIPWorkspace에서 `alert()` 제거 → 인라인 에러 표시
- [ ] 빌드 성공 (경고 0개)
- [ ] 예상 코드 리뷰 점수: 97+/100
