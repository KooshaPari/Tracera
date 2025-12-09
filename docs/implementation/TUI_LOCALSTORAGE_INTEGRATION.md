# TUI LocalStorage Integration

This document describes the integration of TraceRTM's TUI with the LocalStorageManager for offline-first operation with sync capabilities.

## Overview

The TUI has been enhanced to use the LocalStorageManager instead of direct database access, providing:

- **Offline-first operation**: All data stored locally in SQLite + Markdown
- **Real-time sync status**: Visual indicators for online/offline, sync progress, and pending changes
- **Conflict notifications**: Interactive conflict resolution when remote changes conflict with local edits
- **Hybrid storage view**: Items displayed from both SQLite and Markdown sources
- **Reactive updates**: UI automatically updates when data changes or sync completes

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Enhanced TUI Dashboard                    │
│  ┌────────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │ SyncStatusWidget│  │ConflictPanel │  │ Item Lists      │ │
│  └────────────────┘  └──────────────┘  └─────────────────┘ │
└───────────────────────────┬─────────────────────────────────┘
                            │
                    ┌───────▼───────┐
                    │ StorageAdapter │ (Reactive layer)
                    └───────┬───────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌───────▼──────┐  ┌────────▼────────┐
│LocalStorageManager│ │ SyncEngine   │  │ConflictResolver│
└────────────────┘  └──────────────┘  └─────────────────┘
        │                   │                   │
    ┌───┴───┐         ┌─────┴─────┐      ┌─────┴─────┐
    │SQLite │         │ API Client│      │  Backups  │
    │+ MD   │         └───────────┘      └───────────┘
    └───────┘
```

### Key Files

**Adapters:**
- `src/tracertm/tui/adapters/storage_adapter.py` - Reactive interface between LocalStorageManager and TUI

**Widgets:**
- `src/tracertm/tui/widgets/sync_status.py` - Sync status indicator widget
- `src/tracertm/tui/widgets/conflict_panel.py` - Conflict resolution panel
- `src/tracertm/tui/apps/dashboard_v2.py` - Enhanced dashboard with LocalStorage integration

**Storage:**
- `src/tracertm/storage/local_storage.py` - LocalStorageManager (SQLite + Markdown)
- `src/tracertm/storage/sync_engine.py` - Bidirectional sync engine
- `src/tracertm/storage/conflict_resolver.py` - Conflict detection and resolution

## Usage

### Launching the TUI

```bash
# Launch enhanced dashboard (default)
rtm tui dashboard

# Launch legacy dashboard (old behavior)
rtm tui dashboard --legacy
```

### Keyboard Shortcuts

**Enhanced Dashboard:**

| Key      | Action                    | Description                                        |
|----------|---------------------------|----------------------------------------------------|
| `q`      | Quit                      | Exit the application                               |
| `v`      | Switch View               | Cycle through epic/story/test/task views          |
| `r`      | Refresh                   | Reload all data from storage                       |
| `Ctrl+S` | **Sync**                  | **Trigger manual sync with remote server**         |
| `c`      | **Show Conflicts**        | **Open conflict resolution panel**                 |
| `s`      | Search                    | Full-text search across items                      |
| `?`      | Help                      | Show keyboard shortcuts                            |

### Sync Status Indicator

The sync status widget at the top of the dashboard shows:

```
[●] Online | 0 pending | Last sync: 5 minutes ago
```

**Status Indicators:**
- `[●]` Green - Online and connected
- `[●]` Yellow - Offline mode
- `[⟳]` Cyan - Sync in progress
- `[✗]` Red - Sync error
- `[⚠]` Yellow - Conflicts detected

**Components:**
1. **Connection status**: Online/offline/syncing
2. **Pending changes**: Number of local changes not yet synced
3. **Last sync time**: Relative time since last successful sync
4. **Conflict count**: Number of unresolved conflicts (if any)

## Features

### 1. Offline-First Operation

All operations work offline by default:

```python
# Create item (queued for sync automatically)
item = storage_adapter.create_item(
    project=project,
    title="New feature",
    item_type="epic",
    description="Feature description"
)
# ✓ Saved to local SQLite
# ✓ Markdown file generated
# ✓ Queued for sync when online
```

### 2. Real-Time Sync Status

The TUI automatically updates sync status every 5 seconds:

```python
def update_sync_status(self) -> None:
    """Update sync status display."""
    state = self.storage_adapter.get_sync_status()

    sync_widget.set_online(state.status != SyncStatus.ERROR)
    sync_widget.set_syncing(state.status == SyncStatus.SYNCING)
    sync_widget.set_pending_changes(state.pending_changes)
    sync_widget.set_last_sync(state.last_sync)
    sync_widget.set_conflicts(state.conflicts_count)
```

### 3. Manual Sync (Ctrl+S)

Trigger sync manually with `Ctrl+S`:

```python
async def action_sync(self) -> None:
    """Trigger sync operation."""
    result = await self.storage_adapter.trigger_sync()

    if result["success"]:
        self.notify(f"Synced {result['entities_synced']} entities")
    else:
        self.notify(f"Sync failed: {result['error']}", severity="error")
