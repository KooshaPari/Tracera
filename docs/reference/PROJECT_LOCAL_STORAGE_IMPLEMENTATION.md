# Project-Local Storage Implementation Summary

## Overview

Updated `LocalStorageManager` to support the two-tier storage architecture:

1. **Project-local `.trace/`** - Markdown files in project repositories (git-versioned)
2. **Global `~/.tracertm/`** - SQLite index for fast queries (auto-managed)

## Changes to `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/storage/local_storage.py`

### LocalStorageManager Class

#### New Database Schema

Added `project_registry` table to track all registered `.trace/` projects:

```sql
CREATE TABLE project_registry (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    path TEXT NOT NULL UNIQUE,      -- Absolute path to project directory
    last_indexed TEXT,
    remote_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata TEXT
)
```

#### New Methods

1. **`is_trace_project(path: Path) -> bool`**
   - Checks if a path contains a `.trace/` directory
   - Works with both file and directory paths

2. **`get_project_trace_dir(project_path: Path) -> Path | None`**
   - Returns the `.trace/` directory path if it exists
   - Returns None if not found

3. **`init_project(project_path, project_name?, description?, metadata?) -> (trace_dir, project_id)`**
   - Creates complete `.trace/` structure in a project directory
   - Creates subdirectories: `epics/`, `stories/`, `tests/`, `tasks/`, `docs/`, `changes/`, `.meta/`
   - Generates `project.yaml` with metadata and counters
   - Creates `.meta/links.yaml` and `.meta/agents.yaml`
   - Adds `.trace/.meta/sync.yaml` to `.gitignore`
   - Registers project in global SQLite index

4. **`register_project(project_path: Path) -> str`**
   - Registers an existing `.trace/` directory in the global index
   - Loads project ID from `project.yaml`
   - Generates ID if missing
   - Returns project ID

5. **`index_project(project_path: Path) -> dict[str, int]`**
   - Indexes all markdown files from `.trace/` into SQLite
   - Parses YAML frontmatter and markdown content
   - Updates full-text search index
   - Returns counts: `{"epics": N, "stories": M, "tests": K, "tasks": L}`

6. **`get_project_counters(project_path: Path) -> dict[str, int]`**
   - Reads counters from `project.yaml`
   - Returns current values for epic, story, test, task

7. **`increment_project_counter(project_path, item_type) -> (counter_value, external_id)`**
   - Increments counter in `project.yaml`
   - Returns next counter value and generated external ID (e.g., "EPIC-003")

8. **`get_current_project_path() -> Path | None`**
   - Searches for `.trace/` in current directory and up to 10 parent levels
   - Returns project directory path or None

9. **`get_project_storage_for_path(project_path: Path) -> ProjectStorage | None`**
   - Returns ProjectStorage instance for a project-local `.trace/` directory
   - Loads project name and ID from `project.yaml`

#### Helper Methods

10. **`_register_project_in_db(project_id, project_name, project_path)`**
    - Inserts/updates project in `project_registry` table

11. **`_index_markdown_file(md_file, project_id, item_type)`**
    - Parses markdown file with YAML frontmatter
    - Creates/updates Item in SQLite
    - Updates full-text search index

12. **`get_project_storage_by_id(project_id, trace_dir) -> ProjectStorage | None`**
    - Creates ProjectStorage for a specific project ID and trace directory

### ProjectStorage Class

#### Updated Constructor

Now supports two modes:

```python
def __init__(
    self,
    manager: LocalStorageManager,
    project_name: str,
    trace_dir: Path | None = None,
    project_id: str | None = None,
)
```

- **Project-local mode**: When `trace_dir` is provided, uses that `.trace/` directory
- **Legacy mode**: When `trace_dir` is None, uses `~/.tracertm/projects/{project_name}/`

#### New Attributes

- `is_project_local: bool` - Indicates which mode is active
- `project_id: str | None` - Project UUID (for project-local mode)
- `docs_dir: Path` - Directory for documentation
- `changes_dir: Path` - Directory for RFC-style change proposals

### ItemStorage Class

#### Updated Methods

- **`_write_item_markdown()`**: Now creates parent directories if needed (for project-local mode)
- **`_get_item_path()`**: Updated documentation to clarify it writes to `.trace/{type}s/{external_id}.md`

## project.yaml Format

