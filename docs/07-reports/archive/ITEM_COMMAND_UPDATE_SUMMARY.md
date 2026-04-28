# Item Commands Update Summary

## Overview

Updated `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/cli/commands/item.py` to support project-local `.trace/` directories with automatic project detection and fallback to global storage.

## Key Changes

### 1. Project Detection

Added helper functions to detect and manage project-local `.trace/` directories:

```python
def _find_project_root(start_path: Path | None = None) -> Path | None:
    """Find the project root directory by looking for .trace/ directory."""
    current = start_path or Path.cwd()
    for parent in [current] + list(current.parents):
        trace_dir = parent / ".trace"
        if trace_dir.exists() and trace_dir.is_dir():
            return parent
    return None

def _get_project_storage_path(project_path: Path | None = None) -> Path:
    """Get the .trace/ directory path for a project."""
    if project_path:
        trace_dir = project_path / ".trace"
        if not trace_dir.exists():
            raise ProjectNotFoundError(f"No .trace/ directory found in {project_path}")
        return trace_dir

    # Auto-detect project
    project_root = _find_project_root()
    if not project_root:
        raise ProjectNotFoundError("Not in a TraceRTM project. Run 'rtm init' or specify --project")
    return project_root / ".trace"
```

### 2. Counter Management

Added functions to manage auto-incrementing external IDs in `project.yaml`:

```python
def _load_project_yaml(trace_dir: Path) -> dict:
    """Load project.yaml configuration."""
    project_yaml = trace_dir / "project.yaml"
    if not project_yaml.exists():
        return {
            "name": trace_dir.parent.name,
            "description": "",
            "version": "1.0.0",
            "counters": {},
            "settings": {},
        }
    with open(project_yaml, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def _get_next_external_id(trace_dir: Path, item_type: str) -> str:
    """Get next external ID for an item type and increment counter."""
    config = _load_project_yaml(trace_dir)
    if "counters" not in config:
        config["counters"] = {}
    counter = config["counters"].get(item_type, 0)
    counter += 1
    config["counters"][item_type] = counter
    _save_project_yaml(trace_dir, config)
    type_prefix = item_type.upper()
    return f"{type_prefix}-{counter:03d}"
```

### 3. Updated Commands

#### `create_item`

- Added `--project PATH` option
- Auto-detects `.trace/` directory in current directory or parents
- Falls back to global storage if not in a project
- Uses counter from `project.yaml` for external IDs
- Shows enhanced output:
  ```
  ✓ Created EPIC-003: User Authentication
    File: .trace/epics/EPIC-003.md
    Project: my-awesome-project
    Indexed: ~/.tracertm/tracertm.db
  ```

Example usage:
```bash
# Auto-detect project
cd /path/to/my-project
rtm item create "User Authentication" --view FEATURE --type epic

# Specify project explicitly
rtm item create "Login API" --view API --type endpoint --project /path/to/my-project
```

#### `update_item`

- Added `--project PATH` option
- Updates markdown file in `.trace/`
- Increments version in frontmatter
- Re-indexes to SQLite
- Shows enhanced output:
  ```
  ✓ Updated EPIC-003: User Authentication
    Version: 2
    Markdown updated in .trace/epics/EPIC-003.md
  ```

Example usage:
```bash
rtm item update EPIC-003 --status in_progress
rtm item update EPIC-003 --title "New Title" --project /path/to/project
```

#### `delete_item`

- Added `--project PATH` option
- Removes markdown file from `.trace/`
- Updates SQLite index
- Updates `links.yaml` if item had links
- Shows enhanced output:
  ```
  ✓ Deleted EPIC-003
    Markdown file removed: .trace/epics/EPIC-003.md
    SQLite index updated
  ```

Example usage:
```bash
rtm item delete EPIC-003 --force
rtm item delete EPIC-003 --project /path/to/project
```

#### `list_items`

- Added `--project PATH` option
- Queries from SQLite (fast)
- Shows which project items belong to
- Enhanced table title: `Items in my-awesome-project (5)`
- JSON output includes project name:
  ```json
  {
    "project": "my-awesome-project",
    "items": [...],
    "count": 5
  }
  ```

Example usage:
```bash
rtm item list --type epic --status in_progress
rtm item list --project /path/to/project --json
```

## Storage Architecture

### Two-Tier Model

1. **Project-local `.trace/`** - Markdown files (git-versioned)
   ```
   .trace/
   ├── project.yaml          # Counters, settings
   ├── epics/
   │   ├── EPIC-001.md
   │   └── EPIC-002.md
   ├── stories/
   │   └── STORY-001.md
   └── .meta/
       └── links.yaml        # Traceability links
   ```

2. **Global `~/.tracertm/`** - SQLite index (auto-managed)
   ```
   ~/.tracertm/
   ├── tracertm.db          # Fast queries
   └── projects/            # Legacy global storage
   ```

### Workflow

1. **Create**: Write to `.trace/{type}s/{ID}.md` + index to SQLite
2. **Update**: Update markdown + increment version + re-index
3. **Delete**: Remove markdown + update links.yaml + update SQLite
4. **List**: Fast query from SQLite index
5. **Sync**: Queue changes for remote API sync

## Fallback Behavior

If not in a project directory (no `.trace/` found):
- Shows warning: `[yellow]Not in a project directory. Using global storage.[/yellow]`
- Falls back to `~/.tracertm/projects/{project_name}/`
- Uses ConfigManager to get current project
- Still creates markdown files, just in global location

## Benefits

1. **Version Control**: Requirements live WITH the code
2. **LLM-Friendly**: Direct file access for agents
3. **Fast Queries**: SQLite index for complex queries
4. **Offline-First**: Works without network
5. **Auto-Detect**: No manual configuration needed
6. **Backward Compatible**: Falls back to global storage

## Example Output

```bash
$ cd /path/to/my-project
$ rtm item create "User Authentication" --view FEATURE --type epic

✓ Created EPIC-001: User Authentication
  File: .trace/epics/EPIC-001.md
  Project: my-awesome-project
  Indexed: ~/.tracertm/tracertm.db

$ rtm item update EPIC-001 --status in_progress

✓ Updated EPIC-001: User Authentication
  Version: 2
  Markdown updated in .trace/epics/EPIC-001.md

$ rtm item list --type epic

Items in my-awesome-project (1)
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━┓
┃ External  ┃ Title               ┃ Type ┃ Status      ┃ Priority ┃ Owner ┃
┃ ID        ┃                     ┃      ┃             ┃          ┃       ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━┩
│ EPIC-001  │ User Authentication │ epic │ in_progress │ medium   │       │
└───────────┴─────────────────────┴──────┴─────────────┴──────────┴───────┘
```

## Files Modified

- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/cli/commands/item.py`

## New Imports Added

```python
import yaml  # For project.yaml parsing
```

## Testing Checklist

- [ ] Create item in project directory (auto-detect)
- [ ] Create item with `--project` flag
- [ ] Create item outside project (fallback to global)
- [ ] Update item and verify version increment
- [ ] Delete item and verify markdown removed
- [ ] List items and verify project name shown
- [ ] Verify counters increment in project.yaml
- [ ] Verify SQLite indexing works
- [ ] Verify links.yaml updates on delete
- [ ] Test with multiple projects

## Next Steps

1. Update `rtm init` command to create `.trace/` directory structure
2. Add `rtm register` command to index existing `.trace/` directories
3. Add file watcher for auto-indexing on changes
4. Implement conflict resolution for concurrent edits
5. Add migration command to move from global to local storage
