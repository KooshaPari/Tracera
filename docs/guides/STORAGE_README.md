# TraceRTM Local Storage

Hybrid SQLite + Markdown storage system for offline-first operation with automatic sync capabilities.

## Overview

The LocalStorageManager provides:

1. **SQLite database** - Fast queries, relationships, and sync state management
2. **Markdown files** - Human/LLM readable artifacts with YAML frontmatter
3. **Bidirectional sync** - SQLite ↔ Markdown kept in sync automatically
4. **Change tracking** - Sync queue for remote synchronization
5. **Full-text search** - FTS5-based search across all items

## Quick Start

```python
from tracertm.storage import LocalStorageManager

# Initialize
manager = LocalStorageManager()

# Create project
project_storage = manager.get_project_storage("my-project")
project = project_storage.create_or_update_project(
    name="my-project",
    description="My project description"
)

# Create items
item_storage = project_storage.get_item_storage(project)
epic = item_storage.create_item(
    title="User Auth",
    item_type="epic",
    external_id="EPIC-001",
    status="in_progress"
)
```

See `examples/local_storage_example.py` for a complete working example.

## Documentation

Full documentation available at: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/docs/UNIFIED_LOCAL_STORAGE_ARCHITECTURE.md`

## Tests

Run the test suite:
```bash
pytest tests/test_local_storage.py -v
```

All 16 tests passing with full coverage of:
- Database initialization
- Project/Item/Link CRUD
- Full-text search
- Markdown generation
- Sync queue operations

---

## Markdown Parser

The `markdown_parser.py` module provides low-level parsing and writing of Markdown files with YAML frontmatter. It's used by `LocalStorageManager` but can also be used standalone.

### Item Format

Each item is stored as a Markdown file with:

1. **YAML frontmatter** - Metadata (id, type, status, priority, etc.)
2. **Markdown body** - Structured content (title, description, acceptance criteria, notes, history)

Example:

```markdown
---
id: "550e8400-e29b-41d4-a716-446655440000"
external_id: "EPIC-001"
type: epic
status: in_progress
priority: high
owner: "@team-lead"
version: 1
created: 2024-01-15T10:30:00Z
updated: 2024-01-20T14:22:00Z
tags:
  - authentication
  - security
---

# User Authentication System

## Description

Implement a complete user authentication system...

## Acceptance Criteria

- [ ] Users can sign up with email/password
- [ ] OAuth2 integration with Google, GitHub
- [x] Password reset flow

## Notes

Technical considerations...
```

### Standalone Usage

```python
from pathlib import Path
from datetime import datetime
from tracertm.storage.markdown_parser import (
    ItemData,
    LinkData,
    parse_item_markdown,
    write_item_markdown,
    parse_links_yaml,
    write_links_yaml,
    get_item_path,
)

# Create an item
item = ItemData(
    id="550e8400-e29b-41d4-a716-446655440000",
    external_id="EPIC-001",
    item_type="epic",
    status="in_progress",
    priority="high",
    title="User Authentication System",
    description="Implement authentication...",
    created=datetime.now(),
    updated=datetime.now(),
)

# Write to markdown
base_dir = Path.home() / ".tracertm"
item_path = get_item_path(base_dir, "my-project", "epic", "EPIC-001")
write_item_markdown(item, item_path)

# Parse back
parsed_item = parse_item_markdown(item_path)
print(f"Title: {parsed_item.title}")
```

See `examples/storage/markdown_parser_example.py` for complete examples.

### API Reference

#### ItemData

Dataclass representing a TraceRTM item with all metadata and content.

**Key Fields:**
- `id`, `external_id`, `item_type`, `status` (required)
- `priority`, `owner`, `parent`, `version`
- `created`, `updated`, `tags`, `links`
- `title`, `description`, `acceptance_criteria`, `notes`, `history`

#### LinkData

Dataclass representing a traceability link.

**Fields:**
- `id`, `source`, `target`, `link_type`, `created`
- `metadata` - Additional custom data

#### Functions

```python
# Item operations
parse_item_markdown(path: Path) -> ItemData
write_item_markdown(item: ItemData, path: Path) -> None

# Link operations
parse_links_yaml(path: Path) -> list[LinkData]
write_links_yaml(links: list[LinkData], path: Path) -> None

# Configuration operations
parse_config_yaml(path: Path) -> dict[str, Any]
write_config_yaml(config: dict[str, Any], path: Path) -> None

# Path helpers
get_item_path(base_dir: Path, project_name: str, item_type: str, external_id: str) -> Path
get_links_path(base_dir: Path, project_name: str) -> Path
get_config_path(base_dir: Path, project_name: str) -> Path
list_items(base_dir: Path, project_name: str, item_type: str | None = None) -> list[Path]
```

### Directory Structure

```
~/.tracertm/projects/
└── my-project/
    ├── README.md
    ├── epics/
    │   ├── EPIC-001.md
    │   └── EPIC-002.md
    ├── stories/
    │   ├── STORY-001.md
    │   └── STORY-002.md
    ├── tests/
    │   └── TEST-001.md
    ├── tasks/
    │   └── TASK-001.md
    └── .meta/
        ├── links.yaml      # Traceability links
        └── config.yaml     # Project settings
```
