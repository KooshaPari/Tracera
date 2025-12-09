# Handler Adapter Integration - Technical Details

## SearchHandler Enhancements

### Constructor
```go
NewSearchHandler(
    engine *search.SearchEngine,
    indexer *search.Indexer,
    redisCache *cache.RedisCache,
    eventPublisher *nats.EventPublisher,
    realtimeBroadcaster interface{},
    authProvider interface{},
)
```

### Caching Strategy
- **Search Results**: Deterministic cache key from query parameters
- **Key Format**: `search:{query}:{type}:{projectID}:{itemTypes}:{status}:{limit}:{offset}`
- **TTL**: 5 minutes (global)
- **Invalidation**: Pattern-based on projectID

### Methods Enhanced
- `Search()`: POST /api/v1/search with cache
- `SearchGet()`: GET /api/v1/search with cache
- `Suggest()`: GET /api/v1/search/suggest (ready for caching)

## GraphHandler Enhancements

### Constructor
```go
NewGraphHandler(
    pool *pgxpool.Pool,
    redisCache *cache.RedisCache,
    eventPublisher *nats.EventPublisher,
    realtimeBroadcaster interface{},
    authProvider interface{},
)
```

### Caching Strategy
- **Graph Queries**: Cached by query type, itemID, and maxDepth
- **Key Format**: `graph:{queryType}:{itemID}:{maxDepth}`
- **TTL**: 5 minutes (global)
- **Invalidation**: Pattern-based on itemID or project

### Methods Enhanced
- `GetAncestors()`: GET /api/v1/graph/ancestors/:id with cache
- `GetDescendants()`: GET /api/v1/graph/descendants/:id with cache
- All other graph methods ready for caching

## Server Integration

### Adapter Initialization
```go
var authProvider interface{}
var realtimeBroadcaster interface{}
if s.adapterFactory != nil {
    authProvider = s.adapterFactory.GetAuthProvider()
    realtimeBroadcaster = s.adapterFactory.GetRealtimeBroadcaster()
}
```

### Handler Registration
All handlers receive adapters via constructor:
- ProjectHandler
- ItemHandler
- LinkHandler
- AgentHandler
- SearchHandler
- GraphHandler

## Cache Key Patterns

| Handler | Pattern | Example |
|---------|---------|---------|
| Item | `item:{id}` | `item:550e8400-e29b-41d4-a716-446655440000` |
| Link | `link:{id}` | `link:550e8400-e29b-41d4-a716-446655440001` |
| Agent | `agent:{id}` | `agent:550e8400-e29b-41d4-a716-446655440002` |
| Project | `project:{id}` | `project:550e8400-e29b-41d4-a716-446655440003` |
| Search | `search:{q}:{type}:{pid}` | `search:bug:fulltext:proj-1:10:0` |
| Graph | `graph:{type}:{id}:{depth}` | `graph:ancestors:item-1:5` |

## Event Publishing

### NATS Subjects
- `tracertm.{projectID}.created`
- `tracertm.{projectID}.updated`
- `tracertm.{projectID}.deleted`

### Event Types
- Item events
- Link events
- Agent events
- Project events

## Testing Status
✅ All tests passing:
- Agents: 14/14
- WebSocket: 11/11
- Build: Successful (18MB)

