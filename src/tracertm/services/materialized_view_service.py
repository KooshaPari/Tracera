"""Materialized view management service for TraceRTM."""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# Seconds after which a view is considered stale
STALE_THRESHOLD_SECONDS = 5.0


@dataclass
class ViewStaleness:
    """Information about view staleness."""

    view_name: str
    unprocessed_changes: int
    oldest_change: datetime | None
    staleness_seconds: float | None
    is_stale: bool


class MaterializedViewService:
    """Service for managing materialized views and incremental refresh."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    async def refresh_incremental(self) -> dict[str, Any]:
        """Refresh materialized views incrementally based on change log.

        Returns:
            Dict with refresh statistics
        """
        await self.session.execute(text("SELECT refresh_materialized_views_incremental()"))
        await self.session.commit()

        # Get statistics
        stats = await self.get_refresh_stats()

        return {
            "status": "success",
            "refresh_type": "incremental",
            "timestamp": datetime.now(UTC).isoformat(),
            "stats": stats,
        }

    async def refresh_full(self) -> dict[str, Any]:
        """Perform full refresh of all materialized views.

        Returns:
            Dict with refresh statistics
        """
        await self.session.execute(text("SELECT refresh_materialized_views_full()"))
        await self.session.commit()

        stats = await self.get_refresh_stats()

        return {
            "status": "success",
            "refresh_type": "full",
            "timestamp": datetime.now(UTC).isoformat(),
            "stats": stats,
        }

    async def get_staleness(self) -> ViewStaleness:
        """Get staleness information for materialized views.

        Returns:
            ViewStaleness object with staleness information
        """
        result = await self.session.execute(text("SELECT * FROM get_view_staleness()"))
        row = result.fetchone()

        if not row:
            return ViewStaleness(
                view_name="materialized_views",
                unprocessed_changes=0,
                oldest_change=None,
                staleness_seconds=None,
                is_stale=False,
            )

        staleness_seconds = float(row[3]) if row[3] else 0

        return ViewStaleness(
            view_name=row[0],
            unprocessed_changes=int(row[1]),
            oldest_change=row[2],
            staleness_seconds=staleness_seconds,
            is_stale=staleness_seconds > STALE_THRESHOLD_SECONDS,
        )

    async def cleanup_change_log(self, days_to_keep: int = 30) -> int:
        """Clean up old processed change log entries.

        Args:
            days_to_keep: Number of days to keep (default: 30)

        Returns:
            Number of entries deleted
        """
        result = await self.session.execute(text(f"SELECT cleanup_change_log({days_to_keep})"))
        await self.session.commit()

        deleted_count = result.scalar()
        return int(deleted_count) if deleted_count else 0

    async def get_refresh_stats(self) -> dict[str, Any]:
        """Get statistics about materialized views.

        Returns:
            Dict with view statistics
        """
        # Get row counts for each view
        traceability_count = await self.session.execute(text("SELECT COUNT(*) FROM traceability_matrix"))
        impact_count = await self.session.execute(text("SELECT COUNT(*) FROM impact_analysis"))
        coverage_count = await self.session.execute(text("SELECT COUNT(*) FROM coverage_analysis"))

        # Get change log stats
        change_log_stats = await self.session.execute(
            text(
                """
                SELECT
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE processed = FALSE) as unprocessed,
                    COUNT(*) FILTER (WHERE processed = TRUE) as processed
                FROM change_log
            """,
            ),
        )
        cl_row = change_log_stats.fetchone()

        return {
            "views": {
                "traceability_matrix": {
                    "row_count": traceability_count.scalar(),
                },
                "impact_analysis": {
                    "row_count": impact_count.scalar(),
                },
                "coverage_analysis": {
                    "row_count": coverage_count.scalar(),
                },
            },
            "change_log": {
                "total": cl_row[0] if cl_row else 0,
                "unprocessed": cl_row[1] if cl_row else 0,
                "processed": cl_row[2] if cl_row else 0,
            },
        }

    async def auto_refresh_if_stale(self, max_staleness_seconds: float = 5.0) -> bool:
        """Automatically refresh views if they are stale.

        Args:
            max_staleness_seconds: Maximum staleness before refresh (default: 5.0)

        Returns:
            True if refresh was performed, False otherwise
        """
        staleness = await self.get_staleness()

        if staleness.staleness_seconds and staleness.staleness_seconds > max_staleness_seconds:
            await self.refresh_incremental()
            return True

        return False
