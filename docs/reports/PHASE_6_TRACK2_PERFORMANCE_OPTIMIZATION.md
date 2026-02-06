# Phase 6 Track 2: Performance Optimization - Execution Plan
**Status:** EXECUTION IN PROGRESS
**Timeline:** 120 minutes wall-clock
**Target Deadline:** 2026-02-06 04:00 UTC

## Overview
Execute 3 parallel subtracks to optimize dashboard, React Query caching, and Redis hot paths:
- **6.4 Dashboard N+1:** DataLoader batching for projects/items → target <200ms load
- **6.5 React Query:** Fix cache keys + invalidation logic → target LCP <2.5s
- **6.6 Redis Caching:** Hot path caching (user profile 1h, project list 5min) → target >80% hit rate

## Current Baseline (Pre-Optimization)

### 6.4 Dashboard N+1 Problem
**Files:** `backend/internal/handlers/dashboard_handler.go`, `frontend/apps/web/src/views/DashboardView.tsx`

**Current Query Pattern:**
- Single GROUP BY query: `SELECT project_id, status, type, COUNT(*) FROM items GROUP BY project_id, status, type` → ~50-100ms
- Separate projects count query → ~10-20ms
- Frontend: 2 queries (`useDashboardSummary` + `useProjects`) → ~100-150ms total
- Total dashboard render time: ~200-300ms (needs to get <200ms)

**N+1 Risk:**
- Projects list (1 query)
- Dashboard summary (1 query with grouping)
- No per-project detail queries currently

**Solution:** DataLoader batching + Query optimization

### 6.5 React Query Cache Issues
**Files:** `frontend/apps/web/src/hooks/useProjects.ts`, `frontend/apps/web/src/hooks/useDashboardSummary.ts`

**Current Cache Setup:**
```typescript
// useProjects
queryKey: ['projects', token ?? ''],
staleTime: 5 * 60 * 1000, // 5 minutes

// useDashboardSummary
queryKey: ['dashboard-summary', token ?? ''],
staleTime: 5 * 60 * 1000, // 5 minutes
```

**Issues:**
1. Cache keys not scoped by userId/projectId → cache invalidation affects all users/projects
2. Query invalidation too broad:
   ```typescript
   _queryClient.invalidateQueries({ queryKey: ['projects'] })
   ```
3. No cache sharing across components (each component triggers re-fetch if key differs)

**LCP Problem:** Frontend queries fire sequentially → both waiting on backend
- Projects query: 0-50ms
- Dashboard query: starts after projects → 50-150ms (if projects slow)
- Total: 150-200ms just for data fetching

**Solution:**
- Scope cache keys by userId (partition cache per user)
- Fix invalidation to be granular (only invalidate specific project)
- Parallel query execution

### 6.6 Redis Caching
**Current State:** No Redis integration present

**Hot Paths to Cache:**
1. User profile (GET `/api/v1/user/profile`) → 1h TTL
   - Called on every page load, rarely changes
   - Eliminates 20-50ms database query

2. Project list (GET `/api/v1/projects`) → 5min TTL
   - Dashboard queries this frequently
   - High request volume from multiple users

3. Dashboard summary (GET `/api/v1/dashboard/summary`) → 2min TTL
   - Complex aggregation query
   - Most expensive endpoint

**Backend Setup Required:**
- Redis client initialization
- Cache middleware for automatic key generation
- Cache invalidation on mutations (POST/PATCH/DELETE)

**Expected Hit Rate:** >80% for projects/dashboard (high read:write ratio)

## Execution Plan

### Subtrack 6.4: Dashboard N+1 Optimization (40 min)

**Phase 1: Measurement (5 min)**
- Run dashboard load test (benchmark current time)
- Database query analysis (EXPLAIN ANALYZE)
- Frontend query profiling

**Phase 2: Backend Optimization (20 min)**
- Optimize GROUP BY query (add indexes)
- Implement single aggregation query
- Add query result caching in handler
- Test query performance

**Phase 3: Frontend Optimization (10 min)**
- Parallel query execution (Promise.all)
- Combine project + summary data
- Test LCP improvement

**Phase 4: Validation (5 min)**
- Measure new dashboard load time
- Report before/after metrics

