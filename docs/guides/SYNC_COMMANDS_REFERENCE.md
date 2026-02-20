# TraceRTM Sync Commands Reference

## Overview

The TraceRTM CLI now includes comprehensive sync commands for managing offline-first synchronization between local storage and the remote backend API.

## Commands

### 1. `rtm sync` - Full Bidirectional Sync

Run a complete sync cycle: detect local changes, upload to server, download remote changes, and resolve conflicts.

```bash
rtm sync                # Normal sync
rtm sync --force        # Force sync even if recently synced
rtm sync --dry-run      # Preview what would be synced
```

**Features:**
- Detects local changes automatically
- Uploads pending changes to server
- Downloads remote changes
- Auto-resolves conflicts using configured strategy
- Shows detailed results with entity counts, duration, and errors
- Progress spinner during sync

**Example output:**
```
✓ Sync completed successfully

Entities synced: 15
Duration:        2.3s
Conflicts:       2

Conflicts detected:
  • item abc123
  • link xyz789

Run 'rtm sync conflicts' to view all conflicts
```

---

### 2. `rtm sync status` - Show Sync Status

Display current synchronization status including last sync time, pending changes, online/offline status, and conflicts.

```bash
rtm sync status
```

**Shows:**
- Current sync status (up to date, syncing, pending changes, error)
- Online/offline connectivity status
- Last sync timestamp (human-readable: "2h ago", "Just now")
- Number of pending local changes
- Number of unresolved conflicts
- Last error message (if any)

**Example output:**
```
╭─────────── Sync Status ───────────╮
│ Status:          Up to date        │
│ Online:          Online            │
│ Last sync:       2h ago            │
│ Pending changes: 0                 │
╰────────────────────────────────────╯
```

---

### 3. `rtm sync push` - Upload Local Changes Only

Push pending local changes to the server without downloading remote changes.

```bash
rtm sync push          # Normal push
rtm sync push --force  # Force push even with conflicts
```

**Use cases:**
- One-way sync scenarios
- Uploading bulk changes
- Offline work followed by explicit upload

**Example output:**
```
✓ Pushed 8 changes
```

---

### 4. `rtm sync pull` - Download Remote Changes Only

Pull remote changes from the server without uploading local changes.

```bash
rtm sync pull                              # Pull all recent changes
rtm sync pull --since "2024-01-01T00:00:00"  # Pull changes since timestamp
```

**Use cases:**
- Fetching updates from other clients
- Refreshing local cache
- Selective sync with timestamp filtering

**Example output:**
```
✓ Pulled 12 changes

Conflicts: 1
Run 'rtm sync conflicts' to view and resolve
```

---

### 5. `rtm sync conflicts` - List Unresolved Conflicts

Show all conflicts detected during synchronization that require resolution.

```bash
rtm sync conflicts           # List all conflicts
rtm sync conflicts --type item  # Filter by entity type
```

**Displays:**
- Conflict ID (for use with `rtm sync resolve`)
- Entity ID and type
- Local and remote version numbers
- Detection timestamp

**Example output:**
```
Found 2 unresolved conflicts:

┏━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ ID           ┃ Entity    ┃ Type ┃ Local Ver┃ Remote Ver ┃ Detected         ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ conflict_abc…│ item-123  │ item │ 5        │ 6          │ 2024-01-15 14:30 │
│ conflict_xyz…│ link-456  │ link │ 3        │ 4          │ 2024-01-15 14:32 │
└──────────────┴───────────┴──────┴──────────┴────────────┴──────────────────┘

Run 'rtm sync resolve <conflict_id>' to resolve a conflict
```

---

### 6. `rtm sync resolve <conflict_id>` - Resolve Conflict

Resolve a specific sync conflict using a resolution strategy.

```bash
rtm sync resolve conflict_abc123                              # Default (last_write_wins)
rtm sync resolve conflict_abc123 --strategy local_wins        # Prefer local version
rtm sync resolve conflict_abc123 --strategy remote_wins       # Prefer remote version
rtm sync resolve conflict_abc123 --strategy manual --data '{"title": "Merged"}' # Manual merge
```

