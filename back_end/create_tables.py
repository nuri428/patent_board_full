import sys
import os
import asyncio
from sqlalchemy import text

# Add parent directory to path to allow importing shared
# This is necessary because 'shared' is outside of 'back_end'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

# Load .env from project root
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(env_path)

from shared.database import mariadb_engine, Base

# Import all models to ensure they are registered with Base.metadata
# We import from app.models because the script is inside back_end
from app.models import (
    User,
    Report,
    ReportPatent,
    ChatSession,
    ChatMessage,
    Notification,
    ReportAnalytics,
    SearchQuery,
    SystemConfig,
    Patent,
    ReportVersion,
    LLMUsage,
    Workspace,
    WorkspaceMember,
    PromptTemplate,
)


async def init_tables():
    print("Initializing database tables for 'pa_system'...")

    try:
        async with mariadb_engine.begin() as conn:
            # Create all tables defined in the metadata
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Tables created successfully!")

        # Verify table creation
        async with mariadb_engine.connect() as conn:
            result = await conn.execute(text("SHOW TABLES"))
            tables = result.fetchall()
            print("\nList of tables in DB:")
            for table in tables:
                print(f"- {table[0]}")

    except Exception as e:
        print(f"❌ Error creating tables: {e}")
    finally:
        await mariadb_engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_tables())
