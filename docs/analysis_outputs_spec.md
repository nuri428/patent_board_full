# 분석 시스템 결과물 명세서 (Analysis Results Specification)

본 문서는 특허 분석 시스템(Analyzer)을 통해 생성되어 OpenSearch 및 Neo4j에 저장되는 모든 결과물의 구조와 내용을 정의합니다.

> [!IMPORTANT]
> **데이터 추적성**: 모든 분석 결과는 특정 **`AnalysisRun`**에 귀속되며, 각 엔티티 및 관계는 해당 실행 회차를 식별하는 **`analysis_run_id` (또는 `run_id`)**를 공통으로 포함합니다. 이를 통해 분석 시점별 결과 추적 및 이력 관리가 가능합니다.

## 1. OpenSearch 검색 인덱스 결과물

OpenSearch는 주로 **텍스트 검색 및 RAG(Retrieval-Augmented Generation)**를 위한 섹션 단위 데이터를 저장합니다.

### 1.1 주요 인덱스
- **`korean_patents_sections`**: 한국 특허 전문을 섹션별로 분할 저장.
- **`us_patents_sections`**: 미국 특허 전문을 섹션별로 분할 저장.
- **`unified-patents-v1`**: KR/US 통합 인덱스 (하이브리드 검색 및 벡터 검색용).

### 1.2 섹션 데이터 명세
분석기는 특허 전문을 다음과 같은 섹션으로 구분하여 인덱싱합니다.
- **Section Types**: `TITLE`, `ABSTRACT`, `TECHNICAL_FIELD`, `BACKGROUND_ART`, `SUMMARY`, `CLAIMS`, `DETAILED_DESCRIPTION` 등.
- **주요 필드**:
    - `application_number`: 출원번호 (고유 ID 식별자)
    - `section_content`: 해당 섹션의 텍스트 본문.
    - `embedding`: BGE-M3 모델 기반 1024차원 고밀도 벡터 (통합 인덱스 기준).
    - `ipc_codes`, `cpc_codes`: 기술 분류 코드 리스트.

---

## 2. Neo4j 지식 그래프 결과물

Neo4j는 **기술 간 연관성, 유사도, 인적/기관 네트워크 분석** 결과를 저장합니다.

### 2.1 노드(Nodes) 스키마
| 레이블 | 설명 | 주요 속성 |
| :--- | :--- | :--- |
| **Patent** | 특허 엔티티 | `application_number`, `title`, `abstract`, `country_code` |
| **Corporation** | 출원인 / 권리자 / 기업 | `customer_code`, `name`, `name_normalized`, `country` |
| **IPC / CPC** | 국제 특허 분류 | `code`, `section`, `class`, `subclass` |
| **Inventor** | 발명자 | `name` |
| **Technology** | 고도화 기술 분류 (V2) | `technology_id`, `technology_name`, `technology_code` |
| **Keyword** | 추출된 핵심 키워드 | `keyword` |

### 2.2 관계(Relationships) 및 분석 정보
분석 알고리즘에 의해 실시간 또는 배치로 생성되는 관계 데이터입니다.

- **분류 및 소유**:
    - `(Patent)-[:APPLIED_BY]->(Corporation)`: 출원 관계.
    - `(Patent)-[:CLASSIFIED_AS]->(IPC/CPC)`: 표준 분류 관계.
    - `(Patent)-[:BELONGS_TO]->(Technology)`: **V2 매퍼**를 통한 고도화 기술 매핑.
        - `confidence`: 최종 신뢰도 점수 (0.0~1.0).
        - `method`: 분류 방법 (예: `IPC_MAPPING`, `KEYWORD_MATCHING`, `MULTI_METHOD`).
        - `is_partial`: 부문 분류 여부 (Sub-field 미확정 시 `true`).
        - `applied_config_version`: 적용된 정책 버전 (예: `2.1.0`).
        - `synergy_bonus_applied`: 복합 매칭 보너스 적용 여부.
        - `negative_keywords_matched`: 감쇄를 일으킨 부정 키워드 리스트.
        - `confidence_before_cap`: 상한제 적용 전 원본 점수.

### 2.3 고급 네트워크 분석 (GDS 기반)
`run_advanced_network_analysis` 태스크를 통해 수행되는 그래프 데이터 과학(GDS) 분석 결과입니다.

- **중심성 지표 (Centrality)**:
    - `degree_centrality`: 연결 중심성 (영향력 있는 기업/특허 식별).
    - `betweenness_centrality`: 매개 중심성 (기술 중개자 식별).
- **커뮤니티 (Communities)**:
    - `community_id`: Louvain 또는 연결 성분 알고리즘으로 식별된 기술/기업 군집 ID.
- **예측 지표 (Link Prediction)**:
    - `potential_similarity`: 잠재적 유사도 또는 향후 협력 가능성 점수.

---

## 3. 분석 알고리즘 정책 (Policy Details)
V2 매퍼에 적용된 핵심 알고리즘 정책은 `config/classification_settings.json`을 따릅니다.

- **신뢰도 상한 (Confidence Capping)**:
    - 부분 분류(Partial): Max 0.75
    - 전체 분류(Full): Max 1.00
- **부정 키워드 정책 (Negative Keywords)**:
    - 매칭된 부정 키워드당 `weight_decay_factor`(기본 0.3)만큼 감쇄 적용.
- **시너지 보너스 (Synergy Bonus)**:
    - 복수 매칭 방법(IPC+Keyword 등) 적용 시 기본 `1.2배` 보너스 부여.

---

시스템 내 `mapping_tasks.py` 및 `patent_analysis.py`에서 산출하는 종합 분석 요약 정보는 다음과 같습니다.

- **기술 성숙도 지표**: 특정 기술 노드에 연계된 특허의 시간적 흐름 및 인용 관계 분석.
- **분류 신뢰도**: V2 시스템이 부여한 `confidence` 점수를 통해 자동 분류의 정확도 측정.
- **미탐 후보군(False Negatives)**: `--verbose` 분석 시 도출되는, 현재 매핑되지 않았으나 잠재적으로 연관된 키워드 후보군.

---
> [!TIP]
> 모든 특허 데이터의 무결성은 `application_number`를 Key로 하여 RDB, OpenSearch, Neo4j 간에 동기화됩니다.
