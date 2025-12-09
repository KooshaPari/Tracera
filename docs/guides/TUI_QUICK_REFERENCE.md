# TraceRTM TUI - Quick Reference Card

## Installation

```bash
pip install textual sqlalchemy pyyaml
```

## Launch

```bash
rtm tui dashboard          # Enhanced (with sync)
rtm tui dashboard --legacy # Legacy (no sync)
```

## Keyboard Shortcuts

### Main Dashboard

| Key      | Action              |
|----------|---------------------|
| `q`      | Quit                |
| `v`      | Switch View         |
| `r`      | Refresh             |
| `Ctrl+S` | **Sync**            |
| `c`      | **Show Conflicts**  |
| `s`      | Search              |
| `?`      | Help                |

### Conflict Panel

| Key   | Action         |
|-------|----------------|
| `l`   | Use Local      |
| `r`   | Use Remote     |
| `m`   | Merge Manual   |
| `Esc` | Close Panel    |

## Sync Status Indicators

| Icon | Meaning           |
|------|-------------------|
| 🟢   | Online            |
| 🟡   | Offline           |
| 🔵   | Syncing           |
| 🔴   | Error             |
| ⚠️   | Conflicts (count) |

## Storage Locations

| Path                  | Contents           |
|-----------------------|--------------------|
| `~/.tracertm/`        | Base directory     |
| `tracertm.db`         | SQLite database    |
| `projects/`           | Project files      |
| `conflicts/`          | Conflict backups   |

## Quick Commands (Python)

### Create Item

```python
from tracertm.tui.adapters.storage_adapter import StorageAdapter

adapter = StorageAdapter()
project = adapter.create_project("my-project")

item = adapter.create_item(
    project=project,
    title="Feature",
    item_type="epic",
    external_id="EPIC-001"
)
```

### Sync

```python
result = await adapter.trigger_sync()
print(f"Synced: {result['entities_synced']}")
```

### Conflicts

```python
conflicts = adapter.get_unresolved_conflicts()
print(f"Conflicts: {len(conflicts)}")
```

## Troubleshooting

| Issue               | Solution                      |
|---------------------|-------------------------------|
| TUI won't launch    | `pip install textual`         |
| Sync fails          | Check network, use offline    |
| Items missing       | Press `r` to refresh          |
| Slow performance    | Limit items, use search       |

## Documentation

- **[Index](./TUI_INDEX.md)** - Complete documentation index
- **[Integration Guide](./TUI_LOCALSTORAGE_INTEGRATION.md)** - Full usage guide
- **[Demo](./examples/tui_integration_demo.py)** - Run examples

## Support

```bash
# Run demo
python examples/tui_integration_demo.py

# Get help
rtm tui --help
```

---

**Quick Tip:** Press `Ctrl+S` anytime to sync your changes!
