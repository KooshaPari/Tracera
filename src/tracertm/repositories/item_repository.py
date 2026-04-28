"""Item repository for TraceRTM."""

import uuid
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.core.concurrency import ConcurrencyError
from tracertm.models.item import Item
from tracertm.models.item_view import ItemView
from tracertm.models.link import Link
from tracertm.models.node_kind import NodeKind
from tracertm.models.view import View


class ItemRepository:
    """Repository for Item CRUD operations with optimistic locking."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    async def create(
        self,
        project_id: str | uuid.UUID,
        title: str,
        view: str,
        item_type: str,
        description: str | None = None,
        status: str = "todo",
        parent_id: str | uuid.UUID | None = None,
        metadata: dict[str, Any] | None = None,
        _owner: str | None = None,
        priority: str | None = "medium",
        _created_by: str = "system",
    ) -> Item:
        """Create new item with optimistic locking."""
        # Validate parent if provided
        if parent_id:
            parent_item = await self.get_by_id(parent_id)
            if not parent_item:
                msg = f"Parent item {parent_id} not found"
                raise ValueError(msg)
            if parent_item.project_id != project_id:
                msg = f"Parent item {parent_id} not in same project"
                raise ValueError(msg)

        supports_node_kinds = await self._table_exists("node_kinds")
        supports_views = await self._table_exists("views")
        supports_item_views = await self._table_exists("item_views")

        node_kind_obj = None
        if supports_node_kinds:
            node_kind = await self.session.execute(
                select(NodeKind).where(
                    NodeKind.project_id == project_id,
                    NodeKind.name == item_type,
                ),
            )
            node_kind_obj = node_kind.scalar_one_or_none()
            if not node_kind_obj:
                node_kind_obj = NodeKind(
                    id=str(uuid4()),
                    project_id=project_id,
                    name=item_type,
                    description=None,
                    kind_metadata={},
                )
                self.session.add(node_kind_obj)
                await self.session.flush()

        view_obj = None
        if supports_views:
            view_result = await self.session.execute(
                select(View).where(View.project_id == project_id, View.name == view),
            )
            view_obj = view_result.scalar_one_or_none()
            if not view_obj:
                view_obj = View(
                    id=str(uuid4()),
                    project_id=project_id,
                    name=view,
                    description=None,
                    view_metadata={},
                )
                self.session.add(view_obj)
                await self.session.flush()

        priority_value: int | None
        if isinstance(priority, int) or priority is None:
            priority_value = priority
        else:
            priority_map = {"low": 1, "medium": 2, "high": 3, "critical": 4}
            priority_value = priority_map.get(str(priority).lower(), 0)

        item = Item(
            id=uuid4(),
            project_id=project_id,
            title=title,
            description=description,
            view=view or item_type,
            status=status,
            parent_id=parent_id,
            item_metadata=metadata or {},
            priority=priority_value,
            version=1,
        )
        self.session.add(item)
        await self.session.flush()
        if supports_item_views and view_obj is not None:
            self.session.add(
                ItemView(
                    item_id=item.id,
                    view_id=view_obj.id,
                    project_id=project_id,
                    is_primary=True,
                ),
            )
        await self.session.refresh(item)
        return item

    async def _table_exists(self, table_name: str) -> bool:
        result = await self.session.execute(
            text(
                """
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = :table
                """,
            ),
            {"table": table_name},
        )
        return result.scalar() is not None

    async def get_by_id(self, item_id: str | uuid.UUID, project_id: str | uuid.UUID | None = None) -> Item | None:
        """Get item by ID, optionally scoped to project."""
        query = select(Item).where(Item.id == item_id, Item.deleted_at.is_(None))

        if project_id:
            query = query.where(Item.project_id == project_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_by_view(self, project_id: str | uuid.UUID, view: str, include_deleted: bool = False) -> list[Item]:
        """List items by view."""
        query = select(Item).where(Item.project_id == project_id, Item.view == view)
        if not include_deleted:
            query = query.where(Item.deleted_at.is_(None))

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_all(self, project_id: str | uuid.UUID, include_deleted: bool = False) -> list[Item]:
        """List all items in project."""
        query = select(Item).where(Item.project_id == project_id)
        if not include_deleted:
            query = query.where(Item.deleted_at.is_(None))

        query = query.order_by(Item.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(
        self,
        item_id: str | uuid.UUID,
        expected_version: int,
        **updates: Any,
    ) -> Item:
        """Update item with optimistic locking."""
        # Get current item using ORM query for SQLAlchemy tracking
        query = select(Item).where(Item.id == item_id)
        result = await self.session.execute(query)
        item = result.scalar_one_or_none()

        if not item:
            msg = f"Item {item_id} not found"
            raise ValueError(msg)

        # Check version (optimistic lock)
        if item.version != expected_version:
            msg = (
                f"Item {item_id} was modified by another agent "
                f"(expected version {expected_version}, current version {item.version})"
            )
            raise ConcurrencyError(
                msg,
            )

        # Apply updates
        for key, value in updates.items():
            if hasattr(item, key):
                setattr(item, key, value)

        # Increment version
        item.version += 1

        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def delete(self, item_id: str | uuid.UUID, soft: bool = True) -> bool:
        """Delete item (soft delete by default)."""
        if soft:
            # Get item using ORM for tracking
            query = select(Item).where(Item.id == item_id)
            result = await self.session.execute(query)
            item = result.scalar_one_or_none()

            if not item:
                return False

            item.deleted_at = datetime.now(UTC)

            # Cascade soft delete to children
            children_query = select(Item).where(Item.parent_id == item_id, Item.deleted_at.is_(None))
            children_result = await self.session.execute(children_query)
            children = children_result.scalars().all()
            for child in children:
                child.deleted_at = datetime.now(UTC)

            await self.session.flush()
            return True
        # Delete links first to satisfy FK
        await self.session.execute(
            delete(Link).where((Link.source_item_id == item_id) | (Link.target_item_id == item_id)),
        )
        # Permanent delete
        result = await self.session.execute(delete(Item).where(Item.id == item_id))
        return getattr(result, "rowcount", 0) > 0

    async def restore(self, item_id: str | uuid.UUID) -> Item | None:
        """Restore a soft-deleted item."""
        query = select(Item).where(Item.id == item_id)  # Don't filter by deleted_at
        result = await self.session.execute(query)
        item = result.scalar_one_or_none()

        if item and item.deleted_at:
            item.deleted_at = None
            # Note: We don't automatically restore children as it's ambiguous
            # which ones were deleted with parent vs separately.
            await self.session.flush()
            await self.session.refresh(item)
            return item
        return None

    async def get_by_project(
        self,
        project_id: str | uuid.UUID,
        status: str | None = None,
        limit: int = 1000,
        offset: int = 0,
    ) -> list[Item]:
        """Get all items in a project, optionally filtered by status."""
        query = select(Item).where(
            Item.project_id == project_id,
            Item.deleted_at.is_(None),
        )

        if status:
            query = query.where(Item.status == status)

        query = query.order_by(Item.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_view(
        self,
        project_id: str | uuid.UUID,
        view: str,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Item]:
        """Get items by view with optional status filter."""
        query = select(Item).where(
            Item.project_id == project_id,
            Item.view == view,
            Item.deleted_at.is_(None),
        )

        if status:
            query = query.where(Item.status == status)

        query = query.order_by(Item.created_at.desc()).limit(limit).offset(offset)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def query(
        self,
        project_id: str | uuid.UUID,
        filters: dict[str, Any],
        limit: int = 1000,
    ) -> list[Item]:
        """Query items with dynamic filters."""
        query = select(Item).where(
            Item.project_id == project_id,
            Item.deleted_at.is_(None),
        )

        for key, value in filters.items():
            if hasattr(Item, key):
                query = query.where(getattr(Item, key) == value)

        query = query.limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_by_filters(
        self,
        filters: dict[str, Any],
        project_id: str | uuid.UUID,
        limit: int = 1000,
    ) -> list[Item]:
        """List items matching filters (convenience alias for query with (filters, project_id) order)."""
        return await self.query(project_id=project_id, filters=filters, limit=limit)

    async def get_children(self, item_id: str | uuid.UUID) -> list[Item]:
        """Get direct children of an item."""
        query = select(Item).where(Item.parent_id == item_id, Item.deleted_at.is_(None)).order_by(Item.created_at)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_ancestors(self, item_id: str | uuid.UUID) -> list[Item]:
        """Get all ancestors (recursive CTE) up to root."""
        # Recursive CTE for ancestors
        from sqlalchemy import literal

        hierarchy = (
            select(Item.id, Item.parent_id, literal(0).label("level"))
            .where(Item.id == item_id)
            .cte(name="hierarchy", recursive=True)
        )

        parent = select(Item.id, Item.parent_id, (hierarchy.c.level + 1).label("level")).join(
            hierarchy,
            Item.id == hierarchy.c.parent_id,
        )

        hierarchy = hierarchy.union_all(parent)

        # Query items based on CTE, excluding the item itself
        query = (
            select(Item)
            .join(hierarchy, Item.id == hierarchy.c.id)
            .where(Item.id != item_id)  # Exclude self
            .order_by(hierarchy.c.level.desc())  # Root first
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_descendants(self, item_id: str | uuid.UUID) -> list[Item]:
        """Get all descendants (recursive CTE)."""
        from sqlalchemy import literal

        hierarchy = (
            select(Item.id, Item.parent_id, literal(0).label("level"))
            .where(Item.parent_id == item_id)
            .cte(name="hierarchy", recursive=True)
        )

        child = select(Item.id, Item.parent_id, (hierarchy.c.level + 1).label("level")).join(
            hierarchy,
            Item.parent_id == hierarchy.c.id,
        )

        hierarchy = hierarchy.union_all(child)

        query = select(Item).join(hierarchy, Item.id == hierarchy.c.id).order_by(hierarchy.c.level, Item.created_at)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_by_status(self, project_id: str | uuid.UUID) -> dict[str, int]:
        """Count items by status for a project.

        Args:
            project_id: Project ID to count items for

        Returns:
            Dictionary mapping status to count (e.g., {"todo": 3, "done": 2})
        """
        from sqlalchemy import func

        query = (
            select(Item.status, func.count(Item.id))
            .where(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
            )
            .group_by(Item.status)
        )

        result = await self.session.execute(query)
        rows = result.all()
        return {r[0]: r[1] for r in rows}
