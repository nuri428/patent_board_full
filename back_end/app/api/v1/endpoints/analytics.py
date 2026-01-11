from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, extract
from shared.database import get_db
from app.models import Patent, Report
from typing import Dict, Any
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/overview")
async def get_analytics_overview(db: AsyncSession = Depends(get_db)):
    today = datetime.now()
    last_30_days = today - timedelta(days=30)
    last_year = today - timedelta(days=365)

    total_patents = await db.execute(select(func.count(PatentModel.patent_id)))
    total_patents_count = total_patents.scalar() or 0

    patents_last_30 = await db.execute(
        select(func.count(PatentModel.patent_id)).where(
            PatentModel.created_at >= last_30_days
        )
    )
    patents_last_30_count = patents_last_30.scalar() or 0

    patents_last_year = await db.execute(
        select(func.count(PatentModel.patent_id)).where(
            PatentModel.created_at >= last_year
        )
    )
    patents_last_year_count = patents_last_year.scalar() or 0

    total_reports = await db.execute(select(func.count(ReportModel.id)))
    total_reports_count = total_reports.scalar() or 0

    reports_last_30 = await db.execute(
        select(func.count(ReportModel.id)).where(ReportModel.created_at >= last_30_days)
    )
    reports_last_30_count = reports_last_30.scalar() or 0

    return {
        "total_patents": total_patents_count,
        "patents_last_30_days": patents_last_30_count,
        "patents_last_year": patents_last_year_count,
        "total_reports": total_reports_count,
        "reports_last_30_days": reports_last_30_count,
    }


@router.get("/patents/timeline")
async def get_patents_timeline(db: AsyncSession = Depends(get_db), days: int = 365):
    start_date = datetime.now() - timedelta(days=days)

    timeline_query = (
        select(
            func.date(PatentModel.created_at).label("date"),
            func.count(PatentModel.patent_id).label("count"),
        )
        .where(PatentModel.created_at >= start_date)
        .group_by(func.date(PatentModel.created_at))
        .order_by(func.date(PatentModel.created_at))
    )

    result = await db.execute(timeline_query)
    timeline_data = result.all()

    return {
        "timeline": [
            {"date": str(row.date), "count": row.count} for row in timeline_data
        ]
    }


@router.get("/patents/by-month")
async def get_patents_by_month(db: AsyncSession = Depends(get_db), months: int = 12):
    start_date = datetime.now() - timedelta(days=months * 30)

    monthly_query = (
        select(
            extract("year", PatentModel.created_at).label("year"),
            extract("month", PatentModel.created_at).label("month"),
            func.count(PatentModel.patent_id).label("count"),
        )
        .where(PatentModel.created_at >= start_date)
        .group_by(
            extract("year", PatentModel.created_at),
            extract("month", PatentModel.created_at),
        )
        .order_by(
            extract("year", PatentModel.created_at),
            extract("month", PatentModel.created_at),
        )
    )

    result = await db.execute(monthly_query)
    monthly_data = result.all()

    return {
        "monthly": [
            {
                "year": int(row.year),
                "month": int(row.month),
                "month_name": datetime(2000, int(row.month), 1).strftime("%B"),
                "count": row.count,
            }
            for row in monthly_data
        ]
    }


@router.get("/patents/by-status")
async def get_patents_by_status(db: AsyncSession = Depends(get_db)):
    status_query = select(
        PatentModel.status, func.count(PatentModel.patent_id)
    ).group_by(PatentModel.status)

    result = await db.execute(status_query)
    status_data = result.all()

    total_count = sum(row[1] for row in status_data)

    return {
        "status_distribution": [
            {
                "status": row[0],
                "count": row[1],
                "percentage": round((row[1] / total_count * 100), 2)
                if total_count > 0
                else 0,
            }
            for row in status_data
        ],
        "total_count": total_count,
    }


@router.get("/patents/top-assignees")
async def get_top_assignees(db: AsyncSession = Depends(get_db), limit: int = 10):
    assignee_query = (
        select(PatentModel.assignee, func.count(PatentModel.patent_id))
        .where(PatentModel.assignee.isnot(None))
        .group_by(PatentModel.assignee)
        .order_by(func.count(PatentModel.patent_id).desc())
        .limit(limit)
    )

    result = await db.execute(assignee_query)
    assignee_data = result.all()

    return {
        "top_assignees": [
            {"assignee": row[0], "patent_count": row[1]} for row in assignee_data
        ]
    }


@router.get("/patents/filing-trends")
async def get_filing_trends(db: AsyncSession = Depends(get_db), years: int = 5):
    current_year = datetime.now().year
    start_year = current_year - years

    filing_trends_query = (
        select(
            extract("year", PatentModel.filing_date).label("year"),
            func.count(PatentModel.patent_id).label("count"),
        )
        .where(
            PatentModel.filing_date.isnot(None),
            extract("year", PatentModel.filing_date) >= start_year,
        )
        .group_by(extract("year", PatentModel.filing_date))
        .order_by(extract("year", PatentModel.filing_date))
    )

    result = await db.execute(filing_trends_query)
    trends_data = result.all()

    return {
        "filing_trends": [
            {"year": int(row.year), "patent_count": row.count} for row in trends_data
        ]
    }


@router.get("/reports/analytics")
async def get_reports_analytics(db: AsyncSession = Depends(get_db)):
    total_reports = await db.execute(select(func.count(ReportModel.id)))
    total_reports_count = total_reports.scalar() or 0

    report_types_query = select(
        ReportModel.report_type, func.count(ReportModel.id)
    ).group_by(ReportModel.report_type)

    result = await db.execute(report_types_query)
    report_types = result.all()

    return {
        "total_reports": total_reports_count,
        "report_types": [{"type": row[0], "count": row[1]} for row in report_types],
    }


@router.get("/dashboard")
async def get_dashboard_data(db: AsyncSession = Depends(get_db)):
    overview = await get_analytics_overview(db)
    timeline = await get_patents_timeline(db, days=30)
    by_status = await get_patents_by_status(db)
    top_assignees = await get_top_assignees(db, limit=5)
    filing_trends = await get_filing_trends(db, years=3)
    reports_analytics = await get_reports_analytics(db)

    return {
        "overview": overview,
        "timeline": timeline,
        "status_distribution": by_status,
        "top_assignees": top_assignees,
        "filing_trends": filing_trends,
        "reports": reports_analytics,
    }
