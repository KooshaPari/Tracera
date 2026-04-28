"""Item service for TraceRTM."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from loguru import logger
from sqlalchemy.exc import OperationalError

from tracertm.constants import (
    DEFAULT_LIMIT,
    DEFAULT_OFFSET,
    PERCENTAGE_MAX,
    ZERO,
)
from tracertm.core.concurrency import ConcurrencyError, update_with_retry
from tracertm.repositories.event_repository import EventRepository
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from tracertm.models.item import Item


@dataclass
class CreateItemInput:
    """Input for creating an item with optional links and metadata."""

    project_id: str
    title: str
    view: str
    item_type: str
    agent_id: str
    description: str | None = None
    status: str = "todo"
    parent_id: str | None = None
    metadata: dict[str, Any] | None = None
    owner: str | None = None
    priority: str | None = "medium"
    link_to: list[str] | None = None
    link_type: str = "relates_to"


@dataclass
class ListItemsParams:
    """Parameters for listing items in a project."""

    view: str | None = None
    status: str | None = None
    include_deleted: bool = False
    limit: int = DEFAULT_LIMIT
    offset: int = DEFAULT_OFFSET


# Valid status transitions
STATUS_TRANSITIONS = {
    "todo": ["in_progress", "blocked"],
    "in_progress": ["done", "blocked", "todo"],
    "blocked": ["todo", "in_progress"],
    "done": ["todo"],  # Allow reopening
}

# Valid statuses
VALID_STATUSES = ["todo", "in_progress", "blocked", "done"]


class ItemService:
    """Service for item business logic.

    Functional Requirements:
    - FR-APP-001
    - FR-APP-002
    - FR-APP-003
    - FR-APP-004
    - FR-APP-005

    User Stories:
    - US-ITEM-001
    - US-ITEM-002
    - US-ITEM-003
    - US-ITEM-004
    - US-ITEM-005

    Epics:
    - EPIC-003
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session
        self.items = ItemRepository(session)
        self.links = LinkRepository(session)
        self.events = EventRepository(session)

    async def create_item(self, input: CreateItemInput) -> Item:
        """Create item with optional links and event logging.

        Functional Requirements:
        - FR-APP-001

        User Stories:
        - US-ITEM-001

        Epics:
        - EPIC-003
        """
        item = await self.items.create(
            project_id=input.project_id,
            title=input.title,
            view=input.view,
            item_type=input.item_type,
            description=input.description,
            status=input.status,
            parent_id=input.parent_id,
            metadata=input.metadata,
            owner=input.owner,
            priority=input.priority,
            created_by=input.agent_id,
        )

        if input.link_to:
            for target_id in input.link_to:
                await self.links.create(
                    project_id=input.project_id,
                    source_item_id=str(item.id),
                    target_item_id=target_id,
                    link_type=input.link_type,
                )

        await self.events.log(
            project_id=input.project_id,
            event_type="item_created",
            entity_type="item",
            entity_id=str(item.id),
            data={
                "item": {
                    "id": str(item.id),
                    "title": item.title,
                    "view": item.view,
                    "item_type": item.item_type,
                    "status": item.status,
                    "owner": item.owner,
                    "priority": item.priority,
                },
                "links": input.link_to or [],
            },
            agent_id=input.agent_id,
        )

        return item

    async def get_item(self, project_id: str, item_id: str) -> Item | None:
        """Get item by ID, ensuring it belongs to the project.

        Functional Requirements:
        - FR-APP-002

        User Stories:
        - US-ITEM-002

        Epics:
        - EPIC-003
        """
        return await self.items.get_by_id(item_id, project_id)

    async def list_items(self, project_id: str, params: ListItemsParams | None = None) -> list[Item]:
        """List items in a project, optionally filtered by view and status.

        Functional Requirements:
        - FR-APP-005

        User Stories:
        - US-ITEM-005

        Epics:
        - EPIC-003
        """
        p = params or ListItemsParams()
        if p.view:
            return await self.items.get_by_view(project_id, p.view, p.status, limit=p.limit, offset=p.offset)
        return await self.items.get_by_project(project_id, status=p.status, limit=p.limit, offset=p.offset)

    async def update_item(
        self,
        item_id: str,
        agent_id: str,
        **updates: object,
    ) -> Item:
        """Update item with retry on conflict.

        Functional Requirements:
        - FR-APP-003

        User Stories:
        - US-ITEM-003

        Epics:
        - EPIC-003
        """

        async def do_update() -> Item:
            item = await self.items.get_by_id(item_id)
            if not item:
                msg = f"Item {item_id} not found"
                raise ValueError(msg)

            # Update with optimistic locking
            updated_item = await self.items.update(
                item_id=item_id,
                expected_version=item.version,
                **updates,
            )

            # Log event
            await self.events.log(
                project_id=str(updated_item.project_id),
                event_type="item_updated",
                entity_type="item",
                entity_id=item_id,
                data={"changes": updates},
                agent_id=agent_id,
            )

            return updated_item

        return await update_with_retry(do_update)

    async def get_item_with_links(self, item_id: str) -> dict[str, Any] | None:
        """Get item with all its links."""
        item = await self.items.get_by_id(item_id)
        if not item:
            return None

        links = await self.links.get_by_item(item_id)

        return {
            "item": item,
            "links": links,
        }

    async def get_children(self, item_id: str) -> list[Item]:
        """Get direct children of an item."""
        return await self.items.get_children(item_id)

    async def get_ancestors(self, item_id: str) -> list[Item]:
        """Get ancestors (path to root)."""
        return await self.items.get_ancestors(item_id)

    async def get_descendants(self, item_id: str) -> list[Item]:
        """Get all descendants."""
        return await self.items.get_descendants(item_id)

    async def delete_item(
        self,
        item_id: str,
        agent_id: str,
        soft: bool = True,
    ) -> bool:
        """Delete item and its links.

        Functional Requirements:
        - FR-APP-004

        User Stories:
        - US-ITEM-004

        Epics:
        - EPIC-003
        """
        # Check existence first
        item = await self.items.get_by_id(item_id)
        if not item:
            # If doing hard delete, check if it exists but is soft deleted
            if not soft:
                # We need a way to get even deleted items for hard delete confirmation
                # But repository.get_by_id filters them out by default.
                # Let's trust the repo delete logic which handles ID check internally for hard delete if we pass ID
                pass
            else:
                return False

        # Delegate to repository which handles links and cascade
        success = await self.items.delete(item_id, soft=soft)

        if success:
            # Log event
            await self.events.log(
                project_id=str(item.project_id) if item else "unknown",  # Fallback if item not loaded
                event_type="item_deleted",
                entity_type="item",
                entity_id=item_id,
                data={"soft": soft},
                agent_id=agent_id,
            )

        return success

    async def undelete_item(self, item_id: str, agent_id: str) -> Item | None:
        """Restore a soft-deleted item."""
        item = await self.items.restore(item_id)
        if item:
            await self.events.log(
                project_id=str(item.project_id),
                event_type="item_restored",
                entity_type="item",
                entity_id=item_id,
                data={},
                agent_id=agent_id,
            )
        return item

    async def update_metadata(
        self,
        item_id: str,
        agent_id: str,
        metadata_updates: dict[str, Any],
        merge: bool = True,
    ) -> Item:
        """Update item metadata (merge or replace)."""

        async def do_update() -> Item:
            item = await self.items.get_by_id(item_id)
            if not item:
                msg = f"Item {item_id} not found"
                raise ValueError(msg)

            # Prepare new metadata
            if merge:
                current_meta = item.item_metadata or {}
                new_meta = current_meta.copy()
                new_meta.update(metadata_updates)
            else:
                new_meta = metadata_updates

            # Update with optimistic locking
            updated_item = await self.items.update(
                item_id=item_id,
                expected_version=item.version,
                item_metadata=new_meta,
            )

            # Log event
            await self.events.log(
                project_id=str(updated_item.project_id),
                event_type="item_metadata_updated",
                entity_type="item",
                entity_id=item_id,
                data={"metadata_updates": metadata_updates},
                agent_id=agent_id,
            )

            return updated_item

        return await update_with_retry(do_update)

    async def update_item_status(
        self,
        item_id: str,
        new_status: str,
        agent_id: str,
        project_id: str,
    ) -> Item:
        """Update item status with validation and event logging."""
        # Validate new status
        if new_status not in VALID_STATUSES:
            msg = f"Invalid status: {new_status}. Valid statuses: {', '.join(VALID_STATUSES)}"
            raise ValueError(msg)

        async def do_update() -> Item:
            item = await self.items.get_by_id(item_id, project_id)
            if not item:
                msg = f"Item {item_id} not found"
                raise ValueError(msg)

            # Validate transition
            current_status = item.status
            if current_status not in STATUS_TRANSITIONS:
                msg = f"Unknown current status: {current_status}"
                raise ValueError(msg)

            allowed_transitions = STATUS_TRANSITIONS[current_status]
            if new_status not in allowed_transitions:
                msg = (
                    f"Cannot transition from {current_status} to {new_status}. "
                    f"Allowed transitions: {', '.join(allowed_transitions)}"
                )
                raise ValueError(
                    msg,
                )

            # Update status with optimistic locking
            updated_item = await self.items.update(
                item_id=item_id,
                expected_version=item.version,
                status=new_status,
            )

            # Log event
            await self.events.log(
                project_id=project_id,
                event_type="item_status_changed",
                entity_type="item",
                entity_id=item_id,
                data={
                    "old_status": current_status,
                    "new_status": new_status,
                    "item_id": item_id,
                },
                agent_id=agent_id,
            )

            return updated_item

        return await update_with_retry(do_update)

    async def get_item_progress(
        self,
        item_id: str,
        project_id: str,
    ) -> dict[str, Any]:
        """Calculate progress for an item based on its children."""
        item = await self.items.get_by_id(item_id, project_id)
        if not item:
            msg = f"Item {item_id} not found"
            raise ValueError(msg)

        # Get all children
        children = await self.items.get_children(item_id)

        if not children:
            # No children, return item's own status
            return {
                "item_id": item_id,
                "total": 1,
                "done": 1 if item.status == "done" else ZERO,
                "in_progress": 1 if item.status == "in_progress" else ZERO,
                "blocked": 1 if item.status == "blocked" else ZERO,
                "todo": 1 if item.status == "todo" else ZERO,
                "percentage": PERCENTAGE_MAX if item.status == "done" else ZERO,
            }

        # Count children by status
        total = len(children)
        done = sum(1 for child in children if child.status == "done")
        in_progress = sum(1 for child in children if child.status == "in_progress")
        blocked = sum(1 for child in children if child.status == "blocked")
        todo = sum(1 for child in children if child.status == "todo")

        percentage = int((done / total) * PERCENTAGE_MAX) if total > ZERO else ZERO

        return {
            "item_id": item_id,
            "total": total,
            "done": done,
            "in_progress": in_progress,
            "blocked": blocked,
            "todo": todo,
            "percentage": percentage,
        }

    async def bulk_update_preview(
        self,
        filters: dict[str, Any],
        updates: dict[str, Any],
        project_id: str,
    ) -> dict[str, Any]:
        """Preview bulk update without applying changes."""
        # Get items matching filters
        items = await self.items.list_by_filters(filters, project_id)

        # Show what would be updated
        return {
            "total_items": len(items),
            "updates": updates,
            "affected_items": [
                {
                    "id": item.id,
                    "title": item.title,
                    "current_values": {
                        "status": item.status,
                        "priority": item.priority,
                    },
                    "new_values": updates,
                }
                for item in items
            ],
        }

    async def bulk_update_items(
        self,
        filters: dict[str, Any],
        updates: dict[str, Any],
        agent_id: str,
        project_id: str,
    ) -> dict[str, Any]:
        """Bulk update items matching filters."""
        # Get items matching filters
        items = await self.items.list_by_filters(filters, project_id)

        if not items:
            return {
                "success": True,
                "updated": ZERO,
                "failed": ZERO,
                "errors": [],
            }

        updated_count = ZERO
        failed_count = ZERO
        errors = []

        # Update each item
        for item in items:
            try:
                await self.items.update(
                    item_id=str(item.id),
                    expected_version=item.version,
                    **updates,
                )

                # Log event
                await self.events.log(
                    project_id=project_id,
                    event_type="item_bulk_updated",
                    entity_type="item",
                    entity_id=str(item.id),
                    data={"updates": updates},
                    agent_id=agent_id,
                )

                updated_count += 1
            except (ValueError, ConcurrencyError, OperationalError) as e:
                logger.error("Failed to update item %s: %s", item.id, e, exc_info=True)
                failed_count += 1
                errors.append({
                    "item_id": item.id,
                    "error": str(e),
                })

        return {
            "success": failed_count == 0,
            "updated": updated_count,
            "failed": failed_count,
            "errors": errors,
        }

    async def bulk_delete_items(
        self,
        filters: dict[str, Any],
        agent_id: str,
        project_id: str,
        soft_delete: bool = True,
    ) -> dict[str, Any]:
        """Bulk delete items matching filters."""
        # Get items matching filters
        items = await self.items.list_by_filters(filters, project_id)

        if not items:
            return {
                "success": True,
                "deleted": 0,
                "failed": 0,
                "errors": [],
            }

        deleted_count = 0
        failed_count = 0
        errors = []

        # Delete each item
        for item in items:
            try:
                await self.items.delete(str(item.id), soft=soft_delete)

                # Log event
                await self.events.log(
                    project_id=project_id,
                    event_type="item_bulk_deleted",
                    entity_type="item",
                    entity_id=str(item.id),
                    data={"soft_delete": soft_delete},
                    agent_id=agent_id,
                )

                deleted_count += 1
            except (ValueError, ConcurrencyError, OperationalError) as e:
                logger.error("Failed to delete item %s: %s", item.id, e, exc_info=True)
                failed_count += 1
                errors.append({
                    "item_id": item.id,
                    "error": str(e),
                })

        return {
            "success": failed_count == 0,
            "deleted": deleted_count,
            "failed": failed_count,
            "errors": errors,
        }

    async def _collect_related_outgoing(self, project_id: str, item_id: str, link_type: str | None) -> list[Item]:
        """Collect items linked from item_id (outgoing)."""
        out: list[Item] = []
        links = await self.links.get_by_source(item_id)
        for link in links:
            if link_type and link.link_type != link_type:
                continue
            target = await self.items.get_by_id(link.target_item_id)
            if target and target.project_id == project_id:
                out.append(target)
        return out

    async def _collect_related_incoming(self, project_id: str, item_id: str, link_type: str | None) -> list[Item]:
        """Collect items linking to item_id (incoming)."""
        out: list[Item] = []
        links = await self.links.get_by_target(item_id)
        for link in links:
            if link_type and link.link_type != link_type:
                continue
            source = await self.items.get_by_id(link.source_item_id)
            if source and source.project_id == project_id:
                out.append(source)
        return out

    @staticmethod
    def _deduplicate_items(items: list[Item]) -> list[Item]:
        """Return items in order, duplicates removed by id."""
        seen: set[str] = set()
        unique: list[Item] = []
        for item in items:
            if item.id not in seen:
                seen.add(item.id)
                unique.append(item)
        return unique

    async def query_by_relationship(
        self,
        project_id: str,
        item_id: str,
        link_type: str | None = None,
        direction: str = "both",
    ) -> list[Item]:
        """Query items by relationship to a given item.

        Args:
            project_id: Project ID
            item_id: Item ID to find related items for
            link_type: Optional link type filter (None = all link types)
            direction: Direction to search ("outgoing", "incoming", "both")

        Returns:
            List of items related to the given item
        """
        try:
            related: list[Item] = []
            if direction in {"outgoing", "both"}:
                related.extend(await self._collect_related_outgoing(project_id, item_id, link_type))
            if direction in {"incoming", "both"}:
                related.extend(await self._collect_related_incoming(project_id, item_id, link_type))
            return self._deduplicate_items(related)
        except (ValueError, OperationalError, KeyError) as e:
            logger.error("Error getting related items for %s: %s", item_id, e, exc_info=True)
            return []
