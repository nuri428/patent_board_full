# OpenSearch k-NN 검색 마이그레이션 프로젝트 플랜

## 프로젝트 개요

**목표**: 특허 검색 기능을 MariaDB 키워드 검색에서 OpenSearch k-NN 시맨틱 검색으로 마이그레이션하여 검색 관련성 및 사용자 경험 향상

**현재 상태**: 근본 원인 파악 완료, 사용자 결정 대기 중

## 옵션 분석

### 옵션 1: 인덱스 재구성 (권장) ⭐

#### 장점
- ✅ 빠르고 확장 가능한 근사 k-NN 검색
- ✅ HNSW 알고리즘 활용으로 1초 이하 쿼리 시간
- ✅ 4.8M+ 문서에서 프로덕션 준비 완료
- ✅ 장기적 확장성 우수

#### 단점
- ❌ 4.8M 문서 재인덱싱 필요
- ❌ 일시적 다운타임 또는 이중 인덱스 전략 필요
- ❌ 추가 스토리지 필요 (임시)

#### 예상 작업 시간
- 인덱스 생성 및 설정: 1시간
- 재인덱싱 스크립트 작성: 2시간
- 재인덱싱 실행: 4-8시간 (데이터 크기 및 하드웨어 의존)
- 코드 업데이트 및 테스트: 2시간
- 배포 및 검증: 1시간
- **총 예상 시간**: 10-14시간

### 옵션 2: 현재 쿼리 최적화

#### 장점
- ✅ 재인덱싱 불필요
- ✅ 기존 인덱스 활용
- ✅ 빠른 구현 가능

#### 단점
- ❌ 근사 k-NN보다 느림
- ❌ 쿼리 결과 캐싱 필요
- ❌ 제한적 확장성
- ❌ 장기적으로 유지보수 부담

#### 예상 작업 시간
- 사전 필터링 로직 구현: 2시간
- 캐싱 시스템 구현: 3시간
- 타임아웃 설정 조정: 1시간
- 테스트 및 최적화: 2시간
- **총 예상 시간**: 8시간

## 권장 접근 방식: 옵션 1 (인덱스 재구성)

### Phase 1: 새 인덱스 생성 및 설정

#### 1.1 인덱스 매핑 설계
```json
PUT /unified-patents-v2
{
  "settings": {
    "index.knn": true,
    "number_of_shards": 6,
    "number_of_replicas": 1,
    "refresh_interval": "30s"
  },
  "mappings": {
    "properties": {
      "application_number": {"type": "keyword"},
      "country_code": {"type": "keyword"},
      "publication_number": {"type": "keyword"},
      "title": {"type": "text"},
      "abstract": {"type": "text"},
      "section_type": {"type": "keyword"},
      "section_title": {"type": "text"},
      "section_content": {"type": "text"},
      "embedding": {
        "type": "knn_vector",
        "dimension": 1024,
        "method": {
          "engine": "nmslib",
          "space_type": "cosinesimil",
          "name": "hnsw",
          "parameters": {
            "ef_construction": 128,
            "m": 16
          }
        }
      }
    }
  }
}
```

**작업 항목**:
- [ ] 인덱스 매핑 JSON 파일 생성
- [ ] 기존 `unified-patents-v1` 매핑 분석 및 비교
- [ ] 필요한 필드 모두 포함 확인
- [ ] 인덱스 생성 스크립트 작성

**예상 시간**: 1시간

#### 1.2 재인덱싱 전략 선택

**옵션 A: Reindex API 사용** (권장)
```python
POST /_reindex
{
  "source": {
    "index": "unified-patents-v1"
  },
  "dest": {
    "index": "unified-patents-v2"
  }
}
```

**옵션 B: 커스텀 스크립트**
- 병렬 처리로 속도 향상
- 진행 상황 모니터링
- 오류 처리 및 재시도 로직

**작업 항목**:
- [ ] 재인덱싱 방법 결정
- [ ] 스크립트 작성 (옵션 B 선택 시)
- [ ] 테스트 환경에서 소규모 테스트

**예상 시간**: 2시간

### Phase 2: 재인덱싱 실행

#### 2.1 재인덱싱 준비
**작업 항목**:
- [ ] 디스크 공간 확인 (최소 2배 필요)
- [ ] OpenSearch 클러스터 상태 확인
- [ ] 백업 생성 (선택사항)
- [ ] 재인덱싱 중 검색 서비스 전략 결정
  - 옵션 A: 기존 인덱스 계속 사용 (다운타임 없음)
  - 옵션 B: 유지보수 모드 (다운타임 허용)

