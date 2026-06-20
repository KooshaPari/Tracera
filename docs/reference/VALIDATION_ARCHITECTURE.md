# Validation, Configuration & Feature Flags - Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        TraceRTM System                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐              ┌──────────────────┐        │
│  │   Go Backend     │              │  Python Backend  │        │
│  │   (Port 8080)    │◄────────────►│   (Port 8000)   │        │
│  └────────┬─────────┘              └────────┬─────────┘        │
│           │                                 │                  │
│           ├─────────────┬───────────────────┤                  │
│           │             │                   │                  │
│  ┌────────▼────────┐    │          ┌───────▼────────┐         │
│  │   Validation    │    │          │   Validation   │         │
│  │   Layer         │    │          │   Layer        │         │
│  │                 │    │          │                │         │
│  │ ValidateUUID()  │    │          │ validate_uuid()│         │
│  │ NormalizeUUID() │    │          │ normalize_uuid()         │
│  │ IsValidUUID()   │    │          │ is_valid_uuid()│         │
│  └─────────────────┘    │          └────────────────┘         │
│                         │                                      │
│  ┌─────────────────┐    │          ┌────────────────┐         │
│  │  Feature Flags  │    │          │ Feature Flags  │         │
│  │  Store          │    │          │ Store          │         │
│  │                 │    │          │                │         │
│  │ IsEnabled()     │    │          │ is_enabled()   │         │
│  │ SetFlag()       │    │          │ set_flag()     │         │
│  │ ListFlags()     │    │          │ list_flags()   │         │
│  └────────┬────────┘    │          └────────┬───────┘         │
│           │             │                   │                  │
│           └─────────────┼───────────────────┘                  │
│                         │                                      │
└─────────────────────────┼──────────────────────────────────────┘
                          │
                          │
        ┌─────────────────▼─────────────────────────┐
        │          Shared Infrastructure            │
        ├───────────────────────────────────────────┤
        │                                           │
        │  ┌──────────────────────────────────┐    │
        │  │           Redis                  │    │
        │  │                                  │    │
        │  │  feature:flag:nats_events = true│    │
        │  │  feature:flag:shared_cache = true│   │
        │  │  feature:flag:enhanced_logging = │   │
        │  │                          false   │    │
        │  └──────────────────────────────────┘    │
        │                                           │
        │  ┌──────────────────────────────────┐    │
        │  │         PostgreSQL               │    │
        │  │                                  │    │
        │  │  items: CHECK (id ~ UUID_REGEX) │    │
        │  │  links: CHECK (id ~ UUID_REGEX) │    │
        │  │  projects: CHECK (...)           │    │
        │  └──────────────────────────────────┘    │
        │                                           │
        │  ┌──────────────────────────────────┐    │
        │  │      Configuration               │    │
        │  │                                  │    │
        │  │  .env.integration                │    │
        │  │  - DATABASE_URL                  │    │
        │  │  - REDIS_URL                     │    │
        │  │  - NATS_URL                      │    │
        │  │  - JWT_SECRET                    │    │
        │  └──────────────────────────────────┘    │
        │                                           │
        └───────────────────────────────────────────┘
                          │
                          │
        ┌─────────────────▼─────────────────────────┐
        │         Management Tools                  │
        ├───────────────────────────────────────────┤
        │                                           │
        │  ./scripts/feature_flags.sh               │
        │  - init, enable, disable, list            │
        │                                           │
        │  ./scripts/validate_integration_config.sh │
        │  - Health checks for all services         │
        │                                           │
        └───────────────────────────────────────────┘
```

## Data Flow

### UUID Validation Flow

```
User Request
    │
    ▼
API Endpoint
    │
    ├─► Validate UUID (Go/Python)
    │       │
    │       ├─► NormalizeUUID (lowercase, trim)
    │       │
    │       ├─► Regex Match
    │       │       │
    │       │       ├─► Valid ──► Continue
    │       │       │
    │       │       └─► Invalid ──► Return 400 Error
    │       │
    │       └─► Database Query
    │               │
    │               ├─► DB Constraint Check
    │               │       │
    │               │       ├─► Valid ──► Execute
    │               │       │
    │               │       └─► Invalid ──► Constraint Violation
    │               │
    │               └─► Return Result
    │
    └─► Response
