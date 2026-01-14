from typing import List, Dict, Any, Optional
from database import get_neo4j_session


class GraphDatabase:
    @staticmethod
    async def get_competitors(company_name: str) -> List[Dict[str, Any]]:
        """
        Find competitors based on 'COMPETES_WITH' relationship.
        """
        query = """
        MATCH (c1:Corporation)-[r:COMPETES_WITH]->(c2:Corporation)
        WHERE toLower(c1.name) CONTAINS toLower($company_name)
        RETURN c1.name as company, c2.name as competitor, r.strength as strength
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
        WHERE toLower(p.text) CONTAINS toLower($keyword)
        
        OPTIONAL MATCH (pat:Patent)-[:SOLVES]->(p)
        OPTIONAL MATCH (pat2:Patent)-[:USES]->(sol:Solution)-[:SOLVES]->(p)
        
        WITH p, coalesce(pat, pat2) as patent, sol
        WHERE patent IS NOT NULL
        
        RETURN 
            p.text as problem,
            sol.text as solution,
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
        WHERE toLower(t.name) CONTAINS toLower($keyword)
        MATCH (p:Patent)-[:BELONGS_TO]->(t)
        RETURN 
            t.name as technology,
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