**예상 시간**: 1시간

#### 2.2 재인덱싱 실행 및 모니터링
**작업 항목**:
- [ ] 재인덱싱 시작
- [ ] 진행 상황 모니터링
  ```bash
  GET /_tasks?detailed=true&actions=*reindex
  ```
- [ ] 오류 로그 확인
- [ ] 완료 후 문서 수 검증
  ```bash
  GET /unified-patents-v2/_count
  ```

**예상 시간**: 4-8시간 (자동 실행, 모니터링만 필요)

#### 2.3 인덱스 검증
**작업 항목**:
- [ ] 문서 수 일치 확인
- [ ] 샘플 문서 비교
- [ ] 임베딩 필드 확인
- [ ] 테스트 쿼리 실행

**예상 시간**: 1시간

### Phase 3: 코드 업데이트

#### 3.1 MCP 서비스 업데이트

**파일**: `mcp/mcp_server.py`

**변경 사항**:
```python
# Before (script_score - 느림)
search_body = {
    "size": input.limit,
    "query": {
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                "source": "knn_score",
                "lang": "knn",
                "params": {
                    "field": "embedding",
                    "query_value": query_embeddings["dense_vector"],
                    "space_type": "cosinesimil"
                }
            }
        }
    }
}

# After (approximate k-NN - 빠름)
search_body = {
    "size": input.limit,
    "query": {
        "knn": {
            "embedding": {
                "vector": query_embeddings["dense_vector"],
                "k": input.limit
            }
        }
    }
}

# 필터 추가 (필요시)
if input.analysis_run_id:
    search_body["query"] = {
        "bool": {
            "must": {
                "knn": {
                    "embedding": {
                        "vector": query_embeddings["dense_vector"],
                        "k": input.limit
                    }
                }
            },
            "filter": {
                "term": {"analysis_run_id": input.analysis_run_id}
            }
        }
    }
```

**작업 항목**:
- [ ] `semantic_search` 함수 업데이트
- [ ] `search_patent_sections` 함수 업데이트 (하이브리드 검색)
- [ ] 디버그 로깅 제거 또는 조정
- [ ] 에러 핸들링 개선

**예상 시간**: 1시간

#### 3.2 환경 설정 업데이트

**파일**: `.env`, `mcp/config/settings.py`

**변경 사항**:
```bash
# .env
OPENSEARCH_PATENT_INDEX=unified-patents-v2
```

**작업 항목**:
- [ ] 환경 변수 업데이트
- [ ] 설정 파일 검증
- [ ] 개발/스테이징/프로덕션 환경별 설정 확인

**예상 시간**: 30분

#### 3.3 백엔드 통합

**파일**: `back_end/app/crud/patent_db.py`

**작업 항목**:
- [ ] `search_all_patents` 함수에서 시맨틱 검색 활성화
- [ ] OpenSearch 결과를 MariaDB ID로 매핑
- [ ] 기존 필터(날짜, 상태 등)와 통합
- [ ] 에러 핸들링 및 폴백 로직

**예상 시간**: 2시간

### Phase 4: 테스트 및 검증

#### 4.1 단위 테스트
**작업 항목**:
- [ ] `semantic_search` 엔드포인트 테스트
- [ ] 임베딩 생성 테스트
- [ ] 쿼리 형식 검증
- [ ] 에러 케이스 테스트

**예상 시간**: 1시간

#### 4.2 통합 테스트
**작업 항목**:
- [ ] MCP → OpenSearch 통합 테스트
- [ ] Backend → MCP 통합 테스트
- [ ] 전체 검색 플로우 테스트
- [ ] 필터 조합 테스트

**예상 시간**: 1시간

#### 4.3 성능 테스트
**작업 항목**:
- [ ] 쿼리 응답 시간 측정 (목표: <1초)
- [ ] 동시 요청 부하 테스트
- [ ] 메모리 사용량 모니터링
- [ ] 검색 정확도 평가

**테스트 쿼리 예시**:
```bash
# 성능 테스트
time curl -X POST -H "X-API-Key: test-key" \
  -d '{"query": "battery management system", "limit": 10}' \
  http://localhost:8080/tools/semantic_search
```

**예상 시간**: 2시간

