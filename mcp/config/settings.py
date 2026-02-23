import os
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore extra fields in .env
    )

    # Database Configuration
    MARIADB_URL: str = Field(
        "mysql+aiomysql://user:change-me@localhost:3306/patent_db",
        description="Connection URL for the main MariaDB database (aiomysql)",
    )
    PATENTDB_URL: str = Field(
        "mysql+aiomysql://user:change-me@localhost:3306/patent_db",
        description="Connection URL for the patent database (aiomysql)",
    )

    # Neo4j Configuration
    NEO4J_URI: str = Field("bolt://localhost:7687", description="URI for Neo4j database")
    NEO4J_USER: str = Field("neo4j", description="Username for Neo4j")
    NEO4J_PASSWORD: str = Field("change-me", description="Password for Neo4j")
    NEO4J_DATABASE: str = Field("neo4j", description="Neo4j database name")

    OPENSEARCH_HOST: str = Field("localhost", description="OpenSearch host")
    OPENSEARCH_PORT: int = Field(9200, description="OpenSearch port")
    OPENSEARCH_USER: str = Field("change-me", description="OpenSearch username")
    OPENSEARCH_PASSWORD: str = Field("change-me", description="OpenSearch password")
    OPENSEARCH_USE_SSL: bool = Field(False, description="Use SSL for OpenSearch")
    OPENSEARCH_INDEX_PREFIX: str = Field("patents", description="OpenSearch index prefix")

    BGE_M3_MODEL_NAME: str = Field("BAAI/bge-m3", description="BGE-M3 model name")
    BGE_M3_DEVICE: str = Field("cpu", description="BGE-M3 device (cpu/cuda)")
    BGE_M3_USE_FP16: bool = Field(True, description="Use FP16 for BGE-M3")

    # MCP Server Security
    MCP_API_KEY: str | None = Field(None, description="Master API key for MCP server")

    # MCP Server URL (required by client)
    MCP_SERVER_URL: str = Field(
        "http://localhost:8001", description="URL where MCP server is running"
    )

    # Optional: LangSmith/OpenAI (if needed for future extensions, based on .env)
    # OPENAI_API_KEY: str | None = None
    # LANGSMITH_API_KEY: str | None = None

    def validate_security_settings(self) -> bool:
        validation_passed = True

        if self.OPENSEARCH_USER == "change-me":
            logger.warning(
                "OPENSEARCH_USER is set to placeholder value. Configure it via environment variables."
            )
            validation_passed = False

        if self.OPENSEARCH_PASSWORD == "change-me":
            logger.warning(
                "OPENSEARCH_PASSWORD is set to placeholder value. Configure it via environment variables."
            )
            validation_passed = False

        if self.MCP_API_KEY and self.MCP_API_KEY == "change-me":
            logger.warning(
                "MCP_API_KEY is set to placeholder value. Configure a strong key via environment variables."
            )
            validation_passed = False

        if "change-me" in self.MARIADB_URL:
            logger.warning(
                "MARIADB_URL uses placeholder credentials. Configure it via environment variables."
            )
            validation_passed = False

        if "change-me" in self.PATENTDB_URL:
            logger.warning(
                "PATENTDB_URL uses placeholder credentials. Configure it via environment variables."
            )
            validation_passed = False

        if self.NEO4J_PASSWORD == "change-me":
            logger.warning(
                "NEO4J_PASSWORD is set to placeholder value. Configure it via environment variables."
            )
            validation_passed = False

        return validation_passed


settings = Settings(
    MARIADB_URL=os.getenv(
        "MARIADB_URL", "mysql+aiomysql://user:change-me@localhost:3306/patent_db"
    ),
    PATENTDB_URL=os.getenv(
        "PATENTDB_URL", "mysql+aiomysql://user:change-me@localhost:3306/patent_db"
    ),
    NEO4J_URI=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    NEO4J_USER=os.getenv("NEO4J_USER", "neo4j"),
    NEO4J_PASSWORD=os.getenv("NEO4J_PASSWORD", "change-me"),
    NEO4J_DATABASE=os.getenv("NEO4J_DATABASE", "neo4j"),
    OPENSEARCH_HOST=os.getenv("OPENSEARCH_HOST", "localhost"),
    OPENSEARCH_PORT=int(os.getenv("OPENSEARCH_PORT", "9200")),
    OPENSEARCH_USER=os.getenv("OPENSEARCH_USER", "change-me"),
    OPENSEARCH_PASSWORD=os.getenv("OPENSEARCH_PASSWORD", "change-me"),
    OPENSEARCH_USE_SSL=os.getenv("OPENSEARCH_USE_SSL", "false").lower() == "true",
    OPENSEARCH_INDEX_PREFIX=os.getenv("OPENSEARCH_INDEX_PREFIX", "patents"),
    BGE_M3_MODEL_NAME=os.getenv("BGE_M3_MODEL_NAME", "BAAI/bge-m3"),
    BGE_M3_DEVICE=os.getenv("BGE_M3_DEVICE", "cpu"),
    BGE_M3_USE_FP16=os.getenv("BGE_M3_USE_FP16", "true").lower() == "true",
    MCP_API_KEY=os.getenv("MCP_API_KEY"),
    MCP_SERVER_URL=os.getenv("MCP_SERVER_URL", "http://localhost:8001"),
)

if not settings.validate_security_settings():
    logger.warning("MCP security settings validation found placeholder credentials.")