```

### Feature Flag Check Flow

```
Application Startup
    │
    ▼
Initialize FlagStore
    │
    ├─► Connect to Redis
    │
    ├─► Initialize Default Flags
    │       │
    │       ├─► Check if flag exists
    │       │
    │       └─► Set default if missing
    │
    └─► Service Initialization
            │
            ├─► Check Flag: nats_events
            │       │
            │       ├─► Redis GET feature:flag:nats_events
            │       │
            │       └─► Enable/Disable NATS
            │
            ├─► Check Flag: shared_cache
            │       │
            │       └─► Enable/Disable Cache
            │
            └─► Start Services
```

### Configuration Loading Flow

```
Application Start
    │
    ▼
Load .env.integration
    │
    ├─► Parse environment variables
    │
    ├─► Validate required variables
    │       │
    │       ├─► DATABASE_URL ✓
    │       ├─► REDIS_URL ✓
    │       ├─► NATS_URL ✓
    │       └─► JWT_SECRET ✓
    │
    ├─► Test Connections
    │       │
    │       ├─► PostgreSQL
    │       ├─► Redis
    │       ├─► NATS
    │       └─► Neo4j
    │
    └─► Initialize Services
```

## Component Interaction Matrix

| Component | Go Validation | Python Validation | Feature Flags | Database | Redis |
|-----------|--------------|-------------------|---------------|----------|-------|
| **API Endpoint** | ✓ Uses | ✓ Uses | ✓ Checks | ✓ Queries | - |
| **Service Layer** | ✓ Uses | ✓ Uses | ✓ Checks | ✓ Queries | ✓ Stores flags |
| **Database Layer** | - | - | - | ✓ Enforces | - |
| **CLI Tools** | - | - | ✓ Manages | - | ✓ Direct access |
| **Tests** | ✓ Tests | ✓ Tests | ✓ Tests | ✓ Tests | ✓ Mock |

## Validation Layers

```
┌─────────────────────────────────────────────────┐
│          Layer 1: Application Layer             │
│  - Go: validation.ValidateUUID()                │
│  - Python: validate_uuid()                      │
│  - Fast rejection of invalid format             │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│          Layer 2: ORM/Query Layer               │
│  - UUID normalization before queries            │
│  - Type safety in query builders                │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│       Layer 3: Database Constraints             │
│  - CHECK constraint on id columns               │
│  - Regex validation in PostgreSQL               │
│  - Last line of defense                         │
└─────────────────────────────────────────────────┘
```

## Feature Flag Decision Tree

```
Feature Flag Check
    │
    ├─► Flag exists in Redis?
    │       │
    │       ├─► Yes ──► Return value (true/false)
    │       │
    │       └─► No ──► Return default (false)
    │
    └─► Use flag value
            │
            ├─► true ──► Enable feature
            │
            └─► false ──► Disable feature
```

## Configuration Hierarchy

```
Environment Variables
    │
    ├─► .env (local development)
    │
    ├─► .env.integration (shared config)
    │
    ├─► .env.production (production)
    │
    └─► System Environment (deployment)
            │
            └─► Application loads in order:
                1. System env vars (highest priority)
                2. .env.production
                3. .env.integration
                4. .env (lowest priority)
```

## Redis Key Organization

```
Redis Keys
│
├─► feature:flag:* (Feature Flags)
│   ├─► feature:flag:nats_events
│   ├─► feature:flag:cross_backend_calls
│   ├─► feature:flag:shared_cache
│   └─► feature:flag:enhanced_logging
│
├─► go:* (Go backend namespace)
│   └─► (future use)
│
└─► python:* (Python backend namespace)
    └─► (future use)
