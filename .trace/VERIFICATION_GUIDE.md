# Backend Consolidation - Verification Guide

**Quick verification steps for testing all implementations**

---

## Quick Verification Commands

### 1. Start Services

```bash
# Option A: Docker Compose (Recommended)
make dev

# Option B: Native Services
# Terminal 1: Start dependencies
redis-server &
nats-server -js &
createdb tracertm || true

# Terminal 2: Go backend
cd backend && air

# Terminal 3: Python backend
uvicorn tracertm.api.main:app --reload

# Terminal 4: Frontend
cd frontend/apps/web && bun run dev
```

---

## Phase 1: Critical Fixes Verification

### 1.1 Go Route Registrations (5 minutes)

```bash
# Wait for Go backend to start, then test:

# AI Routes
curl http://localhost:8080/api/v1/ai/health
# Expected: 200 OK (not 404)

# Spec Analytics Routes
curl http://localhost:8080/api/v1/spec-analytics/health
# Expected: 200 OK (not 404)

# Execution Routes
curl http://localhost:8080/api/v1/execution/health
# Expected: 200 OK (not 404)

# Workflow Routes
curl http://localhost:8080/api/v1/hatchet/health
# Expected: 200 OK (not 404)

# Chaos Routes
curl http://localhost:8080/api/v1/chaos/health
# Expected: 200 OK (not 404)
```

**✅ Success**: All routes return 200 OK
**❌ Failure**: Any 404 errors → Check server.go route registrations

---

### 1.2 GORM Infrastructure (2 minutes)

```bash
# Test journey detection (uses GORM)
curl -X POST http://localhost:8080/api/v1/journey/detect \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "test-project",
    "start_item_id": "ITEM-001",
    "end_item_id": "ITEM-002"
  }'

# Expected: Journey data OR "no path found" (both are OK)
# NOT Expected: Panic, nil pointer error, 500 error
```

**✅ Success**: Returns JSON response (even if empty)
**❌ Failure**: Panic/crash → Check infrastructure.go GormDB initialization

---

### 1.3 Python Execution Router (2 minutes)

```bash
# Test execution endpoints
curl http://localhost:8000/api/v1/projects/test-project/executions

# Expected: 200 OK with execution list (may be empty)
# NOT Expected: 404 error
```

**✅ Success**: Returns 200 with JSON array
**❌ Failure**: 404 error → Check main.py router registration

---

### 1.4 Event Handlers (5 minutes)

```bash
# Terminal 1: Watch Python logs
tail -f logs/tracertm.log  # Or wherever Python logs

# Terminal 2: Create item via Go backend
curl -X POST http://localhost:8080/api/v1/items \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Item",
    "project_id": "proj-123",
    "type": "requirement"
  }'

# In Terminal 1, look for:
# - "Received item.created event: ITEM-..."
# - "Cache invalidation for python:items:proj-123"
# - "Cache invalidation for python:graph:proj-123"
```

**✅ Success**: Event logged with cache invalidations
**❌ Failure**: No logs → Check NATS connection and event handler registration

---

## Phase 2: Performance Verification

### 2.1 N+1 Query Fix (3 minutes)

```bash
# Enable SQL logging in Python
export LOG_SQL=1

# Create test project with features and scenarios
curl -X POST http://localhost:8000/api/v1/projects \
  -d '{"name": "Test Performance", "description": "Load test"}'

# Create 10 features with scenarios (use script or manual)
# Then list features:
curl http://localhost:8000/api/v1/projects/{project_id}/features

# Check logs: Should see 2 SQL queries, not 11
# Query 1: SELECT features...
# Query 2: SELECT scenarios WHERE feature_id IN (...)
```

**✅ Success**: Only 2 queries for any number of features
**❌ Failure**: N+1 queries → Check specification_repository.py selectinload

---

### 2.2 Bulk Operations Parallelization (5 minutes)

```bash
# Create 50 test items first (use script)

# Time bulk update
time curl -X POST http://localhost:8080/api/v1/bulk/update \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "proj-123",
    "filters": {"type": "requirement"},
    "updates": {"status": "approved"}
  }'

# Expected: ~500ms for 50 items
# Check logs for "parallel_execution: true"
```

**✅ Success**: <1s for 50 items with parallel_execution flag
**❌ Failure**: >2s → Check bulk_service.py asyncio.gather implementation

---

