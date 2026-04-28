# File Watcher for Auto-Indexing

## Overview

The TraceRTM file watcher provides real-time auto-indexing of `.trace/` directory changes into the local SQLite database. It monitors markdown files, YAML configuration, and links files for changes and automatically updates the database index.

## Features

- **Real-time monitoring**: Watches `.trace/` directory for file system changes
- **Debouncing**: Prevents duplicate processing of rapid changes (default: 500ms)
- **Auto-indexing**: Automatically parses and indexes changes to SQLite
- **Optional sync queuing**: Can queue changes for remote API sync
- **Live statistics**: Display real-time event processing stats
- **Graceful shutdown**: Clean shutdown on Ctrl+C

## Watched Files

The file watcher monitors:

- `.trace/**/*.md` - Item markdown files (epics, stories, tests, tasks)
- `.trace/.meta/links.yaml` - Traceability links
- `.trace/project.yaml` - Project metadata

Files **not** watched:
- `.trace/.meta/sync.yaml` (local-only, gitignored)
- Hidden files and directories (except `.trace` and `.meta`)
- Non-markdown/YAML files

## Usage

### Standalone File Watcher

Run the file watcher in the foreground with real-time statistics:

```bash
# Watch current directory
rtm watch

# Watch specific project
rtm watch --path /path/to/project

# Enable auto-sync to remote
rtm watch --auto-sync

# Custom debounce delay (in milliseconds)
rtm watch --debounce 1000

# Custom refresh rate for stats display (in seconds)
rtm watch --refresh 2.0
```

Press `Ctrl+C` to stop watching.

### TUI Integration

Launch the TUI dashboard with background file watcher:

```bash
# Launch dashboard with file watcher
rtm tui dashboard --watch

# Watch specific project
rtm tui dashboard --watch --path /path/to/project
```

The file watcher will automatically stop when you exit the TUI.

## How It Works

### 1. File Change Detection

The watcher uses the `watchdog` library to monitor file system events:

```
.trace/
├── epics/EPIC-001.md        ← Created/Modified/Deleted
├── stories/STORY-001.md     ← Created/Modified/Deleted
├── .meta/
│   └── links.yaml           ← Created/Modified
└── project.yaml             ← Created/Modified
```

### 2. Debouncing

Rapid changes to the same file are debounced:

```
Event: file.md modified (time: 0ms)
Event: file.md modified (time: 100ms)  ← Cancelled
Event: file.md modified (time: 200ms)  ← Cancelled
Event: file.md modified (time: 300ms)  ← Cancelled
[Wait 500ms]
Process: file.md (final state)
```

### 3. Event Processing

After debouncing, events are processed based on file type:

```python
# Item markdown files (.md)
if event_type == "created" or event_type == "modified":
    parse_item_markdown(path)
    create_or_update_item_in_sqlite()
elif event_type == "deleted":
    soft_delete_item_in_sqlite()

# Links file (links.yaml)
if event_type == "modified":
    parse_links_yaml(path)
    sync_links_to_sqlite()

# Project config (project.yaml)
if event_type == "modified":
    parse_config_yaml(path)
    update_project_metadata()
```

### 4. SQLite Index Update

Changes are automatically reflected in the SQLite database:

