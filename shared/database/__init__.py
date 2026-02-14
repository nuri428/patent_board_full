from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from neo4j import GraphDatabase
from typing import AsyncGenerator
import logging

from back_end.app.core.config import settings


logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


mariadb_engine = create_async_engine(
    settings.MARIADB_URL,
    echo=True,
    future=True,
)

mariadb_session_factory = async_sessionmaker(
    mariadb_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Backward-compatible alias used across backend modules
AsyncSessionLocal = mariadb_session_factory

# Patent Database (for patent search)
patentdb_engine = create_async_engine(
    settings.PATENTDB_URL,
    echo=True,
    future=True,
)

patentdb_session_factory = async_sessionmaker(
    patentdb_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_mariadb_db() -> AsyncGenerator[AsyncSession, None]:
    async with mariadb_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


class Neo4jConnection:
    def __init__(self):
        self.driver = None
        self._initialize_driver()

    def _initialize_driver(self):
        try:
            self.driver = GraphDatabase.driver(
                settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
        except Exception:
            logger.exception("Failed to connect to Neo4j")

    def close(self):
        if self.driver:
            self.driver.close()

    def get_session(self):
        if self.driver:
            return self.driver.session()
        raise RuntimeError("Neo4j driver not initialized")


neo4j_connection = Neo4jConnection()


def get_neo4j_db():
    return neo4j_connection.get_session()


async def get_patentdb() -> AsyncGenerator[AsyncSession, None]:
    async with patentdb_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


get_db = get_mariadb_db
