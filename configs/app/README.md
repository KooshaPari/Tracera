# App Configs

Application-level runtime configurations.

## Purpose
Standardized configuration structures for applications.

## Structure
```
configs/app/
├── config.yaml        # Base config structure
└── .env.example     # Environment variable template
```

## Config Schema
```yaml
# Standard application config
app:
  name: ${APP_NAME}
  env: ${APP_ENV}
  port: ${APP_PORT}
  log_level: ${LOG_LEVEL}

database:
  host: ${DB_HOST}
  port: ${DB_PORT}
  name: ${DB_NAME}
  pool_size: ${DB_POOL_SIZE}

auth:
  method: ${AUTH_METHOD}
  jwt_secret: ${env:JWT_SECRET}
  session_duration: ${SESSION_DURATION}

observability:
  metrics_enabled: ${METRICS_ENABLED}
  tracing_enabled: ${TRACING_ENABLED}
```

## .env.example
```bash
# Application
APP_NAME=my-service
APP_ENV=development
APP_PORT=8080
LOG_LEVEL=debug

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=appdb
DB_POOL_SIZE=10

# Auth
AUTH_METHOD=jwt
JWT_SECRET=change-me-in-production
SESSION_DURATION=3600

# Observability
METRICS_ENABLED=true
TRACING_ENABLED=true
```

## Agent Pattern
| Action | Pattern |
|--------|---------|
| Read | Load config at startup |
| Write | Generate from template with params |
| Validate | Enforce schema with JSON Schema |

## Related
- [schemas/data/](../schemas/data/) - Config JSON Schema
- [secrets/](../secrets/) - Secrets referenced by configs