- **Items table**: Updated with item metadata and content
- **Links table**: Synchronized with links.yaml
- **FTS index**: Full-text search index updated
- **Sync queue**: Optional queuing for remote sync

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    .trace/ Directory                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │ EPIC-001.md│  │ STORY-001  │  │links.yaml  │            │
│  │ (modified) │  │   (new)    │  │ (updated)  │            │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘            │
└────────┼───────────────┼───────────────┼────────────────────┘
         │               │               │
         ▼               ▼               ▼
    ┌────────────────────────────────────────┐
    │        Watchdog File Observer          │
    │  (File system event monitoring)        │
    └────────────┬───────────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────────┐
    │        Debounce Timer (500ms)          │
    │  (Prevents duplicate processing)       │
    └────────────┬───────────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────────┐
    │      TraceFileWatcher._process_event   │
    │  ┌──────────────────────────────────┐  │
    │  │ _handle_item_change()            │  │
    │  │ _handle_links_change()           │  │
    │  │ _handle_project_change()         │  │
    │  └──────────────────────────────────┘  │
    └────────────┬───────────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────────┐
    │    Markdown Parser (markdown_parser)   │
    │  ┌──────────────────────────────────┐  │
    │  │ parse_item_markdown()            │  │
    │  │ parse_links_yaml()               │  │
    │  │ parse_config_yaml()              │  │
    │  └──────────────────────────────────┘  │
    └────────────┬───────────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────────┐
    │   LocalStorageManager (SQLite + MD)    │
    │  ┌──────────────────────────────────┐  │
    │  │ create_item() / update_item()    │  │
    │  │ create_link() / update_link()    │  │
    │  │ update_fts_index()               │  │
    │  │ queue_sync() [optional]          │  │
    │  └──────────────────────────────────┘  │
    └────────────┬───────────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────────┐
    │        ~/.tracertm/tracertm.db         │
    │  ┌──────────────────────────────────┐  │
    │  │ items (updated)                  │  │
    │  │ links (synced)                   │  │
    │  │ items_fts (re-indexed)           │  │
    │  │ sync_queue (queued)              │  │
    │  └──────────────────────────────────┘  │
    └────────────────────────────────────────┘
```

## Configuration

### Debounce Delay

Control how long to wait before processing a file change:

```bash
# Default: 500ms
rtm watch

# Faster response (100ms)
rtm watch --debounce 100

# Slower, more conservative (2000ms)
rtm watch --debounce 2000
```

**Recommendation**: Use 500-1000ms for most cases. Lower values may cause duplicate processing during rapid saves.

### Auto-Sync

Enable automatic queuing of changes for remote sync:

```bash
# Without auto-sync (default)
rtm watch

# With auto-sync enabled
rtm watch --auto-sync
```

When enabled, all changes are queued in the `sync_queue` table and can be pushed with `rtm sync push`.

## Statistics Display

The standalone watcher displays live statistics:

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ File Watcher Statistics     ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Status            │ 🟢 Running                │
│ Events Processed  │ 42                        │
│ Events Pending    │ 0                         │
│ Last Event        │ 2024-11-30 10:23:45       │
│                   │                           │
│ Changes by Type   │                           │
│   Created         │ 12                        │
│   Modified        │ 28                        │
│   Deleted         │ 2                         │
└───────────────────┴───────────────────────────┘
```

Refresh rate can be controlled with `--refresh`:

```bash
# Update stats every 2 seconds (default: 1.0)
rtm watch --refresh 2.0
```

## Programmatic Usage

### Basic Usage

```python
from pathlib import Path
from tracertm.storage.file_watcher import TraceFileWatcher
from tracertm.storage.local_storage import LocalStorageManager

# Initialize storage and watcher
storage = LocalStorageManager()
watcher = TraceFileWatcher(
    project_path=Path("/path/to/project"),
    storage=storage,
    debounce_ms=500,
    auto_sync=False,
)

# Start watching
watcher.start()

# Check status
print(f"Running: {watcher.is_running()}")

# Get statistics
stats = watcher.get_stats()
print(f"Events processed: {stats['events_processed']}")

# Stop watching
watcher.stop()
```

### Advanced Usage

```python
import time
from tracertm.storage.file_watcher import TraceFileWatcher

# Custom debounce and auto-sync
watcher = TraceFileWatcher(
    project_path=Path.cwd(),
    storage=storage,
    debounce_ms=1000,  # 1 second debounce
    auto_sync=True,    # Queue changes for sync
)

watcher.start()

try:
    # Run for 1 hour
    time.sleep(3600)
except KeyboardInterrupt:
    print("Stopping watcher...")
finally:
    watcher.stop()

    # Print final statistics
    stats = watcher.get_stats()
    print(f"Total events processed: {stats['events_processed']}")
    print(f"Changes by type: {stats['changes_by_type']}")
```