```

## Database Schema Enhancement

```sql
-- Before (vulnerable to invalid UUIDs)
CREATE TABLE items (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL
);

-- After (enforced validation)
CREATE TABLE items (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    CONSTRAINT items_id_uuid_check
    CHECK (id::text ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
);
```

## Error Handling Flow

```
Invalid UUID Input
    │
    ▼
Application Validation
    │
    ├─► Normalize UUID
    │
    ├─► Regex Match
    │       │
    │       └─► Fail ──► Return 400 Bad Request
    │               │
    │               └─► {
    │                     "error": "Invalid UUID format",
    │                     "details": "UUID must match pattern...",
    │                     "received": "user-input"
    │                   }
    │
    └─► If passes app validation but fails DB constraint
            │
            └─► Database Error ──► Return 500 Internal Error
                    │
                    └─► {
                          "error": "Database constraint violation",
                          "details": "UUID format validation failed"
                        }
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────┐
│              Production Environment             │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────┐         ┌──────────────┐     │
│  │ Go Backend   │         │ Python Backend│    │
│  │ Container    │         │  Container    │    │
│  │              │         │               │    │
│  │ - validation │         │ - validation  │    │
│  │ - features   │         │ - features    │    │
│  └──────┬───────┘         └──────┬────────┘    │
│         │                        │             │
│         └────────┬───────────────┘             │
│                  │                             │
│         ┌────────▼─────────┐                   │
│         │  Shared Services │                   │
│         ├──────────────────┤                   │
│         │ - Redis (Flags)  │                   │
│         │ - PostgreSQL     │                   │
│         │ - NATS           │                   │
│         └──────────────────┘                   │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Performance Characteristics

| Operation | Latency | Notes |
|-----------|---------|-------|
| UUID Validation | < 1μs | Regex match, CPU-bound |
| UUID Normalization | < 1μs | String operations |
| Flag Check (Redis) | ~1ms | Network + Redis GET |
| Flag Set (Redis) | ~1ms | Network + Redis SET |
| DB Constraint Check | ~0.1ms | Part of INSERT/UPDATE |
| Config Load | ~10ms | One-time at startup |

## Security Considerations

```
┌─────────────────────────────────────────────────┐
│              Security Layers                    │
├─────────────────────────────────────────────────┤
│                                                 │
│  1. Input Validation                            │
│     - UUID format enforcement                   │
│     - Prevents injection attacks                │
│                                                 │
│  2. Configuration Security                      │
│     - Secrets in environment variables          │
│     - No credentials in code                    │
│     - .env files in .gitignore                 │
│                                                 │
│  3. Feature Flag Security                       │
│     - Redis authentication required             │
│     - Future: RBAC for flag changes            │
│     - Audit logging recommended                 │
│                                                 │
│  4. Database Security                           │
│     - Constraints prevent invalid data          │
│     - Connection pooling limits                 │
│     - SSL/TLS for connections                   │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Monitoring & Observability

```
Metrics to Track:
│
├─► UUID Validation
│   ├─► validation_attempts_total
│   ├─► validation_failures_total
│   └─► validation_latency_seconds
│
├─► Feature Flags
│   ├─► flag_checks_total (by flag name)
│   ├─► flag_changes_total (by flag name)
│   └─► flag_check_latency_seconds
│
└─► Configuration
    ├─► config_load_duration_seconds
    ├─► service_health_checks_total
    └─► service_health_check_failures_total
```

## Future Enhancements

```
Phase 2: Advanced Features
│
├─► Feature Flags
│   ├─► Percentage-based rollouts
│   ├─► User/team-specific overrides
│   ├─► A/B testing framework
│   └─► Flag change audit log
│
├─► Validation
│   ├─► Custom validator registry
│   ├─► Validation middleware
│   ├─► Request/response schemas
│   └─► OpenAPI integration
│
└─► Configuration
    ├─► Hot-reload capabilities
    ├─► Configuration versioning
    ├─► Environment-specific overrides
    └─► Encrypted secrets management
```
