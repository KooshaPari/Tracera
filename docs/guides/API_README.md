# TraceRTM API Client

This module provides HTTP client functionality for TraceRTM's sync operations with the backend API.

## Components

### Main Modules

1. **sync_client.py** - HTTP API client for sync operations
   - `ApiClient` - Async HTTP client with retry logic
   - `ApiConfig` - Configuration dataclass
   - Error classes for different failure modes

2. **client.py** - Local database client (existing)
   - `TraceRTMClient` - Direct database access for AI agents

## Usage

### Basic Configuration

The API client can be configured via `~/.tracertm/config.yaml`:

```yaml
# API configuration
api_url: https://api.tracertm.io
api_token: your-jwt-token-here
api_timeout: 30.0
api_max_retries: 3

# Sync settings
sync_enabled: true
sync_interval_seconds: 300
sync_conflict_strategy: last_write_wins
```

### Python API

#### Creating a Client

```python
from tracertm.api import ApiClient, ApiConfig

# Option 1: Use configuration from ConfigManager
async with ApiClient() as client:
    status = await client.health_check()
    print(f"API healthy: {status}")

# Option 2: Explicit configuration
config = ApiConfig(
    base_url="https://api.tracertm.io",
    token="your-token",
    timeout=30.0,
    max_retries=3,
)

async with ApiClient(config) as client:
    # Use client
    pass
```

#### Upload Local Changes

```python
from tracertm.api import ApiClient, Change, SyncOperation
from datetime import datetime

changes = [
    Change(
        entity_type="item",
        entity_id="item-001",
        operation=SyncOperation.CREATE,
        data={"title": "New Feature", "status": "todo"},
        version=1,
    )
]

async with ApiClient() as client:
    result = await client.upload_changes(changes)
    print(f"Applied: {result.applied}")
    print(f"Conflicts: {result.conflicts}")
```

#### Download Remote Changes

```python
from datetime import datetime, timedelta

since = datetime.utcnow() - timedelta(hours=1)

async with ApiClient() as client:
    changes = await client.download_changes(since)
    for change in changes:
        print(f"{change.operation}: {change.entity_id}")
```

#### Full Bidirectional Sync

```python
from tracertm.api import ConflictStrategy

async with ApiClient() as client:
    upload_result, remote_changes = await client.full_sync(
        local_changes=my_changes,
        last_sync=last_sync_timestamp,
        conflict_strategy=ConflictStrategy.LAST_WRITE_WINS,
    )
```

## Error Handling

The client provides specific exception types for different failure modes:

```python
from tracertm.api import (
    ApiError,           # Base exception
    NetworkError,       # Network/connection issues
    AuthenticationError,  # Authentication failures
    RateLimitError,     # Rate limiting
    ConflictError,      # Sync conflicts
)

async with ApiClient() as client:
    try:
        result = await client.upload_changes(changes)
    except AuthenticationError as e:
        print(f"Auth failed: {e}")
        # Handle token refresh
    except RateLimitError as e:
        print(f"Rate limited, retry after: {e.retry_after}s")
        # Wait and retry
    except ConflictError as e:
        print(f"Conflicts: {len(e.conflicts)}")
        # Resolve conflicts
    except NetworkError as e:
        print(f"Network error: {e}")
        # Queue for later retry
```

## Retry Logic

The client implements automatic retry with exponential backoff:

- **Max retries**: Configurable (default: 3)
- **Backoff**: Exponential with jitter
- **Rate limiting**: Respects `Retry-After` headers
- **No retry**: Authentication errors (401)

## Conflict Resolution

When conflicts occur during sync, choose a resolution strategy:

- `LAST_WRITE_WINS` - Use the most recent version (default)
- `LOCAL_WINS` - Prefer local changes
- `REMOTE_WINS` - Prefer server changes
- `MANUAL` - Raise exception for manual resolution

```python
from tracertm.api import ConflictStrategy

# Automatic resolution
result, changes = await client.full_sync(
    local_changes=changes,
    conflict_strategy=ConflictStrategy.LOCAL_WINS,
)

# Manual resolution
try:
    result = await client.upload_changes(changes)
except ConflictError as e:
    for conflict in e.conflicts:
        # Analyze conflict
        merged_data = merge_logic(conflict.local_data, conflict.remote_data)

        # Resolve
        await client.resolve_conflict(
            conflict.conflict_id,
            ConflictStrategy.MANUAL,
            merged_data=merged_data,
        )
```

## Data Models

### Change

Represents a local or remote change to sync:

```python
@dataclass
class Change:
    entity_type: str        # "project", "item", "link"
    entity_id: str         # Entity ID
    operation: SyncOperation  # CREATE, UPDATE, DELETE
    data: dict[str, Any]   # Change payload
    version: int           # Version number
    timestamp: datetime    # When change occurred
    client_id: str | None  # Client that made change
```

### Conflict

Represents a sync conflict:

```python
@dataclass
class Conflict:
    conflict_id: str
    entity_type: str
    entity_id: str
    local_version: int
    remote_version: int
    local_data: dict[str, Any]
    remote_data: dict[str, Any]
    timestamp: datetime
```

### UploadResult

Result of uploading changes:

```python
@dataclass
class UploadResult:
    applied: list[str]          # Successfully applied entity IDs
    conflicts: list[Conflict]   # Detected conflicts
    server_time: datetime       # Server timestamp
    errors: list[dict]          # Errors
```

### SyncStatus

Current sync state:

```python
@dataclass
class SyncStatus:
    last_sync: datetime | None   # Last successful sync
    pending_changes: int         # Number of pending changes
    online: bool                 # Connection status
    server_time: datetime | None # Server time
    conflicts_pending: int       # Unresolved conflicts
```

## API Endpoints

The client communicates with these backend endpoints:

- `GET /api/health` - Health check
- `POST /api/sync/upload` - Upload local changes
- `GET /api/sync/changes` - Download remote changes
- `POST /api/sync/resolve` - Resolve conflicts
- `GET /api/sync/status` - Get sync status

## Examples

See `examples/sync_api_usage.py` for complete examples.

## Testing

Run the test suite:

```bash
# Unit tests
pytest tests/unit/api/test_sync_client.py -v

# With coverage
pytest tests/unit/api/test_sync_client.py --cov=src/tracertm/api --cov-report=html
```

## Architecture

The sync client follows these principles:

1. **Async-first**: Uses `httpx.AsyncClient` for non-blocking I/O
2. **Retry resilience**: Automatic retries with exponential backoff
3. **Error handling**: Specific exceptions for different failure modes
4. **Configuration**: Centralized via ConfigManager or explicit ApiConfig
5. **Context manager**: Proper resource cleanup via async context manager

## Integration

The sync client integrates with:

- **ConfigManager**: Reads API settings from `~/.tracertm/config.yaml`
- **LocalStorageManager**: Syncs SQLite database with backend
- **MarkdownParser**: Syncs markdown files
- **SyncEngine**: Coordinates bidirectional sync

## Security

- Uses JWT tokens for authentication
- Supports HTTPS with certificate verification
- Never stores tokens in logs
- Client IDs for audit trails

## Performance

- Connection pooling via httpx
- Configurable timeouts
- Batch operations support
- Delta sync (only changed entities)
