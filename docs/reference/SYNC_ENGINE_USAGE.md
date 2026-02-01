# TraceRTM Sync Engine Usage Guide

## Overview

The Sync Engine provides offline-first synchronization between local storage (SQLite + Markdown) and the remote TraceRTM API. It implements a robust sync flow with conflict resolution, retry logic, and network resilience.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Sync Engine                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Change     │───▶│  Sync Queue  │───▶│   Upload     │  │
│  │   Detector   │    │              │    │   Phase      │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                                         │         │
│         │                                         ▼         │
│         │                                  ┌──────────────┐ │
│         │                                  │   Download   │ │
│         │                                  │   Phase      │ │
│         │                                  └──────────────┘ │
│         │                                         │         │
│         ▼                                         ▼         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Conflict Resolution                         │  │
│  │  (Last-Write-Wins / Local-Wins / Remote-Wins / Manual)│  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. SyncEngine

Main orchestrator for the sync process.

```python
from tracertm.storage import SyncEngine, ConflictStrategy
from tracertm.database.connection import DatabaseConnection
from tracertm.api.client import TraceRTMClient

# Initialize database connection
db = DatabaseConnection("sqlite:///~/.tracertm/tracertm.db")
db.connect()

# Initialize API client
api_client = TraceRTMClient(agent_id="my-agent")

# Initialize storage manager (placeholder - will be implemented)
storage_manager = LocalStorageManager(db)

# Create sync engine
sync_engine = SyncEngine(
    db_connection=db,
    api_client=api_client,
    storage_manager=storage_manager,
    conflict_strategy=ConflictStrategy.LAST_WRITE_WINS,
    max_retries=3,
    retry_delay=1.0
)
```

### 2. Sync Operations

#### Full Sync

```python
import asyncio

async def sync_all():
    result = await sync_engine.sync()

    if result.success:
        print(f"✓ Synced {result.entities_synced} entities in {result.duration_seconds:.2f}s")

        if result.conflicts:
            print(f"⚠ {len(result.conflicts)} conflicts detected")
            for conflict in result.conflicts:
                print(f"  - {conflict['entity_type']} {conflict['entity_id']}")
    else:
        print(f"✗ Sync failed: {result.errors}")

asyncio.run(sync_all())
```

#### Check Sync Status

```python
status = sync_engine.get_status()

print(f"Status: {status.status.value}")
print(f"Last sync: {status.last_sync}")
print(f"Pending changes: {status.pending_changes}")
print(f"Conflicts: {status.conflicts_count}")

if status.last_error:
    print(f"Last error: {status.last_error}")
```

### 3. Change Detection

The `ChangeDetector` automatically identifies local changes by comparing content hashes.

```python
from tracertm.storage import ChangeDetector
from pathlib import Path

detector = ChangeDetector()

# Compute hash of content
content = "# My Epic\n\nDescription here"
content_hash = detector.compute_hash(content)

# Check if content has changed
has_changed = detector.has_changed(content, stored_hash="previous_hash")

# Detect changes in directory
project_dir = Path("~/.tracertm/projects/my-project")
stored_hashes = {
    "epics/EPIC-001.md": "abc123...",
    "stories/STORY-001.md": "def456..."
}

changes = detector.detect_changes_in_directory(project_dir, stored_hashes)
for file_path, new_hash in changes:
    print(f"Changed: {file_path} -> {new_hash}")
```

### 4. Manual Change Queueing

Queue changes manually for sync:

```python
from tracertm.storage import EntityType, OperationType

# Queue a new item creation
sync_engine.queue_change(
    entity_type=EntityType.ITEM,
    entity_id="item-123",
    operation=OperationType.CREATE,
    payload={
        "title": "New Epic",
        "description": "Epic description",
        "item_type": "epic",
        "status": "todo"
    }
)

# Queue an update
sync_engine.queue_change(
    entity_type=EntityType.ITEM,
    entity_id="item-123",
    operation=OperationType.UPDATE,
    payload={
        "status": "in_progress",
        "updated_at": "2024-01-20T15:30:00Z"
    }
)

# Queue a deletion
sync_engine.queue_change(
    entity_type=EntityType.ITEM,
    entity_id="item-456",
    operation=OperationType.DELETE,
    payload={}
)
```

### 5. Sync Queue Management

```python
# Get pending changes count
pending_count = sync_engine.queue.get_count()
print(f"{pending_count} changes pending")

# Get pending changes
pending = sync_engine.queue.get_pending(limit=10)
for change in pending:
    print(f"  {change.operation.value} {change.entity_type.value} {change.entity_id}")
    print(f"    Created: {change.created_at}")
    print(f"    Retries: {change.retry_count}")

# Clear queue (use with caution!)
await sync_engine.clear_queue()
```

