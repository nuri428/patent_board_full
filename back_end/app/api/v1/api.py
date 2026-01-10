from fastapi import APIRouter

from app.api.v1.endpoints import patents, chat, reports, auth, admin, analytics, export, user, notifications

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(patents.router, prefix="/patents", tags=["patents"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(export.router, prefix="/export", tags=["export"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])