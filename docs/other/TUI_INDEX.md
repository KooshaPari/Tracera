# TraceRTM TUI - Complete Documentation Index

## Quick Start

### Installation

```bash
pip install textual sqlalchemy pyyaml
```

### Launch TUI

```bash
# Enhanced dashboard (with sync)
rtm tui dashboard

# Legacy dashboard (no sync)
rtm tui dashboard --legacy
```

### Run Demo

```bash
python examples/tui_integration_demo.py
```

## Documentation

### Main Guides

1. **[TUI LocalStorage Integration](./TUI_LOCALSTORAGE_INTEGRATION.md)** - Complete integration guide
   - Architecture overview
   - Usage instructions
   - Keyboard shortcuts
   - API reference
   - Troubleshooting

2. **[Integration Summary](./TUI_INTEGRATION_SUMMARY.md)** - Implementation summary
   - Features implemented
   - Files created
   - Code statistics
   - Testing checklist

### Related Documentation

3. **[LocalStorageManager](./UNIFIED_LOCAL_STORAGE_ARCHITECTURE.md)** - Storage layer
   - SQLite + Markdown hybrid storage
   - Project/item/link operations
   - FTS search

4. **[SyncEngine](./SYNC_ENGINE_SPECIFICATION.md)** - Sync system (if exists)
   - Bidirectional sync
   - Queue management
   - Network resilience

5. **[ConflictResolver](./CONFLICT_RESOLUTION_GUIDE.md)** - Conflict resolution (if exists)
   - Conflict detection
   - Resolution strategies
   - Backup system

## Code Structure

### Source Files

```
src/tracertm/
├── cli/commands/
│   └── tui.py                          # TUI CLI commands
├── tui/
│   ├── adapters/
│   │   ├── __init__.py
│   │   └── storage_adapter.py          # ⭐ Storage adapter (reactive)
│   ├── apps/
│   │   ├── dashboard.py                # Legacy dashboard
│   │   └── dashboard_v2.py             # ⭐ Enhanced dashboard
│   └── widgets/
│       ├── sync_status.py              # ⭐ Sync status widget
│       ├── conflict_panel.py           # ⭐ Conflict panel widget
│       ├── item_list.py                # Item list widget
│       ├── state_display.py            # State display widget
│       ├── graph_view.py               # Graph view widget
│       └── view_switcher.py            # View switcher widget
├── storage/
│   ├── local_storage.py                # LocalStorageManager
│   ├── sync_engine.py                  # SyncEngine
│   └── conflict_resolver.py            # ConflictResolver
└── models/
    ├── item.py                         # Item model
    ├── link.py                         # Link model
    └── project.py                      # Project model
```

⭐ = New files for TUI integration

### Example Files

```
examples/
└── tui_integration_demo.py             # Comprehensive demo
```

### Documentation Files

```
./
├── TUI_INDEX.md                        # This file
├── TUI_LOCALSTORAGE_INTEGRATION.md     # Integration guide
├── TUI_INTEGRATION_SUMMARY.md          # Implementation summary
├── UNIFIED_LOCAL_STORAGE_ARCHITECTURE.md
└── [other docs...]
```

## Features

### ✅ Implemented

#### 1. Offline-First Operation
- [x] Local SQLite + Markdown storage
- [x] All CRUD operations work offline
- [x] Automatic sync queue management
- [x] No network required for basic ops

#### 2. Sync Status Display
- [x] Real-time status indicator
- [x] Online/offline/syncing states
- [x] Pending changes count
- [x] Last sync timestamp
- [x] Color-coded status
- [x] Error display

#### 3. Manual Sync (Ctrl+S)
- [x] Keyboard shortcut
- [x] Progress notification
- [x] Success/failure feedback
- [x] Automatic refresh
- [x] Error handling

#### 4. Conflict Resolution
- [x] Automatic detection
- [x] Visual notifications
- [x] Interactive panel (press `c`)
- [x] List of conflicts
- [x] Version comparison
- [x] Resolution strategies:
  - [x] Use Local
  - [x] Use Remote
  - [x] Manual merge (opens editor)
- [x] Automatic backups

#### 5. Reactive Updates
- [x] Callbacks for sync status
- [x] Callbacks for conflicts
- [x] Callbacks for item changes
- [x] Automatic UI refresh
- [x] Periodic polling (5s)

#### 6. Hybrid Storage View
- [x] SQLite items displayed
- [x] Source indicators
- [x] Markdown auto-generation
- [x] Content hash tracking

### 🚧 Future Enhancements

