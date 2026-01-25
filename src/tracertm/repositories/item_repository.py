"""Item repository for TraceRTM."""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.core.concurrency import ConcurrencyError
from tracertm.models.item import Item
from tracertm.models.link import Link


class ItemRepository:
    """Repository for Item CRUD operations with optimistic locking."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        project_id: str,
        title: str,
        view: str,
        item_type: str,
        description: str | None = None,
        status: str = "todo",
        parent_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        owner: str | None = None,
        priority: str | None = "medium",
        created_by: str = "system",
    ) -> Item:
        """Create new item with optimistic locking."""
        # Validate parent if provided
        if parent_id:
            parent_item = await self.get_by_id(parent_id)
            if not parent_item:
                raise ValueError(f"Parent item {parent_id} not found")
            if parent_item.project_id != project_id:
                raise ValueError(f"Parent item {parent_id} not in same project")

        item = Item(
            id=str(uuid4()),
            project_id=project_id,
            title=title,
            description=description,
            view=view,
            item_type=item_type,
            status=status,
            parent_id=parent_id,
            item_metadata=metadata or {},
            owner=owner,
            priority=priority,
            version=1,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def get_by_id(self, item_id: str, project_id: str | None = None) -> Item | None:
        """Get item by ID, optionally scoped to project."""
        # Use raw SQL to avoid model column mismatches with database schema
        from sqlalchemy import text
        
        sql = """
            SELECT id, project_id, title, description, view, item_type, status, priority, 
                   created_at, updated_at, item_metadata, deleted_at, parent_id, owner
            FROM items 
            WHERE id = :item_id AND deleted_at IS NULL
        """
        params = {"item_id": item_id}
        
        if project_id:
            sql += " AND project_id = :project_id"
            params["project_id"] = project_id
        
        result = await self.session.execute(text(sql), params)
        row = result.fetchone()
        if not row:
            return None
        
        # Create an Item-like object that works with the actual schema
        item = type('Item', (), {})()  # type: ignore
        item.id = str(row.id)
        item.project_id = str(row.project_id)
        item.title = row.title
        item.description = row.description
        item.view = row.view
        item.item_type = row.item_type
        item.type = row.item_type  # Alias for compatibility
        item.status = row.status
        item.priority = str(row.priority) if row.priority is not None else "medium"
        item.owner = row.owner
        item.parent_id = str(row.parent_id) if row.parent_id else None
        item.created_at = row.created_at
        item.updated_at = row.updated_at
        item.item_metadata = row.item_metadata if row.item_metadata else {}
        item.metadata = item.item_metadata  # Alias
        item.deleted_at = row.deleted_at
        return item

    async def list_by_view(
        self,
        project_id: str,
        view: str,
        include_deleted: bool = False
    ) -> list[Item]:
        """List items by view."""
        query = select(Item).where(Item.project_id == project_id, Item.view == view)
        if not include_deleted:
            query = query.where(Item.deleted_at.is_(None))

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_all(
        self,
        project_id: str,
        include_deleted: bool = False
    ) -> list[Item]:
        """List all items in project."""
        query = select(Item).where(Item.project_id == project_id)
        if not include_deleted:
            query = query.where(Item.deleted_at.is_(None))

        query = query.order_by(Item.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(
        self,
        item_id: str,
        expected_version: int,
        **updates: Any,
    ) -> Item:
        """Update item with optimistic locking."""
        # Get current item
        item = await self.get_by_id(item_id)
        if not item:
            raise ValueError(f"Item {item_id} not found")

        # Check version (optimistic lock)
        if item.version != expected_version:
            raise ConcurrencyError(
                f"Item {item_id} was modified by another agent "
                f"(expected version {expected_version}, current version {item.version})"
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

    async def delete(self, item_id: str, soft: bool = True) -> bool:
        """Delete item (soft delete by default)."""
        if soft:
            item = await self.get_by_id(item_id)
            if not item:
                return False
            item.deleted_at = datetime.now(UTC)

            # Cascade soft delete to children
            query = select(Item).where(Item.parent_id == item_id, Item.deleted_at.is_(None))
            result = await self.session.execute(query)
            children = result.scalars().all()
            for child in children:
                child.deleted_at = datetime.now(UTC)

            await self.session.flush()
            return True
        else:
            # Delete links first to satisfy FK
            await self.session.execute(
                delete(Link).where(
                    (Link.source_item_id == item_id) | (Link.target_item_id == item_id)
                )
            )
            # Permanent delete
            result = await self.session.execute(delete(Item).where(Item.id == item_id))
            return result.rowcount > 0

    async def restore(self, item_id: str) -> Item | None:
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
        project_id: str,
        status: str | None = None,
        limit: int = 1000,
        offset: int = 0,
    ) -> list[Item]:
        """Get all items in a project, optionally filtered by status."""
        # Use raw SQL to avoid model column mismatches with database schema
        from sqlalchemy import text
        
        sql = """
            SELECT id, project_id, title, description, view, item_type, status, priority, 
                   created_at, updated_at, item_metadata, deleted_at, parent_id, owner
            FROM items 
            WHERE project_id = :project_id AND deleted_at IS NULL
        """
        params = {"project_id": project_id}
        
        if status:
            sql += " AND status = :status"
            params["status"] = status
            
        sql += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
        params["limit"] = limit
        params["offset"] = offset
        
        result = await self.session.execute(text(sql), params)
        items = []
        for row in result:
            # Create an Item-like object that works with the actual schema
            item = type('Item', (), {})()  # type: ignore
            item.id = str(row.id)
            item.project_id = str(row.project_id)
            item.title = row.title
            item.description = row.description
            item.view = row.view
            item.item_type = row.item_type
            item.type = row.item_type  # Alias for compatibility
            item.status = row.status
            item.priority = str(row.priority) if row.priority is not None else "medium"
            item.owner = row.owner
            item.parent_id = str(row.parent_id) if row.parent_id else None
            item.created_at = row.created_at
            item.updated_at = row.updated_at
            item.item_metadata = row.item_metadata if row.item_metadata else {}
            item.metadata = item.item_metadata  # Alias
            item.deleted_at = row.deleted_at
            items.append(item)
        return items

    async def get_by_view(
        self,
        project_id: str,
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
        project_id: str,
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

    async def get_children(self, item_id: str) -> list[Item]:
        """Get direct children of an item."""
        query = select(Item).where(
            Item.parent_id == item_id,
            Item.deleted_at.is_(None)
        ).order_by(Item.created_at)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_ancestors(self, item_id: str) -> list[Item]:
        """Get all ancestors (recursive CTE) up to root."""
        # Recursive CTE for ancestors
        from sqlalchemy import literal

        hierarchy = (
            select(Item.id, Item.parent_id, literal(0).label('level'))
            .where(Item.id == item_id)
            .cte(name="hierarchy", recursive=True)
        )

        parent = select(Item.id, Item.parent_id, (hierarchy.c.level + 1).label('level')).join(
            hierarchy, Item.id == hierarchy.c.parent_id
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

    async def get_descendants(self, item_id: str) -> list[Item]:
        """Get all descendants (recursive CTE)."""
        from sqlalchemy import literal

        hierarchy = (
            select(Item.id, Item.parent_id, literal(0).label('level'))
            .where(Item.parent_id == item_id)
            .cte(name="hierarchy", recursive=True)
        )

        child = select(Item.id, Item.parent_id, (hierarchy.c.level + 1).label('level')).join(
            hierarchy, Item.parent_id == hierarchy.c.id
        )

        hierarchy = hierarchy.union_all(child)

        query = (
            select(Item)
            .join(hierarchy, Item.id == hierarchy.c.id)
            .order_by(hierarchy.c.level, Item.created_at)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_by_status(self, project_id: str) -> dict[str, int]:
        """
        Count items by status for a project.

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

        return dict(rows)
