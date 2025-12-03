"""Bulk operation service for TraceRTM."""

import logging
from dataclasses import dataclass
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.core.concurrency import ConcurrencyError
from tracertm.models.item import Item
from tracertm.repositories.event_repository import EventRepository
from tracertm.repositories.item_repository import ItemRepository

logger = logging.getLogger(__name__)


@dataclass
class BulkPreview:
    """Preview of bulk operation before execution."""

    total_count: int
    sample_items: list[dict[str, Any]]  # First 5 items
    validation_warnings: list[str]
    estimated_duration_ms: int

    def is_safe(self) -> bool:
        """Check if operation is safe to execute."""
        return len(self.validation_warnings) == 0


class BulkOperationService:
    """Service for bulk operations with preview."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.items = ItemRepository(session)
        self.events = EventRepository(session)

    async def preview_bulk_update(
        self,
        project_id: str,
        filters: dict[str, Any],
        updates: dict[str, Any],
    ) -> BulkPreview:
        """Preview bulk update before execution."""
        # Query matching items
        matching_items = await self.items.query(project_id, filters)

        # Validation warnings
        warnings = []
        if len(matching_items) > 100:
            warnings.append(
                f"Large operation: {len(matching_items)} items will be updated"
            )

        if "status" in updates:
            new_status = updates["status"]
            if new_status == "complete":
                blocked_count = sum(
                    1 for item in matching_items if item.status == "blocked"
                )
                if blocked_count > 0:
                    warnings.append(
                        f"{blocked_count} blocked items will be marked complete"
                    )

        # Sample items (first 5)
        sample = [
            {
                "id": item.id,
                "title": item.title,
                "current_status": item.status,
                "new_status": updates.get("status", item.status),
            }
            for item in matching_items[:5]
        ]

        # Estimate duration (10ms per item)
        estimated_duration = len(matching_items) * 10

        return BulkPreview(
            total_count=len(matching_items),
            sample_items=sample,
            validation_warnings=warnings,
            estimated_duration_ms=estimated_duration,
        )

    async def execute_bulk_update(
        self,
        project_id: str,
        filters: dict[str, Any],
        updates: dict[str, Any],
        agent_id: str,
        skip_preview: bool = False,
    ) -> list[Item]:
        """Execute bulk update with optional preview."""
        if not skip_preview:
            preview = await self.preview_bulk_update(project_id, filters, updates)
            if not preview.is_safe():
                raise ValueError(
                    f"Bulk operation has warnings: {preview.validation_warnings}"
                )

        # Execute bulk update
        matching_items = await self.items.query(project_id, filters)
        updated_items = []
        conflicts = 0

        for item in matching_items:
            try:
                updated = await self.items.update(
                    item_id=item.id,
                    expected_version=item.version,
                    **updates,
                )
                updated_items.append(updated)
            except ConcurrencyError as e:
                # Log conflict, continue with other items
                logger.warning(f"Conflict updating item {item.id}: {e}")
                conflicts += 1

        # Log bulk operation event
        await self.events.log(
            project_id=project_id,
            event_type="bulk_update",
            entity_type="bulk_operation",
            entity_id=f"bulk_{project_id}",
            data={
                "filters": filters,
                "updates": updates,
                "total_count": len(matching_items),
                "success_count": len(updated_items),
                "conflict_count": conflicts,
            },
            agent_id=agent_id,
        )

        return updated_items
