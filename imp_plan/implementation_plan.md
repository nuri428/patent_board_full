# MCP 기반 고급 분석 기능 UI 통합 플랜

MCP 서버에서 제공하는 OpenSearch(시만틱 검색) 및 Neo4j(네트워크 분석) 기능을 사용자가 웹 화면에서 직접 실행하고 결과를 확인할 수 있도록 통합합니다.

## 핵심 목표
- **백엔드(FastAPI)**: MCP 서버의 도구들을 호출하는 프록시 엔드포인트 구축
- **프론트엔드(React)**: 사용자 입력을 위한 폼과 분석 결과를 시각화할 대시보드 및 상세 페이지 구현

## 단계별 구현 계획

### 1단계: 백엔드 프록시 API 및 서비스 레이어 (Back-end)
MCP 서버와 통신하며 프론트엔드에 필요한 데이터를 정제하여 전달합니다.

#### [MODIFY] [mcp.py](file:///home/nuri/dev/git/patent_board_full/back_end/app/api/v1/endpoints/mcp.py)
- OpenSearch 기반 시만틱 검색 API 엔드포인트 추가 프로젝트
- Neo4j 기반 네트워크 분석(`run_network_analysis`) 및 경쟁사 분석 API 추가
- 기술 매핑(`create_technology_mapping`) 실행 API 추가

#### [NEW] [mcp_service.py](file:///home/nuri/dev/git/patent_board_full/back_end/app/services/mcp_service.py)
- MCP 서버와의 HTTP 통신을 담당하는 클라이언트 클래스 구현 (인증 토큰 처리 포함)

---

### 2단계: 프론트엔드 UI 컴포넌트 (Front-end)
사용자로부터 분석 파라미터를 입력받고 복잡한 결과를 시각적으로 표현합니다.

#### [NEW] [AnalysisWorkbench.jsx](file:///home/nuri/dev/git/patent_board_full/front_end/src/pages/AnalysisWorkbench.jsx)
- **Semantic Search Tab**: 쿼리 입력 및 유사도 기반 특허 목록 표시
- **Network Analysis Tab**: 중심성 지표(Centrality) 및 커뮤니티 구조를 차트(`Chart.js`)나 테이블로 표시
- **Tech Mapping Tab**: 분석 세션별 기술 매핑 실행 및 결과 조회 화면

#### [MODIFY] [App.jsx](file:///home/nuri/dev/git/patent_board_full/front_end/src/App.jsx)
- 신규 분석 워크벤치 페이지 라우팅 추가

---

### 3단계: 데이터 시각화 및 UX 고도화
- **결과 시각화**: Neo4j의 네트워크 분석 결과를 `Chart.js` 또는 `D3.js`를 활용하여 그래프 형태로 시각화 (우선 테이블/차트 데이터 중심)
- **로딩 상태 관리**: 분석 작업이 오래 걸릴 수 있으므로 스켈레톤 UI 또는 프로그레스 바 적용

## 검증 계획

### 자동화 테스트
- `pytest`: 백엔드의 MCP 프록시 엔드포인트 유닛 테스트
- 백엔드에서 MCP 서버로의 요청이 올바른 페이로드와 토큰을 전달하는지 검증

### 수동 검증
1. **시만틱 검색**: 특정 키워드 입력 시 OpenSearch에서 정상적으로 벡터 검색 결과를 가져오는지 확인
2. **네트워크 분석**: 분석 실행 버튼 클릭 후 Neo4j의 GDS 결과(중심성 등)가 화면에 표 형태로 출력되는지 확인
3. **통합 테스트**: 프론트엔드에서 입력된 값이 MCP 서버까지 도달하고 결과가 UI에 최종 반영되는지 확인
