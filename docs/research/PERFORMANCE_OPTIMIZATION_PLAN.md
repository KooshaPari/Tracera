# Performance Optimization Plan - TraceRTM

## Executive Summary

This plan outlines performance optimizations across the frontend (React/Vite) and backend (FastAPI/Redis) stack, based on research from 2025 best practices.

---

## Current State

### Frontend

- **Vite**: 8.0.0-beta.11 (Rolldown-powered)
- **React**: 19.2.0
- **Node.js**: 25.5.0
- **Bundle Size**: 553 KB main (down from 6.3 MB after code-splitting)
- **Build Time**: ~5 seconds

### Backend

- **FastAPI**: async Python API
- **Redis**: CacheService exists but UNUSED
- **Hatchet**: Workflow orchestration configured
- **90+ API endpoints** across 8 routers

---

## Phase 1: Immediate Fixes (Priority: Critical)

### 1.1 Fix Storybook Build (Node.js 25 Incompatibility)

**Issue**: Storybook 10.2.1 has multiple incompatibilities with Node.js 25.5.0:

1. `doctrine` package throws "Middle is not a constructor" (ESM/CJS issue)
2. `ERR_MODULE_NOT_FOUND` for preset imports without `.js` extension (stricter ESM resolution)

**Current Status**: ⚠️ **BLOCKED** - Storybook 10 is not compatible with Node.js 25.

**Workarounds**:

1. **Use Node.js 22 (Recommended)**: Install Node.js 22.x via nvm for Storybook commands

   ```bash
   nvm install 22
   nvm use 22
   bun run --cwd apps/storybook build
   ```

