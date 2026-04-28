# Complete Infrastructure Integration Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Go Backend (Echo)                        │
├─────────────────────────────────────────────────────────────┤
│  Handlers → Services → Adapters → Infrastructure            │
└─────────────────────────────────────────────────────────────┘
         │              │              │              │
    ┌────┴────┐    ┌────┴────┐   ┌────┴────┐   ┌────┴────┐
    │          │    │          │   │          │   │          │
    ▼          ▼    ▼          ▼   ▼          ▼   ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ Redis  │ │ NATS   │ │Supabase│ │ Neo4j  │ │Meilisearch│ │WebSocket│
│ Cache  │ │ Events │ │  SQL   │ │ Graph  │ │ Search │ │ Real-time│
└────────┘ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘
```

## Data Flow

### 1. Request Handling
```
Client Request
    ↓
Handler (ProjectContextMiddleware)
    ↓
Extract project_id from auth
    ↓
Add to context
```

### 2. Cache Check
```
Handler
    ↓
Check Redis cache
    ↓
If hit: Return cached data
If miss: Continue to database
```

### 3. Database Query
```
Handler
    ↓
Query Supabase (PostgreSQL)
    ↓
Get results
    ↓
Store in Redis cache (5 min TTL)
```

### 4. Graph Query
```
Handler
    ↓
Query Neo4j with project_id filter
    ↓
Get relationships
    ↓
Combine with SQL results
```

### 5. Event Publishing
```
Handler (on mutation)
    ↓
Publish to NATS
    ↓
Event subscribers receive
    ↓
Update search index
    ↓
Broadcast via WebSocket
```

### 6. Search Indexing
```
NATS Event
    ↓
Search Service
    ↓
Index in Meilisearch
    ↓
Update search results
```

## Go Implementation

### 1. Initialize All Clients

```go
// backend/main.go
func main() {
    ctx := context.Background()
    
    // Redis
    redisCache, _ := cache.NewRedisCache(os.Getenv("REDIS_URL"))
    defer redisCache.Close()
    
    // NATS
    publisher, _ := nats.NewEventPublisher(os.Getenv("NATS_URL"))
    defer publisher.Close()
    
    // Supabase
    pool, _ := database.NewPool(ctx, os.Getenv("DATABASE_URL"))
    defer pool.Close()
    
    // Neo4j
    graphClient, _ := graph.NewGraphClient(
        os.Getenv("NEO4J_URI"),
        os.Getenv("NEO4J_USER"),
        os.Getenv("NEO4J_PASSWORD"),
    )
    defer graphClient.Close(ctx)
    
    // Meilisearch
    searchClient, _ := search.NewMeilisearch(
        os.Getenv("MEILISEARCH_URL"),
        os.Getenv("MEILISEARCH_KEY"),
    )
    
    // Create adapter
    adapter := &adapter.Adapter{
        Cache:  redisCache,
        DB:     pool,
        Graph:  graphClient,
        Search: searchClient,
        Events: publisher,
    }
    
    // Setup handlers
    e := echo.New()
    e.Use(middleware.ProjectContextMiddleware)
    
    handlers.SetupRoutes(e, adapter)
    
    e.Start(":8080")
}
```

### 2. Adapter Pattern

```go
// backend/internal/adapter/adapter.go
type Adapter struct {
    Cache  cache.Cache
    DB     *pgxpool.Pool
    Graph  *graph.GraphClient
    Search search.Search
    Events *nats.EventPublisher
}

// Use in handlers
func (h *ItemHandler) GetItems(c echo.Context) error {
    projectID := graph.GetProjectID(c.Request().Context())
    
    // Try cache
    cached, _ := h.adapter.Cache.Get(c.Request().Context(), "items:"+projectID)
    if cached != "" {
        return c.JSON(200, cached)
    }
    
    // Query database
    items, _ := h.adapter.DB.Query(c.Request().Context(), "SELECT * FROM items WHERE project_id = $1", projectID)
    
    // Query graph
    relationships, _ := h.adapter.Graph.GetRelationships(c.Request().Context(), projectID)
    
    // Cache result
    h.adapter.Cache.Set(c.Request().Context(), "items:"+projectID, items, 5*time.Minute)
    
    // Publish event
    h.adapter.Events.PublishItemEvent(map[string]interface{}{
        "type": "items.fetched",
        "project_id": projectID,
    })
    
    return c.JSON(200, items)
}
```

### 3. Environment Variables

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

## Testing

### 1. Unit Tests

```go
func TestItemHandlerWithCache(t *testing.T) {
    adapter := &adapter.Adapter{
        Cache: &mockCache{},
        DB:    &mockDB{},
    }
    
    handler := &ItemHandler{adapter: adapter}
    
    // Test cache hit
    // Test cache miss
    // Test database query
}
```

### 2. Integration Tests

```go
func TestFullDataFlow(t *testing.T) {
    // Start all services
    // Create item
    // Check Redis cache
    // Check Neo4j graph
    // Check Meilisearch index
    // Verify NATS event
}
```

## Deployment

### 1. Local Development
```bash
docker-compose up -d
go run backend/main.go
```

### 2. Staging
```bash
# Use Upstash Redis
# Use Synadia NATS
# Use Supabase
# Use Neo4j Aura
# Use Meilisearch Cloud
```

### 3. Production
```bash
# Same as staging
# Add monitoring
# Add backups
# Add alerting
```

## Monitoring

### 1. Redis
- Memory usage
- Commands/sec
- Connected clients

### 2. NATS
- Messages/sec
- Connected clients
- Subject distribution

### 3. Supabase
- Query latency
- Connection count
- Database size

### 4. Neo4j
- Query latency
- Node count
- Memory usage

### 5. Meilisearch
- Search latency
- Indexed documents
- Query count

## Performance Optimization

### 1. Caching Strategy
- Cache-aside pattern
- 5-minute TTL for lists
- 1-hour TTL for details
- Invalidate on mutations

### 2. Database Optimization
- Use indexes
- Connection pooling
- Prepared statements
- Query optimization

### 3. Graph Optimization
- Use labels for indexing
- Filter by project_id
- Limit relationship depth
- Use EXPLAIN for analysis

### 4. Search Optimization
- Batch indexing
- Async updates
- Limit result size
- Use filters

## Troubleshooting

### Connection Issues
```bash
# Test each service
redis-cli ping
nats-cli server info
psql $DATABASE_URL
cypher-shell -a $NEO4J_URI
curl $MEILISEARCH_URL/health
```

### Performance Issues
- Check cache hit rate
- Analyze slow queries
- Monitor connection pools
- Check network latency

## Next Steps

1. ✅ Set up all infrastructure
2. ✅ Create adapter pattern
3. ✅ Integrate with handlers
4. ✅ Write integration tests
5. Deploy to staging
6. Monitor and optimize
7. Deploy to production

See individual setup guides for detailed instructions.

