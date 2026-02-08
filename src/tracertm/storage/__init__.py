"""Storage module for TraceRTM.

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
    "ChangeDetector",
    "Conflict",
    "ConflictBackup",
    # Conflict resolution
    "ConflictResolver",
    "ConflictStatus",
    "ConflictStrategy",
    "EntityType",
    "EntityVersion",
    # Markdown parser
    "ItemData",
    "ItemStorage",
    "LinkData",
    # Local storage
    "LocalStorageManager",
    "OperationType",
    "ProjectStorage",
    "QueuedChange",
    "ResolvedEntity",
    # Sync engine
    "SyncEngine",
    "SyncQueue",
    "SyncResult",
    "SyncState",
    "SyncStateManager",
    "SyncStatus",
    "VectorClock",
    "compare_versions",
    "create_sync_engine",
    "exponential_backoff",
    "format_conflict_summary",
    "get_config_path",
    "get_item_path",
    "get_links_path",
    "list_items",
    "parse_config_yaml",
    "parse_item_markdown",
    "parse_links_yaml",
    "write_config_yaml",
    "write_item_markdown",
    "write_links_yaml",
]
