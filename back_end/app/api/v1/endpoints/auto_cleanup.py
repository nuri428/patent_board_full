"""
Auto Cleanup API Endpoints

Provides REST API endpoints for managing auto cleanup functionality,
including on-demand cleanup triggering, statistics viewing, and configuration management.
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.api.deps import get_current_active_user
from app.models import User
from app.auto_cleanup_scheduler import (
    AutoCleanupScheduler,
    CleanupCycleStats,
    get_scheduler,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["cleanup"])

# Module-level cache for last cleanup cycle statistics
_last_cleanup_stats: Optional[CleanupCycleStats] = None
_last_cleanup_time: Optional[datetime] = None


# ========== Request/Response Models ==========

class CleanupConfigResponse(BaseModel):
    """Response model for cleanup configuration."""

    interval_minutes: int = Field(..., description="Cleanup interval in minutes")
    retention_days: int = Field(..., description="Archived session retention in days")
    scheduler_running: bool = Field(..., description="Whether scheduler is currently running")


class CleanupConfigUpdate(BaseModel):
    """Request model for updating cleanup configuration."""

    interval_minutes: Optional[int] = Field(None, ge=1, description="New cleanup interval in minutes (min 1)")
    retention_days: Optional[int] = Field(None, ge=1, description="New retention period in days (min 1)")


class TriggerCleanupResponse(BaseModel):
    """Response model for triggering cleanup."""

    message: str = Field(..., description="Operation result message")
    cleanup_stats: CleanupCycleStats = Field(..., description="Full cleanup cycle statistics")


class StatsResponse(BaseModel):
    """Response model for cleanup statistics."""

    has_previous_run: bool = Field(..., description="Whether a cleanup cycle has been run before")
    last_cleanup_time: Optional[datetime] = Field(None, description="Timestamp of last cleanup cycle")
    cleanup_stats: Optional[CleanupCycleStats] = Field(None, description="Statistics from last cleanup cycle")


class HealthResponse(BaseModel):
    """Response model for scheduler health check."""

    scheduler_running: bool = Field(..., description="Whether scheduler is currently running")
    last_cleanup_time: Optional[datetime] = Field(None, description="Timestamp of last cleanup cycle")
    last_cleanup_stats: Optional[CleanupCycleStats] = Field(None, description="Statistics from last cleanup cycle")


class SuccessResponse(BaseModel):
    """Generic success response."""

    message: str = Field(..., description="Success message")


# ========== Endpoints ==========


@router.post("/trigger", response_model=TriggerCleanupResponse, status_code=status.HTTP_200_OK)
async def trigger_cleanup(
    current_user: User = Depends(get_current_active_user),
    scheduler: AutoCleanupScheduler = Depends(get_scheduler),
):
    """
    Trigger an immediate cleanup cycle.

    Runs all cleanup policies synchronously and returns full statistics.
    Requires JWT authentication.

    Returns:
        Cleanup cycle statistics including per-policy and aggregate totals.
    """
    global _last_cleanup_stats, _last_cleanup_time

    logger.info(f"User {current_user.id} triggered manual cleanup cycle")

    try:
        # Run cleanup cycle
        cleanup_stats = await scheduler.run_cleanup_cycle()

        # Update module-level cache
        _last_cleanup_stats = cleanup_stats
        _last_cleanup_time = datetime.utcnow()

        logger.info(
            f"Manual cleanup completed by user {current_user.id}: "
            f"checked={cleanup_stats['total_checked']}, cleaned={cleanup_stats['cleaned_count']}, "
            f"errors={len(cleanup_stats['errors'])}"
        )

        return TriggerCleanupResponse(
            message="Cleanup cycle completed successfully",
            cleanup_stats=cleanup_stats,
        )

    except Exception as exc:
        logger.error(f"Manual cleanup failed for user {current_user.id}: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cleanup cycle failed: {str(exc)}",
        )


@router.get("/stats", response_model=StatsResponse, status_code=status.HTTP_200_OK)
async def get_cleanup_stats(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get last cleanup cycle statistics.

    Returns statistics from the most recent cleanup cycle (either scheduled or manually triggered).
    Returns empty stats if no cleanup has been run yet.
    Requires JWT authentication.

    Returns:
        Statistics from the last cleanup cycle or empty if never run.
    """
    global _last_cleanup_stats, _last_cleanup_time

    logger.debug(f"User {current_user.id} requested cleanup statistics")

    if _last_cleanup_stats is None:
        logger.debug("No cleanup statistics available (never run)")
        return StatsResponse(
            has_previous_run=False,
            last_cleanup_time=None,
            cleanup_stats=None,
        )

    return StatsResponse(
        has_previous_run=True,
        last_cleanup_time=_last_cleanup_time,
        cleanup_stats=_last_cleanup_stats,
    )


