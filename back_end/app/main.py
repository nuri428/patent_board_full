from fastapi import FastAPI, Request
import logging
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any
import httpx
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.routes import web_router
from app.core.config import settings
import json
import time
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
import os

frontend_dist_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../front_end/dist")
)

# Custom JSON Formatter
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)


# Initialize logging based on environment
def setup_logging():
    level = logging.DEBUG if settings.DEBUG else logging.INFO
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler()
    if settings.ENVIRONMENT == "production":
        handler.setFormatter(JsonFormatter())
    else:
        # Standard formatted output for development
        formatter = logging.Formatter("%(levelname)s: [%(name)s] %(message)s")
        handler.setFormatter(formatter)

    root_logger.addHandler(handler)


setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Patent Board", version="1.0.0", description="Patent Analysis Board Backend"
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error", "detail": str(exc)},
    )


# CORS Configuration
origins = []

# Add origins from settings
if settings.BACKEND_CORS_ORIGINS:
    if isinstance(settings.BACKEND_CORS_ORIGINS, str):
        try:
            origins.extend(json.loads(settings.BACKEND_CORS_ORIGINS))
        except (ValueError, TypeError):
            origins.extend([o.strip() for o in settings.BACKEND_CORS_ORIGINS.split(",")])
    else:
        origins.extend(settings.BACKEND_CORS_ORIGINS)

# Add default localhost ports for development
origins.extend([
    "http://localhost:3000",
    "http://localhost:3300",
    "http://localhost:8001",
    "http://localhost:8080",
    "http://localhost:5000",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:5000",
    "https://greennuri.info",
    "http://greennuri.info",
])

origins = list(set(origins))  # Remove duplicates

# In DEBUG mode, allow all origins via regex to support various network IPs
allow_origin_regex = None
if settings.DEBUG:
    allow_origin_regex = r"^https?://.*$"
    origins = [] # Regex takes precedence

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    logger.info(
        f"Request: {request.method} {request.url.path} "
        f"Status: {response.status_code} "
        f"Duration: {duration:.4f}s"
    )
    return response


# Include API Router
app.include_router(api_router, prefix="/api/v1")

# Include Web Router (Empty legacy router)
app.include_router(web_router)


async def check_mariadb() -> Dict[str, Any]:
    """Check MariaDB connectivity"""
    try:
        from shared.database import AsyncSessionLocal

        async with AsyncSessionLocal() as db:
            from sqlalchemy import text

            result = await db.execute(text("SELECT 1"))
            result.fetchone()
            return {"status": "healthy", "message": "Connected"}
    except Exception as e:
        logger.error(f"MariaDB health check failed: {e}")
        return {"status": "unhealthy", "message": str(e)}


async def check_neo4j() -> Dict[str, Any]:
    """Check Neo4j connectivity"""
    try:
        from neo4j import AsyncGraphDatabase

        driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
        async with driver.session() as session:
            result = await session.run("RETURN 1 as num")
            record = await result.single()
            await driver.close()
            if record and record["num"] == 1:
                return {"status": "healthy", "message": "Connected"}
            return {"status": "unhealthy", "message": "Unexpected response"}
    except Exception as e:
        logger.error(f"Neo4j health check failed: {e}")
        return {"status": "unhealthy", "message": str(e)}


async def check_mcp_server() -> Dict[str, Any]:
    """Check MCP server connectivity"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.MCP_SERVER_URL}/health")
            if response.status_code == 200:
                return {"status": "healthy", "message": "Connected"}
            return {"status": "unhealthy", "message": f"HTTP {response.status_code}"}
    except Exception as e:
        logger.error(f"MCP server health check failed: {e}")
        return {"status": "unhealthy", "message": str(e)}


async def check_redis() -> Dict[str, Any]:
    """Check Redis connectivity"""
    try:
        import redis.asyncio as redis

        client = redis.from_url(settings.REDIS_URL, socket_connect_timeout=5)
        await client.ping()
        await client.aclose()
        return {"status": "healthy", "message": "Connected"}
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return {"status": "unhealthy", "message": str(e), "optional": True}


async def check_opensearch() -> Dict[str, Any]:
    """Check OpenSearch connectivity via root endpoint"""
    try:
        from app.services.opensearch_service import health_check as os_health
        result = await os_health()
        if result.get("connected"):
            return {"status": "healthy", "message": f"Connected (v{result.get('version', '?')})"}
        return {"status": "unhealthy", "message": result.get("error", "unreachable"), "optional": True}
    except Exception as e:
        logger.error(f"OpenSearch health check failed: {e}")
        return {"status": "unhealthy", "message": str(e), "optional": True}


@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/health/detailed")
async def health_check_detailed():
    """Detailed health check with service dependencies"""
    start_time = datetime.now(timezone.utc)

    # Run all checks concurrently
    results = await asyncio.gather(
        check_mariadb(),
        check_neo4j(),
        check_mcp_server(),
        check_redis(),
        check_opensearch(),
        return_exceptions=True,
    )

    checks = {
        "mariadb": results[0]
        if not isinstance(results[0], Exception)
        else {"status": "unhealthy", "message": str(results[0])},
        "neo4j": results[1]
        if not isinstance(results[1], Exception)
        else {"status": "unhealthy", "message": str(results[1])},
        "mcp_server": results[2]
        if not isinstance(results[2], Exception)
        else {"status": "unhealthy", "message": str(results[2])},
        "redis": results[3]
        if not isinstance(results[3], Exception)
        else {"status": "unhealthy", "message": str(results[3]), "optional": True},
        "opensearch": results[4]
        if not isinstance(results[4], Exception)
        else {"status": "unhealthy", "message": str(results[4]), "optional": True},
    }

    # Determine overall status
    critical_services = ["mariadb", "neo4j", "mcp_server"]
    all_healthy = all(
        checks[service]["status"] == "healthy" for service in critical_services
    )

    end_time = datetime.now(timezone.utc)
    response_time_ms = (end_time - start_time).total_seconds() * 1000

    status_code = 200 if all_healthy else 503

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if all_healthy else "degraded",
            "timestamp": end_time.isoformat(),
            "response_time_ms": round(response_time_ms, 2),
            "version": settings.VERSION,
            "services": checks,
        },
    )


# Serve Frontend SPA - Defined at the end to avoid shadowing routes
if os.path.exists(frontend_dist_path):
    # Mount assets directory first
    assets_path = os.path.join(frontend_dist_path, "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

    # Catch-all route for SPA
    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        # Check if requested path is an API call or health check
        if full_path.startswith("api/") or full_path.startswith("health"):
            return JSONResponse(status_code=404, content={"detail": "Not Found"})

        # Check if the file exists in the dist folder
        file_path = os.path.join(frontend_dist_path, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)

        # Fallback to index.html for SPA routing
        return FileResponse(os.path.join(frontend_dist_path, "index.html"))
else:
    logger.warning(f"Frontend dist directory not found at {frontend_dist_path}")
