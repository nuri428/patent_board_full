"""
Session Auto Cleanup Scheduler

Runs periodic cleanup policies for archived sessions and orphaned records.
Uses APScheduler to execute async cleanup jobs through a sync wrapper.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Awaitable, Callable, TypedDict

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import and_, delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import ChatSession, User
from app.models.archived_session import ArchivedSession
from app.models.patent_analysis import PatentAnalysis
from app.models.session_group import GroupMember, SessionGroup, SessionGroupTag
from shared.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


class CleanupStats(TypedDict):
    type: str
    total_checked: int
    cleaned_count: int
    errors: list[str]


class PolicyStats(TypedDict):
    total_checked: int
    cleaned_count: int
    errors: list[str]


class CleanupCycleStats(TypedDict):
    old_archived_sessions: PolicyStats
    orphaned_group_members: PolicyStats
    orphaned_session_group_tags: PolicyStats
    orphaned_patent_analyses: PolicyStats
    total_checked: int
    cleaned_count: int
    errors: list[str]


class AutoCleanupScheduler:
    """Manage periodic cleanup tasks for stale and orphaned data."""

    def __init__(self):
        """
        Initialize cleanup scheduler and validate cleanup settings.

        Settings used:
        - SESSION_CLEANUP_INTERVAL_MINUTES
        - SESSION_CLEANUP_ARCHIVED_RETENTION_DAYS
        """
        self.cleanup_interval_minutes = getattr(settings, "SESSION_CLEANUP_INTERVAL_MINUTES", 60)
        self.archived_retention_days = getattr(
            settings, "SESSION_CLEANUP_ARCHIVED_RETENTION_DAYS", 30
        )
        self._validate_config()
        self.scheduler = BackgroundScheduler()
        self._is_running = False

    def _validate_config(self) -> None:
        """Validate cleanup configuration and apply safe defaults when needed."""
        if self.cleanup_interval_minutes <= 0:
            logger.warning(
                "Invalid SESSION_CLEANUP_INTERVAL_MINUTES=%s. Falling back to 60.",
                self.cleanup_interval_minutes,
            )
            self.cleanup_interval_minutes = 60

        if self.archived_retention_days <= 0:
            logger.warning(
                "Invalid SESSION_CLEANUP_ARCHIVED_RETENTION_DAYS=%s. Falling back to 30.",
                self.archived_retention_days,
            )
            self.archived_retention_days = 30

    async def _count_rows(self, db: AsyncSession, model: Any) -> int:
        """Return total row count for a given model table."""
        result = await db.execute(select(func.count()).select_from(model))
        return int(result.scalar() or 0)

    @staticmethod
    def _resolve_rowcount(rowcount: int | None, fallback: int) -> int:
        """Normalize SQLAlchemy rowcount values, preserving fallback when unavailable."""
        if rowcount is None or rowcount < 0:
            return fallback
        return int(rowcount)

    async def cleanup_old_archived_sessions(self) -> CleanupStats:
        """
        Delete archived sessions older than the configured retention window.

        Returns:
            Cleanup statistics with checked rows, cleaned rows, and errors.
        """
        stats: CleanupStats = {
            "type": "old_archived_sessions",
            "total_checked": 0,
            "cleaned_count": 0,
            "errors": [],
        }
        cutoff = datetime.utcnow() - timedelta(days=self.archived_retention_days)

        async with AsyncSessionLocal() as db:
            try:
                stats["total_checked"] = await self._count_rows(db, ArchivedSession)
                logger.info("Checking archived_sessions older than %s", cutoff.isoformat())

                result = await db.execute(
                    select(ArchivedSession.id).where(ArchivedSession.archived_at < cutoff)
                )
                stale_ids = result.scalars().all()

                if not stale_ids:
                    logger.info("No archived sessions eligible for cleanup")
                    return stats

                delete_result = await db.execute(
                    delete(ArchivedSession).where(ArchivedSession.id.in_(stale_ids))
                )
                await db.commit()

                stats["cleaned_count"] = self._resolve_rowcount(delete_result.rowcount, len(stale_ids))
                logger.info("Deleted %s old archived sessions", stats["cleaned_count"])

            except Exception as exc:
                await db.rollback()
                error_message = f"Failed archived session cleanup: {exc}"
                stats["errors"].append(error_message)
                logger.error(error_message, exc_info=True)

        return stats

    async def cleanup_orphaned_group_members(self) -> CleanupStats:
        """
        Delete group_members rows that reference missing groups or missing users.

        Returns:
            Cleanup statistics with checked rows, cleaned rows, and errors.
        """
        stats: CleanupStats = {
            "type": "orphaned_group_members",
            "total_checked": 0,
            "cleaned_count": 0,
            "errors": [],
        }

        async with AsyncSessionLocal() as db:
            try:
                stats["total_checked"] = await self._count_rows(db, GroupMember)

                group_exists = (
                    select(SessionGroup.id).where(SessionGroup.id == GroupMember.group_id).exists()
                )
                user_exists = select(User.id).where(User.id == GroupMember.user_id).exists()

                orphaned_result = await db.execute(
                    select(GroupMember.id).where(or_(~group_exists, ~user_exists))
                )
                orphaned_ids = orphaned_result.scalars().all()

                if not orphaned_ids:
                    logger.info("No orphaned group_members found")
                    return stats

                delete_result = await db.execute(
                    delete(GroupMember).where(GroupMember.id.in_(orphaned_ids))
                )
                await db.commit()

                stats["cleaned_count"] = self._resolve_rowcount(
                    delete_result.rowcount, len(orphaned_ids)
                )
                logger.info("Deleted %s orphaned group_members", stats["cleaned_count"])

            except Exception as exc:
                await db.rollback()
                error_message = f"Failed orphaned group_members cleanup: {exc}"
                stats["errors"].append(error_message)
                logger.error(error_message, exc_info=True)

        return stats

    async def cleanup_orphaned_tags(self) -> CleanupStats:
        """
        Delete session_group_tags rows that reference non-existent groups.

        Returns:
            Cleanup statistics with checked rows, cleaned rows, and errors.
        """
        stats: CleanupStats = {
            "type": "orphaned_session_group_tags",
            "total_checked": 0,
            "cleaned_count": 0,
            "errors": [],
        }

        async with AsyncSessionLocal() as db:
            try:
                stats["total_checked"] = await self._count_rows(db, SessionGroupTag)
                group_exists = (
                    select(SessionGroup.id)
                    .where(SessionGroup.id == SessionGroupTag.group_id)
                    .exists()
                )

                orphaned_result = await db.execute(
                    select(SessionGroupTag.id).where(~group_exists)
                )
                orphaned_ids = orphaned_result.scalars().all()

                if not orphaned_ids:
                    logger.info("No orphaned session_group_tags found")
                    return stats

                delete_result = await db.execute(
                    delete(SessionGroupTag).where(SessionGroupTag.id.in_(orphaned_ids))
                )
                await db.commit()

                stats["cleaned_count"] = self._resolve_rowcount(
                    delete_result.rowcount, len(orphaned_ids)
                )
                logger.info("Deleted %s orphaned session_group_tags", stats["cleaned_count"])

            except Exception as exc:
                await db.rollback()
                error_message = f"Failed orphaned session_group_tags cleanup: {exc}"
                stats["errors"].append(error_message)
                logger.error(error_message, exc_info=True)

        return stats

    async def cleanup_orphaned_patent_analyses(self) -> CleanupStats:
        """
        Delete patent_analyses rows with invalid or missing session references.

        A session reference is considered valid when it exists in either:
        - chat_sessions.session_id (active sessions)
        - archived_sessions.session_id (archived sessions)

        Returns:
            Cleanup statistics with checked rows, cleaned rows, and errors.
        """
        stats: CleanupStats = {
            "type": "orphaned_patent_analyses",
            "total_checked": 0,
            "cleaned_count": 0,
            "errors": [],
        }

        async with AsyncSessionLocal() as db:
            try:
                stats["total_checked"] = await self._count_rows(db, PatentAnalysis)

                chat_session_exists = (
                    select(ChatSession.session_id)
                    .where(ChatSession.session_id == PatentAnalysis.session_id)
                    .exists()
                )
                archived_session_exists = (
                    select(ArchivedSession.session_id)
                    .where(ArchivedSession.session_id == PatentAnalysis.session_id)
                    .exists()
                )

                orphan_condition = or_(
                    PatentAnalysis.session_id.is_(None),
                    PatentAnalysis.session_id == "",
                    and_(~chat_session_exists, ~archived_session_exists),
                )

                orphaned_result = await db.execute(
                    select(PatentAnalysis.id).where(orphan_condition)
                )
                orphaned_ids = orphaned_result.scalars().all()

                if not orphaned_ids:
                    logger.info("No orphaned patent_analyses found")
                    return stats

                delete_result = await db.execute(
                    delete(PatentAnalysis).where(PatentAnalysis.id.in_(orphaned_ids))
                )
                await db.commit()

                stats["cleaned_count"] = self._resolve_rowcount(
                    delete_result.rowcount, len(orphaned_ids)
                )
                logger.info("Deleted %s orphaned patent_analyses", stats["cleaned_count"])

            except Exception as exc:
                await db.rollback()
                error_message = f"Failed orphaned patent_analyses cleanup: {exc}"
                stats["errors"].append(error_message)
                logger.error(error_message, exc_info=True)

        return stats

    async def run_cleanup_cycle(self) -> CleanupCycleStats:
        """
        Execute all cleanup policies and aggregate cleanup statistics.

        Returns:
            A dictionary containing per-policy stats and overall totals.
        """
        cycle_stats: CleanupCycleStats = {
            "old_archived_sessions": {"total_checked": 0, "cleaned_count": 0, "errors": []},
            "orphaned_group_members": {"total_checked": 0, "cleaned_count": 0, "errors": []},
            "orphaned_session_group_tags": {
                "total_checked": 0,
                "cleaned_count": 0,
                "errors": [],
            },
            "orphaned_patent_analyses": {"total_checked": 0, "cleaned_count": 0, "errors": []},
            "total_checked": 0,
            "cleaned_count": 0,
            "errors": [],
        }

        logger.info("Starting auto cleanup cycle")

        cleanup_functions: list[Callable[[], Awaitable[CleanupStats]]] = [
            self.cleanup_old_archived_sessions,
            self.cleanup_orphaned_group_members,
            self.cleanup_orphaned_tags,
            self.cleanup_orphaned_patent_analyses,
        ]

        for cleanup_func in cleanup_functions:
            try:
                policy_stats = await cleanup_func()
                policy_key = policy_stats["type"]
                cycle_stats[policy_key] = {
                    "total_checked": policy_stats["total_checked"],
                    "cleaned_count": policy_stats["cleaned_count"],
                    "errors": policy_stats["errors"],
                }
                cycle_stats["total_checked"] += int(policy_stats["total_checked"])
                cycle_stats["cleaned_count"] += int(policy_stats["cleaned_count"])
                cycle_stats["errors"].extend(policy_stats["errors"])
            except Exception as exc:
                error_message = f"Unexpected failure running cleanup policy {cleanup_func.__name__}: {exc}"
                cycle_stats["errors"].append(error_message)
                logger.error(error_message, exc_info=True)

        logger.info(
            "Auto cleanup cycle completed: cleaned=%s checked=%s errors=%s",
            cycle_stats["cleaned_count"],
            cycle_stats["total_checked"],
            len(cycle_stats["errors"]),
        )
        return cycle_stats

    def _sync_wrapper(self) -> None:
        """Run async cleanup cycle in a dedicated event loop for APScheduler."""
        import asyncio

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.run_cleanup_cycle())
            finally:
                loop.close()
        except Exception as exc:
            logger.error("Cleanup sync wrapper failed: %s", exc, exc_info=True)

    def start(self) -> None:
        """Start periodic auto cleanup scheduler."""
        if self._is_running:
            logger.warning("Auto cleanup scheduler is already running")
            return

        try:
            self.scheduler.add_job(
                func=self._sync_wrapper,
                trigger=IntervalTrigger(minutes=self.cleanup_interval_minutes),
                id="auto_cleanup_cycle",
                name="Auto cleanup cycle",
                replace_existing=True,
            )
            self.scheduler.start()
            self._is_running = True
            logger.info(
                "Auto cleanup scheduler started (interval=%s minutes, retention=%s days)",
                self.cleanup_interval_minutes,
                self.archived_retention_days,
            )
        except Exception as exc:
            logger.error("Failed to start auto cleanup scheduler: %s", exc, exc_info=True)
            raise

    def stop(self) -> None:
        """Stop periodic auto cleanup scheduler gracefully."""
        if not self._is_running:
            logger.warning("Auto cleanup scheduler is not running")
            return

        try:
            self.scheduler.shutdown(wait=True)
            self._is_running = False
            logger.info("Auto cleanup scheduler stopped")
        except Exception as exc:
            logger.error("Failed to stop auto cleanup scheduler: %s", exc, exc_info=True)
            raise

    def is_running(self) -> bool:
        """Return scheduler running status."""
        return self._is_running


auto_cleanup_scheduler = AutoCleanupScheduler()


def get_scheduler() -> AutoCleanupScheduler:
    """Dependency injection accessor for the auto cleanup scheduler."""
    return auto_cleanup_scheduler
