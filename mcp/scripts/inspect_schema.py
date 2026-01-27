import asyncio
import os
import sys

# Ensure we can import from mcp root
sys.path.append("/app/mcp")

try:
    from database import get_neo4j_session
    from config.settings import settings
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)


async def inspect():
    print("Inspecting Neo4j Schema... VERSION 2")
    async for session in get_neo4j_session():
        # 1. Count Problem nodes & Get Properties
        res = await session.run("MATCH (p:Problem) RETURN p LIMIT 1")
        rec = await res.single()
        if rec:
            node = rec["p"]
            print(f"Problem Node Properties: {dict(node)}")
        else:
            print("Problem Nodes: 0")

        # 2. Check Labels present
        res = await session.run("CALL db.labels() YIELD label")
        labels = [r["label"] for r in await res.data()]
        print(f"All Labels: {labels}")

        # 3. Check Relationship Types
        res = await session.run("CALL db.relationshipTypes() YIELD relationshipType")
        rels = [r["relationshipType"] for r in await res.data()]
        print(f"All Relationships: {rels}")

        # 4. Check SOLVES connection
        res = await session.run("MATCH ()-[r:SOLVES]->() RETURN count(r) as count")
        rec = await res.single()
        print(f"SOLVES Relationships: {rec['count']}")

        return


if __name__ == "__main__":
    asyncio.run(inspect())