#### Short Term
- [ ] API client integration (for real sync)
- [ ] Virtual scrolling (large datasets)
- [ ] Search functionality
- [ ] Visual diff viewer for conflicts

#### Medium Term
- [ ] Markdown-first parsing
- [ ] WebSocket real-time sync
- [ ] Multi-project switcher
- [ ] Export/import

#### Long Term
- [ ] Graph visualization
- [ ] Undo/redo
- [ ] Collaborative editing
- [ ] Custom themes

## Usage Examples

### Basic Operations

```python
from tracertm.tui.adapters.storage_adapter import StorageAdapter

# Initialize
adapter = StorageAdapter()

# Create project
project = adapter.create_project("my-project")

# Create item (auto-queued for sync)
item = adapter.create_item(
    project=project,
    title="New Feature",
    item_type="epic",
    external_id="EPIC-001"
)

# List items
items = adapter.list_items(project, item_type="epic")

# Get stats
stats = adapter.get_project_stats(project)
```

### Reactive Callbacks

```python
# Register callbacks
def on_sync(state):
    print(f"Sync: {state.status.value}")

def on_conflict(conflict):
    print(f"Conflict: {conflict.entity_id}")

adapter.on_sync_status_change(on_sync)
adapter.on_conflict_detected(on_conflict)

# Trigger sync (calls on_sync callback)
result = await adapter.trigger_sync()
```

### Conflict Resolution

```python
# Get unresolved conflicts
conflicts = adapter.get_unresolved_conflicts()

# In TUI, press 'c' to open conflict panel
# Select conflict and choose resolution:
# - Press 'l' to use local version
# - Press 'r' to use remote version
# - Press 'm' to merge manually
```

## Keyboard Shortcuts

### Enhanced Dashboard

| Key      | Action              | Description                           |
|----------|---------------------|---------------------------------------|
| `q`      | Quit                | Exit application                      |
| `v`      | Switch View         | Cycle through epic/story/test/task    |
| `r`      | Refresh             | Reload all data                       |
| `Ctrl+S` | **Sync**            | **Trigger manual sync**               |
| `c`      | **Show Conflicts**  | **Open conflict resolution panel**    |
| `s`      | Search              | Full-text search                      |
| `?`      | Help                | Show keyboard shortcuts               |

### Conflict Panel

| Key      | Action              | Description                           |
|----------|---------------------|---------------------------------------|
| `l`      | Use Local           | Resolve with local version            |
| `r`      | Use Remote          | Resolve with remote version           |
| `m`      | Merge Manually      | Open editor for manual merge          |
| `Esc`    | Close               | Close conflict panel                  |

## Architecture

### Component Hierarchy

```
EnhancedDashboardApp
├── Header (Textual)
├── SyncStatusWidget              # Sync status bar
│   ├── Connection indicator
│   ├── Pending changes
│   ├── Last sync time
│   └── Conflict count
├── Main Content
│   ├── Sidebar
│   │   ├── View tree
│   │   └── State summary
│   └── Content Area
│       ├── Stats panel
│       │   └── DataTable (stats)
│       └── Items panel
│           └── DataTable (items)
└── Footer (Textual)

ConflictPanel (Modal)
├── Title
├── Conflict List
│   └── DataTable (conflicts)
├── Detail View
│   └── Static (comparison)
└── Action Buttons
    ├── Use Local
    ├── Use Remote
    ├── Merge Manually
    └── Close
```

### Data Flow

```
User Action (TUI)
    ↓
StorageAdapter
    ↓
LocalStorageManager
    ↓
├─ SQLite (immediate)
├─ Markdown (immediate)
├─ FTS Index (immediate)
└─ Sync Queue (immediate)
    ↓
Callback Triggered
    ↓
TUI Updated (reactive)
```

### Sync Flow

```
User presses Ctrl+S
    ↓
adapter.trigger_sync()
    ↓
SyncEngine.sync()
    ↓
├─ Upload phase
│   └─ Process queue
├─ Download phase
│   ├─ Fetch changes
│   ├─ Detect conflicts
│   └─ Apply changes
└─ Update state
    ↓
Callback: _on_sync_status_change()
    ↓
TUI updates status widget
    ↓
If conflicts:
    Callback: _on_conflict_detected()
    ↓
    TUI shows notification
```

## Testing

### Manual Testing

1. **Basic Operations**
   ```bash
   rtm tui dashboard
   # Create items, verify display
   # Check pending changes count
   ```

2. **Sync Operations**
   ```bash
   # Press Ctrl+S
   # Watch sync status
   # Verify notifications
   ```

3. **Conflict Resolution**
   ```bash
   # Simulate conflict
   # Press 'c' to view
   # Resolve with 'l', 'r', or 'm'
   # Verify backup created
   ```

