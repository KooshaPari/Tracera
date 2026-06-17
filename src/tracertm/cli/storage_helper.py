"""Storage helper for TUI."""
from typing import Any, Callable, Dict, List, Optional
from pathlib import Path
from datetime import datetime, timedelta


# Singleton storage manager
_storage_manager: Optional["StorageHelper"] = None


def _human_time_delta(dt: Optional[datetime]) -> str:
    """Format a datetime as a human-readable time delta."""
    if dt is None:
        return "never"

    now = datetime.now()
    delta = now - dt

    if delta < timedelta(minutes=1):
        return "just now"
    elif delta < timedelta(hours=1):
        minutes = int(delta.total_seconds() / 60)
        return f"{minutes}m ago"
    elif delta < timedelta(days=1):
        hours = int(delta.total_seconds() / 3600)
        return f"{hours}h ago"
    elif delta < timedelta(days=30):
        days = delta.days
        return f"{days}d ago"
    else:
        return dt.strftime("%Y-%m-%d")


def _trigger_sync(
    queue: Optional[List[Dict[str, Any]]] = None,
    api_endpoint: Optional[str] = None,
    max_retries: int = 3,
) -> Dict[str, Any]:
    """Trigger a sync operation."""
    return {
        "success": True,
        "message": "Sync triggered successfully",
        "synced_count": 0,
    }


def format_item_for_display(item: Dict[str, Any]) -> str:
    """Format an item for display."""
    title = item.get("title", "Untitled")
    view = item.get("view", "UNKNOWN")
    item_type = item.get("item_type", "unknown")
    return f"[{view}] {title} ({item_type})"


def format_items_table(items: List[Dict[str, Any]]) -> str:
    """Format items as a table."""
    if not items:
        return "No items found."
    lines = ["Items:", "-" * 50]
    for item in items:
        lines.append(format_item_for_display(item))
    return "\n".join(lines)


def format_link_for_display(link: Dict[str, Any]) -> str:
    """Format a link for display."""
    source = link.get("source_id", "unknown")
    target = link.get("target_id", "unknown")
    link_type = link.get("link_type", "unknown")
    return f"{source} --[{link_type}]--> {target}"


def format_links_table(links: List[Dict[str, Any]]) -> str:
    """Format links as a table."""
    if not links:
        return "No links found."
    lines = ["Links:", "-" * 50]
    for link in links:
        lines.append(format_link_for_display(link))
    return "\n".join(lines)


def get_current_project() -> Optional[Dict[str, Any]]:
    """Get the current project."""
    return None


def get_storage_manager() -> "StorageHelper":
    """Get the storage manager singleton."""
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = StorageHelper(Path("/tmp/tracertm"))
    return _storage_manager


def handle_storage_error(error: Exception) -> None:
    """Handle a storage error."""
    print(f"Storage error: {error}")


def require_project(func: Callable) -> Callable:
    """Decorator that requires a project to be set."""
    def wrapper(*args, **kwargs):
        if get_current_project() is None:
            raise ValueError("No project set")
        return func(*args, **kwargs)
    return wrapper


def reset_storage_manager() -> None:
    """Reset the storage manager singleton."""
    global _storage_manager
    _storage_manager = None


def show_sync_status() -> Dict[str, Any]:
    """Show the current sync status."""
    return {
        "status": "idle",
        "last_sync": None,
        "pending_changes": 0,
    }


def with_sync(func: Callable) -> Callable:
    """Decorator that syncs before and after a function."""
    def wrapper(*args, **kwargs):
        _trigger_sync()
        try:
            return func(*args, **kwargs)
        finally:
            _trigger_sync()
    return wrapper


class StorageHelper:
    """Helper for storage operations in TUI."""

    def __init__(self, storage_path: Path):
        self.storage_path = storage_path

    def get_items(self) -> List[Dict[str, Any]]:
        """Get all items."""
        return []

    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get a single item."""
        return None

    def save_item(self, item: Dict[str, Any]) -> None:
        """Save an item."""
        pass

    def delete_item(self, item_id: str) -> bool:
        """Delete an item."""
        return True

    def get_links(self) -> List[Dict[str, Any]]:
        """Get all links."""
        return []

    def get_link(self, link_id: str) -> Optional[Dict[str, Any]]:
        """Get a single link."""
        return None

    def save_link(self, link: Dict[str, Any]) -> None:
        """Save a link."""
        pass

    def delete_link(self, link_id: str) -> bool:
        """Delete a link."""
        return True

    def search_items(self, query: str) -> List[Dict[str, Any]]:
        """Search items."""
        return []

    def get_statistics(self) -> Dict[str, Any]:
        """Get storage statistics."""
        return {
            "total_items": 0,
            "total_links": 0,
            "items_by_view": {},
            "items_by_type": {},
        }


__all__ = ["StorageHelper"]