```

**Sync Flow:**
1. Press `Ctrl+S`
2. Status changes to "Syncing..."
3. Local changes uploaded to server
4. Remote changes downloaded
5. Conflicts detected and displayed
6. Status updates to show result

### 4. Conflict Resolution

When conflicts are detected, press `c` to open the conflict panel:

**Conflict Panel Features:**
- **List view**: All unresolved conflicts with metadata
- **Detail view**: Side-by-side comparison of local vs remote versions
- **Resolution options**:
  - `l` - Use Local version (discard remote)
  - `r` - Use Remote version (discard local)
  - `m` - Merge Manually (open editor)
  - `Esc` - Close panel

**Conflict Display:**
```
⚠ Sync Conflicts Detected

Unresolved Conflicts:
┌──────┬──────────────┬───────┬────────┬─────────────────┐
│ Type │ ID           │ Local │ Remote │ Detected        │
├──────┼──────────────┼───────┼────────┼─────────────────┤
│ item │ abc123...    │ v5    │ v6     │ 2025-01-15 14:30│
└──────┴──────────────┴───────┴────────┴─────────────────┘

Conflict Details:
Entity: item - abc123def456
  Local Version:
    Version: 5
    Timestamp: 2025-01-15 14:25:00
    Client: client-001

  Remote Version:
    Version: 6
    Timestamp: 2025-01-15 14:28:00
    Client: client-002

  Data Differences:
    Modified fields: title, status
```

**Resolution Strategies:**

1. **Last Write Wins** (Default): Newest timestamp wins
2. **Local Wins**: Always prefer local changes
3. **Remote Wins**: Always prefer server changes
4. **Manual**: Create conflict file for manual merge

### 5. Hybrid Storage View

Items are displayed with their source indicator:

```
Items - EPIC
┌──────────────┬────────────────────┬────────┬──────────┬────────────┐
│ ID           │ Title              │ Status │ Priority │ Source     │
├──────────────┼────────────────────┼────────┼──────────┼────────────┤
│ abc123...    │ User Authentication│ done   │ high     │ SQLite+MD  │
│ def456...    │ Payment Integration│ todo   │ medium   │ SQLite     │
└──────────────┴────────────────────┴────────┴──────────┴────────────┘
```

**Source Types:**
- `SQLite+MD` - Item stored in both SQLite and Markdown file
- `SQLite` - Item only in SQLite (not yet written to Markdown)
- `Markdown` - Item parsed from Markdown (future enhancement)

## Reactive Callbacks

The StorageAdapter provides reactive callbacks for TUI updates:

### Sync Status Changes

```python
def _on_sync_status_change(self, state: SyncState) -> None:
    """React to sync status changes."""
    if state.status == SyncStatus.SUCCESS:
        self.notify(f"Synced {state.synced_entities} entities")
    elif state.status == SyncStatus.ERROR:
        self.notify(f"Error: {state.last_error}", severity="error")
```

### Conflict Detection

```python
def _on_conflict_detected(self, conflict: Conflict) -> None:
    """React to conflict detection."""
    self.notify(
        f"Conflict: {conflict.entity_type} {conflict.entity_id[:12]}",
        severity="warning"
    )
```

### Item Changes

```python
def _on_item_change(self, item_id: str) -> None:
    """React to item changes."""
    self.refresh_data()  # Reload item list
```

## Storage Adapter API

### Project Operations

```python
# Get project
project = storage_adapter.get_project("my-project")

# Create project
project = storage_adapter.create_project(
    name="my-project",
    description="Project description",
    metadata={"owner": "team"}
)
```

### Item Operations

```python
# List items
items = storage_adapter.list_items(
    project=project,
    item_type="epic",
    status="in_progress"
)

# Create item
item = storage_adapter.create_item(
    project=project,
    title="New Epic",
    item_type="epic",
    description="Epic description",
    status="todo",
    priority="high",
    external_id="EPIC-001"
)

# Update item
item = storage_adapter.update_item(
    project=project,
    item_id=item.id,
    status="done"
)

# Delete item
storage_adapter.delete_item(project=project, item_id=item.id)
```

### Link Operations

```python
# List links
links = storage_adapter.list_links(
    project=project,
    source_id=epic_id
)

# Create link
link = storage_adapter.create_link(
    project=project,
    source_id=story_id,
    target_id=test_id,
    link_type="tests"
)
```

### Search Operations

```python
# Full-text search
items = storage_adapter.search_items(
    query="authentication",
    project_id=project.id
)
```

### Sync Operations

```python
# Get sync status
state = storage_adapter.get_sync_status()
print(f"Pending: {state.pending_changes}")
print(f"Last sync: {state.last_sync}")

# Trigger sync
result = await storage_adapter.trigger_sync(force=True)
print(f"Synced: {result['entities_synced']}")

