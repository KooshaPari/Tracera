# LocalStorageManager Update Summary

## Overview

Updated `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/storage/local_storage.py` to support project-local `.trace/` directories as specified in `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/docs/PROJECT_LOCAL_STORAGE.md`.

## Architecture

### Two-Tier Storage Model

1. **Project-local `.trace/`** (PRIMARY)
   - Markdown files stored IN the project repository
   - Git-versioned with the code
   - Direct access for LLM agents
   - Location: `<project-root>/.trace/`

2. **Global SQLite index** (SECONDARY)
   - Fast queries across all projects
   - Full-text search
   - Location: `~/.tracertm/tracertm.db`

## Key Features Implemented

### 1. Project Management

**Initialize new project:**
```python
storage = LocalStorageManager()
trace_dir, project_id = storage.init_project(
    Path("/path/to/project"),
    project_name="My Project",
    description="Description"
)
```

Creates:
- `.trace/` directory structure
- `project.yaml` with metadata and counters
- Subdirectories: `epics/`, `stories/`, `tests/`, `tasks/`, `docs/`, `changes/`
- `.meta/` with `links.yaml` and `agents.yaml`
- Adds `.trace/.meta/sync.yaml` to `.gitignore`

**Register existing project:**
```python
project_id = storage.register_project(Path("/path/to/project"))
```

### 2. Counter Management

**Get counters:**
```python
counters = storage.get_project_counters(project_path)
# {"epic": 0, "story": 0, "test": 0, "task": 0}
```

**Increment counter:**
```python
counter, external_id = storage.increment_project_counter(project_path, "epic")
# (1, "EPIC-001")
```

### 3. Indexing

**Index markdown files into SQLite:**
```python
counts = storage.index_project(project_path)
# {"epics": 2, "stories": 5, "tests": 3, "tasks": 0}
```

Parses:
- YAML frontmatter (id, status, priority, etc.)
- Markdown content (title, description)
- Updates full-text search index

### 4. Auto-Detection

**Find project from current directory:**
```python
project_path = storage.get_current_project_path()
# Searches up to 10 parent directories for .trace/
```

### 5. Dual-Mode Storage

**Project-local mode:**
```python
project_storage = storage.get_project_storage_for_path(project_path)
# Uses .trace/ in project directory
```

**Legacy mode:**
```python
project_storage = storage.get_project_storage("project-name")
# Uses ~/.tracertm/projects/project-name/
```

## Database Schema

### New Table: project_registry

```sql
CREATE TABLE project_registry (
    id TEXT PRIMARY KEY,              -- Project UUID
    name TEXT NOT NULL,               -- Project name
    path TEXT NOT NULL UNIQUE,        -- Absolute path to project
    last_indexed TEXT,                -- Last indexing timestamp
    remote_id TEXT,                   -- Remote API project ID
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata TEXT                     -- JSON metadata
)
```

Tracks all registered `.trace/` projects for:
- Multi-project dashboard
- Auto-indexing on startup
- Sync coordination

## File Formats

### project.yaml

```yaml
id: "550e8400-e29b-41d4-a716-446655440000"
name: my-awesome-project
description: Project description
version: 1.0.0

counters:
  epic: 2      # Next: EPIC-003
  story: 5     # Next: STORY-006
  test: 3      # Next: TEST-004
  task: 10     # Next: TASK-011

settings:
  default_priority: medium
  default_status: todo
  auto_link_commits: true

team:
  - name: Alice
    role: pm
    email: alice@example.com

hooks:
  on_item_create: []
  on_item_update: []
  on_link_create: []
```

### Item Markdown (.trace/epics/EPIC-001.md)

```markdown
---
id: "550e8400-e29b-41d4-a716-446655440000"
external_id: "EPIC-001"
type: epic
status: in_progress
priority: high
owner: "@alice"
version: 1
created: 2024-01-15T10:30:00
updated: 2024-01-15T10:30:00
tags:
  - authentication
  - security
links:
  - type: implements
    target: STORY-001
---

# User Authentication System

## Description

Implement complete user authentication with OAuth2 support.
```

## API Changes

### LocalStorageManager

**New methods:**
- `is_trace_project(path: Path) -> bool`
- `get_project_trace_dir(project_path: Path) -> Path | None`
- `init_project(project_path, ...) -> (Path, str)`
- `register_project(project_path: Path) -> str`
- `index_project(project_path: Path) -> dict[str, int]`
- `get_project_counters(project_path: Path) -> dict[str, int]`
- `increment_project_counter(project_path, item_type) -> (int, str)`
- `get_current_project_path() -> Path | None`
- `get_project_storage_for_path(project_path) -> ProjectStorage | None`

**Helper methods:**
- `_register_project_in_db(project_id, project_name, project_path)`
- `_index_markdown_file(md_file, project_id, item_type)`
- `get_project_storage_by_id(project_id, trace_dir) -> ProjectStorage | None`

### ProjectStorage

**Updated constructor:**
```python
def __init__(
    self,
    manager: LocalStorageManager,
    project_name: str,
    trace_dir: Path | None = None,     # NEW
    project_id: str | None = None,     # NEW
)
```