@router.get("/config", response_model=CleanupConfigResponse, status_code=status.HTTP_200_OK)
async def get_cleanup_config(
    current_user: User = Depends(get_current_active_user),
    scheduler: AutoCleanupScheduler = Depends(get_scheduler),
):
    """
    Get current cleanup configuration.

    Returns the current cleanup interval and retention settings.
    Requires JWT authentication.

    Returns:
        Current cleanup configuration including interval, retention, and scheduler status.
    """
    logger.debug(f"User {current_user.id} requested cleanup configuration")

    return CleanupConfigResponse(
        interval_minutes=scheduler.cleanup_interval_minutes,
        retention_days=scheduler.archived_retention_days,
        scheduler_running=scheduler.is_running(),
    )


@router.put("/config", response_model=CleanupConfigResponse, status_code=status.HTTP_200_OK)
async def update_cleanup_config(
    config_update: CleanupConfigUpdate,
    current_user: User = Depends(get_current_active_user),
    scheduler: AutoCleanupScheduler = Depends(get_scheduler),
):
    """
    Update cleanup configuration.

    Updates cleanup interval and/or retention settings.
    Requires admin role.

    Args:
        config_update: Configuration update with optional interval_minutes and retention_days.

    Returns:
        Updated cleanup configuration.

    Raises:
        403 Forbidden: If user is not an admin.
    """
    # Check admin role
    if current_user.role != "admin" and not getattr(current_user, "is_admin", False):
        logger.warning(
            f"Non-admin user {current_user.id} (role={current_user.role}) attempted to update cleanup config"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can update cleanup configuration",
        )

    logger.info(
        f"Admin user {current_user.id} updating cleanup config: "
        f"interval={config_update.interval_minutes}, retention={config_update.retention_days}"
    )

    # Update configuration
    if config_update.interval_minutes is not None:
        scheduler.cleanup_interval_minutes = config_update.interval_minutes
        logger.info(f"Updated cleanup interval to {config_update.interval_minutes} minutes")

    if config_update.retention_days is not None:
        scheduler.archived_retention_days = config_update.retention_days
        logger.info(f"Updated retention period to {config_update.retention_days} days")

    return CleanupConfigResponse(
        interval_minutes=scheduler.cleanup_interval_minutes,
        retention_days=scheduler.archived_retention_days,
        scheduler_running=scheduler.is_running(),
    )


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def get_scheduler_health(
    current_user: User = Depends(get_current_active_user),
    scheduler: AutoCleanupScheduler = Depends(get_scheduler),
):
    """
    Check auto cleanup scheduler health.

    Returns the running status of the scheduler and last cleanup statistics.
    Requires JWT authentication.

    Returns:
        Scheduler health status including running state and last cleanup info.
    """
    logger.debug(f"User {current_user.id} requested scheduler health check")

    return HealthResponse(
        scheduler_running=scheduler.is_running(),
        last_cleanup_time=_last_cleanup_time,
        last_cleanup_stats=_last_cleanup_stats,
    )


def get_last_cleanup_stats() -> Optional[CleanupCycleStats]:
    """
    Get the last cleanup cycle statistics.

    This helper function is used by the scheduler to update stats after each run.

    Returns:
        Last cleanup cycle statistics or None if never run.
    """
    return _last_cleanup_stats


def set_last_cleanup_stats(stats: CleanupCycleStats) -> None:
    """
    Set the last cleanup cycle statistics.

    This helper function is used by the scheduler to cache stats after each run.

    Args:
        stats: Cleanup cycle statistics to cache.
    """
    global _last_cleanup_stats, _last_cleanup_time
    _last_cleanup_stats = stats
    _last_cleanup_time = datetime.utcnow()
