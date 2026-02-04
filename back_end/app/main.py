from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any
import httpx
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.routes import web_router
from app.core.config import settings


logging.basicConfig(level=logging.DEBUG)
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
origins = settings.BACKEND_CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router, prefix="/api/v1")

# Include Web Router (Legacy/Template based)
app.include_router(web_router)


async def check_mariadb() -> Dict[str, Any]:
    """Check MariaDB connectivity"""
    try:
        from shared.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            from sqlalchemy import text
            result = await db.execute(text("SELECT 1"))
            await result.fetchone()
            return {"status": "healthy", "message": "Connected"}
    except Exception as e:
        logger.error(f"MariaDB health check failed: {e}")
        return {"status": "unhealthy", "message": str(e)}


async def check_neo4j() -> Dict[str, Any]:
    """Check Neo4j connectivity"""
    try:
        from neo4j import AsyncGraphDatabase
        driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
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
        await client.close()
        return {"status": "healthy", "message": "Connected"}
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return {"status": "unhealthy", "message": str(e), "optional": True}


@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/health/detailed")
async def health_check_detailed():
    """Detailed health check with service dependencies"""
    start_time = datetime.utcnow()
    
    # Run all checks concurrently
    results = await asyncio.gather(
        check_mariadb(),
        check_neo4j(),
        check_mcp_server(),
        check_redis(),
        return_exceptions=True
    )
    
    checks = {
        "mariadb": results[0] if not isinstance(results[0], Exception) else {"status": "unhealthy", "message": str(results[0])},
        "neo4j": results[1] if not isinstance(results[1], Exception) else {"status": "unhealthy", "message": str(results[1])},
        "mcp_server": results[2] if not isinstance(results[2], Exception) else {"status": "unhealthy", "message": str(results[2])},
        "redis": results[3] if not isinstance(results[3], Exception) else {"status": "unhealthy", "message": str(results[3]), "optional": True},
    }
    
    # Determine overall status
    critical_services = ["mariadb", "neo4j", "mcp_server"]
    all_healthy = all(
        checks[service]["status"] == "healthy" 
        for service in critical_services
    )
    
    end_time = datetime.utcnow()
    response_time_ms = (end_time - start_time).total_seconds() * 1000
    
    status_code = 200 if all_healthy else 503
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if all_healthy else "degraded",
            "timestamp": end_time.isoformat(),
            "response_time_ms": round(response_time_ms, 2),
            "version": settings.VERSION,
            "services": checks
        }
    )
