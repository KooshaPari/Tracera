# Quick Fixes - P0 Critical Issues

## Fix 1: Enable Search Routes (30 minutes)

### Step 1: Modify `backend/main.go`

Add after line 37 (after migrations):

```go
// Initialize search engine and indexer
log.Println("Initializing search engine...")
searchEngine := search.NewSearchEngine(pool)
indexer := search.NewIndexer(pool, 4, 1000)
indexer.Start()
log.Println("✅ Search engine and indexer started")

// Defer indexer shutdown
defer func() {
    indexer.Stop()
    log.Println("✅ Search indexer stopped")
}()
```

Add import:
```go
"github.com/kooshapari/tracertm-backend/internal/search"
```

### Step 2: Modify `backend/internal/server/server.go`

Update `NewServer()` signature to accept search components:

```go
func NewServer(
    pool *pgxpool.Pool,
    cfg *config.Config,
    searchEngine *search.SearchEngine,
    indexer *search.Indexer,
) *Server
```

Add fields to Server struct:

```go
type Server struct {
    // ... existing fields ...
    searchEngine *search.SearchEngine
    indexer      *search.Indexer
}
```

Initialize in NewServer:

```go
s := &Server{
    // ... existing fields ...
    searchEngine: searchEngine,
    indexer:      indexer,
}
```

### Step 3: Uncomment search routes in `setupRoutes()`

Replace lines 266-283 with:

```go
// Search routes
searchHandler := handlers.NewSearchHandler(
    s.searchEngine,
    s.indexer,
    s.redisCache,
    s.eventPublisher,
    realtimeBroadcaster,
    authProvider,
)
api.POST("/search", searchHandler.Search)
api.GET("/search", searchHandler.SearchGet)
api.GET("/search/suggest", searchHandler.Suggest)
api.POST("/search/index/:id", searchHandler.IndexItem)
api.POST("/search/batch-index", searchHandler.BatchIndex)
api.POST("/search/reindex", searchHandler.ReindexAll)
api.GET("/search/stats", searchHandler.IndexStats)
api.GET("/search/health", searchHandler.SearchHealth)
api.DELETE("/search/index/:id", searchHandler.DeleteIndex)
```

### Step 4: Update `backend/main.go` server initialization

Change:
```go
srv := server.NewServer(pool, cfg)
```

To:
```go
srv := server.NewServer(pool, cfg, searchEngine, indexer)
```

---

## Fix 2: Register Coordination Routes (30 minutes)

**NOTE:** This is a temporary fix using the existing GORM-based handler.
Full migration to pgxpool is recommended as P1.

### Step 1: Modify `backend/internal/server/server.go`

Add import:
```go
"gorm.io/driver/postgres"
"gorm.io/gorm"
```

In `NewServer()` after adapter initialization:

```go
// Initialize GORM for coordination handler (temporary - should migrate to pgxpool)
dsn := cfg.DatabaseURL
gormDB, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
if err != nil {
    log.Printf("Warning: Failed to initialize GORM for coordination: %v", err)
} else {
    log.Println("✅ GORM initialized for coordination handler")
}
```

Add to Server struct:
```go
type Server struct {
    // ... existing fields ...
    gormDB *gorm.DB
}
```

Initialize in struct:
```go
s := &Server{
    // ... existing fields ...
    gormDB: gormDB,
}
```

### Step 2: Register coordination routes

Add after graph routes in `setupRoutes()`:

```go
// Coordination routes (multi-agent coordination)
if s.gormDB != nil {
    coordHandler := handlers.NewCoordinationHandler(s.gormDB)

    // Lock management
    api.POST("/coordination/locks/acquire", coordHandler.AcquireLock)
    api.POST("/coordination/locks/:lock_id/release", coordHandler.ReleaseLock)
    api.GET("/coordination/locks", coordHandler.GetActiveLocks)

    // Conflict detection and resolution
    api.POST("/coordination/conflicts/detect", coordHandler.DetectConflict)
    api.POST("/coordination/conflicts/:conflict_id/resolve", coordHandler.ResolveConflict)
    api.GET("/coordination/conflicts", coordHandler.GetPendingConflicts)

    // Team management
    api.POST("/coordination/teams", coordHandler.CreateTeam)
    api.POST("/coordination/teams/:team_id/members", coordHandler.AddTeamMember)
    api.GET("/coordination/agents/:agent_id/permissions", coordHandler.GetAgentPermissions)

    // Distributed operations
    api.POST("/coordination/operations", coordHandler.CreateDistributedOperation)
    api.POST("/coordination/operations/:operation_id/assign", coordHandler.AssignOperationToAgents)
    api.POST("/coordination/operations/:operation_id/start", coordHandler.StartParticipation)
    api.POST("/coordination/operations/:operation_id/complete", coordHandler.CompleteParticipation)
    api.GET("/coordination/operations/:operation_id", coordHandler.GetOperationStatus)

    // Coordinated updates
    api.POST("/coordination/updates", coordHandler.CoordinatedUpdate)
    api.POST("/coordination/updates/:operation_id/complete", coordHandler.CompleteCoordinatedUpdate)
    api.GET("/coordination/agents/:agent_id/operations", coordHandler.GetAgentOperations)

    log.Println("✅ Coordination routes registered (16 endpoints)")
} else {
    log.Println("⚠️  Coordination routes not registered (GORM initialization failed)")
}
```

### Step 3: Add shutdown for coordination handler

In `Shutdown()` method:

```go
func (s *Server) Shutdown(ctx context.Context) error {
    // Existing shutdown code...

    // Close GORM DB (if initialized)
    if s.gormDB != nil {
        sqlDB, err := s.gormDB.DB()
        if err == nil {
            if err := sqlDB.Close(); err != nil {
                log.Printf("Warning: Failed to close GORM DB: %v", err)
            } else {
                log.Println("✅ GORM DB connection closed")
            }
        }
    }

    // Shutdown Echo server
    return s.echo.Shutdown(ctx)
}
```

---

## Verification

After applying fixes, verify:

```bash
# 1. Backend compiles
cd backend
go build -o tracertm-backend

# 2. Check registered routes
curl http://localhost:8080/health

# 3. Test search endpoint (after starting server)
curl -X POST http://localhost:8080/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "limit": 10}'

# 4. Test coordination endpoint
curl -X GET http://localhost:8080/api/v1/coordination/locks

# 5. Count registered routes
grep -E "api\.(POST|GET|PUT|DELETE)" backend/internal/server/server.go | grep -v "^[[:space:]]*\/\/" | wc -l
# Should show: 64 (39 existing + 9 search + 16 coordination)
```

---

## Expected Results

After these fixes:

- ✅ Search functionality accessible (9 new endpoints)
- ✅ Coordination functionality accessible (16 new endpoints)
- ✅ Total API endpoints: 64 (100% of implemented handlers)
- ⚠️ GORM dependency still present (fix in P1)
- ⚠️ Tests still failing (fix in P1)

---

## Next Steps (P1 - This Week)

1. Migrate coordination handler from GORM to pgxpool
2. Fix graph test compilation errors
3. Fix events test UUID errors
4. Remove GORM dependency completely

---

**Total Time:** ~1 hour
**Impact:** Makes 39% more functionality available (25 new endpoints)
**Risk:** Low (additive changes, no breaking modifications)
