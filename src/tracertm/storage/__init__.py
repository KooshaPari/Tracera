"""
Storage module for TraceRTM.

Provides local storage with SQLite + Markdown hybrid storage,
offline sync capabilities, and conflict resolution.
"""

from tracertm.storage.conflict_resolver import (
    Conflict,
    ConflictBackup,
    ConflictResolver,
    ConflictStatus,
    ConflictStrategy,
    EntityVersion,
    ResolvedEntity,
    VectorClock,
    compare_versions,
    format_conflict_summary,
)
from tracertm.storage.local_storage import (
    ItemStorage,
    LocalStorageManager,
    ProjectStorage,
)
from tracertm.storage.markdown_parser import (
    ItemData,
    LinkData,
    get_config_path,
    get_item_path,
    get_links_path,
    list_items,
    parse_config_yaml,
    parse_item_markdown,
    parse_links_yaml,
    write_config_yaml,
    write_item_markdown,
    write_links_yaml,
)
from tracertm.storage.sync_engine import (
    ChangeDetector,
    EntityType,
    OperationType,
    QueuedChange,
    SyncEngine,
    SyncQueue,
    SyncResult,
    SyncState,
    SyncStateManager,
    SyncStatus,
    create_sync_engine,
    exponential_backoff,
)

__all__ = [
    # Local storage
    "LocalStorageManager",
    "ProjectStorage",
    "ItemStorage",
    # Markdown parser
    "ItemData",
    "LinkData",
    "parse_item_markdown",
    "write_item_markdown",
    "parse_links_yaml",
    "write_links_yaml",
    "parse_config_yaml",
    "write_config_yaml",
    "get_item_path",
    "get_links_path",
    "get_config_path",
    "list_items",
    # Sync engine
    "SyncEngine",
    "SyncQueue",
    "SyncStateManager",
    "ChangeDetector",
    "SyncStatus",
    "OperationType",
    "EntityType",
    "SyncState",
    "SyncResult",
    "QueuedChange",
    "create_sync_engine",
    "exponential_backoff",
    # Conflict resolution
    "ConflictResolver",
    "ConflictBackup",
    "Conflict",
    "EntityVersion",
    "VectorClock",
    "ResolvedEntity",
    "ConflictStrategy",
    "ConflictStatus",
    "compare_versions",
    "format_conflict_summary",
]
