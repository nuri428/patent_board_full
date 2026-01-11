import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

# Load env
load_dotenv()

# Get base credentials
MARIADB_HOST = os.getenv("MARIADB_HOST", "192.168.0.10")
MARIADB_PORT = os.getenv("MARIADB_PORT", "3306")
MARIADB_USER = os.getenv("MARIADB_USER", "pa_admin")
MARIADB_PASSWORD = os.getenv("MARIADB_PASSWORD", "Manhae428!")

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://192.168.0.10:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "manhae428!")


async def check_mariadb(db_name, label):
    url = f"mysql+aiomysql://{MARIADB_USER}:{MARIADB_PASSWORD}@{MARIADB_HOST}:{MARIADB_PORT}/{db_name}"
    print(f"Checking {label} - {db_name}...")
    try:
        engine = create_async_engine(url)
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        print(f"✅ {label} ({db_name}): Connection Successful")
        return True
    except Exception as e:
        print(f"❌ {label} ({db_name}): Connection Failed - {str(e)}")
        return False


def check_neo4j(db_name, label):
    print(f"Checking {label} - {db_name}...")
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        # Verify connectivity
        driver.verify_connectivity()

        # Verify database existence by opening a session specifically for it
        with driver.session(database=db_name) as session:
            session.run("RETURN 1")

        print(f"✅ {label} ({db_name}): Connection Successful")
        driver.close()
        return True
    except Exception as e:
        print(f"❌ {label} ({db_name}): Connection Failed - {str(e)}")
        return False


async def main():
    print("--- Verifying Database Connections ---")

    # 1. Backend -> pa_system
    await check_mariadb("pa_system", "BackEnd MariaDB")

    # 2. MCP -> patent_db
    await check_mariadb("patent_db", "MCP MariaDB")

    # 3. MCP -> patentsKg (Neo4j)
    # Note: Neo4j community edition often only supports one 'neo4j' database,
    # but Enterprise allows multiple. We will test 'patentsKg'.
    check_neo4j("patentsKg", "MCP Neo4j")


if __name__ == "__main__":
    asyncio.run(main())
