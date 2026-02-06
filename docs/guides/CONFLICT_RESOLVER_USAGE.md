# Conflict Resolver Usage Guide

This guide demonstrates how to use the TraceRTM conflict resolution system for handling sync conflicts between local and remote changes.

## Overview

The conflict resolver implements multiple strategies for handling conflicts that arise when the same entity is modified both locally and remotely:

- **LAST_WRITE_WINS** (default): Uses the version with the newest timestamp
- **LOCAL_WINS**: Always prefers local changes
- **REMOTE_WINS**: Always prefers remote changes
- **MANUAL**: Creates conflict files for user review and manual merging

## Basic Usage

```python
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tracertm.storage import (
    ConflictResolver,
    ConflictStrategy,
    EntityVersion,
    VectorClock,
)

# Setup database session
engine = create_engine("sqlite:///~/.tracertm/tracertm.db")
Session = sessionmaker(bind=engine)
session = Session()

# Create resolver instance
resolver = ConflictResolver(
    session=session,
    backup_dir=Path.home() / ".tracertm" / "conflicts",
    default_strategy=ConflictStrategy.LAST_WRITE_WINS,
)
```

## Detecting Conflicts

```python
from tracertm.storage import EntityVersion, VectorClock

# Local version (modified by this client)
local_version = EntityVersion(
    entity_id="item-123",
    entity_type="item",
    data={
        "title": "Feature Implementation",
        "status": "in_progress",
        "priority": "high",
    },
    vector_clock=VectorClock(
        client_id="cli-laptop-001",
        version=3,
        timestamp=datetime(2024, 1, 15, 14, 30, tzinfo=UTC),
        parent_version=2,
    ),
    content_hash="abc123def456",
)

# Remote version (modified by another client or web interface)
remote_version = EntityVersion(
    entity_id="item-123",
    entity_type="item",
    data={
        "title": "Feature Implementation",
        "status": "done",
        "owner": "user-456",
    },
    vector_clock=VectorClock(
        client_id="web-session-789",
        version=3,
        timestamp=datetime(2024, 1, 15, 14, 35, tzinfo=UTC),
        parent_version=2,
    ),
    content_hash="xyz789abc012",
)

# Detect conflict
conflict = resolver.detect_conflict(local_version, remote_version)

if conflict:
    print(f"Conflict detected: {conflict.id}")
    print(f"Local version: {conflict.local_version.vector_clock.version}")
    print(f"Remote version: {conflict.remote_version.vector_clock.version}")
else:
    print("No conflict - changes are sequential")
```

## Resolution Strategies

### 1. Last-Write-Wins (Default)

Uses the version with the newest timestamp. If timestamps are equal, uses the higher version number.

```python
# Resolve using default strategy
result = resolver.resolve(conflict)

print(f"Winner: {'local' if result.version == local_version else 'remote'}")
print(f"Resolved data: {result.version.data}")

# Update database with winning version
# ... your update logic here
```

### 2. Local Wins

Always prefers local changes, regardless of timestamps.

```python
result = resolver.resolve(conflict, strategy=ConflictStrategy.LOCAL_WINS)

# Local changes are always kept
assert result.version == conflict.local_version
```

### 3. Remote Wins

Always prefers remote changes, useful when the server is the source of truth.

```python
result = resolver.resolve(conflict, strategy=ConflictStrategy.REMOTE_WINS)

# Remote changes are always kept
assert result.version == conflict.remote_version
```

### 4. Manual Resolution

For complex conflicts requiring user intervention:

```python
# Present conflict to user
from tracertm.storage import format_conflict_summary, compare_versions

print(format_conflict_summary(conflict))

# Show differences
diff = compare_versions(conflict.local_version, conflict.remote_version)
print(f"Added fields: {diff['added']}")
print(f"Removed fields: {diff['removed']}")
print(f"Modified fields: {diff['modified']}")

# User provides merged data
merged_data = {
    "title": "Feature Implementation",  # Keep original
    "status": "done",                   # From remote
    "priority": "high",                 # From local
    "owner": "user-456",                # From remote
}

# Resolve manually
result = resolver.resolve_manual(
    conflict=conflict,
    merged_data=merged_data,
    merged_by="user-123",
)

print(f"Merged version: {result.version.vector_clock.version}")
```

## Working with Backups

The resolver automatically creates backups of conflicting versions:

