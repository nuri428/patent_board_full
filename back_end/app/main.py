from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.routes import web_router
from app.core.config import settings
import json

app = FastAPI(
    title="Patent Board", version="1.0.0", description="Patent Analysis Board Backend"
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
])

origins = list(set(origins))  # Remove duplicates

# In DEBUG mode, allow all origins via regex to support various network IPs
allow_origin_regex = None
if settings.DEBUG:
    allow_origin_regex = r"^https?://.*$"
    origins = [] # Regex takes precedence, so we can clear specific origins to avoid confusion, or keep them. 
                 # Starlette/FastAPI's CORSMiddleware uses allow_origin_regex if provided.

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router, prefix="/api/v1")

# Include Web Router (Legacy/Template based)
app.include_router(web_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