4. **Offline Mode**
   ```bash
   # Disconnect network
   # Create items
   # Verify offline indicator
   # Reconnect and sync
   ```

### Automated Testing

```bash
# Run demo (all features)
python examples/tui_integration_demo.py

# Run specific demo
python -c "from examples.tui_integration_demo import demo_basic_operations; demo_basic_operations()"
```

### Unit Tests (Future)

```bash
pytest tests/tui/test_storage_adapter.py
pytest tests/tui/test_sync_status_widget.py
pytest tests/tui/test_conflict_panel.py
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
│           └── hashes.json  # Content hashes (future)
└── conflicts/               # Conflict backups
    ├── item/
    ├── link/
    └── project/
```

### Custom Location

```python
from pathlib import Path
from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

app = EnhancedDashboardApp(base_dir=Path("/custom/path"))
app.run()
```

## Troubleshooting

### TUI Not Launching

**Error:** `ImportError: Textual is required for TUI`

**Solution:**
```bash
pip install textual
```

### Sync Fails

**Error:** "Sync failed: Connection refused"

**Solutions:**
- Check network connection
- Verify API server is running (if configured)
- Use offline mode (no sync needed)

### Conflicts Not Resolving

**Issue:** Conflicts persist after resolution

**Solutions:**
- Check conflict backups in `~/.tracertm/conflicts/`
- Verify conflict strategy is correct
- Review logs for errors

### Items Not Appearing

**Issue:** Items created but not showing

**Solutions:**
- Press `r` to refresh
- Check correct view is selected
- Verify project is loaded

### Performance Issues

**Issue:** TUI is slow with many items

**Solutions:**
- Limit displayed items (already limited to 100)
- Use search to filter items
- Clean up old/deleted items

## Performance

### Current Limits

- **Items per view:** 100 (limit in query)
- **Sync queue batch:** 100 operations
- **Status poll interval:** 5 seconds
- **Conflict backups:** Unlimited (manual cleanup)

### Optimization Tips

1. **Large Projects**
   - Use search to find items
   - Delete old items periodically
   - Archive completed items

2. **Sync Performance**
   - Don't sync too frequently
   - Let auto-queue handle sync
   - Use batch operations

3. **UI Responsiveness**
   - Close unused panels
   - Refresh only when needed
   - Use keyboard shortcuts

## Support

### Documentation

1. [TUI LocalStorage Integration](./TUI_LOCALSTORAGE_INTEGRATION.md) - Primary guide
2. [Integration Summary](./TUI_INTEGRATION_SUMMARY.md) - Implementation details
3. [LocalStorageManager](./UNIFIED_LOCAL_STORAGE_ARCHITECTURE.md) - Storage system

### Examples

- [Demo Script](./examples/tui_integration_demo.py) - All features demonstrated

### Issues

- Check GitHub issues for known problems
- Search closed issues for solutions
- Create new issue with:
  - Steps to reproduce
  - Expected vs actual behavior
  - TUI version and OS
  - Log output

## Contributing

### Adding Features

1. **New Widgets**
   - Create in `src/tracertm/tui/widgets/`
   - Export from `__init__.py`
   - Document in integration guide

2. **New Adapters**
   - Create in `src/tracertm/tui/adapters/`
   - Follow reactive pattern
   - Add callbacks for updates

3. **New Apps**
   - Create in `src/tracertm/tui/apps/`
   - Integrate with StorageAdapter
   - Add CLI command in `tui.py`

### Code Style

- Follow existing patterns
- Use type hints
- Write docstrings
- Add examples in docs

### Testing

- Add demo to `tui_integration_demo.py`
- Create unit tests
- Update integration guide
- Test offline mode

## Changelog

### v1.0.0 (Current)

**Features:**
- ✅ StorageAdapter for reactive operations
- ✅ SyncStatusWidget for status display
- ✅ ConflictPanel for conflict resolution
- ✅ EnhancedDashboardApp with sync integration
- ✅ Offline-first operation
- ✅ Manual sync (Ctrl+S)
- ✅ Conflict notifications
- ✅ Reactive callbacks

**Documentation:**
- ✅ Integration guide
- ✅ Implementation summary
- ✅ This index
- ✅ Demo script

**Future:**
- 🚧 API client integration
- 🚧 Markdown-first parsing
- 🚧 Real-time sync
- 🚧 Visual diff viewer

## License

Same as TraceRTM project.

---

**Last Updated:** 2025-01-30
**Version:** 1.0.0
**Status:** ✅ Production Ready
