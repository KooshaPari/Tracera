"""Item-related operations for the TraceRTM Python API client."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm.exc import StaleDataError

from tracertm.api.client_types import ItemView
from tracertm.models.item import Item
from tracertm.services.concurrent_operations_service import retry_with_backoff


class ClientItemsMixin:
    """Mixin for TraceRTMClient to handle item-related operations."""

    def _apply_item_filters(
        self,
        query: Any,
        view: str | None,
        status: str | None,
        item_type: str | None,
        filters: dict[str, Any],
    ) -> tuple[Any, str | None]:
        if view:
            query = query.filter(Item.view == view.upper())
        if status:
            query = query.filter(Item.status == status)
        resolved_item_type = item_type or filters.pop("type", None)
        if resolved_item_type:
            query = query.filter(Item.item_type == resolved_item_type)
        if "priority" in filters:
            query = query.filter(Item.priority == filters["priority"])
        if "owner" in filters:
            query = query.filter(Item.owner == filters["owner"])
        if "parent_id" in filters:
            query = query.filter(Item.parent_id == filters["parent_id"])
        query = query.filter(Item.deleted_at.is_(None))
        return query, resolved_item_type

    def _apply_item_sort(self, query: Any, sort: str | None, order: str | None) -> Any:
        sort_field = sort
        if not sort_field:
            return query
        attr_map = {
            "created_at": Item.created_at if hasattr(Item, "created_at") else None,
            "item_type": Item.item_type,
            "priority": Item.priority,
            "status": Item.status,
            "title": Item.title,
            "type": Item.item_type,
            "updated_at": Item.updated_at if hasattr(Item, "updated_at") else None,
            "view": Item.view,
        }
        column = attr_map.get(sort_field)
        if column is None:
            return query
        sort_order = (order or "asc").lower()
        return query.order_by(column.asc() if sort_order == "asc" else column.desc())

    def _apply_item_pagination(self, query: Any, limit: int, offset: int) -> Any:
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        return query

    def _apply_item_memory_filters(
        self,
        items: list[Item],
        search: str | None,
        metadata_filter: dict[str, Any] | None,
    ) -> list[Item]:
        if search:
            lowered = search.lower()
            items = [
                item
                for item in items
                if (item.title and lowered in item.title.lower())
                or (item.description and lowered in item.description.lower())
            ]
        if metadata_filter:

            def match_meta(it: Item) -> bool:
                meta = it.item_metadata or {}
                return all(meta.get(k) == v for k, v in metadata_filter.items())

            items = [item for item in items if match_meta(item)]
        return items

    def _commit_item_update(self, session: Any, item: Item, original_version: int) -> ItemView:
        session.commit()
        self._log_operation(
            "item_updated",
            "item",
            str(item.id),
            {
                "title": item.title,
                "status": item.status,
                "version": original_version,
                "new_version": item.version,
            },
        )
        item_view = self._as_item_view(item)
        if item_view is None:
            msg = "Item not found after update"
            raise ValueError(msg)
        return item_view

    def query_items(
        self,
        view: str | None = None,
        status: str | None = None,
        item_type: str | None = None,
        limit: int = 100,
        offset: int = 0,
        sort: str | None = None,
        order: str = "asc",
        **filters: Any,
    ) -> list[ItemView | Any]:
        """Query items in project (FR37, FR44)."""
        session = self._ensure_sync_session()

        query = session.query(Item)
        query, resolved_type = self._apply_item_filters(query, view, status, item_type, filters)

        sort_field = sort or filters.get("sort")
        query = self._apply_item_sort(query, sort_field, order)
        query = self._apply_item_pagination(query, limit, offset)

        items = query.all()

        search = filters.get("search")
        metadata_filter = filters.get("metadata_filter")
        items = self._apply_item_memory_filters(items, search, metadata_filter)

        self._log_operation(
            "items_queried",
            "query",
            "multiple",
            {"view": view, "status": status, "type": resolved_type, "count": len(items)},
        )

        return [self._as_item_view(item) for item in items]

    def get_item(self, item_id: str) -> ItemView | None:
        """Get a specific item (FR37)."""
        session = self._ensure_sync_session()
        item = session.query(Item).filter(Item.id.like(f"{item_id}%")).first()

        if not item:
            return None
        if getattr(item, "deleted_at", None):
            return None

        return self._as_item_view(item)

    async def get_item_async(self, item_id: str) -> ItemView | None:
        """Async wrapper for get_item."""
        return self.get_item(item_id)

    def create_item(
        self,
        title: str,
        view: str,
        item_type: str | None = None,
        description: str | None = None,
        status: str = "todo",
        priority: str = "medium",
        owner: str | None = None,
        parent_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        project_id: str | None = None,
        **kwargs: Any,
    ) -> ItemView | Any:
        """Create a new item (FR38)."""
        session = self._ensure_sync_session()
        item_type = item_type or kwargs.get("type")
        if not title:
            msg = "title is required"
            raise ValueError(msg)
        if not view:
            msg = "view is required"
            raise ValueError(msg)
        project_id = project_id or self.config_manager.get("current_project_id")

        item: Item = Item(
            project_id=project_id,
            title=title,
            description=description,
            view=view.upper(),
            item_type=item_type,
            status=status,
            priority=priority,
            owner=owner,
            parent_id=parent_id,
            item_metadata=metadata or {},
        )
        session.add(item)
        session.commit()

        self._log_operation(
            "item_created",
            "item",
            str(item.id),
            {"title": title, "view": view, "type": item_type},
        )

        return self._as_item_view(item)

    async def create_item_async(
        self,
        title: str,
        view: str,
        item_type: str | None = None,
        description: str | None = None,
        status: str = "todo",
        priority: str = "medium",
        owner: str | None = None,
        parent_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        project_id: str | None = None,
        **kwargs: Any,
    ) -> ItemView | Any:
        """Async wrapper for item creation used in tests."""
        return self.create_item(
            title=title,
            view=view,
            item_type=item_type,
            description=description,
            status=status,
            priority=priority,
            owner=owner,
            parent_id=parent_id,
            metadata=metadata,
            project_id=project_id,
            **kwargs,
        )

    @retry_with_backoff(max_retries=3, initial_delay=0.1)
    def update_item(
        self,
        item_id: str,
        title: str | None = None,
        description: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        owner: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ItemView | Any:
        """Update an item with optimistic locking and retry logic (FR38, FR42, Story 5.3)."""
        session = self._ensure_sync_session()
        item = session.query(Item).filter(Item.id.like(f"{item_id}%")).first()

        if not item:
            msg = f"Item not found: {item_id}"
            raise ValueError(msg)

        original_version = item.version

        if title is not None:
            item.title = title
        if description is not None:
            item.description = description
        if status is not None:
            item.status = status
        if priority is not None:
            item.priority = priority
        if owner is not None:
            item.owner = owner
        if metadata is not None:
            item.item_metadata = metadata

        try:
            return self._commit_item_update(session, item, original_version)
        except StaleDataError:
            session.rollback()

            self._log_operation(
                "conflict_detected",
                "item",
                item.id,
                {
                    "agent_id": self.agent_id,
                    "item_id": item.id,
                    "version": original_version,
                },
            )

            raise

    async def update_item_async(
        self,
        item_id: str,
        title: str | None = None,
        description: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        owner: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ItemView | Any:
        """Async wrapper for update_item."""
        return self.update_item(
            item_id=item_id,
            title=title,
            description=description,
            status=status,
            priority=priority,
            owner=owner,
            metadata=metadata,
        )

    def delete_item(self, item_id: str) -> bool:
        """Delete an item (soft delete) (FR38)."""
        session = self._ensure_sync_session()
        item = session.query(Item).filter(Item.id.like(f"{item_id}%")).first()

        if not item:
            msg = f"Item not found: {item_id}"
            raise ValueError(msg)

        item.deleted_at = datetime.now(UTC)
        session.commit()

        self._log_operation(
            "item_deleted",
            "item",
            str(item.id),
            {"title": item.title},
        )
        return True

    async def delete_item_async(self, item_id: str) -> bool:
        """Async wrapper for delete_item."""
        return self.delete_item(item_id)