### Subtrack 6.5: React Query Cache Keys (30 min)

**Phase 1: Analysis (5 min)**
- Audit all query keys in project
- Identify cache invalidation patterns
- List all mutations and their invalidations

**Phase 2: Fix Cache Keys (10 min)**
- Update useProjects: add userId to key
- Update useDashboardSummary: add userId to key
- Update useProject: ensure proper scoping

**Phase 3: Fix Invalidation (10 min)**
- useCreateProject: only invalidate broad 'projects' key
- useDeleteProject: only invalidate specific project
- useUpdateProject: granular invalidation
- Remove overly broad invalidations

**Phase 4: Test & Verify (5 min)**
- Manual test: create/update/delete projects
- Verify cache isn't stale
- Check LCP improvement

### Subtrack 6.6: Redis Caching (35 min)

**Phase 1: Redis Setup (5 min)**
- Check if Redis client exists in backend
- Initialize Redis connection if needed
- Add cache middleware

**Phase 2: User Profile Caching (10 min)**
- Create cache key: `user:profile:{userId}`
- TTL: 1 hour
- Invalidate on profile updates
- Test hit rate

**Phase 3: Project List Caching (10 min)**
- Create cache key: `user:projects:{userId}`
- TTL: 5 minutes
- Invalidate on create/update/delete
- Test hit rate

**Phase 4: Dashboard Summary Caching (7 min)**
- Create cache key: `user:dashboard:{userId}`
- TTL: 2 minutes (more aggressive than projects)
- Invalidate on item mutations
- Test hit rate

**Phase 5: Monitoring (3 min)**
- Log cache hits/misses
- Report hit rate statistics

## Success Criteria

### 6.4 Dashboard Load Time
- **Target:** <200ms total dashboard load (including rendering)
- **Current:** ~250-350ms
- **Success:** Measured improvement >20%

### 6.5 LCP Metric
- **Target:** <2.5s Largest Contentful Paint
- **Current:** ~3.0-3.5s (estimated from slow queries)
- **Success:** Achieves <2.5s

### 6.6 Redis Hit Rate
- **Target:** >80% for cached endpoints
- **Current:** 0% (no caching)
- **Success:** Achieves >80% hit rate

## Parallel Execution Map

```
T+0 ─────────────────── All 3 subtracks START
│
├─→ 6.4: Measure → Optimize Backend → Optimize Frontend → Validate
├─→ 6.5: Analyze → Fix Keys → Fix Invalidation → Test
├─→ 6.6: Setup Redis → Profile → Projects → Summary → Monitor
│
T+120 ─────────────────── All 3 subtracks COMPLETE
```

## Files to Modify

### 6.4 Dashboard N+1
- `backend/internal/handlers/dashboard_handler.go` (optimization)
- `frontend/apps/web/src/views/DashboardView.tsx` (parallel queries)
- `frontend/apps/web/src/api/system.ts` (query export)

### 6.5 React Query
- `frontend/apps/web/src/hooks/useProjects.ts` (cache keys + invalidation)
- `frontend/apps/web/src/hooks/useDashboardSummary.ts` (cache keys)

### 6.6 Redis Caching
- `backend/internal/cache/redis.go` (NEW - client setup)
- `backend/internal/middleware/cache.go` (NEW - caching middleware)
- `backend/internal/handlers/user_handler.go` (add cache invalidation)
- `backend/internal/handlers/project_handler.go` (add cache invalidation)

## Metrics to Report

### Performance Metrics
- Dashboard load time (ms)
- LCP score (seconds)
- Database query time (ms)
- API response time (ms)

### Cache Metrics
- Redis hit rate (%)
- Cache miss rate (%)
- Calls saved per hour
- Memory usage (MB)

---

## Implementation Status

### 6.4: [PENDING] Dashboard N+1 Optimization
Status: Ready for implementation
Files: 2 to modify

### 6.5: [PENDING] React Query Cache
Status: Ready for implementation
Files: 2 to modify

### 6.6: [PENDING] Redis Caching
Status: Ready for implementation
Files: 4 to create/modify

**Start Time:** 2026-02-06 02:00 UTC
**Est. Completion:** 2026-02-06 04:00 UTC
