# Schema Validation, Configuration & Feature Flags

Complete implementation guide for validation, shared configuration, and feature flag infrastructure.

## Overview

This implementation provides:
1. UUID validation in both Go and Python backends
2. Database-level UUID constraints
3. Shared integration configuration
4. Feature flag management via Redis
5. CLI tools for managing feature flags

## Files Created

### Validation Layer

#### Go Backend
- `/backend/internal/validation/id_validator.go` - UUID validation utilities
- `/backend/internal/validation/id_validator_test.go` - Comprehensive tests

#### Python Backend
- `/src/tracertm/validation/__init__.py` - Module exports
- `/src/tracertm/validation/id_validator.py` - UUID validation utilities
- `/tests/unit/validation/test_id_validator.py` - Comprehensive tests

### Database Constraints
- `/alembic/versions/006_add_uuid_constraints.py` - Migration to add UUID format checks

### Configuration
- `/.env.integration` - Shared configuration for both backends
- `/scripts/validate_integration_config.sh` - Configuration validation script

### Feature Flags

#### Go Backend
- `/backend/internal/features/flags.go` - Feature flag store
- `/backend/internal/features/flags_test.go` - Comprehensive tests

#### Python Backend
- `/src/tracertm/infrastructure/feature_flags.py` - Feature flag store
- `/src/tracertm/infrastructure/__init__.py` - Updated exports

#### Management
- `/scripts/feature_flags.sh` - CLI tool for managing flags

## Usage

### 1. UUID Validation

#### Go
```go
import "backend/internal/validation"

// Validate UUID
if err := validation.ValidateUUID(id); err != nil {
    return fmt.Errorf("invalid UUID: %w", err)
}

// Normalize UUID
normalized := validation.NormalizeUUID(id)

// Check validity (boolean)
if !validation.IsValidUUID(id) {
    return errors.New("invalid UUID")
}

// Validate multiple UUIDs
if err := validation.ValidateUUIDs(id1, id2, id3); err != nil {
    return err
}
```

#### Python
```python
from tracertm.validation import validate_uuid, normalize_uuid, is_valid_uuid

# Validate UUID (raises ValueError if invalid)
try:
    validate_uuid(id_str)
except ValueError as e:
    print(f"Invalid UUID: {e}")

# Normalize UUID
normalized = normalize_uuid(id_str)

# Check validity (boolean)
if not is_valid_uuid(id_str):
    raise ValueError("Invalid UUID")

# Generate new UUID
new_id = generate_uuid()
```

### 2. Database Migration

Apply UUID constraints:
```bash
# Run migration
cd /path/to/project
alembic upgrade head

# Verify constraints
psql $DATABASE_URL -c "\d items"
# Should show: CHECK (id ~ '^[0-9a-f]{8}-...')
```

### 3. Configuration Management

#### Load Integration Config
```bash
# Load into environment
source .env.integration

# Validate configuration
./scripts/validate_integration_config.sh
```

#### Expected Output
```
======================================================================
TraceRTM Integration Configuration Validation
======================================================================

Infrastructure Checks:
----------------------------------------------------------------------
Checking PostgreSQL... ✓ OK
Checking NATS... ✓ OK
Checking Redis... ✓ OK
Checking Neo4j... ✓ OK

Backend Service Checks:
----------------------------------------------------------------------
Checking Go Backend... ✓ OK
Checking Python Backend... ✓ OK

Configuration Validation:
----------------------------------------------------------------------
Checking DATABASE_URL... ✓ Set
Checking REDIS_URL... ✓ Set
Checking NATS_URL... ✓ Set
...

======================================================================
All integration checks passed!
```

### 4. Feature Flags

#### CLI Usage
```bash
# Initialize default flags
./scripts/feature_flags.sh init

# Enable a flag
./scripts/feature_flags.sh enable nats_events

# Disable a flag
./scripts/feature_flags.sh disable enhanced_logging

# Get flag status
./scripts/feature_flags.sh get nats_events

# Set flag explicitly
./scripts/feature_flags.sh set cross_backend_calls true

# List all flags
./scripts/feature_flags.sh list
```

#### Go Code
```go
import (
    "context"
    "backend/internal/features"
    "github.com/redis/go-redis/v9"
)

// Create feature flag store
redisClient := redis.NewClient(&redis.Options{
    Addr: "localhost:6379",
})
flagStore := features.NewFlagStore(redisClient)

// Initialize defaults
ctx := context.Background()
if err := flagStore.InitializeDefaultFlags(ctx); err != nil {
    log.Fatal(err)
}

// Check if feature is enabled
if flagStore.IsEnabled(ctx, features.FlagNATSEvents) {
    // Use NATS events
}

// Enable/disable flags
flagStore.EnableFlag(ctx, features.FlagCrossBackendCalls)
flagStore.DisableFlag(ctx, features.FlagEnhancedLogging)

// List all flags
flags, err := flagStore.ListFlags(ctx)
for name, enabled := range flags {
    fmt.Printf("%s: %v\n", name, enabled)
}
```

