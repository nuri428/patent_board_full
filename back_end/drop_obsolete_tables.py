import sys
import os
import asyncio
from sqlalchemy import text
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load .env
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(env_path)

from shared.database import mariadb_engine


async def drop_tables():
    print("Dropping 'report_patents' and 'patents' tables...")
    try:
        async with mariadb_engine.begin() as conn:
            # We must drop report_patents first because it has a FK to patents (previously)
            # Even if we removed the FK in code, the DB still has it.
            await conn.execute(text("DROP TABLE IF EXISTS report_patents"))
            await conn.execute(text("DROP TABLE IF EXISTS patents"))

        print("✅ Tables dropped successfully!")
    except Exception as e:
        print(f"❌ Error dropping tables: {e}")
    finally:
        await mariadb_engine.dispose()


if __name__ == "__main__":
    asyncio.run(drop_tables())
