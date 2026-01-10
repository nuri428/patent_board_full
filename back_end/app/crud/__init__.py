from .user import UserCRUD, get_user_crud
from .patent import PatentCRUD, get_patent_crud
from .report import ReportCRUD, get_report_crud
from .chat import ChatCRUD, get_chat_crud
from .notification import NotificationCRUD, get_notification_crud
from .analytics import AnalyticsCRUD, get_analytics_crud

__all__ = [
    "UserCRUD", "get_user_crud",
    "PatentCRUD", "get_patent_crud", 
    "ReportCRUD", "get_report_crud",
    "ChatCRUD", "get_chat_crud",
    "NotificationCRUD", "get_notification_crud",
    "AnalyticsCRUD", "get_analytics_crud"
]