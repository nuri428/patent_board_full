from .user import User, UserCreate, UserUpdate, UserInDB
from .patent import (
    Patent,
    PatentCreate,
    PatentUpdate,
    PatentSearchRequest,
    PatentSearchResponse,
    PatentDetail,
    PatentSearch,
)
from .report import (
    Report,
    ReportCreate,
    ReportUpdate,
    ReportDetail,
    ReportPatent,
    ReportAnalytics,
    ReportGenerationRequest,
    ReportGenerationStatus,
)
from .chat import (
    ChatSession,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ChatSessionCreate,
    ChatMessageCreate,
    ChatSessionDetail,
)
from .notification import Notification, NotificationCreate
from .analytics import AnalyticsData, SystemMetrics, UserAnalytics, PatentAnalytics

__all__ = [
    # User schemas
    "User",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    # Patent schemas
    "Patent",
    "PatentCreate",
    "PatentUpdate",
    "PatentSearchRequest",
    "PatentSearchResponse",
    "PatentDetail",
    "PatentSearch",
    # Report schemas
    "Report",
    "ReportCreate",
    "ReportUpdate",
    "ReportDetail",
    "ReportPatent",
    "ReportAnalytics",
    "ReportGenerationRequest",
    "ReportGenerationStatus",
    # Chat schemas
    "ChatSession",
    "ChatMessage",
    "ChatRequest",
    "ChatResponse",
    "ChatSessionCreate",
    "ChatMessageCreate",
    "ChatSessionDetail",
    # Notification schemas
    "Notification",
    "NotificationCreate",
    # Analytics schemas
    "AnalyticsData",
    "SystemMetrics",
    "UserAnalytics",
    "PatentAnalytics",
]