#### 4.4 사용자 수용 테스트
**작업 항목**:
- [ ] 다양한 검색 쿼리 테스트
  - "AI for healthcare data"
  - "renewable energy storage"
  - "quantum computing algorithms"
- [ ] 검색 결과 관련성 평가
- [ ] 기존 키워드 검색과 비교
- [ ] 사용자 피드백 수집

**예상 시간**: 1시간

### Phase 5: 배포 및 전환

#### 5.1 배포 전 체크리스트
- [ ] 모든 테스트 통과 확인
- [ ] 코드 리뷰 완료
- [ ] 배포 계획 문서화
- [ ] 롤백 계획 준비
- [ ] 모니터링 대시보드 설정

#### 5.2 배포 전략

**옵션 A: Blue-Green 배포**
1. 새 인덱스(`unified-patents-v2`)로 전환
2. 트래픽 일부를 새 버전으로 라우팅
3. 모니터링 및 검증
4. 점진적으로 트래픽 증가
5. 완전 전환 후 기존 인덱스 유지 (롤백용)

**옵션 B: 직접 전환**
1. 유지보수 모드 활성화
2. 환경 변수 업데이트
3. 서비스 재시작
4. 검증 후 서비스 재개

**작업 항목**:
- [ ] 배포 전략 선택
- [ ] 배포 스크립트 준비
- [ ] 배포 실행
- [ ] 서비스 상태 확인

**예상 시간**: 1시간

#### 5.3 배포 후 모니터링
**작업 항목**:
- [ ] 검색 쿼리 응답 시간 모니터링
- [ ] 에러 로그 확인
- [ ] OpenSearch 클러스터 상태 확인
- [ ] 사용자 피드백 수집
- [ ] 성능 메트릭 수집

**모니터링 기간**: 1주일

#### 5.4 기존 인덱스 정리
**작업 항목**:
- [ ] 새 인덱스 안정성 확인 (1-2주 후)
- [ ] 기존 `unified-patents-v1` 인덱스 삭제 또는 아카이브
- [ ] 디스크 공간 확보

**예상 시간**: 30분

### Phase 6: 프론트엔드 통합 (선택사항)

#### 6.1 UI 업데이트

**파일**: `front_end/src/pages/PatentSearch.jsx`

**작업 항목**:
- [ ] 검색 입력을 시맨틱 쿼리로 전달
- [ ] 검색 결과 표시 개선
- [ ] 관련성 점수 표시 (선택사항)
- [ ] 로딩 상태 개선

**예상 시간**: 2시간

#### 6.2 사용자 경험 개선
**작업 항목**:
- [ ] 검색 제안 기능
- [ ] 유사 특허 추천
- [ ] 검색 히스토리
- [ ] 필터 UI 개선

**예상 시간**: 4시간 (우선순위 낮음)

## 대안 접근 방식: 옵션 2 (쿼리 최적화)

### 구현 계획 (옵션 2 선택 시)

#### 1. 사전 필터링 구현
```python
# 문서 세트를 줄이기 위한 사전 필터링
search_body = {
    "size": input.limit,
    "query": {
        "script_score": {
            "query": {
                "bool": {
                    "should": [
                        {"match": {"title": input.query}},
                        {"match": {"abstract": input.query}}
                    ],
                    "minimum_should_match": 1
                }
            },
            "script": {
                "source": "knn_score",
                "lang": "knn",
                "params": {
                    "field": "embedding",
                    "query_value": query_embeddings["dense_vector"],
                    "space_type": "cosinesimil"
                }
            }
        }
    }
}
```

**작업 항목**:
- [ ] 효과적인 사전 필터 전략 설계
- [ ] 코드 구현
- [ ] 성능 테스트

**예상 시간**: 2시간

#### 2. 캐싱 시스템 구현
**작업 항목**:
- [ ] Redis 캐싱 설정
- [ ] 쿼리 임베딩 캐싱
- [ ] 검색 결과 캐싱 (TTL: 1시간)
- [ ] 캐시 무효화 전략

**예상 시간**: 3시간

#### 3. 타임아웃 및 성능 튜닝
**작업 항목**:
- [ ] OpenSearch 타임아웃 설정 증가
- [ ] 결과 크기 제한 (`limit` 파라미터)
- [ ] 비동기 처리 최적화

**예상 시간**: 1시간

## 리스크 및 완화 전략

### 리스크 1: 재인덱싱 중 서비스 중단
**완화 전략**:
- Blue-Green 배포 사용
- 기존 인덱스 유지하며 새 인덱스 병렬 구축
- 트래픽 점진적 전환

