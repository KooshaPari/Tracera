"""Service for Chaos Mode features."""

from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.repositories.event_repository import EventRepository
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository


class ChaosModeService:
    """Service for advanced chaos mode features."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.items = ItemRepository(session)
        self.links = LinkRepository(session)
        self.events = EventRepository(session)

    async def detect_zombies(
        self,
        project_id: str,
        days_inactive: int = 30,
    ) -> dict[str, Any]:
        """Detect zombie items (orphaned/dead items)."""
        items = await self.items.query(project_id, {})

        zombies = []
        for item in items:
            # Check if item has no links
            has_links = await self.links.get_by_source(item.id)
            has_incoming = await self.links.get_by_target(item.id)

            # Check if item is stale
            is_stale = False
            if hasattr(item, "updated_at"):
                days_since_update = (datetime.utcnow() - item.updated_at).days
                is_stale = days_since_update > days_inactive

            # Item is zombie if orphaned and stale
            if not has_links and not has_incoming and is_stale:
                zombies.append(
                    {
                        "item_id": item.id,
                        "title": item.title,
                        "status": item.status,
                        "days_inactive": days_since_update if is_stale else 0,
                    }
                )

        return {
            "zombie_count": len(zombies),
            "zombies": zombies,
            "total_items": len(items),
            "zombie_percentage": (len(zombies) / len(items) * 100) if items else 0,
        }

    async def analyze_impact(
        self,
        project_id: str,
        item_id: str,
    ) -> dict[str, Any]:
        """Analyze impact of changing an item."""
        item = await self.items.get_by_id(item_id)
        if not item:
            return {"error": "Item not found"}

        # Find all items that depend on this item
        direct_impact = await self.links.get_by_source(item_id)

        # Find all items this item depends on
        dependencies = await self.links.get_by_target(item_id)

        # Calculate transitive impact
        transitive_impact = set()
        for link in direct_impact:
            transitive = await self._get_transitive_impact(link.target_item_id)
            transitive_impact.update(transitive)

        return {
            "item_id": item_id,
            "item_title": item.title,
            "direct_impact": len(direct_impact),
            "dependencies": len(dependencies),
            "transitive_impact": len(transitive_impact),
            "total_impact": len(direct_impact) + len(transitive_impact),
            "impact_items": [
                {"id": link.target_item_id, "type": link.link_type}
                for link in direct_impact
            ],
        }

    async def _get_transitive_impact(self, item_id: str) -> set[str]:
        """Get transitive impact of an item."""
        visited = set()
        to_visit = [item_id]

        while to_visit:
            current = to_visit.pop()
            if current in visited:
                continue

            visited.add(current)

            # Get all items that depend on current
            links = await self.links.get_by_source(current)
            for link in links:
                if link.target_item_id not in visited:
                    to_visit.append(link.target_item_id)

        return visited

    async def create_temporal_snapshot(
        self,
        project_id: str,
        snapshot_name: str,
        agent_id: str = "system",
    ) -> dict[str, Any]:
        """Create a temporal snapshot of project state."""
        items = await self.items.query(project_id, {})
        # Get all links by querying all items
        links = []
        for item in items:
            source_links = await self.links.get_by_source(item.id)
            links.extend(source_links)

        snapshot = {
            "name": snapshot_name,
            "timestamp": datetime.utcnow().isoformat(),
            "project_id": project_id,
            "item_count": len(items),
            "link_count": len(links),
            "items": [
                {
                    "id": item.id,
                    "title": item.title,
                    "status": item.status,
                    "view": item.view,
                }
                for item in items
            ],
            "links": [
                {
                    "id": link.id,
                    "source": link.source_item_id,
                    "target": link.target_item_id,
                    "type": link.link_type,
                }
                for link in links
            ],
        }

        # Log event
        await self.events.log(
            project_id=project_id,
            event_type="snapshot_created",
            entity_type="snapshot",
            entity_id=snapshot_name,
            data=snapshot,
            agent_id=agent_id,
        )

        return snapshot

    async def mass_update_items(
        self,
        project_id: str,
        item_ids: list[str],
        updates: dict[str, Any],
        agent_id: str = "system",
    ) -> dict[str, Any]:
        """Mass update multiple items."""
        updated = []
        errors = []

        for item_id in item_ids:
            try:
                item = await self.items.get_by_id(item_id)
                if not item:
                    errors.append(f"Item {item_id} not found")
                    continue

                # Update item
                updated_item = await self.items.update(
                    item_id=item_id,
                    expected_version=item.version,
                    **updates,
                )

                # Log event
                await self.events.log(
                    project_id=project_id,
                    event_type="item_mass_updated",
                    entity_type="item",
                    entity_id=item_id,
                    data={"updates": updates},
                    agent_id=agent_id,
                )

                updated.append(updated_item.id)
            except Exception as e:
                errors.append(f"Failed to update {item_id}: {e!s}")

        return {
            "updated_count": len(updated),
            "error_count": len(errors),
            "updated_items": updated,
            "errors": errors,
        }

    async def get_project_health(
        self,
        project_id: str,
    ) -> dict[str, Any]:
        """Get overall project health metrics."""
        items = await self.items.query(project_id, {})
        # Get all links by querying all items
        links = []
        for item in items:
            source_links = await self.links.get_by_source(item.id)
            links.extend(source_links)

        # Calculate metrics
        total_items = len(items)
        completed_items = len([i for i in items if i.status == "complete"])
        in_progress_items = len([i for i in items if i.status == "in_progress"])
        todo_items = len([i for i in items if i.status == "todo"])

        # Detect zombies
        zombies_result = await self.detect_zombies(project_id)

        # Calculate health score (0-100)
        health_score = 100
        if total_items > 0:
            # Reduce score for incomplete items
            health_score -= (todo_items / total_items) * 20
            # Reduce score for zombies
            health_score -= (zombies_result["zombie_percentage"] / 100) * 30

        return {
            "health_score": max(0, health_score),
            "total_items": total_items,
            "completed": completed_items,
            "in_progress": in_progress_items,
            "todo": todo_items,
            "total_links": len(links),
            "zombie_count": zombies_result["zombie_count"],
            "completion_percentage": (
                (completed_items / total_items * 100) if total_items > 0 else 0
            ),
        }

    async def explode_file(
        self,
        content: str,
        project_id: str,
        view: str,
    ) -> int:
        """Explode file content into multiple items."""

        items_created = 0
        lines = content.split("\n")
        current_parent = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Markdown headers (## Title)
            if line.startswith("#"):
                level = len(line) - len(line.lstrip("#"))
                title = line.lstrip("#").strip()

                if title:
                    item = await self.items.create(
                        project_id=project_id,
                        title=title,
                        view=view,
                        item_type="feature" if level == 1 else "story",
                        status="todo",
                        parent_id=current_parent,
                    )
                    items_created += 1

                    # Set as parent for next level
                    if level == 1 or level == 2:
                        current_parent = item.id

            # YAML list items (- Item)
            elif line.startswith("- "):
                title = line[2:].strip()
                if title:
                    await self.items.create(
                        project_id=project_id,
                        title=title,
                        view=view,
                        item_type="task",
                        status="todo",
                        parent_id=current_parent,
                    )
                    items_created += 1

            # Plain text lines (treat as items)
            elif len(line) > 10:  # Only create items for substantial lines
                await self.items.create(
                    project_id=project_id,
                    title=line[:100],  # Truncate long lines
                    view=view,
                    item_type="note",
                    status="todo",
                    parent_id=current_parent,
                )
                items_created += 1

        return items_created

    async def track_scope_crash(
        self,
        project_id: str,
        reason: str,
        item_ids: list[str],
        agent_id: str = "system",
    ) -> dict[str, Any]:
        """Track scope crash (mass cancellation)."""
        items_affected = 0

        for item_id in item_ids:
            item = await self.items.get_by_id(item_id)
            if item and item.project_id == project_id:
                # Update item status to cancelled
                await self.items.update(
                    item_id=item_id,
                    expected_version=item.version,
                    status="cancelled",
                )
                items_affected += 1

        # Log crash event
        event = await self.events.log(
            project_id=project_id,
            event_type="scope_crash",
            entity_type="project",
            entity_id=project_id,
            data={
                "reason": reason,
                "items_affected": items_affected,
                "item_ids": item_ids,
            },
            agent_id=agent_id,
        )

        return {
            "event_id": event.id,
            "items_affected": items_affected,
            "reason": reason,
        }

    async def cleanup_zombies(
        self,
        project_id: str,
        days_inactive: int = 30,
    ) -> int:
        """Cleanup (delete) zombie items."""
        zombies_result = await self.detect_zombies(project_id, days_inactive)
        deleted_count = 0

        for zombie in zombies_result.get("zombies", []):
            item_id = zombie["item_id"]
            item = await self.items.get_by_id(item_id)
            if item:
                # Soft delete by setting deleted_at
                await self.items.update(
                    item_id=item_id,
                    expected_version=item.version,
                    deleted_at=datetime.utcnow(),
                )
                deleted_count += 1

        return deleted_count

    async def create_snapshot(
        self,
        project_id: str,
        name: str,
        description: str | None = None,
        agent_id: str = "system",
    ) -> dict[str, Any]:
        """Create a temporal snapshot (wrapper for create_temporal_snapshot)."""
        snapshot = await self.create_temporal_snapshot(project_id, name, agent_id)

        if description:
            snapshot["description"] = description

        return {
            "snapshot_id": snapshot.get("name"),
            "items_count": snapshot.get("item_count", 0),
            "links_count": snapshot.get("link_count", 0),
            "timestamp": snapshot.get("timestamp"),
        }
