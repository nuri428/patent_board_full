from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from shared.database import get_db
from app.models import Patent, Report, ChatSession, ChatMessage
from typing import Dict, Any
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/dashboard")
async def get_user_dashboard(db: AsyncSession = Depends(get_db)):
    today = datetime.now()
    last_30_days = today - timedelta(days=30)

    total_patents = await db.execute(select(func.count(Patent.patent_id)))
    total_patents_count = total_patents.scalar() or 0

    recent_patents_query = (
        select(Patent)
        .where(Patent.created_at >= last_30_days)
        .order_by(Patent.created_at.desc())
        .limit(5)
    )
    recent_patents_result = await db.execute(recent_patents_query)
    recent_patents = recent_patents_result.scalars().all()

    user_reports_query = (
        select(Report)
        .where(Report.created_at >= last_30_days)
        .order_by(Report.created_at.desc())
        .limit(5)
    )
    user_reports_result = await db.execute(user_reports_query)
    user_reports = user_reports_result.scalars().all()

    chat_history_query = (
        select(ChatMessage)
        .where(ChatMessage.timestamp >= last_30_days)
        .order_by(ChatMessage.timestamp.desc())
        .limit(10)
    )
    chat_history_result = await db.execute(chat_history_query)
    chat_history = chat_history_result.scalars().all()

    patents_by_status_query = select(
        Patent.status, func.count(Patent.patent_id)
    ).group_by(Patent.status)
    status_result = await db.execute(patents_by_status_query)
    status_distribution = dict(status_result.all())

    return {
        "overview": {
            "total_patents": total_patents_count,
            "recent_patents_count": len(recent_patents),
            "recent_reports_count": len(user_reports),
            "recent_chats_count": len(chat_history),
        },
        "recent_patents": [
            {
                "patent_id": patent.patent_id,
                "title": patent.title,
                "status": patent.status,
                "created_at": patent.created_at.isoformat()
                if patent.created_at
                else None,
            }
            for patent in recent_patents
        ],
        "recent_reports": [
            {
                "id": report.id,
                "topic": report.topic,
                "report_type": report.report_type,
                "created_at": report.created_at.isoformat()
                if report.created_at
                else None,
            }
            for report in user_reports
        ],
        "recent_activity": [
            {
                "type": "chat",
                "message": chat.user_message[:100] + "..."
                if len(chat.user_message) > 100
                else chat.user_message,
                "timestamp": chat.timestamp.isoformat() if chat.timestamp else None,
            }
            for chat in chat_history
        ],
        "status_distribution": status_distribution,
    }


@router.get("/preferences")
async def get_user_preferences():
    return {
        "theme": "light",
        "language": "en",
        "notifications": {
            "email": True,
            "push": False,
            "report_completion": True,
            "patent_updates": False,
        },
        "dashboard": {
            "default_view": "overview",
            "widgets": ["overview", "recent_patents", "analytics", "activity"],
            "refresh_interval": 300,
        },
        "search": {
            "default_limit": 25,
            "auto_suggestions": True,
            "search_history": True,
        },
    }


@router.post("/preferences")
async def update_user_preferences(preferences: Dict[str, Any]):
    return {"message": "Preferences updated successfully", "preferences": preferences}


@router.get("/bookmarks")
async def get_user_bookmarks():
    return {"patents": [], "searches": [], "reports": []}


@router.post("/bookmarks/patent/{patent_id}")
async def bookmark_patent(patent_id: str):
    return {"message": f"Patent {patent_id} bookmarked successfully"}


@router.delete("/bookmarks/patent/{patent_id}")
async def remove_patent_bookmark(patent_id: str):
    return {"message": f"Patent {patent_id} bookmark removed successfully"}


@router.get("/activity")
async def get_user_activity(db: AsyncSession = Depends(get_db), days: int = 7):
    start_date = datetime.now() - timedelta(days=days)

    patents_query = (
        select(
            func.date(Patent.created_at).label("date"),
            func.count(Patent.patent_id).label("patent_count"),
        )
        .where(Patent.created_at >= start_date)
        .group_by(func.date(Patent.created_at))
        .order_by(func.date(Patent.created_at).desc())
    )

    patents_result = await db.execute(patents_query)
    patents_activity = patents_result.all()

    reports_query = (
        select(
            func.date(Report.created_at).label("date"),
            func.count(Report.id).label("report_count"),
        )
        .where(Report.created_at >= start_date)
        .group_by(func.date(Report.created_at))
        .order_by(func.date(Report.created_at).desc())
    )

    reports_result = await db.execute(reports_query)
    reports_activity = reports_result.all()

    return {
        "patents_activity": [
            {"date": str(row.date), "count": row.patent_count}
            for row in patents_activity
        ],
        "reports_activity": [
            {"date": str(row.date), "count": row.report_count}
            for row in reports_activity
        ],
    }


@router.get("/recommendations")
async def get_user_recommendations(db: AsyncSession = Depends(get_db)):
    similar_patents_query = (
        select(Patent)
        .where(Patent.status == "granted")
        .order_by(func.random())
        .limit(3)
    )

    similar_result = await db.execute(similar_patents_query)
    similar_patents = similar_result.scalars().all()

    trending_assignees_query = (
        select(Patent.assignee, func.count(Patent.patent_id))
        .where(Patent.created_at >= datetime.now() - timedelta(days=30))
        .group_by(Patent.assignee)
        .order_by(func.count(Patent.patent_id).desc())
        .limit(5)
    )

    trending_result = await db.execute(trending_assignees_query)
    trending_assignees = trending_result.all()

    return {
        "recommended_patents": [
            {
                "patent_id": patent.patent_id,
                "title": patent.title,
                "assignee": patent.assignee,
            }
            for patent in similar_patents
        ],
        "trending_assignees": [
            {"assignee": row[0], "patent_count": row[1]}
            for row in trending_assignees
            if row[0]
        ],
        "suggested_searches": [
            "artificial intelligence",
            "machine learning",
            "blockchain technology",
            "biomedical devices",
            "renewable energy",
        ],
    }
