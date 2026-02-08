from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from neo4j import GraphDatabase, AsyncGraphDatabase
from opensearchpy import OpenSearch
from typing import AsyncGenerator, Generator
import contextlib
import asyncio

from config.settings import settings

# MariaDB Async Engine (for main application data if needed)
# Not strictly used if we focus on PATENTDB_URL for patents, but good to have if AUTH is separate.
# Based on .env, MARIADB_URL and PATENTDB_URL might be the same or different.
# We will create engines for both if they are distinct, or just one generic one.
# For now, let's create a Session for the main PATENTDB as that seems primary for MCP tools.
# We also need a separate connection for the Auth DB (MARIADB_URL)

# Auth DB Engine (MARIADB_URL)
auth_engine = create_async_engine(settings.MARIADB_URL, echo=False, pool_pre_ping=True)

AuthSessionLocal = async_sessionmaker(
    bind=auth_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_auth_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async session for Auth DB
    """
    async with AuthSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Using PATENTDB_URL for patent data access
patent_engine = create_async_engine(
    settings.PATENTDB_URL, echo=False, pool_pre_ping=True
)

PatentSessionLocal = async_sessionmaker(
    bind=patent_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_patent_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async session for Patent DB (MariaDB)
    """
    async with PatentSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Neo4j Driver (Async)
# Using AsyncGraphDatabase for async support
neo4j_driver = AsyncGraphDatabase.driver(
    settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
)


async def get_neo4j_session():
    """
    Dependency/Context manager for getting Neo4j async session
    """
    async with neo4j_driver.session(database=settings.NEO4J_DATABASE) as session:
        yield session


opensearch_client = OpenSearch(
    hosts=[{
        'host': settings.OPENSEARCH_HOST, 
        'port': settings.OPENSEARCH_PORT
    }],
    http_auth=(settings.OPENSEARCH_USER, settings.OPENSEARCH_PASSWORD),
    use_ssl=settings.OPENSEARCH_USE_SSL,
    verify_certs=settings.OPENSEARCH_USE_SSL,
)


async def get_opensearch_client():
    """
    Async wrapper for the synchronous OpenSearch client
    """
    return opensearch_client


async def close_connections():
    """
    Cleanup function to close DB connections on app shutdown
    """
    await patent_engine.dispose()
    await auth_engine.dispose()
    await neo4j_driver.close()
    # Close synchronous OpenSearch client (run in thread to avoid blocking)
    if hasattr(opensearch_client, 'close'):
        await asyncio.to_thread(opensearch_client.close)
