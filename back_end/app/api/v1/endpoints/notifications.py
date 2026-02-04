from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from datetime import datetime
import json

from shared.database import get_db
from app.crud.notification import NotificationCRUD, get_notification_crud
from app.api.deps import get_current_active_user
from app.schemas.user import User

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str = None):
        await websocket.accept()
        self.active_connections.append(websocket)

        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = []
            self.user_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: str = None):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

        if user_id and user_id in self.user_connections:
            if websocket in self.user_connections[user_id]:
                self.user_connections[user_id].remove(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.user_connections:
            for connection in self.user_connections[user_id]:
                await connection.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@router.get("/")
async def get_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    limit: int = 20,
    unread_only: bool = False
):
    """Get user notifications"""
    crud = get_notification_crud(db)
    notifications = await crud.get_user_notifications(
        user_id=current_user.id,
        unread_only=unread_only,
        skip=0,
        limit=limit
    )
    
    return {
        "notifications": [
            {
                "id": str(n.id),
                "type": n.notification_type,
                "title": n.title,
                "message": n.message,
                "timestamp": n.created_at.isoformat() if n.created_at else datetime.now().isoformat(),
                "read": n.is_read,
                "data": n.data or {},
            }
            for n in notifications
        ]
    }


@router.post("/mark-read/{notification_id}")
async def mark_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark a notification as read"""
    crud = get_notification_crud(db)
    success = await crud.mark_as_read(notification_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"message": "Notification marked as read"}


@router.post("/mark-all-read")
async def mark_all_notifications_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark all notifications as read"""
    crud = get_notification_crud(db)
    count = await crud.mark_all_as_read(current_user.id)
    
    return {"message": f"{count} notifications marked as read"}


@router.get("/unread-count")
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get count of unread notifications"""
    crud = get_notification_crud(db)
    count = await crud.get_unread_count(current_user.id)
    
    return {"unread_count": count}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a notification"""
    crud = get_notification_crud(db)
    success = await crud.delete(notification_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"message": "Notification deleted"}


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)


async def notify_report_completion(
    report_id: str, patent_ids: List[str], user_id: str = None
):
    message = {
        "type": "report_completion",
        "title": "Report Completed",
        "message": f"Analysis of {len(patent_ids)} patents is complete.",
        "data": {"report_id": report_id, "patent_count": len(patent_ids)},
        "timestamp": datetime.now().isoformat(),
    }

    message_json = json.dumps(message)

    if user_id:
        await manager.send_personal_message(message_json, user_id)
    else:
        await manager.broadcast(message_json)


async def notify_patent_status_change(patent_id: str, old_status: str, new_status: str):
    message = {
        "type": "patent_status_change",
        "title": "Patent Status Updated",
        "message": f"Patent {patent_id} status changed from {old_status} to {new_status}.",
        "data": {
            "patent_id": patent_id,
            "old_status": old_status,
            "new_status": new_status,
        },
        "timestamp": datetime.now().isoformat(),
    }

    message_json = json.dumps(message)
    await manager.broadcast(message_json)


async def notify_new_patent(patent_id: str, title: str):
    message = {
        "type": "new_patent",
        "title": "New Patent Added",
        "message": f"Patent {patent_id}: {title[:50]}... has been added to the database.",
        "data": {"patent_id": patent_id, "title": title},
        "timestamp": datetime.now().isoformat(),
    }

    message_json = json.dumps(message)
    await manager.broadcast(message_json)


@router.get("/preferences")
async def get_notification_preferences(
    current_user: User = Depends(get_current_active_user)
):
    return {
        "email_notifications": True,
        "push_notifications": False,
        "report_completion": True,
        "patent_updates": True,
        "system_alerts": True,
        "digest_frequency": "daily",
    }


@router.post("/preferences")
async def update_notification_preferences(
    preferences: Dict[str, Any],
    current_user: User = Depends(get_current_active_user)
):
    return {"message": "Notification preferences updated", "preferences": preferences}


@router.get("/settings")
async def get_notification_settings(
    current_user: User = Depends(get_current_active_user)
):
    return {
        "enabled": True,
        "types": {
            "report_completion": {
                "enabled": True,
                "email": True,
                "push": False,
                "sound": True,
            },
            "patent_updates": {
                "enabled": True,
                "email": True,
                "push": False,
                "sound": False,
            },
            "system_alerts": {
                "enabled": True,
                "email": True,
                "push": True,
                "sound": True,
            },
        },
        "ui": {
            "desktop_notifications": True,
            "notification_position": "top-right",
            "auto_hide_after": 5000,
            "show_preview": True,
        },
    }


@router.post("/test")
async def test_notification(
    current_user: User = Depends(get_current_active_user)
):
    test_message = {
        "type": "test",
        "title": "Test Notification",
        "message": "This is a test notification to verify the system is working.",
        "timestamp": datetime.now().isoformat(),
    }

    message_json = json.dumps(test_message)
    await manager.broadcast(message_json)

    return {"message": "Test notification sent"}
