# Git Commit Summary - 2026-02-10

## OpenSearch k-NN 검색 마이그레이션 작업

총 **6개의 논리적 커밋**이 생성되었습니다.

### 커밋 목록

#### 1. `cea0ed2` - feat(mcp): OpenSearch k-NN 설정 및 의존성 업데이트
**변경 파일**: 4개
- `.env`
- `mcp/config/settings.py`
- `mcp/pyproject.toml`
- `mcp/uv.lock`

**주요 변경사항**:
- OpenSearch 인덱스 환경변수 추가 (`OPENSEARCH_PATENT_INDEX`)
- sentence-transformers, transformers 최신 버전으로 업데이트
- sentencepiece 의존성 추가
- FlagEmbedding 제거 (안정성 문제)

---

#### 2. `99a9450` - feat(mcp): OpenSearch k-NN 시맨틱 검색 구현
**변경 파일**: 3개
- `mcp/database.py`
- `mcp/services/embedding_service.py`
- `mcp/mcp_server.py`

**주요 변경사항**:
- AsyncOpenSearch 클라이언트로 전환
- sentence-transformers 기반 임베딩 서비스 리팩토링
- semantic_search 엔드포인트에 script_score 쿼리 구현
- BGE-M3 모델 안정적 로딩 및 비동기 처리

**기술적 노트**:
- unified-patents-v1 인덱스는 `index.knn: true` 설정 누락
- 근사 k-NN 쿼리 작동 안 함
- script_score 방식은 작동하나 4.8M 문서에서 타임아웃 발생

---

#### 3. `3121527` - docs: OpenSearch k-NN 마이그레이션 조사 문서화 및 테스트 스크립트
**변경 파일**: 8개 (신규 생성)
- `docs/work_log_2026-02-10.md`
- `docs/project_plan_opensearch_knn.md`
- `mcp/scripts/inspect_unified_index.py`
- `mcp/test_opensearch_knn.py`
- `mcp/gen_test_query.py`
- `mcp/gen_script_score_query.py`
- `mcp/test_knn_query.sh`
- `mcp/scripts/output.txt`

**주요 내용**:
- 금일 작업 내역 상세 기록
- 향후 작업 계획 (옵션 1: 인덱스 재구성, 옵션 2: 쿼리 최적화)
- 인덱스 구조 분석 스크립트
- k-NN 쿼리 테스트 도구

**주요 발견사항**:
- 인덱스에 `index.knn: true` 설정 누락 확인
- 표준 k-NN 쿼리 0건 결과 반환
- script_score 쿼리는 작동하나 brute-force로 타임아웃
- 프로덕션 사용을 위해 인덱스 재구성 필요

---

#### 4. `e599999` - feat(backend): OpenSearch k-NN 시맨틱 검색 백엔드 통합
**변경 파일**: 5개
- `back_end/app/crud/patent_db.py`
- `back_end/app/core/config.py`
- `back_end/app/schemas/patent.py`
- `back_end/pyproject.toml`
- `back_end/app/scripts/index_patents.py` (신규)

**주요 변경사항**:
- `search_all_patents`에 시맨틱 검색 통합
- MCPClient.semantic_search 호출 로직
- OpenSearch 결과를 MariaDB ID로 매핑
- 실패 시 기존 키워드 검색으로 폴백
- MCP 서비스 설정 추가

**현재 상태**:
- MCP semantic_search 타임아웃으로 실제 사용 불가
- 인덱스 재구성 후 활성화 예정

---

#### 5. `7285ccc` - feat(infra): 프로덕션 환경 설정 및 API 엔드포인트 개선
**변경 파일**: 2개
- `docker-compose.prod.yml`
- `back_end/app/api/v1/endpoints/patents.py`

**주요 변경사항**:
- 프로덕션 Docker 설정 업데이트
- API 엔드포인트 개선

---

#### 6. `c1621db` - style(frontend): UI 개선 및 입력 필드 가시성 향상
**변경 파일**: 6개
- `front_end/src/pages/PatentSearch.jsx`
- `front_end/src/pages/Dashboard.jsx`
- `front_end/src/pages/Login.jsx`
- `front_end/src/components/Layout/ProtectedLayout.jsx`
- `front_end/src/index.css`
- `front_end/src/App.jsx`

**주요 변경사항**:
- 검색 입력 필드 개선 ('title' → 'query')
- 입력 텍스트 가시성 향상 (bg-white, text-slate-900)
- 대시보드 및 로그인 페이지 UI 개선
- 전역 스타일 업데이트

---

## 커밋 통계

### 파일 변경 요약
- **총 변경 파일**: 28개
- **신규 생성 파일**: 9개
- **수정된 파일**: 19개

### 코드 변경량
- **삽입**: ~3,700 라인
- **삭제**: ~2,500 라인
- **순 증가**: ~1,200 라인

### 커밋 분류
- **기능 추가 (feat)**: 4개
- **문서화 (docs)**: 1개
- **스타일 (style)**: 1개

## Git 상태

```
Branch: dev
Ahead of origin/dev by 6 commits
Working tree: clean
```

## 다음 단계

### 즉시 실행 가능
```bash
# 원격 저장소에 푸시
git push origin dev
```

### 사용자 결정 필요
1. **인덱스 재구성** (권장) - 14-18시간 소요
   - 새 인덱스 생성 with `index.knn: true`
   - 4.8M 문서 재인덱싱
   - 빠른 근사 k-NN 검색 활성화

2. **쿼리 최적화** - 8시간 소요
   - 사전 필터링 구현
   - 캐싱 시스템 추가
   - 제한적 확장성

## 참고 문서

- [작업 일지](file:///home/nuri/dev/git/patent_board_full/docs/work_log_2026-02-10.md)
- [프로젝트 플랜](file:///home/nuri/dev/git/patent_board_full/docs/project_plan_opensearch_knn.md)
- [Walkthrough](file:///home/nuri/.gemini/antigravity/brain/f8ba1185-5a97-4fd5-8d55-a69ce8dfacdc/walkthrough.md)

---

**작성일**: 2026-02-10  
**브랜치**: dev  
**커밋 범위**: cea0ed2...c1621db (6 commits)
