import asyncio
import sys
import os
from neo4j import AsyncGraphDatabase

# Add mcp path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings


async def inspect_schema():
    print(f"Connecting to Neo4j at {settings.NEO4J_URI}...")

    driver = AsyncGraphDatabase.driver(
        settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
    )

    try:
        async with driver.session(database=settings.NEO4J_DATABASE) as session:
            # 1. Get Node Labels
            print("\n[1] Node Labels:")
            result = await session.run("CALL db.labels()")
            data = await result.data()
            print(f"Raw Data: {data}")
            labels = [list(r.values())[0] for r in data]
            print(f"Found: {labels}")

            # 2. Get Relationship Types
            print("\n[2] Relationship Types:")
            result = await session.run("CALL db.relationshipTypes()")
            data = await result.data()
            print(f"Raw Data: {data}")
            rels = [list(r.values())[0] for r in data]
            print(f"Found: {rels}")

            # 3. Get Schema Visualization (Nodes -> Rel -> Nodes)
            print("\n[3] Schema Relationships (Source -[REL]-> Target):")
            query = """
            MATCH (a)-[r]->(b)
            WITH labels(a) AS local_labels, type(r) AS rel_type, labels(b) AS remote_labels
            RETURN DISTINCT local_labels, rel_type, remote_labels
            LIMIT 50
            """
            result = await session.run(query)
            schema_data = await result.data()
            for row in schema_data:
                src = row["local_labels"][0] if row["local_labels"] else "Unknown"
                tgt = row["remote_labels"][0] if row["remote_labels"] else "Unknown"
                print(f"  ({src}) -[:{row['rel_type']}]-> ({tgt})")

            # 4. Sample Patent Properties
            if "Patent" in labels:
                print("\n[4] Sample 'Patent' Node Properties:")
                result = await session.run("MATCH (p:Patent) RETURN p LIMIT 1")
                data = await result.single()
                if data:
                    print(f"  Keys: {list(data['p'].keys())}")

            # 5. Sample Problem Properties
            if "Problem" in labels:
                print("\n[5] Sample 'Problem' Node Properties:")
                result = await session.run("MATCH (n:Problem) RETURN n LIMIT 1")
                data = await result.single()
                if data:
                    print(f"  Keys: {list(data['n'].keys())}")
                    print(f"  Sample: {data['n']}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await driver.close()


if __name__ == "__main__":
    asyncio.run(inspect_schema())