### 6. Conflict Resolution Strategies

The sync engine supports multiple conflict resolution strategies:

```python
from tracertm.storage import ConflictStrategy

# Strategy 1: Last Write Wins (default)
# The most recent change (based on timestamp) wins
sync_engine_lww = SyncEngine(
    db_connection=db,
    api_client=api_client,
    storage_manager=storage_manager,
    conflict_strategy=ConflictStrategy.LAST_WRITE_WINS
)

# Strategy 2: Local Wins
# Local changes always take precedence over remote
sync_engine_local = SyncEngine(
    db_connection=db,
    api_client=api_client,
    storage_manager=storage_manager,
    conflict_strategy=ConflictStrategy.LOCAL_WINS
)

# Strategy 3: Remote Wins
# Remote changes always take precedence over local
sync_engine_remote = SyncEngine(
    db_connection=db,
    api_client=api_client,
    storage_manager=storage_manager,
    conflict_strategy=ConflictStrategy.REMOTE_WINS
)

# Strategy 4: Manual
# Create conflict files for manual resolution
sync_engine_manual = SyncEngine(
    db_connection=db,
    api_client=api_client,
    storage_manager=storage_manager,
    conflict_strategy=ConflictStrategy.MANUAL
)
```

### 7. Periodic Sync

Set up automatic periodic sync:

```python
import asyncio

async def periodic_sync(interval_seconds: int = 300):
    """Run sync every N seconds."""
    while True:
        try:
            result = await sync_engine.sync()
            if result.success:
                print(f"✓ Periodic sync completed: {result.entities_synced} entities")
            else:
                print(f"✗ Periodic sync failed: {result.errors}")
        except Exception as e:
            print(f"✗ Periodic sync error: {e}")

        await asyncio.sleep(interval_seconds)

# Run in background
asyncio.create_task(periodic_sync(interval_seconds=300))
```

### 8. Vector Clocks for Ordering

The sync engine uses vector clocks to establish partial ordering of events:

```python
from tracertm.storage import VectorClock

# Create vector clock
clock = sync_engine.create_vector_clock(
    client_id="cli-abc123",
    version=5,
    parent_version=4
)

print(f"Client: {clock.client_id}")
print(f"Version: {clock.version}")
print(f"Timestamp: {clock.timestamp}")
print(f"Parent: {clock.parent_version}")
```

## Sync Flow

### 1. Change Detection

```
Local Files → Hash Computation → Compare with Stored Hash → Queue Changes
```

### 2. Upload Phase

```
Sync Queue → Process Entries → Upload to API → Remove from Queue
              ↓
           Retry on Failure (with exponential backoff)
```

### 3. Download Phase

```
API → Get Changes Since Last Sync → Apply to Local Storage
                                   ↓
                              Conflict Resolution
```

### 4. Conflict Resolution

```
Local Change ←→ Remote Change
        ↓
   Apply Strategy
        ↓
┌───────┴───────┐
│  Last Write   │  Use most recent timestamp
│   Local Wins  │  Keep local version
│  Remote Wins  │  Use remote version
│    Manual     │  Create conflict file
└───────────────┘
```

## Error Handling

### Network Failures

The sync engine automatically retries failed operations with exponential backoff:

```python
# Configure retry behavior
sync_engine = SyncEngine(
    db_connection=db,
    api_client=api_client,
    storage_manager=storage_manager,
    max_retries=5,        # Max retry attempts
    retry_delay=2.0       # Initial delay (seconds)
)

# Retry delays: 2s, 4s, 8s, 16s, 32s
```

### Handling Sync Errors

```python
result = await sync_engine.sync()

if not result.success:
    for error in result.errors:
        print(f"Error: {error}")

    # Check sync state
    status = sync_engine.get_status()
    if status.last_error:
        print(f"Last error: {status.last_error}")

# Reset sync state if needed
await sync_engine.reset_sync_state()
```

## Database Schema

The sync engine creates these tables:

```sql
-- Sync queue for pending changes
CREATE TABLE sync_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,     -- project, item, link, agent
    entity_id TEXT NOT NULL,
    operation TEXT NOT NULL,       -- create, update, delete
    payload TEXT NOT NULL,         -- JSON payload
    created_at TEXT NOT NULL,
    retry_count INTEGER DEFAULT 0,
    last_error TEXT,
    UNIQUE(entity_type, entity_id, operation)
);

-- Sync state metadata
CREATE TABLE sync_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Example sync_state entries:
-- key='last_sync', value='2024-01-20T15:30:00Z'
-- key='status', value='success'
-- key='last_error', value='Network timeout'
```

