from neo4j import GraphDatabase
from typing import List, Dict, Optional, Tuple
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class Neo4jPatentSearch:
    def __init__(self, uri: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None):
        self.uri = uri or getattr(settings, 'NEO4J_URI', 'bolt://localhost:7687')
        self.username = username or getattr(settings, 'NEO4J_USERNAME', 'neo4j')
        self.password = password or getattr(settings, 'NEO4J_PASSWORD', 'password')
        self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
    
    def close(self):
        if self.driver:
            self.driver.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def search_patents_by_text(self, 
                              query: str,
                              country_code: Optional[str] = None,
                              limit: int = 20,
                              offset: int = 0) -> List[Dict]:
        """특허 제목, 초록으로 텍스트 검색"""
        with self.driver.session() as session:
            country_filter = f"AND p.country_code = '{country_code}'" if country_code else ""
            
            cypher = f"""
            MATCH (p:Patent)
            WHERE toLower(p.title) CONTAINS toLower($query) 
               OR toLower(p.abstract) CONTAINS toLower($query)
               {country_filter}
            RETURN p.application_number as patent_id,
                   p.document_number as doc_num,
                   p.title as title,
                   p.abstract as abstract,
                   p.country_code as country,
                   p.cpc_main as cpc_main,
                   p.ipc_main as ipc_main,
                   p.indexed_at as indexed_at
            ORDER BY p.indexed_at DESC
            SKIP $offset LIMIT $limit
            """
            
            result = session.run(cypher, query=query, limit=limit, offset=offset)
            return [record.data() for record in result]
    
    def search_patents_by_corporation(self, 
                                    corporation_name: str,
                                    relationship_type: str = 'APPLIED_BY',
                                    limit: int = 20) -> List[Dict]:
        """회사 이름으로 특허 검색"""
        with self.driver.session() as session:
            cypher = f"""
            MATCH (p:Patent)-[r:{relationship_type}]->(c:Corporation)
            WHERE toLower(c.name) CONTAINS toLower($corp_name)
               OR toLower(c.name_normalized) CONTAINS toLower($corp_name)
            RETURN p.application_number as patent_id,
                   p.document_number as doc_num,
                   p.title as title,
                   p.abstract as abstract,
                   p.country_code as country,
                   c.name as corporation,
                   c.customer_code as corp_code,
                   r.order as inventorship_order
            ORDER BY r.order ASC, p.indexed_at DESC
            LIMIT $limit
            """
            
            result = session.run(cypher, corp_name=corporation_name, limit=limit)
            return [record.data() for record in result]
    
    def search_patents_by_inventor(self, 
                                  inventor_name: str,
                                  limit: int = 20) -> List[Dict]:
        """발명자 이름으로 특허 검색"""
        with self.driver.session() as session:
            cypher = """
            MATCH (p:Patent)-[r:INVENTED_BY]->(i:Inventor)
            WHERE toLower(i.name) CONTAINS toLower($inventor_name)
            RETURN p.application_number as patent_id,
                   p.document_number as doc_num,
                   p.title as title,
                   p.abstract as abstract,
                   p.country_code as country,
                   i.name as inventor,
                   i.inventor_id as inventor_id,
                   r.order as inventorship_order
            ORDER BY r.order ASC, p.indexed_at DESC
            LIMIT $limit
            """
            
            result = session.run(cypher, inventor_name=inventor_name, limit=limit)
            return [record.data() for record in result]
    
    def search_patents_by_ipc(self, 
                           ipc_code: str,
                           is_main: bool = False,
                           limit: int = 20) -> List[Dict]:
        """IPC 코드로 특허 검색"""
        with self.driver.session() as session:
            is_main_filter = "AND r.is_main = true" if is_main else ""
            
            cypher = f"""
            MATCH (p:Patent)-[r:CLASSIFIED_AS]->(i:IPC)
            WHERE i.code STARTS WITH $ipc_code
               {is_main_filter}
            RETURN p.application_number as patent_id,
                   p.document_number as doc_num,
                   p.title as title,
                   p.abstract as abstract,
                   p.country_code as country,
                   i.code as ipc_code,
                   r.is_main as is_main_classification
            ORDER BY p.indexed_at DESC
            LIMIT $limit
            """
            
            result = session.run(cypher, ipc_code=ipc_code, limit=limit)
            return [record.data() for record in result]
    
    def search_patents_by_cpc(self, 
                            cpc_code: str,
                            limit: int = 20) -> List[Dict]:
        """CPC 코드로 특허 검색 (US 특허)"""
        with self.driver.session() as session:
            cypher = """
            MATCH (p:Patent {country_code: 'US'})
            WHERE p.cpc_main STARTS WITH $cpc_code
            RETURN p.application_number as patent_id,
                   p.document_number as doc_num,
                   p.title as title,
                   p.abstract as abstract,
                   p.country_code as country,
                   p.cpc_main as cpc_main
            ORDER BY p.indexed_at DESC
            LIMIT $limit
            """
            
            result = session.run(cypher, cpc_code=cpc_code, limit=limit)
            return [record.data() for record in result]
    
    def search_patents_by_keyword(self, 
                                keywords: List[str],
                                country_code: Optional[str] = None,
                                min_frequency: int = 1,
                                limit: int = 20) -> List[Dict]:
        """키워드로 특허 검색 (KR 특허 주로)"""
        with self.driver.session() as session:
            country_filter = f"AND p.country_code = '{country_code}'" if country_code else ""
            keyword_list = ', '.join([f"'{kw}'" for kw in keywords])
            
            cypher = f"""
            MATCH (p:Patent)-[r:CONTAINS_KEYWORD]->(k:Keyword)
            WHERE k.keyword IN [{keyword_list}]
               AND r.frequency >= $min_frequency
               {country_filter}
            WITH p, collect(k.keyword) as matched_keywords, sum(r.frequency) as total_freq
            RETURN p.application_number as patent_id,
                   p.document_number as doc_num,
                   p.title as title,
                   p.abstract as abstract,
                   p.country_code as country,
                   matched_keywords,
                   total_freq
            ORDER BY total_freq DESC, p.indexed_at DESC
            LIMIT $limit
            """
            
            result = session.run(cypher, min_frequency=min_frequency, limit=limit)
            return [record.data() for record in result]
    
    def search_patents_by_technology(self, 
                                   technology_id: str,
                                   min_confidence: float = 0.5,
                                   limit: int = 20) -> List[Dict]:
        """기술 분류로 특허 검색"""
        with self.driver.session() as session:
            cypher = """
            MATCH (p:Patent)-[r:BELONGS_TO]->(t:Technology)
            WHERE t.technology_id = $tech_id
               AND r.confidence >= $min_confidence
            RETURN p.application_number as patent_id,
                   p.document_number as doc_num,
                   p.title as title,
                   p.abstract as abstract,
                   p.country_code as country,
                   t.technology_id as technology_id,
                   r.confidence as confidence
            ORDER BY r.confidence DESC, p.indexed_at DESC
            LIMIT $limit
            """
            
            result = session.run(cypher, tech_id=technology_id, min_confidence=min_confidence, limit=limit)
            return [record.data() for record in result]
    
    def search_similar_patents(self, 
                             patent_id: str,
                             similarity_threshold: float = 0.7,
                             limit: int = 20) -> List[Dict]:
        """유사 특허 검색 (KR: RELATED_TO, US: SIMILAR_TO)"""
        with self.driver.session() as session:
            cypher = """
            MATCH (p1:Patent)-[r:RELATED_TO|SIMILAR_TO]->(p2:Patent)
            WHERE (p1.application_number = $patent_id OR p1.document_number = $patent_id)
               AND r.similarity >= $threshold
            RETURN p2.application_number as patent_id,
                   p2.document_number as doc_num,
                   p2.title as title,
                   p2.abstract as abstract,
                   p2.country_code as country,
                   type(r) as relationship_type,
                   r.similarity as similarity_score
            ORDER BY r.similarity DESC
            LIMIT $limit
            """
            
            result = session.run(cypher, patent_id=patent_id, threshold=similarity_threshold, limit=limit)
            return [record.data() for record in result]
    
    def search_by_problem_solution(self, 
                                 problem_text: str = None,
                                 solution_text: str = None,
                                 limit: int = 20) -> List[Dict]:
        """문제-해결책 기반 특허 검색 (US 특허)"""
        with self.driver.session() as session:
            conditions = []
            params = {}
            
            if problem_text:
                conditions.append("toLower(pr.description) CONTAINS toLower($problem_text)")
                params['problem_text'] = problem_text
            
            if solution_text:
                conditions.append("toLower(sol.description) CONTAINS toLower($solution_text)")
                params['solution_text'] = solution_text
            
            where_clause = " AND ".join(conditions) if conditions else "true"
            
            cypher = f"""
            MATCH (p:Patent {{country_code: 'US'}})
            OPTIONAL MATCH (p)-[:SOLVES]->(pr:Problem)
            OPTIONAL MATCH (p)-[:USES]->(sol:Solution)
            WHERE {where_clause}
            RETURN p.application_number as patent_id,
                   p.document_number as doc_num,
                   p.title as title,
                   p.abstract as abstract,
                   pr.description as problem,
                   sol.description as solution
            ORDER BY p.indexed_at DESC
            LIMIT $limit
            """
            
            params['limit'] = limit
            result = session.run(cypher, **params)
            return [record.data() for record in result]
    
    def get_patent_details_with_relationships(self, patent_id: str) -> Optional[Dict]:
        """특허 상세 정보와 관계 정보 조회"""
        with self.driver.session() as session:
            cypher = """
            MATCH (p:Patent)
            WHERE p.application_number = $patent_id OR p.document_number = $patent_id
            OPTIONAL MATCH (p)-[applied:APPLIED_BY]->(corp_applied:Corporation)
            OPTIONAL MATCH (p)-[owned:OWNED_BY]->(corp_owned:Corporation)
            OPTIONAL MATCH (p)-[invented:INVENTED_BY]->(inventor:Inventor)
            OPTIONAL MATCH (p)-[classified:CLASSIFIED_AS]->(ipc:IPC)
            OPTIONAL MATCH (p)-[belongs:BELONGS_TO]->(tech:Technology)
            OPTIONAL MATCH (p)-[contains:CONTAINS_KEYWORD]->(keyword:Keyword)
            OPTIONAL MATCH (p)-[solves:SOLVES]->(problem:Problem)
            OPTIONAL MATCH (p)-[uses:USES]->(solution:Solution)
            RETURN p,
                   collect(DISTINCT {
                       corporation: corp_applied,
                       type: 'APPLIED_BY',
                       order: applied.order
                   }) as applied_by,
                   collect(DISTINCT {
                       corporation: corp_owned,
                       type: 'OWNED_BY',
                       order: owned.order
                   }) as owned_by,
                   collect(DISTINCT {
                       inventor: inventor,
                       type: 'INVENTED_BY',
                       order: invented.order
                   }) as invented_by,
                   collect(DISTINCT {
                       ipc: ipc,
                       type: 'CLASSIFIED_AS',
                       is_main: classified.is_main
                   }) as classifications,
                   collect(DISTINCT {
                       technology: tech,
                       type: 'BELONGS_TO',
                       confidence: belongs.confidence
                   }) as technologies,
                   collect(DISTINCT {
                       keyword: keyword,
                       type: 'CONTAINS_KEYWORD',
                       frequency: contains.frequency,
                       tf_idf: contains.tf_idf
                   }) as keywords,
                   collect(DISTINCT {
                       problem: problem,
                       type: 'SOLVES'
                   }) as problems,
                   collect(DISTINCT {
                       solution: solution,
                       type: 'USES'
                   }) as solutions
            """
            
            result = session.run(cypher, patent_id=patent_id).single()
            if result:
                data = result.data()
                patent_data = dict(data['p'])
                patent_data['relationships'] = {
                    'applied_by': data['applied_by'],
                    'owned_by': data['owned_by'],
                    'invented_by': data['invented_by'],
                    'classifications': data['classifications'],
                    'technologies': data['technologies'],
                    'keywords': data['keywords'],
                    'problems': data['problems'],
                    'solutions': data['solutions']
                }
                return patent_data
            return None
    
    def advanced_search(self, 
                       query: Optional[str] = None,
                       corporation: Optional[str] = None,
                       inventor: Optional[str] = None,
                       ipc_code: Optional[str] = None,
                       cpc_code: Optional[str] = None,
                       keywords: Optional[List[str]] = None,
                       country_code: Optional[str] = None,
                       limit: int = 20,
                       offset: int = 0) -> List[Dict]:
        """통합 고급 검색"""
        with self.driver.session() as session:
            conditions = []
            params = {'limit': limit, 'offset': offset}
            
            if query:
                conditions.append("(toLower(p.title) CONTAINS toLower($query) OR toLower(p.abstract) CONTAINS toLower($query))")
                params['query'] = query
            
            if corporation:
                conditions.append("(p)-[:APPLIED_BY|OWNED_BY]->(c:Corporation WHERE toLower(c.name) CONTAINS toLower($corporation))")
                params['corporation'] = corporation
            
            if inventor:
                conditions.append("(p)-[:INVENTED_BY]->(i:Inventor WHERE toLower(i.name) CONTAINS toLower($inventor))")
                params['inventor'] = inventor
            
            if ipc_code:
                conditions.append("(p)-[:CLASSIFIED_AS]->(ipc:IPC WHERE ipc.code STARTS WITH $ipc_code)")
                params['ipc_code'] = ipc_code
            
            if cpc_code:
                conditions.append("p.cpc_main STARTS WITH $cpc_code")
                params['cpc_code'] = cpc_code
            
            if keywords:
                conditions.append("(p)-[:CONTAINS_KEYWORD]->(k:Keyword WHERE k.keyword IN $keywords)")
                params['keywords'] = keywords
            
            if country_code:
                conditions.append("p.country_code = $country_code")
                params['country_code'] = country_code
            
            where_clause = " AND ".join(conditions) if conditions else "true"
            
            cypher = f"""
            MATCH (p:Patent)
            WHERE {where_clause}
            RETURN p.application_number as patent_id,
                   p.document_number as doc_num,
                   p.title as title,
                   p.abstract as abstract,
                   p.country_code as country,
                   p.cpc_main as cpc_main,
                   p.ipc_main as ipc_main,
                   p.indexed_at as indexed_at
            ORDER BY p.indexed_at DESC
            SKIP $offset LIMIT $limit
            """
            
            result = session.run(cypher, **params)
            return [record.data() for record in result]
    
    def get_patent_network(self, patent_id: str, depth: int = 2) -> Dict:
        """특허 관계망 시각화 데이터 조회"""
        with self.driver.session() as session:
            cypher = """
            MATCH (p:Patent)
            WHERE p.application_number = $patent_id OR p.document_number = $patent_id
            MATCH (p)-[r*1..{depth}]-(related)
            RETURN p as center_patent,
                   collect(DISTINCT related) as related_patents,
                   collect(DISTINCT r) as relationships
            """
            
            result = session.run(cypher, patent_id=patent_id, depth=depth).single()
            if result:
                return {
                    'center_patent': dict(result['center_patent']),
                    'related_patents': [dict(node) for node in result['related_patents'] if dict(node)],
                    'relationships': [dict(rel) for rel in result['relationships']]
                }
            return None