# Get pending changes count
count = storage_adapter.get_pending_changes_count()
```

### Conflict Operations

```python
# Get unresolved conflicts
conflicts = storage_adapter.get_unresolved_conflicts()

# Get conflict count
count = storage_adapter.get_conflict_count()
```

## Data Flow

### Creating an Item

```
User creates item in TUI
    ↓
StorageAdapter.create_item()
    ↓
LocalStorageManager.create_item()
    ↓
├─ Write to SQLite (immediate)
├─ Generate Markdown file (immediate)
├─ Update FTS index (immediate)
└─ Queue for sync (immediate)
    ↓
Callback triggered: _on_item_change()
    ↓
TUI refreshes item list
```

### Sync Operation

```
User presses Ctrl+S
    ↓
StorageAdapter.trigger_sync()
    ↓
SyncEngine.sync()
    ↓
├─ Detect local changes
├─ Upload phase (local → remote)
│   └─ Process sync queue
├─ Download phase (remote → local)
│   ├─ Fetch remote changes
│   ├─ Detect conflicts
│   └─ Apply non-conflicting changes
└─ Update sync state
    ↓
Callback triggered: _on_sync_status_change()
    ↓
TUI updates sync status widget
    ↓
If conflicts detected:
    Callback triggered: _on_conflict_detected()
    ↓
    TUI shows conflict notification
```

## Testing

### Manual Testing

1. **Launch TUI:**
   ```bash
   rtm tui dashboard
   ```

2. **Create items offline:**
   - Note: Database operations need to be implemented in TUI
   - Observe "pending changes" count increasing

3. **Trigger sync (Ctrl+S):**
   - Watch status change to "Syncing..."
   - Check for sync completion notification

4. **Simulate conflict:**
   - Modify same item locally and remotely
   - Sync and observe conflict notification
   - Press `c` to resolve conflict

5. **Test offline mode:**
   - Disconnect network
   - Create/modify items
   - Observe "offline" indicator
   - Reconnect and sync

### Unit Tests

Test files to create:

```bash
tests/tui/
├── test_storage_adapter.py      # StorageAdapter tests
├── test_sync_status_widget.py   # Widget tests
└── test_conflict_panel.py       # Conflict panel tests
```

**Example test:**

```python
def test_storage_adapter_create_item():
    """Test creating item through adapter."""
    adapter = StorageAdapter()
    project = adapter.create_project("test-project")

    item = adapter.create_item(
        project=project,
        title="Test Item",
        item_type="epic"
    )

    assert item.id is not None
    assert item.title == "Test Item"
    assert adapter.get_pending_changes_count() == 2  # project + item
```

## Configuration

### Storage Location

Default: `~/.tracertm/`

```
~/.tracertm/
├── tracertm.db              # SQLite database
├── projects/
│   └── my-project/
│       ├── README.md        # Project info
│       ├── epics/           # Epic markdown files
│       ├── stories/         # Story markdown files
│       ├── tests/           # Test markdown files
│       ├── tasks/           # Task markdown files
│       └── .meta/
│           ├── links.yaml   # Traceability links
│           └── hashes.json  # Content hashes
└── conflicts/               # Conflict backups
    ├── item/
    └── link/
```

### Sync Configuration

Configure sync engine behavior:

```python
storage_adapter = StorageAdapter(
    base_dir=Path("~/.tracertm"),
    sync_engine=SyncEngine(
        conflict_strategy=ConflictStrategy.LAST_WRITE_WINS,
        max_retries=3,
        retry_delay=1.0
    )
)
```

## Troubleshooting

### TUI not launching

**Error:** `ImportError: Textual is required for TUI`

**Solution:**
```bash
pip install textual
```

### Sync fails

**Error:** "Sync failed: Connection refused"

**Solution:**
- Check network connection
- Verify API server is running
- Check API credentials in config

### Conflicts not resolving

**Issue:** Conflicts persist after resolution

**Solution:**
- Check conflict resolver logs
- Verify conflict strategy is correct
- Manually inspect backup files in `~/.tracertm/conflicts/`

### Items not appearing

**Issue:** Items created but not showing in TUI

**Solution:**
- Press `r` to refresh
- Check SQLite database directly
- Verify project is loaded correctly

## Future Enhancements

1. **Markdown-first mode**: Parse items from Markdown files as primary source
2. **Real-time sync**: WebSocket-based live updates
3. **Conflict diff view**: Visual diff viewer for conflicts
4. **Undo/redo**: Operation history with undo support
5. **Multi-project view**: Switch between projects without restarting
6. **Export/import**: Bulk export to/import from Markdown
7. **Search highlighting**: Highlight search terms in results
8. **Link visualization**: Interactive graph view of links

## Related Documentation

- [LocalStorageManager](./UNIFIED_LOCAL_STORAGE_ARCHITECTURE.md)
- [SyncEngine](./SYNC_ENGINE_SPECIFICATION.md)
- [ConflictResolver](./CONFLICT_RESOLUTION_GUIDE.md)
- [TUI Architecture](./TUI_ARCHITECTURE.md)
