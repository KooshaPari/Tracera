# Conflict Resolver Quick Reference

## Import

```python
from tracertm.storage import (
    ConflictResolver,
    ConflictStrategy,
    EntityVersion,
    VectorClock,
    compare_versions,
    format_conflict_summary,
)
```

## Initialize

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///~/.tracertm/tracertm.db")
Session = sessionmaker(bind=engine)
session = Session()

resolver = ConflictResolver(
    session=session,
    backup_dir=Path.home() / ".tracertm" / "conflicts",
    default_strategy=ConflictStrategy.LAST_WRITE_WINS,
)
```

## Create Entity Versions

```python
from datetime import UTC, datetime

local = EntityVersion(
    entity_id="item-123",
    entity_type="item",
    data={"title": "My Item", "status": "active"},
    vector_clock=VectorClock("client-1", 3, datetime.now(UTC)),
    content_hash="hash123",
)

remote = EntityVersion(
    entity_id="item-123",
    entity_type="item",
    data={"title": "My Item", "status": "done"},
    vector_clock=VectorClock("client-2", 3, datetime.now(UTC)),
    content_hash="hash456",
)
```

## Detect Conflict

```python
conflict = resolver.detect_conflict(local, remote)

if conflict:
    print(f"Conflict: {conflict.id}")
else:
    print("No conflict - changes are sequential")
```

## Resolve Conflict

### Automatic (Last-Write-Wins)
```python
result = resolver.resolve(conflict)
winner = result.version
```

### Local Wins
```python
result = resolver.resolve(conflict, ConflictStrategy.LOCAL_WINS)
```

### Remote Wins
```python
result = resolver.resolve(conflict, ConflictStrategy.REMOTE_WINS)
```

### Manual
```python
merged_data = {
    "title": "My Item",
    "status": "done",      # From remote
    "priority": "high",    # From local
}

result = resolver.resolve_manual(conflict, merged_data, merged_by="user-123")
```

## Query Conflicts

### List Unresolved
```python
conflicts = resolver.list_unresolved()
# OR filter by type
item_conflicts = resolver.list_unresolved(entity_type="item")
```

### Get Specific Conflict
```python
conflict = resolver.get_conflict("conflict_item-123_1705329600")
```

### Get Statistics
```python
stats = resolver.get_conflict_stats()
print(stats['total'])
print(stats['by_status'])
print(stats['by_entity_type'])
```

## Utilities

### Format Summary
```python
summary = format_conflict_summary(conflict)
print(summary)
# Output:
# Conflict: item 'item-123'
#   Local:  v3 @ 2024-01-15 14:30
#   Remote: v3 @ 2024-01-15 14:35
#   Status: unresolved
```

### Compare Versions
```python
diff = compare_versions(local, remote)
print(f"Added: {diff['added']}")
print(f"Removed: {diff['removed']}")
print(f"Modified: {diff['modified']}")
```

## Backups

### List Backups
```python
from tracertm.storage import ConflictBackup

backup_mgr = ConflictBackup(Path.home() / ".tracertm" / "conflicts")
backups = backup_mgr.list_backups()

for backup in backups:
    print(f"{backup['conflict_id']}: {backup['backup_path']}")
```

### Load Backup
```python
versions = backup_mgr.load_backup(Path(backup['backup_path']))
if versions:
    local, remote = versions
    print(local.data)
    print(remote.data)
```

### Delete Backup
```python
backup_mgr.delete_backup(Path(backup['backup_path']))
```

## Vector Clock Operations

### Check Ordering
```python
clock1 = VectorClock("client-1", 1, datetime.now(UTC))
clock2 = VectorClock("client-1", 2, datetime.now(UTC))

if clock1.happens_before(clock2):
    print("clock1 happened before clock2")

if clock1.is_concurrent(clock2):
    print("Clocks are concurrent - conflict!")
```

### Serialize
```python
data = clock.to_dict()
restored = VectorClock.from_dict(data)
```

## Strategies Reference

| Strategy | Use Case | Winner |
|----------|----------|--------|
| LAST_WRITE_WINS | General use | Newest timestamp |
| LOCAL_WINS | Offline-first | Always local |
| REMOTE_WINS | Server authoritative | Always remote |
| MANUAL | Critical data | User decides |

## Conflict Status Flow

```
UNRESOLVED → (resolve) → RESOLVED_AUTO
UNRESOLVED → (resolve_manual) → RESOLVED_MANUAL
UNRESOLVED → (error) → FAILED
```

## Common Patterns

### Integration with Sync
```python
def sync_entity(local_entity, remote_entity):
    local_version = to_entity_version(local_entity)
    remote_version = to_entity_version(remote_entity)

    conflict = resolver.detect_conflict(local_version, remote_version)

    if conflict:
        result = resolver.resolve(conflict)
        return result.version
    else:
        # No conflict, use newer version
        if remote_version.vector_clock.happens_before(local_version.vector_clock):
            return local_version
        else:
            return remote_version
```

### CLI Integration
```python
@click.command()
def resolve_conflicts():
    conflicts = resolver.list_unresolved()

    for conflict in conflicts:
        print(format_conflict_summary(conflict))
        choice = click.prompt("Resolve? (y/n)")

        if choice.lower() == 'y':
            result = resolver.resolve(conflict)
            print(f"Resolved: {result.version.data}")
```

## Error Handling

```python
try:
    conflict = resolver.detect_conflict(local, remote)
    if conflict:
        result = resolver.resolve(conflict)
except ValueError as e:
    print(f"Invalid conflict resolution: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Configuration

### ~/.tracertm/config.yaml
```yaml
sync:
  conflict_strategy: last_write_wins
  auto_resolve: true
  backup_dir: ~/.tracertm/conflicts
  backup_retention_days: 30
```

## Performance Tips

1. Use content hashes for quick comparison
2. Index queries by entity_type and status
3. Clean up old backups periodically
4. Batch resolve conflicts when possible
5. Use appropriate strategy for workload

## Testing

```python
# Run tests
pytest tests/unit/storage/test_conflict_resolver.py -v

# With coverage
pytest tests/unit/storage/test_conflict_resolver.py --cov=tracertm.storage.conflict_resolver

# Type check
mypy src/tracertm/storage/conflict_resolver.py --strict
```

## Documentation

- [README](./CONFLICT_RESOLVER_README.md) - Architecture and overview
- [Usage Guide](./CONFLICT_RESOLVER_USAGE.md) - Detailed examples
- [CLI Integration](./CONFLICT_RESOLUTION_CLI_INTEGRATION.md) - Command implementations
