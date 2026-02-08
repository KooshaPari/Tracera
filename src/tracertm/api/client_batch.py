"""Batch-related operations for the TraceRTM Python API client."""

from typing import Any

from tracertm.api.client_types import BatchResult, ItemView
from tracertm.models.link import Link


class ClientBatchMixin:
    """Mixin for TraceRTMClient to handle batch operations."""

    def batch_create_items(
        self, items_data: list[dict[str, Any]], project_id: str | None = None,
    ) -> list[ItemView | Any] | BatchResult:
        """Create multiple items from payload dictionaries."""
        project_id = project_id or self.config_manager.get("current_project_id")
        created: list[ItemView | Any] = []
        for data in items_data:
            data = dict[str, Any](data)
            data.setdefault("project_id", project_id)
            title = data.pop("title", "")
            view = data.pop("view", "FEATURE")
            if "type" in data:
                data["item_type"] = data.pop("type")
            created.append(self.create_item(title, view, **data))
        return created if self._patched_session else BatchResult(created, {"items_created": len(created)})

    def batch_update_items(self, updates: list[dict[str, Any]]) -> list[ItemView | Any] | BatchResult:
        """Update multiple items from payload dictionaries."""
        updated: list[ItemView | Any] = []
        for upd in updates:
            payload = dict[str, Any](upd)
            if "item_id" in payload and "id" not in payload:
                payload["id"] = payload.pop("item_id")
            item_id = payload.pop("id", None)
            if item_id is None:
                item_id = payload.pop("item_id", None)
            if item_id is None:
                continue
            try:
                updated.append(self.update_item(item_id, payload))
            except ValueError:
                continue
        return updated if self._patched_session else BatchResult(updated, {"items_updated": len(updated)})

    def batch_delete_items(self, item_ids: list[str]) -> bool | BatchResult:
        """Soft-delete multiple items."""
        deleted = 0
        for item_id in item_ids:
            try:
                if self.delete_item(item_id):
                    deleted += 1
            except ValueError:
                continue
        return True if self._patched_session else BatchResult([], {"items_deleted": deleted})

    def batch_create_links(self, links_data: list[dict[str, Any]]) -> list[Link]:
        """Create multiple links from payload dictionaries."""
        return [self.create_link(**payload) for payload in links_data]
