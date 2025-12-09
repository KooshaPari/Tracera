# Environment Manager - Quick Reference

## Setup (All Codebases)

```bash
# 1. Copy template
cp .env.template .env

# 2. Edit with your values
nano .env

# 3. Verify setup
cd backend && go run cmd/setup/main.go -verify
```

## Backend (Go)

### Import
```go
import (
    "tracertm/backend/internal/env"
    "tracertm/backend/internal/config"
)
```

### Basic Usage
```go
// Create manager
envMgr := env.New()
envMgr.Load()

// Get values
port := envMgr.GetOrDefault("PORT", "8080")
debug := envMgr.GetBoolOrDefault("DEBUG", false)
timeout := envMgr.GetDurationOrDefault("TIMEOUT", 30*time.Second)

// Validate
if err := envMgr.Validate([]string{"DATABASE_URL"}); err != nil {
    log.Fatal(err)
}
```

### Load Configuration
```go
cfg, err := config.LoadWithEnvManager()
if err != nil {
    log.Fatal(err)
}

// Use config
fmt.Println(cfg.DatabaseURL)
fmt.Println(cfg.Port)
```

## CLI (Python)

### Import
```python
from tracertm.env_manager import EnvManager
from tracertm.config_loader import load_cli_config, validate_cli_config
```

### Basic Usage
```python
# Create manager
env_mgr = EnvManager()

# Get values
port = env_mgr.get("PORT", "8080")
debug = env_mgr.get_bool("DEBUG", False)
items = env_mgr.get_list("ITEMS", ",")

# Validate
env_mgr.validate(["DATABASE_URL"])
```

### Load Configuration
```python
config = load_cli_config()
validate_cli_config(config)

# Use config
print(config.api_url)
print(config.log_level)
```

## Frontend (TypeScript)

### Import
```typescript
import { 
  EnvManager, 
  loadFrontendConfig, 
  validateFrontendConfig 
} from "@tracertm/env-manager";
```

### Basic Usage
```typescript
// Create manager
const env = new EnvManager();

// Get values
const apiUrl = env.get("VITE_API_URL");
const timeout = env.getNumber("VITE_API_TIMEOUT", 30000);
const debug = env.getBoolean("VITE_DEBUG", false);

// Validate
env.validate(["VITE_API_URL", "VITE_WS_URL"]);
```

### Load Configuration
```typescript
const config = loadFrontendConfig();
validateFrontendConfig(config);

// Use config
console.log(config.apiUrl);
console.log(config.logLevel);
```

## Common Environment Variables

```bash
# Application
APP_ENV=development
APP_DEBUG=true
APP_PORT=8080

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/tracertm

# Cache
REDIS_URL=redis://localhost:6379
UPSTASH_REDIS_REST_URL=https://instance.upstash.io
UPSTASH_REDIS_REST_TOKEN=token

# Message Queue
NATS_URL=nats://localhost:4222

# Graph Database
NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Frontend
VITE_API_URL=http://localhost:8080
VITE_WS_URL=ws://localhost:8080
VITE_WORKOS_CLIENT_ID=client_id
VITE_ENVIRONMENT=development
```

## Type Conversions

### Go
```go
envMgr.Get(key)                    // string
envMgr.GetInt(key)                 // int, error
envMgr.GetBool(key)                // bool, error
envMgr.GetDuration(key)            // time.Duration, error
envMgr.GetOrDefault(key, default)  // string
envMgr.GetIntOrDefault(key, def)   // int
envMgr.GetBoolOrDefault(key, def)  // bool
```

### Python
```python
env_mgr.get(key)                   # str | None
env_mgr.get_int(key)               # int (raises ValueError)
env_mgr.get_bool(key)              # bool
env_mgr.get_list(key)              # list[str]
env_mgr.get_json(key)              # dict | list
env_mgr.get_required(key)          # str (raises ValueError)
```

### TypeScript
```typescript
env.get(key)                       // string | undefined
env.getNumber(key)                 // number | undefined
env.getBoolean(key)                // boolean
env.getArray(key)                  // string[]
env.getJSON(key)                   // any
env.getRequired(key)               // string (throws)
```

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

| Issue | Solution |
|-------|----------|
| .env not loading | Check file exists in correct directory |
| Type conversion error | Verify value format (e.g., "true" for bool) |
| Required var missing | Check .env file and variable name (case-sensitive) |
| Connection refused | Verify service URLs and credentials |

## Files Reference

| Language | Manager | Config | Docs |
|----------|---------|--------|------|
| Go | `backend/internal/env/env.go` | `backend/internal/config/loader.go` | `ENV_MANAGER_GUIDE.md` |
| Python | `cli/tracertm/env_manager.py` | `cli/tracertm/config_loader.py` | `ENV_MANAGER_GUIDE.md` |
| TypeScript | `frontend/packages/env-manager/src/index.ts` | `frontend/packages/env-manager/src/config.ts` | `frontend/packages/env-manager/README.md` |