class MCPPatentSearch:
    """MCP(Microservice Control Panel)에서 사용할 Neo4j 특허 검색 통합 클래스"""
    
    def __init__(self):
        self.neo4j_search = Neo4jPatentSearch()
    
    def search_by_application_number(self, application_number: str) -> Optional[Dict]:
        """출원번호로 특허 검색"""
        return self.neo4j_search.get_patent_details_with_relationships(application_number)
    
    def search_by_document_number(self, document_number: str) -> Optional[Dict]:
        """문서번호(등록번호)로 특허 검색 (US 특허)"""
        return self.neo4j_search.get_patent_details_with_relationships(document_number)
    
    def text_search(self, query: str, country: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """텍스트 기반 특허 검색"""
        return self.neo4j_search.search_patents_by_text(query, country, limit)
    
    def corporation_search(self, corp_name: str, relationship: str = 'APPLIED_BY', limit: int = 20) -> List[Dict]:
        """회사 이름으로 특허 검색"""
        return self.neo4j_search.search_patents_by_corporation(corp_name, relationship, limit)
    
    def inventor_search(self, inventor_name: str, limit: int = 20) -> List[Dict]:
        """발명자 이름으로 특허 검색"""
        return self.neo4j_search.search_patents_by_inventor(inventor_name, limit)
    
    def classification_search(self, code: str, classification_type: str = 'ipc', limit: int = 20) -> List[Dict]:
        """분류 코드로 검색 (IPC 또는 CPC)"""
        if classification_type.lower() == 'cpc':
            return self.neo4j_search.search_patents_by_cpc(code, limit)
        else:
            return self.neo4j_search.search_patents_by_ipc(code, False, limit)
    
    def keyword_search(self, keywords: List[str], country: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """키워드로 특허 검색"""
        return self.neo4j_search.search_patents_by_keyword(keywords, country, 1, limit)
    
    def similarity_search(self, patent_id: str, threshold: float = 0.7, limit: int = 20) -> List[Dict]:
        """유사 특허 검색"""
        return self.neo4j_search.search_similar_patents(patent_id, threshold, limit)
    
    def advanced_search(self, **search_params) -> List[Dict]:
        """고급 검색"""
        return self.neo4j_search.advanced_search(**search_params)
    
    def get_patent_network(self, patent_id: str, depth: int = 2) -> Dict:
        """특허 관계망 데이터 조회"""
        return self.neo4j_search.get_patent_network(patent_id, depth)