from pydantic_settings import BaseSettings
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # Database
    MARIADB_URL: str = "mysql+aiomysql://patent_user:password@localhost/patent_db"
    PATENTDB_URL: str = "mysql+aiomysql://patent_user:password@localhost/patent_db"
    PA_SYSTEM_DB_URL: str = "mysql+aiomysql://chatbot_user:password@localhost/pa_system"
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # API
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 2000
    OPENAI_TOP_P: float = 1.0
    OPENAI_FREQUENCY_PENALTY: float = 0.0
    OPENAI_PRESENCE_PENALTY: float = 0.0

    # MCP Server
    MCP_SERVER_URL: str = "http://localhost:8081"
    MCP_TIMEOUT: int = 30

    # LangGraph Configuration
    MAX_CONVERSATION_LENGTH: int = 1000
    MAX_CONTEXT_TOKENS: int = 4000
    RESPONSE_TIMEOUT: int = 30
    CHECKPOINT_MEMORY_BACKEND: str = "memory"  # "memory", "redis", "sql"

# CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # React frontend
        "http://localhost:8002",
        "http://localhost:3300",
        "http://localhost:3301",
        "http://localhost:8003",  # LangGraph API
    ]

    # App
    PROJECT_NAME: str = "Patent Board"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Chatbot Configuration
    CHATBOT_DEFAULT_TEMPERATURE: float = 0.7
    CHATBOT_MAX_TOKENS: int = 2000
    CHATBOT_TOP_P: float = 1.0
    CHATBOT_SYSTEM_PROMPT_TEMPLATE: str = """
You are an AI assistant specialized in patent analysis and intellectual property. 
You help users understand patents, provide insights about patent landscapes, and assist with IP strategy.

Key guidelines:
1. Be accurate and specific in patent-related information
2. Provide context and explanations for technical concepts
3. If you mention patents, always cite the patent ID when available
4. Be helpful and informative about intellectual property concepts
5. Maintain professional tone suitable for IP professionals

User preferences and context:
{user_preferences_section}

Recent conversation context:
{conversation_history_section}

Relevant patents found:
{patent_context_section}
"""
    CHATBOT_CONTEXT_HISTORY_LIMIT: int = 5
    CHATBOT_PATENT_CONTEXT_LIMIT: int = 3

    # Context Engineering Configuration
    CONTEXT_ENGINEERING_PATENT_KEYWORDS: List[str] = [
        "patent", "patents", "intellectual property", "ip", "invention",
        "innovation", "technology", "application", "filing", "grant",
        "prior art", "claims", "abstract", "description", "specification",
        "trademark", "copyright", "licensing", "franchise", "royalty"
    ]
    
    CONTEXT_ENGINEERING_TECHNOLOGY_DOMAINS: Dict[str, List[str]] = {
        "artificial intelligence": ["AI", "machine learning", "neural network", "deep learning"],
        "biotechnology": ["biotech", "genetic", "DNA", "RNA", "protein"],
        "software": ["software", "algorithm", "code", "program", "application"],
        "hardware": ["hardware", "device", "circuit", "electronic", "semiconductor"],
        "chemistry": ["chemical", "compound", "molecule", "synthesis", "catalyst"],
        "mechanical": ["mechanical", "machine", "apparatus", "system", "process"]
    }
    
    CONTEXT_ENGINEERING_PATENT_VERBS: List[str] = [
        "search", "find", "lookup", "analyze", "examine", "research",
        "compare", "study", "review", "summarize", "explain", "describe"
    ]
    
    CONTEXT_ENGINEERING_PATENT_ID_PATTERN: str = r'\b(?:US|WO|EP|JP|CN|KR|CA|AU|DE|FR|GB|IL|RU)[0-9]{5,}\b'
    
    # User Pattern Analysis Configuration
    USER_PATTERN_ANALYSIS_ENABLED: bool = True
    USER_PATTERN_KEYWORD_THRESHOLD: int = 3
    USER_PATTERN_PATENT_ID_THRESHOLD: int = 1
    USER_PATTERN_VERB_THRESHOLD: int = 2
    
    # Technical Assessment Configuration
    TECHNICAL_COMPLEXITY_TERMS: List[str] = [
        "algorithm", "neural network", "deep learning", "machine learning",
        "artificial intelligence", "blockchain", "quantum", "nanotechnology",
        "biotechnology", "genetic", "molecular", "synthetic"
    ]
    
    # URL Generation Configuration
    URL_GENERATION_SOURCES: List[str] = ["google", "uspto", "kipris"]
    URL_GENERATION_DEFAULT_COUNTRY: str = "auto"

    class Config:
        env_file = ".env"
        extra = "ignore"
    
    def validate_configuration(self) -> bool:
        """Validate configuration settings and log warnings for missing critical settings"""
        validation_passed = True
        
        # Check OpenAI configuration
        if not self.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY is not set. AI features will be disabled.")
            validation_passed = False
        
        if not self.OPENAI_MODEL:
            logger.warning("OPENAI_MODEL is not set. Using default gpt-4-turbo-preview.")
            self.OPENAI_MODEL = "gpt-4-turbo-preview"
        
        # Check database URLs
        if not self.MARIADB_URL:
            logger.error("MARIADB_URL is not set. Database connection will fail.")
            validation_passed = False
        
        if not self.PA_SYSTEM_DB_URL:
            logger.error("PA_SYSTEM_DB_URL is not set. Chatbot system database connection will fail.")
            validation_passed = False
        
        if not self.REDIS_URL:
            logger.warning("REDIS_URL is not set. Redis cache will be disabled.")
            # Redis is optional, so don't fail validation
        
        # Check MCP server URL
        if not self.MCP_SERVER_URL:
            logger.warning("MCP_SERVER_URL is not set. Patent search functionality will be disabled.")
            validation_passed = False
        
        # Validate configuration values
        if self.OPENAI_TEMPERATURE < 0 or self.OPENAI_TEMPERATURE > 2:
            logger.warning(f"OPENAI_TEMPERATURE {self.OPENAI_TEMPERATURE} is outside recommended range (0-2)")
        
        if self.OPENAI_MAX_TOKENS < 100 or self.OPENAI_MAX_TOKENS > 32000:
            logger.warning(f"OPENAI_MAX_TOKENS {self.OPENAI_MAX_TOKENS} is outside typical range (100-32000)")
        
        if self.MAX_CONTEXT_TOKENS < 1000 or self.MAX_CONTEXT_TOKENS > 100000:
            logger.warning(f"MAX_CONTEXT_TOKENS {self.MAX_CONTEXT_TOKENS} seems unusually high")
        
        # Validate CORS origins
        if not self.BACKEND_CORS_ORIGINS:
            logger.error("BACKEND_CORS_ORIGINS is empty. CORS will not work properly.")
            validation_passed = False
        
        # Validate ContextEngineering settings
        if not self.CONTEXT_ENGINEERING_PATENT_KEYWORDS:
            logger.error("CONTEXT_ENGINEERING_PATENT_KEYWORDS is empty. Patent intent detection will fail.")
            validation_passed = False
        
        if not self.CONTEXT_ENGINEERING_TECHNOLOGY_DOMAINS:
            logger.error("CONTEXT_ENGINEERING_TECHNOLOGY_DOMAINS is empty. Domain detection will fail.")
            validation_passed = False
        
        # Validate URL generation settings
        if not self.URL_GENERATION_SOURCES:
            logger.warning("URL_GENERATION_SOURCES is empty. Patent URL generation will fail.")
            validation_passed = False
        
        if validation_passed:
            logger.info("Configuration validation passed successfully")
        else:
            logger.warning("Some configuration validation checks failed. Please check your environment variables.")
        
        return validation_passed


# Initialize settings and perform validation
settings = Settings()

# Perform validation on startup
if not settings.validate_configuration():
    logger.warning("Some configuration validation checks failed. Please check your environment variables.")
