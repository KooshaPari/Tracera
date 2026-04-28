"""Progress tracking service for Epic 7 (FR68-FR73).

Calculates completion percentages, tracks velocity, and identifies blocked/stalled items.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from tracertm.models.item import Item
from tracertm.models.link import Link


class ProgressService:
    """Service for progress tracking and calculation."""

    def __init__(self, session: Session) -> None:
        """Initialize progress service."""
        self.session = session

    def calculate_completion(self, item_id: str) -> float:
        """Calculate completion percentage for an item (FR68).

        For parent items, calculates average of children.
        For leaf items, uses status-based completion.

        Args:
            item_id: Item ID

        Returns:
            Completion percentage (0-100)
        """
        item = self.session.query(Item).filter(Item.id == item_id).first()
        if not item:
            return 0.0

        # Get children
        children = self.session.query(Item).filter(Item.parent_id == item_id, Item.deleted_at.is_(None)).all()

        if not children:
            # Leaf item - calculate from status
            status_completion = {
                "todo": 0.0,
                "in_progress": 50.0,
                "blocked": 0.0,
                "complete": 100.0,
                "cancelled": 0.0,
            }
            return status_completion.get(item.status, 0.0)

        # Parent item - average of children
        child_completions = [self.calculate_completion(child.id) for child in children]
        if not child_completions:
            return 0.0

        return sum(child_completions) / len(child_completions)

    def get_blocked_items(self, project_id: str) -> list[dict[str, Any]]:
        """Get items that are blocking others (FR70).

        Args:
            project_id: Project ID

        Returns:
            List of blocked items with blocking information
        """
        # Find items with "blocks" links pointing to them
        blocked_items = []

        blocking_links = (
            self.session
            .query(Link)
            .filter(
                Link.project_id == project_id,
                Link.link_type == "blocks",
            )
            .all()
        )

        # Group by target (blocked item)
        blocked_map: dict[str, list[str]] = {}
        for link in blocking_links:
            if link.target_item_id not in blocked_map:
                blocked_map[link.target_item_id] = []
            blocked_map[link.target_item_id].append(link.source_item_id)

        # Get item details
        for item_id, blocker_ids in blocked_map.items():
            item = self.session.query(Item).filter(Item.id == item_id).first()
            if item is not None:
                blockers = [self.session.query(Item).filter(Item.id == bid).first() for bid in blocker_ids]
                blockers_filtered = [b for b in blockers if b is not None]

                blocked_items.append({
                    "item_id": item.id,
                    "title": item.title,
                    "status": item.status,
                    "blockers": [{"id": b.id, "title": b.title, "status": b.status} for b in blockers_filtered],
                })

        return blocked_items

    def get_stalled_items(self, project_id: str, days_threshold: int = 7) -> list[dict[str, Any]]:
        """Get items with no progress (stalled items) (FR71).

        Args:
            project_id: Project ID
            days_threshold: Days without updates to consider stalled

        Returns:
            List of stalled items
        """
        threshold_date = datetime.now(UTC) - timedelta(days=days_threshold)

        stalled = (
            self.session
            .query(Item)
            .filter(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
                Item.status.in_(["todo", "in_progress", "blocked"]),
                Item.updated_at < threshold_date,
            )
            .all()
        )

        return [
            {
                "item_id": item.id,
                "title": item.title,
                "status": item.status,
                "last_updated": item.updated_at.isoformat() if item.updated_at else None,
                "days_stalled": (datetime.now(UTC) - item.updated_at).days if item.updated_at else None,
            }
            for item in stalled
        ]

    def calculate_velocity(self, project_id: str, days: int = 7) -> dict[str, Any]:
        """Calculate velocity (items completed per time period) (FR73).

        Args:
            project_id: Project ID
            days: Time period in days

        Returns:
            Dictionary with velocity metrics
        """
        start_date = datetime.now(UTC) - timedelta(days=days)

        # Count items completed in period
        completed = (
            self.session
            .query(func.count(Item.id))
            .filter(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
                Item.status == "complete",
                Item.updated_at >= start_date,
            )
            .scalar()
        ) or 0

        # Count items created in period
        created = (
            self.session
            .query(func.count(Item.id))
            .filter(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
                Item.created_at >= start_date,
            )
            .scalar()
        ) or 0

        return {
            "period_days": days,
            "items_completed": completed,
            "items_created": created,
            "completion_rate": completed / days if days > 0 else 0,
            "net_change": created - completed,
        }

    def generate_progress_report(
        self,
        project_id: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> dict[str, Any]:
        """Generate progress report for time period (FR72).

        Args:
            project_id: Project ID
            start_date: Optional start date
            end_date: Optional end date

        Returns:
            Dictionary with progress report data
        """
        if not start_date:
            start_date = datetime.now(UTC) - timedelta(days=30)
        if not end_date:
            end_date = datetime.now(UTC)

        # Get all items
        items = (
            self.session
            .query(Item)
            .filter(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
            )
            .all()
        )

        # Calculate statistics
        total_items = len(items)
        by_status: dict[str, int] = {}
        by_view: dict[str, int] = {}

        for item in items:
            by_status[item.status] = by_status.get(item.status, 0) + 1
            by_view[item.view] = by_view.get(item.view, 0) + 1

        # Calculate overall completion
        completed = by_status.get("complete", 0)
        completion_percentage = (completed / total_items * 100) if total_items > 0 else 0

        # Get velocity
        days = (end_date - start_date).days
        velocity = self.calculate_velocity(project_id, days)

        # Get blocked and stalled items
        blocked = self.get_blocked_items(project_id)
        stalled = self.get_stalled_items(project_id)

        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days,
            },
            "summary": {
                "total_items": total_items,
                "completed": completed,
                "completion_percentage": round(completion_percentage, 2),
            },
            "by_status": by_status,
            "by_view": by_view,
            "velocity": velocity,
            "blocked_items": len(blocked),
            "stalled_items": len(stalled),
            "blocked": blocked[:10],  # Limit for report
            "stalled": stalled[:10],  # Limit for report
        }
