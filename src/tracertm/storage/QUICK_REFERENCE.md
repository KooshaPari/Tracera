# LocalStorageManager Quick Reference

## Imports

```python
from tracertm.storage import LocalStorageManager, ProjectStorage, ItemStorage
```

## Initialization

```python
# Use default location (~/.tracertm)
manager = LocalStorageManager()

# Custom location
from pathlib import Path
manager = LocalStorageManager(base_dir=Path("/custom/path"))
```

## Projects

```python
# Get project storage
ps = manager.get_project_storage("my-project")

# Create/update project
project = ps.create_or_update_project(
    name="my-project",
    description="Description here",
    metadata={"key": "value"}
)

# Get existing project
project = ps.get_project()
```

## Items

```python
# Get item storage
item_storage = ps.get_item_storage(project)

# Create item
item = item_storage.create_item(
    title="Title",
    item_type="epic",           # epic, story, test, task
    external_id="EPIC-001",     # Optional but recommended
    description="Description",
    status="todo",              # todo, in_progress, done
    priority="high",            # low, medium, high
    owner="@username",
    parent_id=None,             # Optional parent item ID
    metadata={"key": "value"}   # Custom metadata
)

# Update item
updated = item_storage.update_item(
    item_id=item.id,
    title="New title",          # Optional
    status="in_progress",       # Optional
    metadata={"new": "data"}    # Merged with existing
)

# Get item
item = item_storage.get_item(item_id)

# List items
all_items = item_storage.list_items()
epics = item_storage.list_items(item_type="epic")
in_progress = item_storage.list_items(status="in_progress")

# Delete item (soft delete)
item_storage.delete_item(item_id)
```

## Links

```python
# Create link
link = item_storage.create_link(
    source_id=epic.id,
    target_id=story.id,
    link_type="implements",     # implements, tested_by, depends_on, blocks, relates_to
    metadata={"note": "text"}
)

# List links
all_links = item_storage.list_links()
epic_links = item_storage.list_links(source_id=epic.id)
implements = item_storage.list_links(link_type="implements")

# Delete link
item_storage.delete_link(link_id)
```

## Search

```python
# Search all items
results = manager.search_items("authentication")

# Search in project
results = manager.search_items("OAuth", project_id=project.id)
```

## Sync Queue

```python
# Get pending changes (automatically queued)
queue = manager.get_sync_queue(limit=100)

# Clear synced entry
manager.clear_sync_queue_entry(queue_id)
```

## Sync State

```python
# Update sync metadata
manager.update_sync_state("last_sync", "2024-01-20T14:30:00Z")

# Get sync metadata
last_sync = manager.get_sync_state("last_sync")
```

## Item Types

- `epic` - High-level features
- `story` - User stories
- `test` - Test cases
- `task` - Implementation tasks

## Link Types

- `implements` - Epic → Story, Story → Task
- `tested_by` - Story/Task → Test
- `depends_on` - Blocking dependency
- `blocks` - Reverse dependency
- `relates_to` - General relationship

## File Locations

```
~/.tracertm/
├── tracertm.db              # SQLite database
└── projects/
    └── <project-name>/
        ├── README.md
        ├── epics/
        │   └── EPIC-001.md
        ├── stories/
        │   └── STORY-001.md
        ├── tests/
        │   └── TEST-001.md
        ├── tasks/
        │   └── TASK-001.md
        └── .meta/
            └── links.yaml
```

## Common Patterns

### Create Epic with Stories

```python
# Create epic
epic = item_storage.create_item(
    title="User Authentication",
    item_type="epic",
    external_id="EPIC-001"
)

# Create stories
story1 = item_storage.create_item(
    title="User Registration",
    item_type="story",
    external_id="STORY-001",
    parent_id=epic.id
)

# Link epic to story
item_storage.create_link(
    source_id=epic.id,
    target_id=story1.id,
    link_type="implements"
)
```

### Create Story with Test

```python
# Create story
story = item_storage.create_item(
    title="Login Feature",
    item_type="story",
    external_id="STORY-002"
)

# Create test
test = item_storage.create_item(
    title="Test Login Flow",
    item_type="test",
    external_id="TEST-001"
)

# Link story to test
item_storage.create_link(
    source_id=story.id,
    target_id=test.id,
    link_type="tested_by"
)
```

### Batch Operations

```python
# Get session for batch
session = manager.get_session()
try:
    for title in ["Epic 1", "Epic 2", "Epic 3"]:
        item = Item(
            project_id=project.id,
            title=title,
            item_type="epic",
            view="epic",
            status="todo"
        )
        session.add(item)
    session.commit()
finally:
    session.close()
```

## Error Handling

```python
try:
    item = item_storage.get_item(item_id)
    if not item:
        raise ValueError(f"Item not found: {item_id}")
except ValueError as e:
    print(f"Error: {e}")
```

## Testing

```python
import tempfile
from pathlib import Path

# Use temporary directory for tests
with tempfile.TemporaryDirectory() as tmpdir:
    manager = LocalStorageManager(base_dir=Path(tmpdir))
    # Test operations...
```