**New attributes:**
- `is_project_local: bool` - Mode indicator
- `project_id: str | None` - Project UUID
- `docs_dir: Path` - Documentation directory
- `changes_dir: Path` - RFC proposals directory

### ItemStorage

No API changes, but now:
- Writes to project-local `.trace/` when in project-local mode
- Writes to `~/.tracertm/projects/` when in legacy mode
- Both modes index to global SQLite

## Backward Compatibility

✅ **Fully backward compatible**

- Legacy mode still works: `storage.get_project_storage("name")`
- Existing code continues to function
- New code uses: `storage.get_project_storage_for_path(path)`

## Testing

Created comprehensive test suite:

**File:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/test_project_local_storage.py`

**Tests:**
- Project detection (is_trace_project, get_project_trace_dir)
- Project initialization (init_project)
- Project registration (register_project)
- Counter management (get/increment)
- Indexing (index_project)
- Auto-detection (get_current_project_path)
- Dual-mode storage (local vs legacy)

**Run tests:**
```bash
pytest tests/test_project_local_storage.py -v
```

## Demo Script

**File:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/examples/project_local_demo.py`

Demonstrates complete workflow:
1. Initialize project with `.trace/`
2. Create items (epics, stories, tests)
3. Manage counters
4. Index into SQLite
5. Query and search
6. Show generated markdown files
7. Auto-detect from subdirectories

**Run demo:**
```bash
python examples/project_local_demo.py
```

## Documentation

Created detailed documentation:

1. **`docs/PROJECT_LOCAL_STORAGE.md`** - Architecture overview (provided)
2. **`docs/PROJECT_LOCAL_STORAGE_IMPLEMENTATION.md`** - Implementation details
3. **`STORAGE_UPDATE_SUMMARY.md`** - This file

## Migration Path

### For New Projects

```bash
cd /path/to/new-project
rtm init
# Creates .trace/ structure
```

### For Existing Projects (Legacy)

```python
# Option 1: Initialize .trace/ and copy markdown files
storage.init_project(project_path)
# Manually copy files from ~/.tracertm/projects/{name}/ to .trace/
storage.index_project(project_path)

# Option 2: Use migration command (when implemented)
rtm migrate --project my-project --to ./
```

## Next Steps

1. **CLI Integration**
   - Update `rtm init` to use `storage.init_project()`
   - Update `rtm create` to use project-local mode
   - Add `rtm register` command
   - Add `rtm index` command

2. **File Watcher**
   - Watch `.trace/` for changes
   - Auto-index on file modifications
   - Update SQLite in real-time

3. **Sync System**
   - Implement `.trace/` → SQLite → Remote API sync
   - Handle conflicts (local vs remote changes)
   - Track sync state in `.trace/.meta/sync.yaml`

4. **Migration Tool**
   - Add `rtm migrate` command
   - Migrate from `~/.tracertm/projects/` to `.trace/`
   - Preserve all metadata and history

5. **TUI/Desktop App**
   - Support project-local mode
   - Show multi-project dashboard
   - Enable auto-indexing on startup

## Files Modified

1. **`src/tracertm/storage/local_storage.py`**
   - Added 400+ lines of new functionality
   - Updated docstrings
   - Added type hints

2. **`tests/test_project_local_storage.py`** (NEW)
   - 15+ test cases
   - Full coverage of new features

3. **`examples/project_local_demo.py`** (NEW)
   - Complete workflow demonstration
   - Executable demo script

4. **`docs/PROJECT_LOCAL_STORAGE_IMPLEMENTATION.md`** (NEW)
   - Detailed implementation guide
   - API documentation
   - Usage examples

5. **`STORAGE_UPDATE_SUMMARY.md`** (NEW)
   - This summary document

## Success Criteria

✅ All requirements met:

1. ✅ Support TWO storage modes (project-local + global index)
2. ✅ New methods implemented:
   - `init_project()` ✅
   - `register_project()` ✅
   - `index_project()` ✅
   - `get_project_trace_dir()` ✅
   - `is_trace_project()` ✅
   - `get_project_counters()` ✅
   - `increment_project_counter()` ✅
3. ✅ Updated existing methods to write to `.trace/`
4. ✅ Added project.yaml parsing/writing
5. ✅ Backward compatibility maintained
6. ✅ Global SQLite tracks projects via `project_registry` table
7. ✅ Type checking passes (mypy)
8. ✅ Syntax checking passes (py_compile)
9. ✅ Comprehensive tests created
10. ✅ Documentation complete

## Summary

The LocalStorageManager now fully supports the two-tier storage architecture with:

- **Project-local `.trace/`** for git-versioned markdown files
- **Global SQLite index** for fast queries and search
- **Dual-mode operation** (local + legacy)
- **Full backward compatibility**
- **Comprehensive testing**
- **Complete documentation**

This enables:
- Requirements living WITH the code
- LLM agent direct file access
- Multi-project dashboards
- Offline-first operation
- Git-based collaboration

Ready for CLI integration and file watcher implementation!
