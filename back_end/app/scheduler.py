"""
Session Archival Scheduler

Handles periodic archival of inactive Redis sessions to MariaDB.
Supports on-demand archival and graceful startup/shutdown.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.redis_client import redis_client
from app.crud.crud_archived_session import ArchivedSessionCRUD
from shared.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


class SessionArchivalScheduler:
    """
    Manages session archival with APScheduler.

    Features:
    - Periodic archival of inactive sessions
    - On-demand archival trigger
    - Graceful startup/shutdown
    - Configurable archival interval
    - Error handling with logging
    """

    def __init__(self):
        """
        Initialize the archival scheduler.

        Uses configuration from settings:
        - SESSION_ARCHIVAL_INTERVAL_MINUTES: Interval between archival jobs
        - SESSION_INACTIVITY_THRESHOLD_MINUTES: Inactivity threshold for archival
        """
        self.archive_interval_minutes = settings.SESSION_ARCHIVAL_INTERVAL_MINUTES
        self.inactivity_threshold_minutes = settings.SESSION_INACTIVITY_THRESHOLD_MINUTES
        self.scheduler = BackgroundScheduler()
        self._is_running = False

    async def archive_session(self, session_id: str) -> bool:
        """
        Archive a single session to MariaDB and remove from Redis.

        Args:
            session_id: The session ID to archive

        Returns:
            True if archival succeeded, False otherwise
        """
        async with AsyncSessionLocal() as db:
            try:
                # Get session from Redis
                session_data = await redis_client.get_session(session_id)
                if not session_data:
                    logger.warning(f"Session {session_id} not found in Redis, skipping archival")
                    return False

                user_id = session_data.get("user_id")
                if user_id is None:
                    logger.error(f"Session {session_id} has no user_id, skipping archival")
                    return False

                title = session_data.get("title", "Untitled Session")
                messages = session_data.get("messages", [])
                context = session_data.get("metadata", {})

                # Create archived session in MariaDB
                archived_crud = ArchivedSessionCRUD(db)
                await archived_crud.create(
                    session_id=session_id,
                    user_id=user_id,
                    title=title,
                    messages=messages,
                    context=context,
                )
                logger.info(f"Archived session {session_id} for user {user_id}")

                # Delete from Redis
                deleted = await redis_client.delete_session(session_id)
                if deleted:
                    logger.info(f"Deleted session {session_id} from Redis")
                else:
                    logger.warning(f"Failed to delete session {session_id} from Redis")

                return True

            except Exception as e:
                logger.error(f"Failed to archive session {session_id}: {e}", exc_info=True)
                return False

    async def archive_inactive_sessions(self) -> dict:
        """
        Archive all sessions inactive for > configured threshold.

        Finds sessions in Redis that haven't been accessed recently,
        archives them to MariaDB, and removes from Redis.

        Returns:
            Dictionary with archival statistics:
            {
                "total_checked": int,
                "archived": int,
                "failed": int,
                "errors": list[str]
            }
        """
        stats = {
            "total_checked": 0,
            "archived": 0,
            "failed": 0,
            "errors": []
        }

        try:
            # Get all session keys from Redis
            import redis.asyncio as redis
            redis_conn = redis.from_url(settings.REDIS_URL, decode_responses=True)
            keys = await redis_conn.keys("session:*")
            await redis_conn.close()

            stats["total_checked"] = len(keys)

            if not keys:
                logger.info("No sessions found in Redis for archival")
                return stats

            # Check each session for inactivity
            inactive_threshold = timedelta(minutes=self.inactivity_threshold_minutes)
            now = datetime.utcnow()

            for key in keys:
                session_id = key.replace("session:", "")
                try:
                    # Get session data to check last_access
                    session_data = await redis_client.get_session(session_id)
                    if not session_data:
                        continue

                    # Check if session is inactive
                    last_access_str = session_data.get("last_access")
                    if not last_access_str:
                        # No last_access timestamp, assume inactive
                        last_access = datetime.fromisoformat(
                            session_data.get("created_at", now.isoformat())
                        )
                    else:
                        last_access = datetime.fromisoformat(last_access_str)

                    # Archive if inactive beyond threshold
                    if (now - last_access) > inactive_threshold:
                        success = await self.archive_session(session_id)
                        if success:
                            stats["archived"] += 1
                        else:
                            stats["failed"] += 1
                            stats["errors"].append(f"Failed to archive session {session_id}")

                except Exception as e:
                    logger.error(f"Error processing session {session_id}: {e}")
                    stats["failed"] += 1
                    stats["errors"].append(f"Error processing {session_id}: {str(e)}")

            logger.info(
                f"Archival job completed: {stats['archived']} archived, "
                f"{stats['failed']} failed, {stats['total_checked']} checked"
            )

        except Exception as e:
            logger.error(f"Archive inactive sessions job failed: {e}", exc_info=True)
            stats["errors"].append(f"Job execution error: {str(e)}")

        return stats

    def _sync_archive_wrapper(self) -> None:
        """
        Synchronous wrapper for archival job (APScheduler requires sync functions).
        Runs the async archival in a new event loop.
        """
        import asyncio

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.archive_inactive_sessions())
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Archive job wrapper failed: {e}", exc_info=True)

    def start(self) -> None:
        """Start the archival scheduler."""
        if self._is_running:
            logger.warning("Scheduler is already running")
            return

        try:
            # Add periodic archival job
            self.scheduler.add_job(
                func=self._sync_archive_wrapper,
                trigger=IntervalTrigger(minutes=self.archive_interval_minutes),
                id="archive_inactive_sessions",
                name="Archive inactive sessions",
                replace_existing=True,
            )

            # Start the scheduler
            self.scheduler.start()
            self._is_running = True
            logger.info(
                f"Session archival scheduler started (interval: {self.archive_interval_minutes} minutes)"
            )

        except Exception as e:
            logger.error(f"Failed to start archival scheduler: {e}", exc_info=True)
            raise

    def stop(self) -> None:
        """Stop the archival scheduler gracefully."""
        if not self._is_running:
            logger.warning("Scheduler is not running")
            return

        try:
            # Shutdown scheduler (wait for jobs to complete)
            self.scheduler.shutdown(wait=True)
            self._is_running = False
            logger.info("Session archival scheduler stopped")

        except Exception as e:
            logger.error(f"Failed to stop archival scheduler: {e}", exc_info=True)
            raise

    def is_running(self) -> bool:
        """Check if the scheduler is running."""
        return self._is_running


# Global scheduler instance
scheduler = SessionArchivalScheduler()


def get_scheduler() -> SessionArchivalScheduler:
    """Dependency injection for archival scheduler."""
    return scheduler
