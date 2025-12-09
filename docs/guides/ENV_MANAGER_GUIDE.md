# Environment Manager Guide

This guide explains how to use the unified environment management system across all TraceRTM codebases.

## Overview

TraceRTM now includes modern environment managers for all codebases:
- **Go Backend**: `backend/internal/env/env.go`
- **Python CLI**: `cli/tracertm/env_manager.py`
- **TypeScript Frontend**: `frontend/packages/env-manager/src/index.ts`

## Setup

### 1. Copy Environment Template

```bash
cp .env.template .env
```

### 2. Fill in Your Values

Edit `.env` with your configuration:

```bash
# Application
APP_ENV=development
APP_DEBUG=true
APP_PORT=8080

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/tracertm

# Cache
REDIS_URL=redis://default:password@host:port
UPSTASH_REDIS_REST_URL=https://your-instance.upstash.io
UPSTASH_REDIS_REST_TOKEN=your_token

# ... other services
```

## Backend (Go)

### Basic Usage

```go
import "tracertm/backend/internal/env"

// Create manager
envMgr := env.New()
envMgr.Load()

// Get string
apiUrl := envMgr.Get("API_URL")

// Get required
dbUrl, err := envMgr.GetRequired("DATABASE_URL")

// Get with default
port := envMgr.GetOrDefault("PORT", "8080")

// Get typed values
timeout, err := envMgr.GetInt("TIMEOUT")
debug := envMgr.GetBoolOrDefault("DEBUG", false)
duration := envMgr.GetDurationOrDefault("CACHE_TTL", 1*time.Hour)
```

### Configuration Loading

```go
import "tracertm/backend/internal/config"

// Load with environment manager
cfg, err := config.LoadWithEnvManager()
if err != nil {
    log.Fatal(err)
}
```

## CLI (Python)

### Basic Usage

```python
from tracertm.env_manager import EnvManager

# Create manager
env_mgr = EnvManager()

# Get string
api_url = env_mgr.get("API_URL")

# Get required
db_url = env_mgr.get_required("DATABASE_URL")

# Get with default
port = env_mgr.get("PORT", "8080")

# Get typed values
timeout = env_mgr.get_int("TIMEOUT", 30)
debug = env_mgr.get_bool("DEBUG", False)
items = env_mgr.get_list("ITEMS", separator=",")
```

### Configuration Loading

```python
from tracertm.config_loader import load_cli_config, validate_cli_config

# Load configuration
config = load_cli_config()

# Validate
validate_cli_config(config)

# Use
print(config.api_url)
print(config.log_level)
```

## Frontend (TypeScript)

### Basic Usage

```typescript
import { EnvManager } from "@tracertm/env-manager";

// Create manager
const env = new EnvManager();

// Get string
const apiUrl = env.get("VITE_API_URL");

// Get required
const wsUrl = env.getRequired("VITE_WS_URL");

// Get with default
const timeout = env.getNumber("VITE_API_TIMEOUT", 30000);

// Get typed values
const debug = env.getBoolean("VITE_DEBUG", false);
const items = env.getArray("VITE_ITEMS", ",");
const config = env.getJSON("VITE_CONFIG");
```

### Configuration Loading

```typescript
import { loadFrontendConfig, validateFrontendConfig } from "@tracertm/env-manager";

// Load configuration
const config = loadFrontendConfig();

// Validate
validateFrontendConfig(config);

// Use
console.log(config.apiUrl);
console.log(config.logLevel);
```

## Environment Variables

### Required Variables

- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string (or Upstash REST)
- `NATS_URL` - NATS message broker URL
- `VITE_API_URL` - Backend API URL (frontend)
- `VITE_WS_URL` - WebSocket URL (frontend)

### Optional Variables

See `.env.template` for all available variables with descriptions.

## Best Practices

1. **Never commit .env files** - Use `.env.template` instead
2. **Use type-safe getters** - Use `GetInt`, `GetBool`, etc. instead of string parsing
3. **Validate on startup** - Call `Validate()` with required variables
4. **Use defaults wisely** - Provide sensible defaults for optional variables
5. **Document variables** - Keep `.env.template` updated with descriptions
6. **Separate by environment** - Use different .env files for dev/staging/prod

## Validation

### Go

```go
requiredVars := []string{"DATABASE_URL", "REDIS_URL"}
if err := envMgr.Validate(requiredVars); err != nil {
    log.Fatal(err)
}
```

### Python

```python
env_mgr.validate(["DATABASE_URL", "REDIS_URL"])
```

### TypeScript

```typescript
env.validate(["VITE_API_URL", "VITE_WS_URL"]);
```

## Troubleshooting

### Variables not loading

1. Check `.env` file exists in correct directory
2. Verify variable names match exactly (case-sensitive)
3. Check for syntax errors in `.env` file

### Type conversion errors

1. Ensure values are in correct format (e.g., "true" for bool, "30" for int)
2. Use `GetOrDefault` to provide fallback values
3. Check error messages for specific format requirements

## Migration from Old System

If migrating from manual environment handling:

1. Create `.env.template` with all variables
2. Update code to use new managers
3. Test in development environment
4. Deploy to staging/production

