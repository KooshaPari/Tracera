# Go Implementation Template for All Infrastructure

## File Structure

```
backend/
├── main.go                          # Entry point
├── go.mod                           # Dependencies
├── go.sum                           # Dependency lock
├── internal/
│   ├── cache/
│   │   └── redis.go                 # Redis client
│   ├── nats/
│   │   ├── publisher.go             # Event publisher
│   │   └── subscriber.go            # Event subscriber
│   ├── graph/
│   │   ├── client.go                # Neo4j client
│   │   └── project_context.go       # Project isolation
│   ├── search/
│   │   └── meilisearch.go           # Search client
│   ├── adapter/
│   │   └── adapter.go               # Dependency injection
│   ├── middleware/
│   │   └── project_context.go       # Project middleware
│   └── handlers/
│       ├── item.go                  # Item handler
│       ├── link.go                  # Link handler
│       ├── agent.go                 # Agent handler
│       ├── project.go               # Project handler
│       ├── search.go                # Search handler
│       └── graph.go                 # Graph handler
```

## Dependencies to Add

```bash
go get github.com/redis/go-redis/v9
go get github.com/nats-io/nats.go
go get github.com/neo4j/neo4j-go-driver/v5
go get github.com/meilisearch/meilisearch-go
go get github.com/labstack/echo/v4
go get github.com/jackc/pgx/v5
```

## main.go Template

```go
package main

import (
    "context"
    "log"
    "os"
    
    "github.com/labstack/echo/v4"
    "github.com/kooshapari/tracertm-backend/internal/adapter"
    "github.com/kooshapari/tracertm-backend/internal/cache"
    "github.com/kooshapari/tracertm-backend/internal/graph"
    "github.com/kooshapari/tracertm-backend/internal/nats"
    "github.com/kooshapari/tracertm-backend/internal/search"
    "github.com/kooshapari/tracertm-backend/internal/database"
    "github.com/kooshapari/tracertm-backend/internal/handlers"
    "github.com/kooshapari/tracertm-backend/internal/middleware"
)

func main() {
    ctx := context.Background()
    
    // Initialize Redis
    redisCache, err := cache.NewRedisCache(os.Getenv("REDIS_URL"))
    if err != nil {
        log.Fatal("Redis connection failed:", err)
    }
    defer redisCache.Close()
    
    // Initialize NATS
    publisher, err := nats.NewEventPublisher(os.Getenv("NATS_URL"))
    if err != nil {
        log.Fatal("NATS connection failed:", err)
    }
    defer publisher.Close()
    
    // Initialize Supabase
    pool, err := database.NewPool(ctx, os.Getenv("DATABASE_URL"))
    if err != nil {
        log.Fatal("Database connection failed:", err)
    }
    defer pool.Close()
    
    // Initialize Neo4j
    graphClient, err := graph.NewGraphClient(
        os.Getenv("NEO4J_URI"),
        os.Getenv("NEO4J_USER"),
        os.Getenv("NEO4J_PASSWORD"),
    )
    if err != nil {
        log.Fatal("Neo4j connection failed:", err)
    }
    defer graphClient.Close(ctx)
    
    // Initialize Meilisearch
    searchClient, err := search.NewMeilisearch(
        os.Getenv("MEILISEARCH_URL"),
        os.Getenv("MEILISEARCH_KEY"),
    )
    if err != nil {
        log.Fatal("Meilisearch connection failed:", err)
    }
    
    // Create adapter
    adapterInstance := &adapter.Adapter{
        Cache:  redisCache,
        DB:     pool,
        Graph:  graphClient,
        Search: searchClient,
        Events: publisher,
    }
    
    // Setup Echo
    e := echo.New()
    
    // Middleware
    e.Use(middleware.ProjectContextMiddleware)
    
    // Routes
    handlers.SetupRoutes(e, adapterInstance)
    
    // Start server
    e.Start(":8080")
}
```

## Adapter Pattern

```go
// backend/internal/adapter/adapter.go
package adapter

import (
    "github.com/jackc/pgx/v5/pgxpool"
    "github.com/kooshapari/tracertm-backend/internal/cache"
    "github.com/kooshapari/tracertm-backend/internal/graph"
    "github.com/kooshapari/tracertm-backend/internal/nats"
    "github.com/kooshapari/tracertm-backend/internal/search"
)

type Adapter struct {
    Cache  cache.Cache
    DB     *pgxpool.Pool
    Graph  *graph.GraphClient
    Search search.Search
    Events *nats.EventPublisher
}
```

## Handler Template

```go
// backend/internal/handlers/item.go
package handlers

import (
    "github.com/labstack/echo/v4"
    "github.com/kooshapari/tracertm-backend/internal/adapter"
    "github.com/kooshapari/tracertm-backend/internal/graph"
)

type ItemHandler struct {
    adapter *adapter.Adapter
}

func NewItemHandler(a *adapter.Adapter) *ItemHandler {
    return &ItemHandler{adapter: a}
}

func (h *ItemHandler) GetItems(c echo.Context) error {
    ctx := c.Request().Context()
    projectID := graph.GetProjectID(ctx)
    
    // Try cache
    cached, _ := h.adapter.Cache.Get(ctx, "items:"+projectID)
    if cached != "" {
        return c.JSON(200, cached)
    }
    
    // Query database
    items, err := h.adapter.DB.Query(ctx, 
        "SELECT * FROM items WHERE project_id = $1", projectID)
    if err != nil {
        return err
    }
    
    // Cache result
    h.adapter.Cache.Set(ctx, "items:"+projectID, items, 5*time.Minute)
    
    // Publish event
    h.adapter.Events.PublishItemEvent(map[string]interface{}{
        "type": "items.fetched",
        "project_id": projectID,
    })
    
    return c.JSON(200, items)
}
```

## Environment Variables

```bash
# .env.local
REDIS_URL=redis://localhost:6379
NATS_URL=nats://localhost:4222
DATABASE_URL=postgresql://postgres:password@localhost:5432/tracertm
NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
MEILISEARCH_URL=http://localhost:7700
MEILISEARCH_KEY=masterKey
```

## Testing Template

```go
// backend/internal/handlers/item_test.go
package handlers

import (
    "testing"
    "github.com/stretchr/testify/assert"
)

func TestGetItems(t *testing.T) {
    // Setup
    adapter := setupTestAdapter()
    handler := NewItemHandler(adapter)
    
    // Test
    // Assert
}
```

## Build & Run

```bash
# Build
go build -o tracertm-backend backend/main.go

# Run
./tracertm-backend

# Or with environment variables
REDIS_URL=redis://localhost:6379 \
NATS_URL=nats://localhost:4222 \
DATABASE_URL=postgresql://... \
NEO4J_URI=neo4j://localhost:7687 \
NEO4J_USER=neo4j \
NEO4J_PASSWORD=password \
MEILISEARCH_URL=http://localhost:7700 \
./tracertm-backend
```

## Docker Build

```dockerfile
FROM golang:1.25-alpine AS builder
WORKDIR /app
COPY . .
RUN go build -o tracertm-backend backend/main.go

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/tracertm-backend .
EXPOSE 8080
CMD ["./tracertm-backend"]
```

## Next Steps

1. Copy this template
2. Implement each client
3. Create handlers
4. Write tests
5. Deploy

See INFRASTRUCTURE_INTEGRATION_COMPLETE.md for detailed examples.