```yaml
id: "550e8400-e29b-41d4-a716-446655440000"
name: my-awesome-project
description: A project to build awesome things
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
  - name: Bob
    role: dev
    email: bob@example.com

hooks:
  on_item_create: []
  on_item_update: []
  on_link_create: []

metadata:
  # Optional custom metadata
```

## Markdown File Format

Items are stored in `.trace/{type}s/{EXTERNAL_ID}.md` with YAML frontmatter:

```markdown
---
id: "550e8400-e29b-41d4-a716-446655440000"
external_id: "EPIC-001"
type: epic
status: in_progress
priority: high
owner: "@alice"
parent: null
version: 3
created: 2024-01-15T10:30:00
updated: 2024-01-20T14:22:00
tags:
  - authentication
  - security
links:
  - type: implements
    target: STORY-001
---

# User Authentication System

## Description

Implement a complete user authentication system supporting OAuth2, JWT tokens,
and session management.

## Acceptance Criteria

- [ ] Users can sign up with email/password
- [ ] OAuth2 integration with Google, GitHub
- [ ] JWT token refresh mechanism
```

## Usage Examples

### Initialize a New Project

```python
from pathlib import Path
from tracertm.storage.local_storage import LocalStorageManager

storage = LocalStorageManager()
project_path = Path("/path/to/my-project")

trace_dir, project_id = storage.init_project(
    project_path,
    project_name="My Awesome Project",
    description="A project to build awesome things"
)

print(f"Created .trace/ at: {trace_dir}")
print(f"Project ID: {project_id}")
```

### Register an Existing Project

```python
# After git clone
storage = LocalStorageManager()
project_path = Path("/path/to/cloned-project")

project_id = storage.register_project(project_path)
print(f"Registered project: {project_id}")
```

### Index Project Files

```python
storage = LocalStorageManager()
project_path = Path("/path/to/my-project")

counts = storage.index_project(project_path)
print(f"Indexed {counts['epics']} epics, {counts['stories']} stories")
```

### Create Items in Project-Local Mode

```python
storage = LocalStorageManager()
project_path = Path.cwd()

# Get project storage
project_storage = storage.get_project_storage_for_path(project_path)

# Get or create project in database
project = project_storage.get_project()
if not project:
    project = project_storage.create_or_update_project(
        name="My Project",
        description="Test project"
    )

# Get item storage
item_storage = project_storage.get_item_storage(project)

# Increment counter and create epic
counter, external_id = storage.increment_project_counter(project_path, "epic")

epic = item_storage.create_item(
    title="User Authentication",
    item_type="epic",
    external_id=external_id,
    description="Implement auth system",
    status="todo",
    priority="high"
)

# Markdown file created at: .trace/epics/EPIC-001.md
# SQLite index updated in: ~/.tracertm/tracertm.db
```

### Auto-Detect Current Project

```python
storage = LocalStorageManager()

# Works from any subdirectory in the project
project_path = storage.get_current_project_path()

if project_path:
    print(f"Found project at: {project_path}")
    project_storage = storage.get_project_storage_for_path(project_path)
else:
    print("No .trace/ project found")
```

## Backward Compatibility

The implementation maintains backward compatibility:

- Legacy mode still works: `storage.get_project_storage("project-name")` uses `~/.tracertm/projects/`
- New project-local mode: `storage.get_project_storage_for_path(path)` uses `.trace/`
- Both modes write to the same global SQLite index
- Both modes support full-text search and queries

## Migration Path

To migrate from legacy `~/.tracertm/projects/` to project-local `.trace/`:

1. Create `.trace/` in project: `storage.init_project(project_path)`
2. Copy markdown files from `~/.tracertm/projects/{name}/` to `.trace/`
3. Run `storage.index_project(project_path)` to update SQLite index
4. Commit `.trace/` to git

## Testing

Created comprehensive test suite in `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/test_project_local_storage.py`:

- Test project detection (`is_trace_project`, `get_project_trace_dir`)
- Test project initialization (`init_project`)
- Test project registration (`register_project`)
- Test counter management (`get_project_counters`, `increment_project_counter`)
- Test indexing (`index_project`)
- Test auto-detection (`get_current_project_path`)
- Test project storage modes (local vs legacy)

## Files Modified

1. `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/storage/local_storage.py` - Implementation
2. `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/test_project_local_storage.py` - Tests

## Next Steps

1. Update CLI commands to use project-local mode by default
2. Add file watcher for auto-indexing `.trace/` changes
3. Implement sync between `.trace/` and remote API
4. Add migration command: `rtm migrate --from legacy --to local`
5. Update documentation for users
