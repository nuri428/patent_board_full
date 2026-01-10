from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class NotificationBase(BaseModel):
    title: str
    message: str
    notification_type: str  # report_ready, system_alert, patent_update, etc.


class NotificationCreate(NotificationBase):
    user_id: int


class Notification(NotificationBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    is_read: bool = False
    created_at: datetime
    read_at: Optional[datetime] = None