### 리스크 2: 재인덱싱 실패
**완화 전략**:
- 소규모 테스트 먼저 수행
- 체크포인트 및 재시도 로직
- 백업 유지

### 리스크 3: 성능 목표 미달
**완화 전략**:
- 성능 테스트 조기 수행
- HNSW 파라미터 튜닝 (ef_construction, m)
- 샤드 수 조정

### 리스크 4: 검색 정확도 저하
**완화 전략**:
- A/B 테스트로 기존 검색과 비교
- 사용자 피드백 수집
- 임베딩 모델 재평가 (필요시)

## 성공 지표

### 성능 지표
- [ ] 검색 응답 시간 < 1초 (95 percentile)
- [ ] 동시 사용자 100명 지원
- [ ] 에러율 < 0.1%

### 품질 지표
- [ ] 검색 결과 관련성 > 80% (사용자 평가)
- [ ] 클릭률 향상 > 20%
- [ ] 사용자 만족도 > 4.0/5.0

### 운영 지표
- [ ] 시스템 가동률 > 99.9%
- [ ] 평균 복구 시간 < 5분
- [ ] 배포 성공률 100%

## 타임라인

### 옵션 1 (인덱스 재구성) - 권장
| Phase | 작업 | 예상 시간 | 담당자 |
|-------|------|----------|--------|
| 1 | 인덱스 생성 및 설정 | 1시간 | DevOps/Backend |
| 2 | 재인덱싱 스크립트 작성 | 2시간 | Backend |
| 3 | 재인덱싱 실행 | 4-8시간 | 자동 |
| 4 | 코드 업데이트 | 2시간 | Backend |
| 5 | 테스트 및 검증 | 4시간 | QA/Backend |
| 6 | 배포 | 1시간 | DevOps |
| **총계** | | **14-18시간** | |

### 옵션 2 (쿼리 최적화)
| Phase | 작업 | 예상 시간 | 담당자 |
|-------|------|----------|--------|
| 1 | 사전 필터링 구현 | 2시간 | Backend |
| 2 | 캐싱 시스템 | 3시간 | Backend |
| 3 | 성능 튜닝 | 1시간 | Backend |
| 4 | 테스트 | 2시간 | QA/Backend |
| **총계** | | **8시간** | |

## 의사결정 포인트

### 즉시 결정 필요
1. **옵션 선택**: 인덱스 재구성 vs 쿼리 최적화
2. **배포 전략**: Blue-Green vs 직접 전환
3. **다운타임 허용 여부**: 유지보수 모드 가능 여부

### 구현 중 결정
1. 재인덱싱 방법 (Reindex API vs 커스텀 스크립트)
2. 캐싱 전략 (옵션 2 선택 시)
3. HNSW 파라미터 튜닝

## 다음 단계

### 즉시 실행 (사용자 결정 후)
1. [ ] 옵션 선택 확정
2. [ ] 상세 구현 계획 수립
3. [ ] 리소스 할당 (개발자, 서버 등)
4. [ ] 킥오프 미팅

### 1주차 (옵션 1 선택 시)
1. [ ] 새 인덱스 생성
2. [ ] 재인덱싱 스크립트 작성 및 테스트
3. [ ] 재인덱싱 실행

### 2주차
1. [ ] 코드 업데이트 및 테스트
2. [ ] 배포 준비
3. [ ] 배포 실행 및 모니터링

## 참고 문서

- [OpenSearch k-NN Documentation](https://opensearch.org/docs/latest/search-plugins/knn/)
- [HNSW Algorithm](https://arxiv.org/abs/1603.09320)
- [BGE-M3 Model](https://huggingface.co/BAAI/bge-m3)
- 프로젝트 내부 문서:
  - [`walkthrough.md`](file:///home/nuri/.gemini/antigravity/brain/f8ba1185-5a97-4fd5-8d55-a69ce8dfacdc/walkthrough.md)
  - [`implementation_plan.md`](file:///home/nuri/.gemini/antigravity/brain/f8ba1185-5a97-4fd5-8d55-a69ce8dfacdc/implementation_plan.md)
  - [`work_log_2026-02-10.md`](file:///home/nuri/dev/git/patent_board_full/docs/work_log_2026-02-10.md)

---

**작성일**: 2026-02-10  
**최종 수정**: 2026-02-10  
**상태**: 사용자 결정 대기 중  
**우선순위**: 높음