### 2.3 Database Indexes (2 minutes)

```bash
# Apply migration
alembic upgrade head

# Verify indexes exist
psql -d tracertm -c "
  SELECT indexname, tablename
  FROM pg_indexes
  WHERE tablename IN ('items', 'links', 'scenarios')
  ORDER BY tablename, indexname;
"

# Expected to see:
# - ix_items_deleted_project
# - ix_items_project_deleted_type
# - ix_links_source_target
# - ix_links_type_project
# - ix_scenarios_feature
```

**✅ Success**: All indexes present
**❌ Failure**: Missing indexes → Check migration 046 applied correctly

---

### 2.4 Graph Caching (5 minutes)

```bash
# First request (cache miss)
time curl http://localhost:8000/api/v1/graph/shortest-path \
  -d '{
    "project_id": "proj-123",
    "source_id": "REQ-001",
    "target_id": "TEST-042"
  }'
# Expected: ~1-2s

# Second request (cache hit)
time curl http://localhost:8000/api/v1/graph/shortest-path \
  -d '{
    "project_id": "proj-123",
    "source_id": "REQ-001",
    "target_id": "TEST-042"
  }'
# Expected: <200ms

# Check Redis
redis-cli KEYS "tracertm:graph:*"
# Expected: Cache keys present

# Check logs for "Cache hit for path REQ-001 -> TEST-042"
```

**✅ Success**: 10x faster on second request with cache hit log
**❌ Failure**: Same speed both times → Check shortest_path_service.py cache integration

---

### 2.5 Frontend Graph Rendering (10 minutes)

```bash
# Start frontend dev server
cd frontend/apps/web
bun run dev

# Open browser to http://localhost:3000
# Navigate to: Projects → {any project} → Graph View

# Open Chrome DevTools:
# 1. Performance tab → Click Record
# 2. Load graph with 2000+ nodes
# 3. Stop recording

# Check metrics:
# - Initial render: <1s
# - No long tasks (>50ms)
# - Smooth 60fps scrolling/zooming

# Console should show:
# - "Parent map built: 2000 nodes in {X}ms"
# - "Nodes enriched: 2000 nodes in {X}ms"
# - No warnings about re-renders
```

**✅ Success**: Smooth rendering, no frame drops, <1s initial load
**❌ Failure**: Slow/janky → Check FlowGraphViewInner.tsx optimizations

---

## Load Testing (Optional, 30 minutes)

```bash
# Ensure k6 is installed
./scripts/install_k6.sh

# Run comprehensive load tests
./scripts/run_load_tests.sh

# Expected results:
# - Feature listing: p95 < 100ms (was 10s+)
# - Bulk updates: p95 < 1s for 50 items (was 5s+)
# - Graph queries: p95 < 500ms (was 2s+)
# - Error rate: <1%

# Check generated report:
cat load-tests/results/summary.json
```

**✅ Success**: All p95 targets met, low error rate
**❌ Failure**: High latency/errors → Review specific failed endpoints

---

## Integration Testing (15 minutes)

```bash
# Run end-to-end flow
# 1. Create project via Go backend
PROJECT_ID=$(curl -X POST http://localhost:8080/api/v1/projects \
  -d '{"name": "E2E Test"}' | jq -r '.id')

# 2. Create items via Go
ITEM_ID=$(curl -X POST http://localhost:8080/api/v1/items \
  -d "{\"project_id\": \"$PROJECT_ID\", \"title\": \"Test Item\", \"type\": \"requirement\"}" \
  | jq -r '.id')

# 3. Check Python received event (check logs)
# Expected: "Received item.created event: {ITEM_ID}"

# 4. Verify item accessible via Python
curl http://localhost:8000/api/v1/projects/$PROJECT_ID/items/$ITEM_ID
# Expected: 200 with item data

# 5. Create link
LINK_ID=$(curl -X POST http://localhost:8080/api/v1/links \
  -d "{
    \"source_item_id\": \"$ITEM_ID\",
    \"target_item_id\": \"...\",
    \"link_type\": \"traces_to\"
  }" | jq -r '.id')

# 6. Check graph cache invalidated (logs)
# Expected: "Cache invalidation for python:graph:{PROJECT_ID}"

# 7. Query graph via Python
curl http://localhost:8000/api/v1/graph/shortest-path \
  -d "{\"project_id\": \"$PROJECT_ID\", \"source_id\": \"...\", \"target_id\": \"...\"}"
# Expected: 200 with path data

# 8. Update item via bulk operation
curl -X POST http://localhost:8080/api/v1/bulk/update \
  -d "{\"project_id\": \"$PROJECT_ID\", \"filters\": {}, \"updates\": {\"status\": \"approved\"}}"
# Expected: <1s response with parallel_execution flag
```