```python
from tracertm.storage import ConflictBackup

# Create backup manager
backup_mgr = ConflictBackup(Path.home() / ".tracertm" / "conflicts")

# List all backups
backups = backup_mgr.list_backups()
for backup in backups:
    print(f"Conflict: {backup['conflict_id']}")
    print(f"Entity: {backup['entity_type']} {backup['entity_id']}")
    print(f"Detected: {backup['detected_at']}")
    print(f"Backup path: {backup['backup_path']}")
    print()

# Load a specific backup
backup_path = Path(backups[0]['backup_path'])
versions = backup_mgr.load_backup(backup_path)

if versions:
    local, remote = versions
    print(f"Local data: {local.data}")
    print(f"Remote data: {remote.data}")

# Delete old backups (optional)
backup_mgr.delete_backup(backup_path)
```

## Querying Conflicts

### List Unresolved Conflicts

```python
# All unresolved conflicts
unresolved = resolver.list_unresolved()
print(f"Total unresolved: {len(unresolved)}")

# Filter by entity type
item_conflicts = resolver.list_unresolved(entity_type="item")
project_conflicts = resolver.list_unresolved(entity_type="project")
```

### Get Conflict Statistics

```python
stats = resolver.get_conflict_stats()

print(f"Total conflicts: {stats['total']}")
print(f"By status: {stats['by_status']}")
print(f"By entity type: {stats['by_entity_type']}")

# Example output:
# Total conflicts: 15
# By status: {'unresolved': 3, 'resolved_auto': 10, 'resolved_manual': 2}
# By entity type: {'item': 12, 'project': 2, 'link': 1}
```

### Get Specific Conflict

```python
conflict = resolver.get_conflict("conflict_item-123_1705329600")

if conflict:
    print(f"Status: {conflict.status.value}")
    print(f"Strategy: {conflict.resolution_strategy}")
    print(f"Resolved at: {conflict.resolved_at}")
    print(f"Backup path: {conflict.backup_path}")
```

## Integration with Sync Engine

The conflict resolver is designed to integrate with the sync engine:

```python
from tracertm.storage import SyncEngine, ConflictResolver

class SyncEngineWithConflicts:
    def __init__(self, session, api_client, resolver):
        self.session = session
        self.api_client = api_client
        self.resolver = resolver

    def sync_item(self, local_item, remote_item):
        """Sync an item, handling conflicts if they occur."""

        # Convert to EntityVersion objects
        local_version = self._to_entity_version(local_item)
        remote_version = self._to_entity_version(remote_item)

        # Check for conflicts
        conflict = self.resolver.detect_conflict(local_version, remote_version)

        if conflict:
            # Resolve based on configured strategy
            result = self.resolver.resolve(conflict)

            # Apply winning version
            self._apply_version(result.version)

            return {
                "status": "conflict_resolved",
                "strategy": result.strategy_used.value,
                "version": result.version.vector_clock.version,
            }
        else:
            # No conflict, apply newer version
            if remote_version.vector_clock.happens_before(local_version.vector_clock):
                return {"status": "local_newer", "action": "push"}
            else:
                self._apply_version(remote_version)
                return {"status": "remote_newer", "action": "pull"}

    def _to_entity_version(self, item):
        """Convert item to EntityVersion."""
        # Implementation depends on your data model
        pass

    def _apply_version(self, version):
        """Apply winning version to database."""
        # Implementation depends on your data model
        pass
```

## CLI/TUI Integration Example

