from typing import List, Dict, Any, Optional
from database import get_neo4j_session
from fastapi import HTTPException


"""
Neo4j Index Strategy Documentation
==================================

INDEXING STRATEGY:
The patent graph uses Neo4j's native indexing capabilities for optimal query performance.

CURRENT INDEXES (to be created in Neo4j):
----------------------------------------
1. Patent Node Indexes:
   - CREATE INDEX patent_id_idx IF NOT EXISTS FOR (p:Patent) ON (p.patent_id)
   - CREATE INDEX patent_app_number_idx IF NOT EXISTS FOR (p:Patent) ON (p.application_number)
   - CREATE INDEX patent_reg_number_idx IF NOT EXISTS FOR (p:Patent) ON (p.registration_number)
   - CREATE INDEX patent_title_idx IF NOT EXISTS FOR (p:Patent) ON (p.title)

2. Technology Node Indexes:
   - CREATE INDEX tech_id_idx IF NOT EXISTS FOR (t:Technology) ON (t.technology_id)
   - CREATE INDEX tech_code_idx IF NOT EXISTS FOR (t:Technology) ON (t.technology_code)

3. Corporation Node Indexes:
   - CREATE INDEX corp_name_idx IF NOT EXISTS FOR (c:Corporation) ON (c.name)
   - CREATE INDEX corp_code_idx IF NOT EXISTS FOR (c:Corporation) ON (c.customer_code)

4. Inventor Node Indexes:
   - CREATE INDEX inventor_name_idx IF NOT EXISTS FOR (i:Inventor) ON (i.name)

5. Constraint Indexes (Unique):
   - CREATE CONSTRAINT patent_app_number_unique IF NOT EXISTS
     FOR (p:Patent) REQUIRE p.application_number IS UNIQUE
   - CREATE CONSTRAINT tech_id_unique IF NOT EXISTS
     FOR (t:Technology) REQUIRE t.technology_id IS UNIQUE

QUERY OPTIMIZATION PATTERNS:
--------------------------
1. MATCH with property filters use indexes automatically
2. Full-text search uses: CALL db.index.fulltext.queryNodes()
3. Relationship traversal optimized by direction

PERFORMANCE NOTES:
----------------
- Patent lookups by application_number are primary key lookups (fastest)
- Technology code lookups use B-tree indexes
- Full-text search on titles/descriptions uses Lucene indexes
- Relationship traversals benefit from dense node optimization

RECOMMENDED MAINTENANCE:
----------------------
- Run CALL db.stats.retrieve('GRAPH COUNTS') monthly
- Monitor index selectivity via SHOW INDEXES
- Rebuild indexes if selectivity drops below 0.5
"""


