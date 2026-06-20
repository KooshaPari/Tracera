# Validation, Configuration & Feature Flags - Quick Reference

## UUID Validation

### Go
```go
import "backend/internal/validation"

validation.ValidateUUID(id)                 // Returns error if invalid
normalized := validation.NormalizeUUID(id)  // Lowercase + trim
validation.IsValidUUID(id)                  // Returns bool
validation.ValidateUUIDs(id1, id2, id3)     // Validate multiple
```

### Python
```python
from tracertm.validation import validate_uuid, normalize_uuid, is_valid_uuid

validate_uuid(id)                  # Raises ValueError if invalid
normalized = normalize_uuid(id)    # Lowercase + trim
is_valid_uuid(id)                  # Returns bool
```

## Feature Flags - CLI

```bash
./scripts/feature_flags.sh init                    # Initialize defaults
./scripts/feature_flags.sh enable <flag>           # Enable flag
./scripts/feature_flags.sh disable <flag>          # Disable flag
./scripts/feature_flags.sh get <flag>              # Check status
./scripts/feature_flags.sh set <flag> true|false   # Set explicitly
./scripts/feature_flags.sh list                    # List all flags
```

## Feature Flags - Code

### Go
```go
import "backend/internal/features"

flagStore := features.NewFlagStore(redisClient)
flagStore.InitializeDefaultFlags(ctx)
flagStore.IsEnabled(ctx, features.FlagNATSEvents)
flagStore.EnableFlag(ctx, "feature_name")
flagStore.ListFlags(ctx)
```

### Python
```python
from tracertm.infrastructure import FeatureFlagStore, FLAG_NATS_EVENTS

flag_store = FeatureFlagStore(redis_client)
await flag_store.initialize_default_flags()
await flag_store.is_enabled(FLAG_NATS_EVENTS)
await flag_store.enable_flag("feature_name")
await flag_store.list_flags()
```

## Configuration

```bash
# Load integration config
source .env.integration

# Validate all services
./scripts/validate_integration_config.sh

# Apply database constraints
alembic upgrade head
```

## Default Flags

| Flag | Default | Purpose |
|------|---------|---------|
| `nats_events` | ✓ | NATS event publishing |
| `cross_backend_calls` | ✓ | HTTP delegation |
| `shared_cache` | ✓ | Redis caching |
| `python_spec_analytics` | ✓ | Spec analytics service |
| `go_graph_analysis` | ✓ | Graph analysis service |
| `enhanced_logging` | ✗ | Debug logging |
| `metrics_collection` | ✓ | Metrics |
| `distributed_tracing` | ✓ | Tracing |

## Files

```
backend/internal/validation/id_validator.go
backend/internal/features/flags.go
src/tracertm/validation/id_validator.py
src/tracertm/infrastructure/feature_flags.py
scripts/feature_flags.sh
scripts/validate_integration_config.sh
.env.integration
alembic/versions/006_add_uuid_constraints.py
```

## Tests

```bash
# Go
cd backend && go test ./internal/validation/... -v
cd backend && go test ./internal/features/... -v

# Python
python -c "from tracertm.validation import generate_uuid, validate_uuid; u = generate_uuid(); validate_uuid(u); print('✓ OK')"
```

## Common Operations

```bash
# Setup
./scripts/feature_flags.sh init
alembic upgrade head

# Daily use
./scripts/feature_flags.sh enable new_feature
./scripts/feature_flags.sh list

# Debugging
redis-cli -u $REDIS_URL KEYS "feature:flag:*"
redis-cli -u $REDIS_URL GET "feature:flag:nats_events"
```

## Redis Key Pattern

```
feature:flag:<flag_name> = "true" | "false"
```

## UUID Format

```
Regex: ^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$
Example: 123e4567-e89b-12d3-a456-426614174000
```
