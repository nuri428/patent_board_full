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


async def check_neo4j():
    print(f"Checking Neo4j Connection to: {settings.NEO4J_URI}")
    try:
        async for session in get_neo4j_session():
            print("Session acquired.")
            result = await session.run("MATCH (n) RETURN count(n) as c")
            record = await result.single()
            print(f"SUCCESS: Connected to Neo4j. Total Nodes: {record['c']}")

            # Check for data
            if record["c"] == 0:
                print("WARNING: Database is empty.")
            return
    except Exception as e:
        print(f"FAILURE: Could not connect to Neo4j. Error: {e}")


if __name__ == "__main__":
    print("Starting System Verification (Docker Internal)...")
    asyncio.run(check_neo4j())