**Strategies:**

1. **last_write_wins** (default)
   - Uses version with newest timestamp
   - If timestamps equal, uses higher version number

2. **local_wins**
   - Always prefers local version
   - Discards remote changes

3. **remote_wins**
   - Always prefers remote version
   - Discards local changes

4. **manual**
   - Requires `--data` with merged JSON
   - Full control over resolution
   - Creates new version number

**Example output:**
```
✓ Conflict resolved using local_wins
  Entity: item item-123
  Version: 6

Backup saved to: ~/.tracertm/conflicts/item/item-123_20240115_143000
```

**Backup:**
- All conflicts are backed up before resolution
- Backup includes local version, remote version, and metadata
- Located in `~/.tracertm/conflicts/<entity_type>/<entity_id>_<timestamp>/`

---

### 7. `rtm sync queue` - Show Pending Sync Queue

Display all changes queued for synchronization.

```bash
rtm sync queue             # Show queue (default limit: 50)
rtm sync queue --limit 100 # Show more items
```

**Shows:**
- Queue entry ID
- Entity type and ID
- Operation (create, update, delete)
- Created timestamp
- Retry count
- Status (ready, retry, error)
- Error messages (if any)

**Example output:**
```
Sync queue (15 pending):

┏━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┓
┃ ID ┃ Entity             ┃ Operation┃ Created         ┃ Retries┃ Status ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━┩
│ 1  │ item/abc123...     │ update   │ 2024-01-15 14:30│ 0      │ Ready  │
│ 2  │ link/xyz789...     │ create   │ 2024-01-15 14:31│ 1      │ Retry 1│
│ 3  │ item/def456...     │ delete   │ 2024-01-15 14:32│ 3      │ Error  │
└────┴────────────────────┴──────────┴─────────────────┴────────┴────────┘

Items with errors (1):
  • def456: Network timeout after 3 retries...

Run 'rtm sync push' to process the queue
```

**Features:**
- Retry tracking with exponential backoff
- Error messages for failed items
- Maximum retry limits (configurable)

---

### 8. `rtm sync clear-queue` - Clear Sync Queue

Remove all pending changes from the sync queue.

```bash
rtm sync clear-queue          # Interactive confirmation
rtm sync clear-queue --force  # Skip confirmation
```

**Warning:** This permanently deletes all pending changes. Use with caution!

**Example output:**
```
Warning: This will delete 15 pending changes
Are you sure you want to clear the queue? [y/N]: y

✓ Cleared 15 items from sync queue
```

---

## Configuration

Sync commands use configuration from `~/.tracertm/config.json`:

```json
{
  "api_url": "https://api.tracertm.io",
  "api_token": "your-api-token",
  "api_timeout": 30.0,
  "api_max_retries": 3,
  "sync_conflict_strategy": "last_write_wins"
}
```

**Configuration options:**

- `api_url`: Backend API endpoint
- `api_token`: Authentication token
- `api_timeout`: Request timeout in seconds (default: 30)
- `api_max_retries`: Maximum retry attempts (default: 3)
- `sync_conflict_strategy`: Default conflict resolution strategy

---

## Implementation Details

### Architecture

The sync commands integrate with:

1. **SyncEngine** (`tracertm.storage.sync_engine`)
   - Main sync orchestration
   - Change detection and queuing
   - Upload/download phases
   - Retry logic with exponential backoff

2. **ApiClient** (`tracertm.api.sync_client`)
   - Async HTTP client for backend API
   - Authentication and error handling
   - Rate limiting support
   - Network resilience

3. **ConflictResolver** (`tracertm.storage.conflict_resolver`)
   - Conflict detection using vector clocks
   - Multiple resolution strategies
   - Automatic backup creation
   - Conflict history tracking

### Key Features

- **Async/await support**: All network operations are async for better performance
- **Rich terminal output**: Tables, panels, progress spinners, color-coded status
- **Error handling**: Comprehensive error messages with helpful hints
- **Offline resilience**: Graceful degradation when API is unavailable
- **Progress tracking**: Real-time feedback during sync operations
- **Human-readable timestamps**: "2h ago", "Just now", "3d ago"
- **Conflict backups**: Automatic backup before conflict resolution

