import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore extra fields in .env
    )

    # Database Configuration
    MARIADB_URL: str = Field(
        ..., description="Connection URL for the main MariaDB database (aiomysql)"
    )
    PATENTDB_URL: str = Field(
        ..., description="Connection URL for the patent database (aiomysql)"
    )

    # Neo4j Configuration
    NEO4J_URI: str = Field(..., description="URI for Neo4j database")
    NEO4J_USER: str = Field(..., description="Username for Neo4j")
    NEO4J_PASSWORD: str = Field(..., description="Password for Neo4j")
    NEO4J_DATABASE: str = Field("neo4j", description="Neo4j database name")

    OPENSEARCH_HOST: str = Field("localhost", description="OpenSearch host")
    OPENSEARCH_PORT: int = Field(9200, description="OpenSearch port")
    OPENSEARCH_USER: str = Field("admin", description="OpenSearch username")
    OPENSEARCH_PASSWORD: str = Field("admin", description="OpenSearch password")
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


settings = Settings()