2. **Wait for Storybook fix**: Monitor [Storybook Issue #31284](https://github.com/storybookjs/storybook/issues/31284) for updates

3. **NODE_OPTIONS flag** (Partial fix - works for Node.js 22.12-22.14, not 25):
   ```json
   {
     "scripts": {
       "dev:node22": "NODE_OPTIONS=--no-experimental-require-module storybook dev -p 6006",
       "build:node22": "NODE_OPTIONS=--no-experimental-require-module storybook build"
     }
   }
   ```

**Root Cause**: Node.js 25 has stricter ESM module resolution that requires explicit `.js` extensions. Storybook's internal code imports presets without extensions.

**References**:

- [Storybook Issue #31284](https://github.com/storybookjs/storybook/issues/31284)
- [Node.js Issue #57555](https://github.com/nodejs/node/issues/57555)

### 1.2 Fix SWC Plugin Warning

**Issue**: `vite:react-swc` uses deprecated `esbuild` option.

**Solution**: SWC plugin needs update for Vite 8. For now, this is just a warning and doesn't affect builds.

---

## Phase 2: Frontend Optimizations (Priority: High)

### 2.1 React Compiler Integration (Automatic Memoization)

**Benefit**: 30-60% reduction in unnecessary re-renders, automatic optimization without manual `useMemo`/`useCallback`.

**Implementation**:

```bash
bun add -d babel-plugin-react-compiler@latest
```

```javascript
// vite.config.mjs
import reactSWC from '@vitejs/plugin-react-swc';

export default defineConfig({
  plugins: [
    reactSWC({
      plugins: [['babel-plugin-react-compiler', {}]],
    }),
  ],
});
```

**Note**: React Compiler works with React 17+, best with React 19.

**References**:

- [React Compiler v1.0](https://react.dev/blog/2025/10/07/react-compiler-1)
- [React 19 Memoization Guide](https://dev.to/joodi/react-19-memoization-is-usememo-usecallback-no-longer-necessary-3ifn)

### 2.2 Enhanced TanStack Query Caching

**Current Config**:

```javascript
staleTime: 2 * 60 * 1000,  // 2 minutes
gcTime: 10 * 60 * 1000,    // 10 minutes
```

**Optimized Config by Query Type**:

```typescript
// src/lib/queryConfig.ts
export const QUERY_CONFIGS = {
  // Static data (projects list, item types)
  static: {
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
    refetchOnMount: false,
  },

  // Frequently changing (items, links)
  dynamic: {
    staleTime: 30 * 1000, // 30 seconds
    gcTime: 5 * 60 * 1000, // 5 minutes
    refetchOnMount: true,
  },

  // Graph data (expensive computations)
  graph: {
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 15 * 60 * 1000, // 15 minutes
    refetchOnMount: false,
  },

  // Real-time data
  realtime: {
    staleTime: 0, // Always stale
    gcTime: 1 * 60 * 1000, // 1 minute
    refetchInterval: 5000, // 5 seconds
  },
};
```

**References**:

- [TanStack Query Caching](https://tanstack.com/query/v5/docs/react/guides/caching)
- [Caching Strategies Guide](https://www.dhiwise.com/post/optimizing-performance-with-react-query-v5-best-practices)

### 2.3 Image Optimization

**Install Plugin**:

```bash
bun add -d vite-plugin-image-optimizer sharp svgo
```

**Configure**:

```javascript
// vite.config.mjs
import { ViteImageOptimizer } from 'vite-plugin-image-optimizer';

plugins: [
  ViteImageOptimizer({
    png: { quality: 80 },
    jpeg: { quality: 75 },
    webp: { quality: 80, lossless: false },
    avif: { quality: 70, lossless: false },
    svg: {
      plugins: [{ name: 'removeViewBox', active: false }],
    },
  }),
],
```

**References**:

- [vite-plugin-image-optimizer](https://github.com/FatehAK/vite-plugin-image-optimizer)
- [Modern Image Optimization 2025](https://www.frontendtools.tech/blog/modern-image-optimization-techniques-2025)

### 2.4 Prefetching Critical Routes

```typescript
// src/routes/__root.tsx
import { useEffect } from 'react';
import { useRouter } from '@tanstack/react-router';

function RootComponent() {
  const router = useRouter();

  useEffect(() => {
    // Prefetch likely navigation targets
    router.preloadRoute({ to: '/projects' });
    router.preloadRoute({ to: '/graph' });
  }, [router]);

  return <Outlet />;
}
```

### 2.5 Font Optimization

```css
/* src/index.css */
@font-face {
  font-family: 'Inter';
  src: url('/fonts/inter-var.woff2') format('woff2');
  font-display: swap; /* Prevents FOIT */
  font-weight: 100 900;
}
```

---

## Phase 3: Backend Optimizations (Priority: High) ✅ IMPLEMENTED

### 3.1 Integrate Redis Caching for API Endpoints ✅

**Status**: COMPLETE - Redis caching integrated into key API endpoints.

**Implemented Endpoints**:

1. `GET /api/v1/projects` - List projects (10 min cache)
2. `GET /api/v1/projects/{id}` - Get project (5 min cache)
3. `GET /api/v1/projects/{id}/graphs` - List graphs (5 min cache)
4. `GET /api/v1/projects/{id}/graph` - Graph projection (10 min cache)

**New Endpoints**:

- `GET /api/v1/cache/stats` - Cache statistics monitoring
- `POST /api/v1/cache/clear` - Clear cache (admin only)

**Files Modified**:

- `src/tracertm/services/cache_service.py` - Upgraded to async Redis with connection pooling
- `src/tracertm/api/deps.py` - Added `get_cache_service()` dependency
- `src/tracertm/api/main.py` - Integrated caching into endpoints

**Previous State**: `CacheService` existed but was NOT integrated with any routes.

**Target Endpoints** (high-traffic, expensive queries):

1. `GET /api/v1/projects` - List projects
2. `GET /api/v1/graph/full` - Full graph data
3. `GET /api/v1/graph/ancestors/{id}` - Graph traversal
4. `GET /api/v1/graph/descendants/{id}` - Graph traversal
5. `GET /api/v1/items` - List items
6. `GET /api/v1/search` - Search results

**Implementation Pattern**:

```python
# src/tracertm/api/deps.py
from functools import lru_cache
from tracertm.services.cache_service import CacheService

@lru_cache()
def get_cache_service() -> CacheService:
    return CacheService()

# src/tracertm/api/routers/projects.py
from tracertm.api.deps import get_cache_service

@router.get("/")
async def list_projects(
    db: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache_service),
):
    cache_key = "projects:list"

    # Try cache first
    cached = await cache.get(cache_key)
    if cached:
        return cached

    # Fetch from DB
    result = await project_repository.list_all(db)

    # Cache for 5 minutes
    await cache.set(cache_key, result, ttl_seconds=300)

    return result
```

**Cache Invalidation**:

```python
@router.post("/")
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache_service),
):
    project = await project_repository.create(db, data)

    # Invalidate list cache
    await cache.delete("projects:list")

    return project
```

**References**:

- [Redis with FastAPI Tutorial](https://redis.io/tutorials/develop/python/fastapi/)
- [FastAPI Caching Best Practices](https://dev.to/sivakumarmanoharan/caching-in-fastapi-unlocking-high-performance-development-20ej)

### 3.2 Async Redis Client Optimization

**Current**: Uses synchronous `redis.from_url()`

**Optimized**:

```python
# src/tracertm/services/cache_service.py
import redis.asyncio as redis

class CacheService:
    def __init__(self, redis_url: str | None = None):
        redis_url = redis_url or "redis://localhost:6379"
        self.redis_client = redis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,  # Connection pooling
        )
```

### 3.3 Graph Query Caching Strategy

Graph operations are expensive. Implement tiered caching:

```python
GRAPH_CACHE_CONFIG = {
    "full_graph": {
        "ttl": 600,           # 10 minutes
        "key_pattern": "graph:full:{project_id}",
    },
    "ancestors": {
        "ttl": 300,           # 5 minutes
        "key_pattern": "graph:ancestors:{item_id}:{depth}",
    },
    "descendants": {
        "ttl": 300,           # 5 minutes
        "key_pattern": "graph:descendants:{item_id}:{depth}",
    },
    "impact_analysis": {
        "ttl": 180,           # 3 minutes (more volatile)
        "key_pattern": "graph:impact:{item_id}:{depth}",
    },
}
```

### 3.4 Database Query Optimization

Add SQLAlchemy query caching for hot paths:

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# Eager load relationships to avoid N+1 queries
stmt = (
    select(Item)
    .options(selectinload(Item.links))
    .options(selectinload(Item.project))
    .where(Item.project_id == project_id)
)
```

---

## Phase 4: Infrastructure Optimizations (Priority: Medium)

### 4.1 HTTP Caching Headers

```python
# src/tracertm/api/middleware.py
from starlette.middleware.base import BaseHTTPMiddleware

class CacheHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)

        # Static assets
        if request.url.path.startswith("/static"):
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"

        # API responses (conditional)
        elif request.url.path.startswith("/api"):
            if request.method == "GET":
                response.headers["Cache-Control"] = "private, max-age=60"

        return response
```

### 4.2 Compression (Already handled by Vite 8)

Vite 8 with Rolldown uses Lightning CSS for CSS minification and Oxc for JS minification. No additional config needed.

### 4.3 CDN Configuration (Production)

For Vercel deployment:

```json
// vercel.json
{
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [{ "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }]
    }
  ]
}
```

---

## Phase 5: Monitoring & Measurement (Priority: Medium)

### 5.1 Performance Metrics to Track

| Metric                         | Target  | Tool              |
| ------------------------------ | ------- | ----------------- |
| LCP (Largest Contentful Paint) | < 2.5s  | Lighthouse        |
| FID (First Input Delay)        | < 100ms | Lighthouse        |
| CLS (Cumulative Layout Shift)  | < 0.1   | Lighthouse        |
| TTI (Time to Interactive)      | < 3.8s  | Lighthouse        |
| Bundle Size (main)             | < 500KB | Vite build output |
| API Response Time (p95)        | < 200ms | FastAPI metrics   |
| Redis Hit Rate                 | > 80%   | Redis INFO        |

### 5.2 Add Performance Monitoring

```typescript
// src/lib/performance.ts
export function reportWebVitals() {
  if (typeof window !== 'undefined' && 'performance' in window) {
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        console.log(`[Perf] ${entry.name}: ${entry.startTime.toFixed(2)}ms`);
        // Send to analytics
      }
    });

    observer.observe({ entryTypes: ['largest-contentful-paint', 'first-input', 'layout-shift'] });
  }
}
```

---

## Implementation Order

| Phase | Task                      | Priority | Effort | Impact                  |
| ----- | ------------------------- | -------- | ------ | ----------------------- |
| 1.1   | Fix Storybook Node.js 25  | Critical | Low    | Unblocks builds         |
| 1.2   | SWC warning (monitor)     | Low      | None   | Informational           |
| 2.1   | React Compiler            | High     | Medium | 30-60% fewer re-renders |
| 2.2   | TanStack Query config     | High     | Low    | Reduced API calls       |
| 2.3   | Image optimization        | Medium   | Low    | 50-80% image savings    |
| 3.1   | Redis caching integration | High     | Medium | 3-10x faster API        |
| 3.2   | Async Redis client        | High     | Low    | Better concurrency      |
| 3.3   | Graph query caching       | High     | Medium | Critical path speedup   |
| 4.1   | HTTP cache headers        | Medium   | Low    | Browser caching         |
| 5.1   | Performance monitoring    | Medium   | Medium | Visibility              |

---

## Expected Results

After implementing all phases:

| Metric                  | Current | Target   |
| ----------------------- | ------- | -------- |
| Initial Load            | ~1.5s   | < 1.0s   |
| Bundle Size             | 553 KB  | < 500 KB |
| API Response (cached)   | N/A     | < 50ms   |
| API Response (uncached) | ~200ms  | < 150ms  |
| Redis Hit Rate          | 0%      | > 80%    |
| Build Time              | 5s      | < 4s     |

---

## References

### Frontend

- [Vite 8 Beta Announcement](https://vite.dev/blog/announcing-vite8-beta)
- [React Performance 15 Best Practices 2025](https://dev.to/alex_bobes/react-performance-optimization-15-best-practices-for-2025-17l9)
- [TanStack Query Caching](https://tanstack.com/query/v5/docs/react/guides/caching)
- [vite-plugin-image-optimizer](https://github.com/FatehAK/vite-plugin-image-optimizer)

### Backend

- [Redis FastAPI Tutorial](https://redis.io/tutorials/develop/python/fastapi/)
- [FastAPI Caching Best Practices](https://blog.poespas.me/posts/2025/03/01/fastapi-context-based-caching-redis/)
- [3x Faster FastAPI with Redis](https://medium.com/@bhagyarana80/3x-faster-responses-in-fastapi-smart-caching-with-async-lru-and-redis-for-high-concurrency-apis-6b8428772f22)

### React Compiler

- [React Compiler v1.0](https://react.dev/blog/2025/10/07/react-compiler-1)
- [InfoQ: React Compiler Brings Automatic Memoization](https://www.infoq.com/news/2025/12/react-compiler-meta/)