**✅ Success**: All steps complete without errors
**❌ Failure**: Any step fails → Review specific component

---

## Quick Health Check Script

Create `scripts/verify_consolidation.sh`:

```bash
#!/bin/bash
set -e

echo "🔍 Backend Consolidation Verification"
echo "======================================"

# Check Go backend
echo "1. Testing Go routes..."
for route in ai spec-analytics execution hatchet chaos; do
  if curl -s http://localhost:8080/api/v1/$route/health > /dev/null; then
    echo "  ✅ $route routes OK"
  else
    echo "  ❌ $route routes FAILED"
  fi
done

# Check Python backend
echo "2. Testing Python routes..."
if curl -s http://localhost:8000/api/v1/projects/test/executions > /dev/null; then
  echo "  ✅ Execution routes OK"
else
  echo "  ❌ Execution routes FAILED"
fi

# Check database indexes
echo "3. Checking database indexes..."
INDEX_COUNT=$(psql -d tracertm -t -c "SELECT COUNT(*) FROM pg_indexes WHERE indexname LIKE 'ix_items_%';")
if [ "$INDEX_COUNT" -ge 2 ]; then
  echo "  ✅ Indexes present ($INDEX_COUNT)"
else
  echo "  ❌ Indexes missing"
fi

# Check Redis
echo "4. Checking Redis cache..."
if redis-cli PING > /dev/null 2>&1; then
  echo "  ✅ Redis OK"
else
  echo "  ❌ Redis unavailable"
fi

echo ""
echo "✅ Verification complete!"
```

Run with: `chmod +x scripts/verify_consolidation.sh && ./scripts/verify_consolidation.sh`

---

## Troubleshooting

### Routes Return 404
1. Check server.go has route registrations (lines 689-710)
2. Verify handler functions exist and exported
3. Restart Go backend: `pkill -f tracertm-server && go run main.go`

### GORM Crashes
1. Check infrastructure.go has GormDB field (line 26)
2. Verify initialization in InitializeInfrastructure (lines 55-64)
3. Check logs: `tail -f logs/backend.log | grep GORM`

### Events Not Processing
1. Verify NATS running: `ps aux | grep nats-server`
2. Check connection: `nats-server --addr=localhost:4222`
3. Review Python logs: `tail -f logs/tracertm.log | grep "Received.*event"`

### Slow Queries
1. Verify migration applied: `alembic current`
2. Check indexes: `psql -d tracertm -c "\di"`
3. Enable query logging: `export LOG_SQL=1`
4. Review EXPLAIN plans for slow queries

### Cache Not Working
1. Verify Redis running: `redis-cli PING`
2. Check cache initialization in services
3. Review cache logs: `tail -f logs/tracertm.log | grep -i cache`

---

## Performance Benchmarks

Expected performance after all optimizations:

| Metric | Target | Command to Test |
|--------|--------|----------------|
| Feature listing (100 items) | <100ms | `curl /api/v1/projects/{id}/features` |
| Bulk update (50 items) | <500ms | `curl -X POST /api/v1/bulk/update` |
| Graph path query (cached) | <200ms | `curl /api/v1/graph/shortest-path` |
| Graph path query (uncached) | <2s | `curl /api/v1/graph/shortest-path` (first time) |
| Frontend render (2000 nodes) | <1s | Open graph view in browser |
| Active items query | <50ms | `curl /api/v1/projects/{id}/items` |

---

## Success Criteria

All verifications should pass:
- ✅ All 5 delegation routes accessible (200 OK)
- ✅ Journey detection returns data (no crashes)
- ✅ Execution endpoints accessible via Python
- ✅ Events logged with cache invalidation
- ✅ N+1 queries eliminated (2 queries max)
- ✅ Bulk operations use parallel execution
- ✅ Database indexes present
- ✅ Graph caching working (10x faster on cache hit)
- ✅ Frontend renders smoothly (2000+ nodes)

**Status**: Ready for production when all criteria met ✅