## Error Handling

The file watcher handles errors gracefully:

### Parse Errors

If a file fails to parse, the error is logged and the file is skipped:

```
ERROR: Failed to parse /path/to/EPIC-001.md: Invalid YAML frontmatter
```

### Missing Files

Deleted files are handled correctly:

```
INFO: Processing deleted for item: EPIC-001.md
INFO: Deleted item: EPIC-001
```

### Database Errors

Database errors are logged but don't crash the watcher:

```
ERROR: Error processing modified event for /path/to/file.md: database locked
```

## Performance

### Benchmarks

- **Event detection**: < 1ms (watchdog overhead)
- **Debouncing**: 500ms default (configurable)
- **Parse + index**: ~10-50ms per item (depends on size)
- **Memory usage**: ~5-10MB (plus SQLite cache)

### Optimization Tips

1. **Increase debounce**: For projects with frequent saves, use `--debounce 1000` or higher
2. **Batch operations**: The watcher automatically batches rapid changes via debouncing
3. **FTS updates**: Full-text search index is updated efficiently using SQLite FTS5
4. **SQLite WAL mode**: LocalStorageManager uses WAL mode for concurrent reads/writes

## Troubleshooting

### Watcher Not Starting

```
Failed to initialize file watcher: No .trace/ directory found
```

**Solution**: Ensure the project has a `.trace/` directory. Run `rtm init` to create one.

### Changes Not Detected

```
Events processed: 0
```

**Possible causes**:
1. File is in `.trace/.meta/sync.yaml` (ignored)
2. File is hidden (starts with `.`)
3. File is not `.md` or `.yaml`
4. Watchdog not installed: `pip install watchdog`

### High CPU Usage

```
CPU: 100%
```

**Solution**: Increase debounce delay to reduce processing frequency:
```bash
rtm watch --debounce 2000
```

### Database Lock Errors

```
ERROR: database is locked
```

**Solution**: Ensure only one process is writing to the database at a time. The watcher uses SQLite WAL mode to allow concurrent reads.

## Integration Examples

### With Git Hooks

Auto-index after git pull:

```bash
# .git/hooks/post-merge
#!/bin/bash
rtm index --path .
```

### With systemd

Run watcher as a service:

```ini
# /etc/systemd/system/tracertm-watcher.service
[Unit]
Description=TraceRTM File Watcher
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/project
ExecStart=/usr/local/bin/rtm watch --auto-sync
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable tracertm-watcher
sudo systemctl start tracertm-watcher
```

### With Docker

```dockerfile
FROM python:3.12-slim

RUN pip install tracertm

WORKDIR /project

CMD ["rtm", "watch", "--auto-sync"]
```

Run:
```bash
docker run -v /path/to/project:/project tracertm-watcher
```

## API Reference

### TraceFileWatcher

```python
class TraceFileWatcher:
    def __init__(
        self,
        project_path: Path,
        storage: LocalStorageManager,
        debounce_ms: int = 500,
        auto_sync: bool = False,
    )
```

**Methods**:

- `start()`: Start watching for changes
- `stop()`: Stop watching
- `is_running() -> bool`: Check if watcher is running
- `get_stats() -> dict`: Get statistics about processed events

**Statistics**:

```python
{
    "events_processed": int,      # Total events processed
    "events_pending": int,         # Events waiting for debounce
    "last_event_time": str | None, # ISO timestamp of last event
    "changes_by_type": {           # Breakdown by event type
        "created": int,
        "modified": int,
        "deleted": int,
    },
    "is_running": bool,            # Current running status
}
```

## See Also

- [LocalStorageManager](./local_storage.py) - SQLite + Markdown storage
- [Markdown Parser](./markdown_parser.py) - Item and config parsing
- [Sync Engine](./sync_engine.py) - Remote sync coordination
- [Project-Local Storage Architecture](../../docs/PROJECT_LOCAL_STORAGE.md) - Overall design
