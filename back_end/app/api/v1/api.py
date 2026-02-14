from fastapi import APIRouter

from app.api.v1.endpoints import (
    chat,
    reports,
    auth,
    admin,
    analytics,
    export,
    user,
    notifications,
    workspaces,
    prompts,
    mcp,
    patents,
    patent_analysis,
    patent_search,
    patent_country_search,
    visualization,
    health,
    sessions,
    session_groups,
    auto_cleanup,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(export.router, prefix="/export", tags=["export"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(
    notifications.router, prefix="/notifications", tags=["notifications"]
)
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["workspaces"])
api_router.include_router(prompts.router, prefix="/prompts", tags=["prompts"])
api_router.include_router(mcp.router, prefix="/mcp", tags=["mcp"])
api_router.include_router(patents.router, prefix="/patents", tags=["patents"])
api_router.include_router(
    patent_analysis.router, prefix="/patent-analyses", tags=["patent-analyses"]
)
api_router.include_router(
    patent_search.router, tags=["patent-search"]
)
api_router.include_router(
    patent_country_search.router, tags=["patent-country-search"]
)
api_router.include_router(
    visualization.router, prefix="/visualization", tags=["visualization"]
)
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(session_groups.router, prefix="/session-groups", tags=["session-groups"])
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auto_cleanup.router, prefix="/cleanup", tags=["cleanup"])
