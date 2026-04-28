# Production-Grade Environment Manager Upgrade Guide

## Overview

Upgrade from basic environment managers to production-grade infrastructure using industry-standard tools already in your dependencies.

## Python: Pydantic Settings (RECOMMENDED FIRST)

### Why Pydantic Settings?
- ✅ Already in `pyproject.toml` (pydantic-settings>=2.3.0)
- ✅ Type-safe with IDE support
- ✅ Automatic validation
- ✅ Nested configuration
- ✅ Used by FastAPI, Starlette, etc.

### Implementation

```python
# cli/tracertm/config.py (NEW - replaces env_manager.py)
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional

class DatabaseSettings(BaseSettings):
    url: str
    pool_size: int = 20
    echo: bool = False
    
    class Config:
        env_prefix = "DATABASE_"

class CacheSettings(BaseSettings):
    redis_url: Optional[str] = None
    upstash_url: Optional[str] = None
    upstash_token: Optional[str] = None
    ttl: int = 3600
    
    class Config:
        env_prefix = "CACHE_"

class Settings(BaseSettings):
    # Application
    env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=False, alias="APP_DEBUG")
    port: int = Field(default=8000, alias="APP_PORT")
    
    # Services
    database: DatabaseSettings = DatabaseSettings()
    cache: CacheSettings = CacheSettings()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    @validator("env")
    def validate_env(cls, v):
        if v not in ["development", "staging", "production"]:
            raise ValueError("Invalid environment")
        return v

# Usage
settings = Settings()
print(settings.database.url)
print(settings.cache.redis_url)
```

### Benefits Over Basic Manager
- Type validation at runtime
- Nested configuration objects
- IDE autocomplete
- JSON schema generation
- Automatic coercion (str → int, bool, etc.)

## Go: Viper Configuration

### Why Viper?
- Industry standard (used by Kubernetes, Docker, etc.)
- Multiple format support (YAML, JSON, TOML, ENV)
- Nested configuration
- Watch for changes
- Defaults and overrides

### Implementation

```go
// backend/internal/config/viper.go (NEW)
package config

import (
    "github.com/spf13/viper"
)

func LoadConfig() (*Config, error) {
    v := viper.New()
    
    v.SetConfigFile(".env")
    v.SetConfigType("env")
    v.AutomaticEnv()
    
    // Set defaults
    v.SetDefault("port", 8080)
    v.SetDefault("env", "development")
    
    if err := v.ReadInConfig(); err != nil {
        // .env is optional
        if _, ok := err.(viper.ConfigFileNotFoundError); !ok {
            return nil, err
        }
    }
    
    cfg := &Config{
        Port:        v.GetInt("port"),
        Env:         v.GetString("env"),
        DatabaseURL: v.GetString("database_url"),
        RedisURL:    v.GetString("redis_url"),
    }
    
    return cfg, nil
}
```

### Add to go.mod
```bash
go get github.com/spf13/viper
```

## TypeScript: Zod Schema Validation

### Why Zod?
- Type-safe schema validation
- Runtime validation
- Excellent error messages
- Coercion and transformation
- Used by tRPC, Remix, etc.

### Implementation

```typescript
// frontend/packages/env-manager/src/schema.ts (NEW)
import { z } from "zod"

export const envSchema = z.object({
  // Application
  VITE_ENVIRONMENT: z.enum(["development", "staging", "production"]).default("development"),
  VITE_DEBUG: z.enum(["true", "false"]).transform(v => v === "true").default("false"),
  VITE_PORT: z.coerce.number().default(3000),
  
  // API
  VITE_API_URL: z.string().url(),
  VITE_WS_URL: z.string().url(),
  VITE_API_TIMEOUT: z.coerce.number().default(30000),
  
  // Auth
  VITE_WORKOS_CLIENT_ID: z.string(),
})

export type Env = z.infer<typeof envSchema>

export function loadEnv(): Env {
  try {
    return envSchema.parse(process.env)
  } catch (error) {
    if (error instanceof z.ZodError) {
      console.error("Environment validation failed:")
      error.errors.forEach(err => {
        console.error(`  ${err.path.join(".")}: ${err.message}`)
      })
    }
    throw error
  }
}
```

### Add to package.json
```bash
npm install zod
```

## Structured Logging

### Python (Using structlog - Already in dependencies!)

```python
# cli/tracertm/logging.py (NEW)
import structlog
from pythonjsonlogger import jsonlogger

def setup_logging(debug: bool = False):
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

logger = structlog.get_logger()
```

### Go (Add logrus)

```bash
go get github.com/sirupsen/logrus
```

### TypeScript (Add Winston)

```bash
npm install winston
```

## Observability: OpenTelemetry

### Python (Already in dependencies!)

```python
# cli/tracertm/observability.py (NEW)
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.prometheus import PrometheusMetricReader

def setup_observability():
    # Tracing
    trace.set_tracer_provider(TracerProvider())
    
    # Metrics
    metric_reader = PrometheusMetricReader()
    
    return trace.get_tracer(__name__)
```

### Go (Add OpenTelemetry)

```bash
go get go.opentelemetry.io/otel
go get go.opentelemetry.io/otel/sdk
```

### TypeScript (Add OpenTelemetry)

```bash
npm install @opentelemetry/api @opentelemetry/sdk-node
```

## Migration Checklist

- [ ] Python: Replace EnvManager with Pydantic Settings
- [ ] Python: Add structlog configuration
- [ ] Python: Add OpenTelemetry setup
- [ ] Go: Add Viper for configuration
- [ ] Go: Add logrus for logging
- [ ] Go: Add OpenTelemetry instrumentation
- [ ] TypeScript: Add Zod for validation
- [ ] TypeScript: Add Winston for logging
- [ ] TypeScript: Add OpenTelemetry instrumentation
- [ ] Update all services to use new infrastructure
- [ ] Test configuration loading in all codebases
- [ ] Update documentation

## Benefits Summary

| Aspect | Before | After |
|--------|--------|-------|
| Validation | Manual | Automatic |
| Type Safety | Partial | Full |
| Nested Config | No | Yes |
| Logging | Basic | Structured |
| Observability | None | Full |
| IDE Support | Limited | Excellent |
| Production Ready | No | Yes |

## Next Steps

1. Start with Python (Pydantic Settings)
2. Move to Go (Viper)
3. Finish with TypeScript (Zod)
4. Add structured logging to all
5. Implement observability

This transforms your infrastructure from "works" to "production-grade"! 🚀