#### Python Code
```python
from redis.asyncio import Redis
from tracertm.infrastructure import (
    FeatureFlagStore,
    FLAG_NATS_EVENTS,
    FLAG_CROSS_BACKEND_CALLS
)

# Create feature flag store
redis_client = Redis.from_url("redis://localhost:6379")
flag_store = FeatureFlagStore(redis_client)

# Initialize defaults
await flag_store.initialize_default_flags()

# Check if feature is enabled
if await flag_store.is_enabled(FLAG_NATS_EVENTS):
    # Use NATS events
    pass

# Enable/disable flags
await flag_store.enable_flag(FLAG_CROSS_BACKEND_CALLS)
await flag_store.disable_flag("enhanced_logging")

# List all flags
flags = await flag_store.list_flags()
for name, enabled in flags.items():
    print(f"{name}: {enabled}")
```

## Default Feature Flags

| Flag | Default | Description |
|------|---------|-------------|
| `nats_events` | `true` | Enable NATS event publishing |
| `cross_backend_calls` | `true` | Enable HTTP delegation between backends |
| `shared_cache` | `true` | Enable Redis caching |
| `python_spec_analytics` | `true` | Use Python spec analytics service |
| `go_graph_analysis` | `true` | Use Go graph analysis service |
| `enhanced_logging` | `false` | Enable detailed debug logging |
| `metrics_collection` | `true` | Enable metrics collection |
| `distributed_tracing` | `true` | Enable distributed tracing |

## Testing

### Run Go Tests
```bash
cd backend
go test ./internal/validation/... -v
go test ./internal/features/... -v
```

### Run Python Tests
```bash
# Activate virtual environment
source .venv/bin/activate

# Run validation tests
pytest tests/unit/validation/ -v

# Run with coverage
pytest tests/unit/validation/ --cov=tracertm.validation --cov-report=term-missing
```

### Test Database Constraints
```sql
-- Should succeed
INSERT INTO items (id, name) VALUES ('123e4567-e89b-12d3-a456-426614174000', 'Test');

-- Should fail with constraint violation
INSERT INTO items (id, name) VALUES ('invalid-uuid', 'Test');
-- ERROR: new row for relation "items" violates check constraint "items_id_uuid_check"
```

## Integration Patterns

### Backend Initialization
```go
// Go backend startup
func main() {
    // Initialize Redis
    redisClient := redis.NewClient(&redis.Options{
        Addr: os.Getenv("REDIS_URL"),
    })

    // Initialize feature flags
    flagStore := features.NewFlagStore(redisClient)
    ctx := context.Background()
    if err := flagStore.InitializeDefaultFlags(ctx); err != nil {
        log.Fatal(err)
    }

    // Use flags to configure services
    if flagStore.IsEnabled(ctx, features.FlagNATSEvents) {
        // Initialize NATS
    }

    // ... rest of setup
}
```

```python
# Python backend startup
async def startup():
    # Initialize Redis
    redis_client = Redis.from_url(os.getenv("REDIS_URL"))

    # Initialize feature flags
    flag_store = FeatureFlagStore(redis_client)
    await flag_store.initialize_default_flags()

    # Use flags to configure services
    if await flag_store.is_enabled(FLAG_NATS_EVENTS):
        # Initialize NATS
        pass

    # ... rest of setup
```

## Success Criteria

✅ UUID validation enforced in both backends
✅ Database constraints prevent invalid UUIDs
✅ `.env.integration` loads correctly
✅ Validation script passes all checks
✅ Feature flags readable/writable from both backends
✅ CLI tool works for flag management
✅ Comprehensive test coverage for all modules
✅ Documentation complete

## Troubleshooting

### Configuration Validation Fails
```bash
# Check if services are running
docker-compose ps

# Test individual connections
psql $DATABASE_URL -c "SELECT 1"
redis-cli -u $REDIS_URL PING
```

### Feature Flags Not Persisting
```bash
# Check Redis connection
redis-cli -u $REDIS_URL KEYS "feature:flag:*"

# Manually set a flag to test
redis-cli -u $REDIS_URL SET "feature:flag:test" "true"
redis-cli -u $REDIS_URL GET "feature:flag:test"
```

### Database Constraints Failing
```sql
-- Check existing constraints
SELECT constraint_name, check_clause
FROM information_schema.check_constraints
WHERE constraint_name LIKE '%uuid%';

-- Drop and recreate if needed
ALTER TABLE items DROP CONSTRAINT IF EXISTS items_id_uuid_check;
```

## Next Steps

1. Integrate validation into API endpoints
2. Add feature flag checks to service initialization
3. Create monitoring dashboard for flag status
4. Add audit logging for flag changes
5. Implement gradual rollout capabilities
