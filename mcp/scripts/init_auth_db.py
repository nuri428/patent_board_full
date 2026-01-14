import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from database import auth_engine
from auth.models import Base
from config.settings import settings


async def init_db():
    print("Initializing Auth Database...")
    async with auth_engine.begin() as conn:
        print("Creating tables...")
        await conn.run_sync(Base.metadata.create_all)

    print("Auth Database initialized successfully.")
    await auth_engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())
