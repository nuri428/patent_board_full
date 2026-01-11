from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.routes import web_router

app = FastAPI(
    title="Patent Board", version="1.0.0", description="Patent Analysis Board Backend"
)

# CORS Configuration
origins = [
    "http://localhost:3000",
    "http://localhost:3300",
    "http://localhost:8001",
    "http://localhost:8080",
]

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


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