## Best Practices

### 1. Check Before Syncing

```python
# Don't sync if already syncing
if not sync_engine.is_syncing():
    result = await sync_engine.sync()
else:
    print("Sync already in progress")
```

### 2. Handle Conflicts Gracefully

```python
result = await sync_engine.sync()

if result.conflicts:
    # Log conflicts for review
    for conflict in result.conflicts:
        logger.warning(f"Conflict: {conflict}")

    # Optionally notify user
    print(f"⚠ {len(result.conflicts)} conflicts need attention")
```

### 3. Monitor Sync Status

```python
status = sync_engine.get_status()

# Alert if too many pending changes
if status.pending_changes > 100:
    print(f"⚠ {status.pending_changes} changes pending - consider syncing")

# Alert if sync hasn't run recently
from datetime import datetime, timedelta
if status.last_sync:
    time_since_sync = datetime.utcnow() - status.last_sync
    if time_since_sync > timedelta(hours=1):
        print(f"⚠ Last sync was {time_since_sync} ago")
```

### 4. Graceful Shutdown

```python
async def shutdown():
    # Process any pending changes before shutdown
    if sync_engine.queue.get_count() > 0:
        print("Processing pending changes before shutdown...")
        result = await sync_engine.sync()
        print(f"Synced {result.entities_synced} entities")

    # Close connections
    sync_engine.db.close()
```

## Integration Examples

### CLI Integration

```python
import click
from tracertm.storage import SyncEngine, SyncStatus

@click.command()
@click.option('--force', is_flag=True, help='Force sync even if recently synced')
async def sync(force):
    """Sync local changes with remote API."""
    engine = get_sync_engine()  # Your factory function

    status = engine.get_status()
    click.echo(f"Status: {status.status.value}")
    click.echo(f"Pending changes: {status.pending_changes}")

    if status.status == SyncStatus.SYNCING:
        click.echo("⚠ Sync already in progress")
        return

    click.echo("Syncing...")
    result = await engine.sync(force=force)

    if result.success:
        click.secho(
            f"✓ Synced {result.entities_synced} entities in {result.duration_seconds:.2f}s",
            fg='green'
        )
    else:
        click.secho(f"✗ Sync failed: {result.errors}", fg='red')
```

### TUI Integration

```python
from textual.app import App
from textual.widgets import Header, Footer, Static

class SyncStatus(Static):
    """Display sync status."""

    def on_mount(self):
        self.set_interval(5.0, self.update_status)

    async def update_status(self):
        engine = get_sync_engine()
        status = engine.get_status()

        self.update(
            f"Status: {status.status.value} | "
            f"Pending: {status.pending_changes} | "
            f"Last sync: {status.last_sync or 'Never'}"
        )
```

## Troubleshooting

### Queue is Growing

```python
# Check for failed items
pending = sync_engine.queue.get_pending(limit=100)
failed = [c for c in pending if c.retry_count >= sync_engine.max_retries]

if failed:
    print(f"{len(failed)} items failed max retries")
    for item in failed:
        print(f"  {item.entity_type.value} {item.entity_id}: {item.last_error}")
```

### Sync State Corruption

```python
# Reset sync state
await sync_engine.reset_sync_state()
await sync_engine.clear_queue()

# Rebuild from scratch
await sync_engine.detect_and_queue_changes()
result = await sync_engine.sync()
```

### Debugging Sync Issues

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('tracertm.storage.sync_engine')
logger.setLevel(logging.DEBUG)

# Run sync with verbose output
result = await sync_engine.sync()
```

## Future Enhancements

The sync engine is designed to be extended with:

1. **Real-time Sync** - WebSocket support for live updates
2. **Selective Sync** - Sync only specific projects or entity types
3. **Compression** - Compress payloads for bandwidth efficiency
4. **Encryption** - Encrypt sync payloads for security
5. **Metrics** - Detailed sync performance metrics
6. **Webhooks** - Trigger webhooks on sync events

## See Also

- [UNIFIED_LOCAL_STORAGE_ARCHITECTURE.md](./UNIFIED_LOCAL_STORAGE_ARCHITECTURE.md) - Full architecture
- [conflict_resolver.py](../src/tracertm/storage/conflict_resolver.py) - Conflict resolution
- [local_storage.py](../src/tracertm/storage/local_storage.py) - Local storage manager