```python
import click
from rich.console import Console
from rich.table import Table

console = Console()

@click.command()
@click.option('--strategy', type=click.Choice(['auto', 'local', 'remote', 'manual']),
              default='auto', help='Conflict resolution strategy')
def resolve_conflicts(strategy):
    """Resolve pending sync conflicts."""

    # Setup
    session = get_session()
    resolver = ConflictResolver(session)

    # Get unresolved conflicts
    conflicts = resolver.list_unresolved()

    if not conflicts:
        console.print("[green]No conflicts to resolve![/green]")
        return

    console.print(f"[yellow]Found {len(conflicts)} conflicts[/yellow]\n")

    # Display conflicts
    table = Table(title="Pending Conflicts")
    table.add_column("ID", style="cyan")
    table.add_column("Entity Type", style="magenta")
    table.add_column("Entity ID", style="green")
    table.add_column("Local Version", style="blue")
    table.add_column("Remote Version", style="blue")

    for conflict in conflicts:
        table.add_row(
            conflict.id,
            conflict.entity_type,
            conflict.entity_id,
            str(conflict.local_version.vector_clock.version),
            str(conflict.remote_version.vector_clock.version),
        )

    console.print(table)
    console.print()

    # Resolve conflicts
    strategy_map = {
        'auto': ConflictStrategy.LAST_WRITE_WINS,
        'local': ConflictStrategy.LOCAL_WINS,
        'remote': ConflictStrategy.REMOTE_WINS,
        'manual': ConflictStrategy.MANUAL,
    }

    for conflict in conflicts:
        if strategy == 'manual':
            # Interactive resolution
            resolve_manual_interactive(resolver, conflict)
        else:
            # Automatic resolution
            result = resolver.resolve(conflict, strategy_map[strategy])
            console.print(
                f"[green]✓[/green] Resolved {conflict.id} using {strategy} strategy"
            )

def resolve_manual_interactive(resolver, conflict):
    """Interactively resolve a conflict."""
    console.print(f"\n[bold]Conflict: {conflict.entity_id}[/bold]")

    # Show versions
    console.print("\n[cyan]Local version:[/cyan]")
    console.print_json(data=conflict.local_version.data)

    console.print("\n[magenta]Remote version:[/magenta]")
    console.print_json(data=conflict.remote_version.data)

    # Show diff
    diff = compare_versions(conflict.local_version, conflict.remote_version)
    if diff['added']:
        console.print(f"\n[green]Added: {', '.join(diff['added'])}[/green]")
    if diff['removed']:
        console.print(f"[red]Removed: {', '.join(diff['removed'])}[/red]")
    if diff['modified']:
        console.print(f"[yellow]Modified: {', '.join(diff['modified'])}[/yellow]")

    # Get user input
    choice = click.prompt(
        "\nChoose resolution",
        type=click.Choice(['local', 'remote', 'merge']),
    )

    if choice == 'merge':
        # Manual merge (simplified - real implementation would be more interactive)
        merged_data = dict(conflict.local_version.data)
        merged_data.update(conflict.remote_version.data)
        result = resolver.resolve_manual(conflict, merged_data)
    elif choice == 'local':
        result = resolver.resolve(conflict, ConflictStrategy.LOCAL_WINS)
    else:
        result = resolver.resolve(conflict, ConflictStrategy.REMOTE_WINS)

    console.print(f"[green]✓ Resolved {conflict.id}[/green]")

if __name__ == '__main__':
    resolve_conflicts()
```

## Best Practices

1. **Choose the Right Strategy**:
   - Use `LAST_WRITE_WINS` for most scenarios (good default)
   - Use `LOCAL_WINS` for offline-first workflows where local changes are priority
   - Use `REMOTE_WINS` when server is authoritative source of truth
   - Use `MANUAL` for important data that requires human review

2. **Monitor Conflicts**:
   - Regularly check `get_conflict_stats()` to monitor conflict rate
   - High conflict rate may indicate issues with sync frequency or client clocks

3. **Backup Management**:
   - Backups are automatically created before resolution
   - Periodically clean up old backups to save disk space
   - Consider archiving backups for audit trail

4. **Vector Clocks**:
   - Ensure consistent `client_id` per device/session
   - Increment version on every local change
   - Track parent_version for causality

5. **Testing**:
   - Test conflict scenarios in development
   - Verify resolution strategies work as expected
   - Check that backups are created correctly

## Error Handling

```python
from sqlalchemy.exc import SQLAlchemyError

try:
    conflict = resolver.detect_conflict(local, remote)
    if conflict:
        result = resolver.resolve(conflict)
        # Apply result...
except SQLAlchemyError as e:
    logger.error(f"Database error during conflict resolution: {e}")
    # Handle database errors
except ValueError as e:
    logger.error(f"Invalid conflict resolution: {e}")
    # Handle validation errors
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    # Handle unexpected errors
```

## Configuration

Configure conflict resolution behavior in `~/.tracertm/config.yaml`:

```yaml
sync:
  conflict_strategy: last_write_wins  # last_write_wins, local_wins, remote_wins, manual
  backup_dir: ~/.tracertm/conflicts
  auto_resolve: true  # Auto-resolve conflicts during sync
  backup_retention_days: 30  # Delete backups older than 30 days
```