### Database Schema

Sync state is stored in SQLite tables:

**sync_queue**
```sql
CREATE TABLE sync_queue (
    id INTEGER PRIMARY KEY,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    operation TEXT NOT NULL,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL,
    retry_count INTEGER DEFAULT 0,
    last_error TEXT,
    UNIQUE(entity_type, entity_id, operation)
)
```

**sync_state**
```sql
CREATE TABLE sync_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
```

**conflicts**
```sql
CREATE TABLE conflicts (
    id TEXT PRIMARY KEY,
    entity_id TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    local_version TEXT NOT NULL,
    remote_version TEXT NOT NULL,
    detected_at TEXT NOT NULL,
    status TEXT NOT NULL,
    resolution_strategy TEXT,
    resolved_at TEXT,
    resolved_version TEXT,
    backup_path TEXT,
    metadata TEXT
)
```

---

## Workflow Examples

### Example 1: Normal Sync Workflow

```bash
# Check current status
rtm sync status

# Perform full sync
rtm sync

# Check for conflicts
rtm sync conflicts

# Resolve any conflicts
rtm sync resolve conflict_abc123 --strategy last_write_wins
```

### Example 2: Offline Work Followed by Sync

```bash
# Work offline, make changes
rtm item create "New Feature" --view FEATURE --type feature
rtm item update item-123 --status done

# Check what's pending
rtm sync queue

# When back online, push changes
rtm sync push

# Then pull remote changes
rtm sync pull
```

### Example 3: Manual Conflict Resolution

```bash
# List conflicts
rtm sync conflicts

# Get conflict details
rtm sync resolve conflict_abc123 --strategy manual --data '{
  "title": "Manually Merged Title",
  "description": "Combined description from both versions",
  "status": "in_progress"
}'
```

### Example 4: Force Sync After Issues

```bash
# Clear stuck queue
rtm sync clear-queue --force

# Force fresh sync
rtm sync --force
```

---

## Error Handling

Sync commands provide clear error messages with actionable hints:

**Network errors:**
```
✗ Sync failed
  • Network error after 3 retries: Connection timeout

Check your network connection and API configuration
```

**Authentication errors:**
```
✗ Sync failed
  • Authentication failed. Check API token.

Run 'rtm config set api_token <your-token>' to update
```

**Conflict errors:**
```
Conflicts detected:
  • item abc123
  • link xyz789

Run 'rtm sync conflicts' to view and resolve
```

---

## Best Practices

1. **Regular syncs**: Run `rtm sync` regularly to avoid large backlogs
2. **Check status**: Use `rtm sync status` to monitor sync health
3. **Resolve conflicts promptly**: Don't let conflicts accumulate
4. **Use appropriate strategies**: Choose conflict resolution based on your workflow
5. **Monitor queue**: Check `rtm sync queue` if syncs seem slow
6. **Backup awareness**: Conflicts are backed up automatically before resolution

---

## File Locations

- **Sync commands**: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/cli/commands/sync.py`
- **Sync engine**: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/storage/sync_engine.py`
- **API client**: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/api/sync_client.py`
- **Conflict resolver**: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/storage/conflict_resolver.py`
- **Conflict backups**: `~/.tracertm/conflicts/<entity_type>/<entity_id>_<timestamp>/`
- **Configuration**: `~/.tracertm/config.json`

---

## Testing

To test the sync commands:

```bash
# Check command registration
rtm sync --help

# Test individual commands
rtm sync status
rtm sync queue
rtm sync conflicts

# Test with dry-run
rtm sync --dry-run
```

---

## Future Enhancements

Potential additions to sync commands:

- `rtm sync auto` - Auto-sync on file changes (daemon mode)
- `rtm sync history` - View sync history and statistics
- `rtm sync repair` - Repair corrupted sync state
- `rtm sync export` - Export conflict backups
- `rtm sync stats` - Detailed sync performance metrics
- `rtm sync schedule` - Configure automatic sync intervals
