# Project-Local Storage Quick Reference

## Common Operations

### Initialize New Project

```python
from pathlib import Path
from tracertm.storage.local_storage import LocalStorageManager

storage = LocalStorageManager()

# In project directory
trace_dir, project_id = storage.init_project(
    Path.cwd(),
    project_name="My Project",
    description="Project description"
)
```

Creates:
```
my-project/
├── .trace/
│   ├── project.yaml          # Metadata + counters
│   ├── epics/               # Epic markdown files
│   ├── stories/             # Story markdown files
│   ├── tests/               # Test markdown files
│   ├── tasks/               # Task markdown files
│   ├── docs/                # Documentation
│   ├── changes/             # RFC proposals
│   └── .meta/
│       ├── links.yaml       # Traceability matrix
│       └── agents.yaml      # Agent configs
└── .gitignore               # Updated with .trace/.meta/sync.yaml
```

### Register Existing Project

```python
# After git clone
project_id = storage.register_project(Path("/path/to/project"))
```

### Create Items

```python
# Get project storage
project_storage = storage.get_project_storage_for_path(Path.cwd())

# Get project from DB
project = project_storage.get_project()
if not project:
    project = project_storage.create_or_update_project(
        name="My Project", description="..."
    )

# Get item storage
item_storage = project_storage.get_item_storage(project)

# Generate external ID
_, epic_id = storage.increment_project_counter(Path.cwd(), "epic")

# Create epic
epic = item_storage.create_item(
    title="User Authentication",
    item_type="epic",
    external_id=epic_id,  # "EPIC-001"
    description="Implement auth system",
    status="in_progress",
    priority="high",
    owner="@alice"
)
```

Result:
- Markdown file: `.trace/epics/EPIC-001.md`
- SQLite entry: `~/.tracertm/tracertm.db` (items table)
- FTS index: Updated for search

### Index Project

```python
# Parse all markdown files and update SQLite
counts = storage.index_project(Path("/path/to/project"))
# {"epics": 2, "stories": 5, "tests": 3, "tasks": 0}
```

### Query Items

```python
# List items
epics = item_storage.list_items(item_type="epic", status="in_progress")

# Full-text search
results = storage.search_items("authentication", project_id=project.id)

# Get item
item = item_storage.get_item("item-uuid")
```

### Auto-Detect Project

```python
# Find .trace/ in current directory or parents
project_path = storage.get_current_project_path()

if project_path:
    project_storage = storage.get_project_storage_for_path(project_path)
```

### Check if Project

```python
if storage.is_trace_project(Path("/path/to/check")):
    print("Has .trace/")
```

### Get Counters

```python
counters = storage.get_project_counters(Path.cwd())
# {"epic": 2, "story": 5, "test": 3, "task": 10}

# Next IDs:
# EPIC-003, STORY-006, TEST-004, TASK-011
```

### Increment Counter

```python
counter, external_id = storage.increment_project_counter(
    Path.cwd(), "story"
)
# (6, "STORY-006")
```

## File Formats

### project.yaml

```yaml
id: "uuid-here"
name: my-project
description: Project description
version: 1.0.0

counters:
  epic: 2
  story: 5
  test: 3
  task: 10

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

### Item Markdown

```markdown
---
id: "uuid-here"
external_id: "EPIC-001"
type: epic
status: in_progress
priority: high
owner: "@alice"
parent: null
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

# User Authentication

## Description

Implement complete authentication system.
```

### links.yaml

```yaml
links:
  - id: "link-uuid"
    source: EPIC-001
    target: STORY-001
    type: implements
    created: 2024-01-15T10:30:00
```

## Storage Modes

### Project-Local (NEW)

```python
# Uses .trace/ in project directory
storage.get_project_storage_for_path(Path("/path/to/project"))
```

- Files: `<project>/.trace/{type}s/{EXTERNAL_ID}.md`
- Git-versioned
- LLM-agent friendly

### Legacy

```python
# Uses ~/.tracertm/projects/
storage.get_project_storage("project-name")
```

- Files: `~/.tracertm/projects/{name}/{type}s/{EXTERNAL_ID}.md`
- Not git-versioned
- Backward compatible

### Both Index to SQLite

- Location: `~/.tracertm/tracertm.db`
- Tables: `projects`, `items`, `links`, `items_fts`, `project_registry`
- Fast queries across all projects

## CLI Commands (Future)

```bash
# Initialize project
rtm init

# Register existing .trace/
rtm register

# Index .trace/ → SQLite
rtm index

# Create items
rtm create epic "User Auth"
rtm create story "Login Page" --parent EPIC-001

# List/search
rtm list --type epic --status in_progress
rtm search "authentication"

# Sync
rtm sync         # Bidirectional sync
rtm sync push    # Local → Remote
rtm sync pull    # Remote → Local
```

## Database Schema

### project_registry

```sql
CREATE TABLE project_registry (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    path TEXT NOT NULL UNIQUE,
    last_indexed TEXT,
    remote_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata TEXT
)
```

Tracks all `.trace/` projects for:
- Multi-project dashboard
- Auto-indexing
- Sync coordination

## Key Methods

| Method | Purpose |
|--------|---------|
| `init_project()` | Create new `.trace/` structure |
| `register_project()` | Register existing `.trace/` |
| `index_project()` | Parse markdown → SQLite |
| `is_trace_project()` | Check for `.trace/` |
| `get_project_trace_dir()` | Get `.trace/` path |
| `get_current_project_path()` | Auto-detect project |
| `get_project_counters()` | Read counters |
| `increment_project_counter()` | Generate next ID |
| `get_project_storage_for_path()` | Get ProjectStorage |

## Best Practices

1. **Always commit .trace/** to git (except `.trace/.meta/sync.yaml`)
2. **Use project-local mode** for new projects
3. **Index after bulk changes** (`storage.index_project()`)
4. **Auto-detect in scripts** (`get_current_project_path()`)
5. **Version frontmatter** (increment `version` field)
6. **Use external IDs** (EPIC-001) in comments/docs

## Migration

From legacy `~/.tracertm/projects/`:

```python
# 1. Initialize .trace/
storage.init_project(Path("/path/to/project"))

# 2. Copy markdown files
# cp ~/.tracertm/projects/my-project/* .trace/

# 3. Re-index
storage.index_project(Path("/path/to/project"))

# 4. Commit
# git add .trace/
# git commit -m "Add TraceRTM project structure"
```

## Troubleshooting

**Q: .trace/ not detected?**
- Check `storage.is_trace_project(path)` returns True
- Ensure `project.yaml` exists in `.trace/`

**Q: Items not appearing in queries?**
- Run `storage.index_project(path)` to update SQLite
- Check items exist in `.trace/{type}s/` as markdown

**Q: Counters out of sync?**
- Counters stored in `project.yaml`
- Use `increment_project_counter()` to update atomically

**Q: Want to see all projects?**
```python
session = storage.get_session()
result = session.execute(text("SELECT * FROM project_registry"))
for row in result:
    print(row)
```