class GraphDatabase:
    @staticmethod
    async def get_competitors(company_name: str) -> List[Dict[str, Any]]:
        """
        Find competitors based on 'COMPETES_WITH' relationship.
        """
        query = """
        MATCH (c1:Corporation)-[r:COMPETES_WITH]->(c2:Corporation)
        WHERE toLower(c1.name) CONTAINS toLower($company_name)
        RETURN c1.name as company, c2.name as competitor, coalesce(r.strength, 0) as strength
        LIMIT 20
        """
        async for session in get_neo4j_session():
            result = await session.run(query, company_name=company_name)
            records = await result.data()
            return records
        return []

    @staticmethod
    async def search_by_problem_solution(keyword: str) -> List[Dict[str, Any]]:
        """
        Find patents that solve a problem matching the keyword.
        Path: (Patent)-[:SOLVES]->(Problem) or (Patent)-[:USES]->(Solution)-[:SOLVES]->(Problem)
        """
        # Note: Based on schema inspection, the primary path seems to be:
        # (Patent)-[:SOLVES]->(Problem) OR (Solution)-[:SOLVES]->(Problem)
        # We will check both direct Patent->Problem and indirect Patent->Solution->Problem
        query = """
        MATCH (p:Problem)
        WHERE toLower(p.description) CONTAINS toLower($keyword)
        
        OPTIONAL MATCH (pat:Patent)-[:SOLVES]->(p)
        OPTIONAL MATCH (pat2:Patent)-[:USES]->(sol:Solution)-[:SOLVES]->(p)
        
        WITH p, coalesce(pat, pat2) as patent, sol
        WHERE patent IS NOT NULL
        
        RETURN 
            p.description as problem,
            sol.description as solution,
            patent.registration_number as patent_number,
            patent.title as title
        LIMIT 10
        """
        async for session in get_neo4j_session():
            result = await session.run(query, keyword=keyword)
            records = await result.data()
            return records
        return []

    @staticmethod
    async def get_tech_cluster(tech_keyword: str) -> List[Dict[str, Any]]:
        """
        Find technology clusters and related patents.
        Path: (Patent)-[:BELONGS_TO]->(Technology)
        """
        query = """
        MATCH (t:Technology)
        WHERE toUpper(t.code) CONTAINS toUpper($keyword)
        MATCH (p:Patent)-[:BELONGS_TO]->(t)
        RETURN 
            t.code as technology_code,
            t.level as technology_level,
            count(p) as patent_count,
            collect(p.title)[..5] as top_patents
        ORDER BY patent_count DESC
        LIMIT 10
        """
        async for session in get_neo4j_session():
            result = await session.run(query, keyword=tech_keyword)
            records = await result.data()
            return records
        return []

    @staticmethod
    async def find_path(start_name: str, end_name: str) -> List[Dict[str, Any]]:
        """
        Find shortest path between two entities (e.g. Corporations).
        """
        query = """
        MATCH (start), (end)
        WHERE (start:Corporation OR start:Inventor) AND toLower(start.name) CONTAINS toLower($start_name)
          AND (end:Corporation OR end:Inventor) AND toLower(end.name) CONTAINS toLower($end_name)
          AND id(start) <> id(end)
        
        MATCH p = shortestPath((start)-[*..4]-(end))
        RETURN 
            [n in nodes(p) | labels(n)[0] + ': ' + coalesce(n.name, n.title, n.text, 'Unknown')] as path_nodes,
            length(p) as distance
        LIMIT 5
        """
        async for session in get_neo4j_session():
            result = await session.run(query, start_name=start_name, end_name=end_name)
            records = await result.data()
            return records
        return []

    @staticmethod
    async def run_advanced_network_analysis() -> Dict[str, Any]:
        results = {}

        degree_centrality_query = """
        MATCH (n)
        WHERE n:Corporation OR n:Patent OR n:Technology
        WITH n, size((n)--()) as degree
        WHERE degree > 0
        RETURN 
            labels(n)[0] as node_type,
            coalesce(n.name, n.title, n.technology_name) as name,
            degree,
            n.application_number as patent_id,
            n.customer_code as corp_id
        ORDER BY degree DESC
        LIMIT 20
        """

        betweenness_centrality_query = """
        MATCH (n)
        WHERE n:Corporation OR n:Technology
        WITH n, size((n)-[]-()) as connections
        WHERE connections > 2
        MATCH paths = allShortestPaths((start)-[*..3]-(end))
        WHERE ANY(node IN nodes(paths) WHERE node = n)
        WITH n, count(paths) as path_count
        RETURN 
            labels(n)[0] as node_type,
            coalesce(n.name, n.technology_name) as name,
            path_count as betweenness_score
        ORDER BY path_count DESC
        LIMIT 10
        """

        collaboration_potential_query = """
        MATCH (c1:Corporation)
        MATCH (c2:Corporation)
        WHERE c1 <> c2
        AND NOT (c1)-[]-(c2)
        
        OPTIONAL MATCH (c1)-[:BELONGS_TO]->(t:Technology)<-[:BELONGS_TO]-(c2)
        OPTIONAL MATCH (c1)<-[:APPLIED_BY]-(i:Inventor)-[:APPLIED_BY]->(c2)
        
        WITH c1, c2, 
             count(DISTINCT t) as shared_technologies,
             count(DISTINCT i) as shared_inventors
        
        WHERE shared_technologies > 0 OR shared_inventors > 0
        
        RETURN 
            c1.name as company1,
            c2.name as company2,
            shared_technologies,
            shared_inventors,
            (shared_technologies * 2 + shared_inventors * 3) as collaboration_score
        ORDER BY collaboration_score DESC
        LIMIT 15
        """

        network_structure_query = """
        MATCH (n1)-[r]-(n2)
        WHERE (n1:Corporation OR n1:Technology) AND (n2:Corporation OR n2:Technology)
        WITH n1, n2, r
        ORDER BY n1.name, n2.name
        RETURN 
            toString(id(n1)) + '-' + toString(id(n2)) as edge_id,
            labels(n1)[0] as node1_type,
            coalesce(n1.name, n1.technology_name) as node1_name,
            type(r) as relationship_type,
            labels(n2)[0] as node2_type,
            coalesce(n2.name, n2.technology_name) as node2_name
        LIMIT 50
        """

        async for session in get_neo4j_session():
            degree_result = await session.run(degree_centrality_query)
            results["degree_centrality"] = await degree_result.data()

            betweenness_result = await session.run(betweenness_centrality_query)
            results["betweenness_centrality"] = await betweenness_result.data()

            network_result = await session.run(network_structure_query)
            results["community_edges"] = await network_result.data()

            collaboration_result = await session.run(collaboration_potential_query)
            results["link_prediction"] = await collaboration_result.data()

            return results

        return {}

    @staticmethod
    async def create_technology_mapping(
        patent_id: str,
        technology_id: str,
        confidence: float,
        method: str,
        analysis_run_id: str,
        is_partial: bool = False,
        applied_config_version: str = "2.1.0",
        synergy_bonus_applied: bool = False,
        negative_keywords_matched: Optional[List[str]] = None,
        confidence_before_cap: Optional[float] = None,
    ) -> Dict[str, Any]:
        negative_keywords_matched = negative_keywords_matched or []
        confidence_before_cap = (
            confidence_before_cap if confidence_before_cap is not None else confidence
        )

        query = """
        MATCH (p:Patent {application_number: $patent_id})
        MATCH (t:Technology {technology_id: $technology_id})
        
        MERGE (p)-[r:BELONGS_TO]->(t)
        SET r.confidence = $confidence,
            r.method = $method,
            r.is_partial = $is_partial,
            r.applied_config_version = $applied_config_version,
            r.synergy_bonus_applied = $synergy_bonus_applied,
            r.negative_keywords_matched = $negative_keywords_matched,
            r.confidence_before_cap = $confidence_before_cap,
            r.analysis_run_id = $analysis_run_id,
            r.created_at = datetime()
        
        RETURN p, r, t
        """

        async for session in get_neo4j_session():
            result = await session.run(
                query,
                {
                    "patent_id": patent_id,
                    "technology_id": technology_id,
                    "confidence": confidence,
                    "method": method,
                    "is_partial": is_partial,
                    "applied_config_version": applied_config_version,
                    "synergy_bonus_applied": synergy_bonus_applied,
                    "negative_keywords_matched": negative_keywords_matched,
                    "confidence_before_cap": confidence_before_cap,
                    "analysis_run_id": analysis_run_id,
                },
            )
            record = await result.single()

            if record:
                return {
                    "patent_id": record["p"]["application_number"],
                    "technology_id": record["t"]["technology_id"],
                    "technology_name": record["t"].get("technology_name"),
                    "confidence": confidence,
                    "method": method,
                    "analysis_run_id": analysis_run_id,
                }

        raise HTTPException(status_code=404, detail="Patent or Technology not found")

    @staticmethod
    async def get_technology_mappings(
        analysis_run_id: Optional[str] = None,
        patent_id: Optional[str] = None,
        technology_id: Optional[str] = None,
        confidence_threshold: float = 0.0,
    ) -> List[Dict[str, Any]]:
        query_conditions = []
        parameters = {}

        base_query = """
        MATCH (p:Patent)-[r:BELONGS_TO]->(t:Technology)
        WHERE 1=1
        """

        if analysis_run_id:
            query_conditions.append("r.analysis_run_id = $analysis_run_id")
            parameters["analysis_run_id"] = analysis_run_id

        if patent_id:
            query_conditions.append("p.application_number = $patent_id")
            parameters["patent_id"] = patent_id

        if technology_id:
            query_conditions.append("t.technology_id = $technology_id")
            parameters["technology_id"] = technology_id

        query_conditions.append("r.confidence >= $confidence_threshold")
        parameters["confidence_threshold"] = confidence_threshold

        if query_conditions:
            base_query += " AND " + " AND ".join(query_conditions)

        base_query += """
        RETURN 
            p.application_number as patent_id,
            p.title as patent_title,
            t.technology_id as technology_id,
            t.technology_name as technology_name,
            t.technology_code as technology_code,
            r.confidence as confidence,
            r.method as method,
            r.is_partial as is_partial,
            r.applied_config_version as applied_config_version,
            r.synergy_bonus_applied as synergy_bonus_applied,
            r.negative_keywords_matched as negative_keywords_matched,
            r.confidence_before_cap as confidence_before_cap,
            r.analysis_run_id as analysis_run_id
        ORDER BY r.confidence DESC
        LIMIT 100
        """

        async for session in get_neo4j_session():
            result = await session.run(base_query, parameters)
            records = await result.data()
            return records

        return []
