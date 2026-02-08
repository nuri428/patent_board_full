from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import sys
import os
import logging

sys.path.append(
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        "..",
        "..",
        "..",
        "shared",
    )
)
from shared.database import get_db
from app.crud.report_version import report_version as version_crud
from app.api import deps
from app.models import User
from app.schemas.report import (
    ReportCreate,
    ReportUpdate,
    Report,
    ReportGenerationRequest,
    ReportGenerationStatus,
)
from app.crud.report import get_report_crud
from fastapi import Request
from app.crud.audit import get_audit_crud

logger = logging.getLogger(__name__)
router = APIRouter()


async def generate_report_background(
    report_id: int,
    topic: str,
    report_type: str,
    patent_ids: list,
    parameters: dict,
    user_id: str = None,
):
    """
    Background task to generate report using PatentReportGenerator.
    Updates report status as it progresses and sends WebSocket notification on completion.
    """
    # Import here to avoid circular dependencies
    from app.langgraph import report_generator
    from shared.database import AsyncSessionLocal
    from app.api.v1.endpoints.notifications import notify_report_completion

    # Create new DB session for background task
    async with AsyncSessionLocal() as db:
        try:
            crud = get_report_crud(db)

            # Update status to "processing"
            await crud.update(
                report_id,
                ReportUpdate(status="processing", updated_at=datetime.utcnow()),
            )

            logger.info(
                f"Starting report generation for report_id={report_id}, topic={topic}"
            )

            # Call PatentReportGenerator
            # Note: This runs the LangGraph workflow
            result = await report_generator.generate_report(
                topic=topic,
                report_type=report_type,
                patent_ids=patent_ids,
                parameters=parameters,
            )

            # Update report with completed status and content
            await crud.update(
                report_id,
                ReportUpdate(
                    status="completed",
                    content=result.get("content", ""),
                    generated_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                ),
            )

            # Create analytics record
            await crud.create_analytics(
                report_id=report_id,
                patent_count=len(patent_ids),
                processing_time_seconds=result.get("processing_time_seconds"),
                generation_tokens_used=result.get("tokens_used"),
                query_complexity_score=result.get("complexity_score"),
            )

            logger.info(f"Report generation completed for report_id={report_id}")

            # Send WebSocket notification to user
            await notify_report_completion(
                report_id=str(report_id),
                patent_ids=patent_ids,
                user_id=user_id,
            )

        except Exception as e:
            logger.error(
                f"Report generation failed for report_id={report_id}: {str(e)}"
            )

            # Update status to failed
            try:
                await crud.update(
                    report_id,
                    ReportUpdate(
                        status="failed",
                        description=f"Generation failed: {str(e)}",
                        updated_at=datetime.utcnow(),
                    ),
                )

                # Send failure notification
                await notify_report_completion(
                    report_id=str(report_id),
                    patent_ids=patent_ids,
                    user_id=user_id,
                )
            except Exception as update_error:
                logger.error(f"Failed to update report status: {str(update_error)}")


@router.post(
    "/generate",
    response_model=ReportGenerationStatus,
    status_code=status.HTTP_202_ACCEPTED,
)
async def generate_report(
    request: Request,
    gen_request: ReportGenerationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Trigger async report generation.
    Returns immediately with report_id. Check status via GET /{report_id}.
    """
    crud = get_report_crud(db)

    # Create report record with pending status
    report_create = ReportCreate(
        title=f"Report: {gen_request.topic}",
        description=f"Generated report on {gen_request.topic}",
        report_type=gen_request.report_type,
        topic=gen_request.topic,
        patent_ids=gen_request.patent_ids or [],
        parameters=gen_request.parameters or {},
    )

    report = await crud.create(report_create, owner_id=current_user.id)

    # Audit Log
    audit_crud = get_audit_crud(db)
    await audit_crud.log(
        action="report_gen_start",
        user_id=current_user.id,
        username=current_user.email,
        resource_type="report",
        resource_id=str(report.id),
        description=f"Started report generation: {gen_request.topic}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    # Add background task
    background_tasks.add_task(
        generate_report_background,
        report_id=report.id,
        topic=gen_request.topic,
        report_type=gen_request.report_type,
        patent_ids=gen_request.patent_ids or [],
        parameters=gen_request.parameters or {},
        user_id=str(current_user.id),
    )

    logger.info(
        f"Report generation queued: report_id={report.id}, user={current_user.id}"
    )

    return ReportGenerationStatus(
        report_id=report.id,
        status="pending",
        progress_percentage=0,
        current_stage="queued",
        estimated_completion=None,
        error_message=None,
    )


@router.get("/{report_id}/status", response_model=ReportGenerationStatus)
async def get_report_status(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Get report generation status and progress.
    """
    crud = get_report_crud(db)
    report = await crud.get(report_id)

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if report.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this report"
        )

    # Calculate progress based on status
    progress_map = {
        "pending": 0,
        "processing": 50,
        "completed": 100,
        "failed": 0,
    }

    return ReportGenerationStatus(
        report_id=report.id,
        status=report.status,
        progress_percentage=progress_map.get(report.status, 0),
        current_stage=report.status,
        estimated_completion=None,
        error_message=report.description if report.status == "failed" else None,
    )


@router.get("/{report_id}/versions")
async def get_report_versions(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Get all versions of a report.
    """
    versions = await version_crud.get_by_report_id(db, report_id=report_id)
    return versions


@router.get("/{report_id}", response_model=Report)
async def get_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Get report by ID including status and content.
    """
    crud = get_report_crud(db)
    report = await crud.get(report_id)

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if report.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this report"
        )

    return report


@router.get("/", response_model=list[Report])
async def list_reports(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    List all reports for current user with optional status filter.
    """
    crud = get_report_crud(db)
    reports = await crud.get_multi(
        skip=skip,
        limit=limit,
        owner_id=int(current_user.id),
        status=status,
    )
    return reports
