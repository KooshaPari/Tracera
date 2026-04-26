# phenotype-go-middleware

Shared HTTP middleware utilities for Phenotype services using chi router.

## Features

- **Default Middleware Stack**: Pre-configured chi router middleware
- **Request Logging**: Structured logging with duration and status codes
- **CORS Support**: Cross-origin resource sharing with sensible defaults
- **Request ID Tracking**: Automatic UUID generation and propagation
- **Health Checks**: Liveness and readiness probe handlers

## Installation

```bash
go get github.com/KooshaPari/phenotype-go-middleware
```

## Quick Start

```go
import (
    "github.com/go-chi/chi/v5"
    "github.com/KooshaPari/phenotype-go-middleware"
)

router := chi.NewRouter()

// Apply default middleware stack
if err := middleware.DefaultMiddlewareStack(router); err != nil {
    log.Fatal(err)
}

// Add health check endpoints
router.Get("/health", middleware.HealthCheckHandler)
router.Get("/ready", middleware.ReadinessCheckHandler)
```

## License

MIT
