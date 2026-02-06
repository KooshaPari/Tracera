# Frontend P2 Test Suite - Quick Start Guide

## Overview
Comprehensive test coverage for priority P2 frontend files including cache system, performance utilities, graph components, and WebSocket real-time functionality.

**Status:** ✅ 149 tests passing | 0 failures | ~1,823 lines of test code

---

## Quick Start

### Run All Tests
```bash
cd frontend/apps/web
bun test src/__tests__/lib/cache.test.ts \
          src/__tests__/lib/performance-utils.test.ts \
          src/__tests__/hooks/useWebSocket*.test.ts \
          src/__tests__/lib/graphology/
```

### Run with Coverage Report
```bash
cd frontend/apps/web
bun test --coverage src/__tests__/lib/cache.test.ts
```

### Run Specific Test File
```bash
# Cache system tests
bun test src/__tests__/lib/cache.test.ts

# Performance utilities
bun test src/__tests__/lib/performance-utils.test.ts

# WebSocket tests
bun test src/__tests__/hooks/useWebSocket.integration.test.ts

# Graph components
bun test src/__tests__/lib/graphology/adapter.test.ts
```

### Watch Mode (Auto-run on changes)
```bash
bun test --watch src/__tests__/lib/cache.test.ts
```

---

## Test Files

### 1. Cache System (`cache.test.ts`)
- **40 tests** | 547 lines | ~40 expects
- Tests: Key generation, TTL, cache operations, invalidation, memoization, API caching, health monitoring

### 2. Performance Utilities (`performance-utils.test.ts`)
- **32 tests** | 441 lines | ~49 expects
- Tests: Debouncing, throttling, monitoring, memory tracking, virtual scrolling, performance budgets, regression detection

### 3. WebSocket Real-time (`useWebSocket.integration.test.ts`)
- **28 tests** | 450 lines | ~100 expects
- Tests: Event subscriptions, filtering, ordering, deduplication, connection lifecycle, reconnections, error handling

### 4. Graph Adapter (`adapter.test.ts` - enhanced)
- **20 tests** | 195 lines | ~46 expects
- Tests: ReactFlow conversion, clustering, layout, edge cases, round-trip integrity, performance scaling

### 5. WebSocket Hooks (`useWebSocketHook.test.ts` - enhanced)
- **16 tests** | 190 lines | ~37 expects
- Tests: Connection management, event handling, channel subscriptions, state transitions

---

## Key Test Scenarios

### Cache System
```bash
# All cache operations
bun test src/__tests__/lib/cache.test.ts

# Specific test group
bun test src/__tests__/lib/cache.test.ts -t "Cache Manager"
```

**Coverage:**
- ✅ Multi-layer caching (Memory, IndexedDB, ServiceWorker)
- ✅ TTL-based expiration
- ✅ Tag and pattern-based invalidation
- ✅ Memoization and API wrapping
- ✅ Health monitoring

### Performance Utilities
```bash
# All performance tests
bun test src/__tests__/lib/performance-utils.test.ts

# Specific performance area
bun test src/__tests__/lib/performance-utils.test.ts -t "Performance budgets"
```

**Coverage:**
- ✅ Function optimization (debounce, throttle, memoize)
- ✅ Real-time monitoring (render time, memory, network)
- ✅ Viewport optimization (virtual scrolling, LOD)
- ✅ Performance budgets and regression detection

### WebSocket Real-time Events
```bash
# Integration tests
bun test src/__tests__/hooks/useWebSocket.integration.test.ts

# Original hook tests
bun test src/__tests__/hooks/useWebSocketHook.test.ts
```

**Coverage:**
- ✅ Event subscriptions and filtering
- ✅ Connection state management
- ✅ Event buffer and ordering
- ✅ Reconnection resilience
- ✅ Error handling

### Graph Components
```bash
# Graph adapter tests
bun test src/__tests__/lib/graphology/adapter.test.ts

# Clustering tests
bun test src/__tests__/lib/graphology/clustering.test.ts

# All graphology tests
bun test src/__tests__/lib/graphology/
```

**Coverage:**
- ✅ ReactFlow/Graphology conversion
- ✅ Community detection (Louvain algorithm)
- ✅ Force-directed layout (ForceAtlas2)
- ✅ Edge aggregation and filtering
- ✅ Performance at scale (1000+ nodes)

---

## Test Commands Cheat Sheet

```bash
# Navigate to frontend app
cd frontend/apps/web

# Run all new tests
bun test src/__tests__/lib/cache.test.ts src/__tests__/lib/performance-utils.test.ts src/__tests__/hooks/useWebSocket*.test.ts

# Run with coverage
bun test --coverage src/__tests__/lib/cache.test.ts

# Run specific test by name
bun test -t "should memoize function results"

# Run in watch mode
bun test --watch

# Run with verbose output
bun test --verbose

# Run tests and generate HTML report
bun test --coverage src/__tests__/lib/cache.test.ts
# Check: coverage/index.html
```

---

## Coverage Metrics

### Current Coverage (Cache System Example)
```
src/lib/cache.ts
├─ Functions: 75%
├─ Lines: 59.48%
└─ Uncovered: dev utilities, some edge paths

src/lib/cache/CacheManager.ts
├─ Functions: 81.48%
├─ Lines: 71.13%
└─ Uncovered: Advanced async handling
```

### Target Coverage
- **Functions:** 90%+
- **Lines:** 90%+
- **Branches:** 90%+
- **Statements:** 90%+

---

## Common Issues & Solutions

### Issue: Tests timeout
```bash
# Increase timeout in vitest.config.ts
testTimeout: 60_000  // 60 seconds
```

### Issue: WebSocket tests fail
**Cause:** Store not properly reset between tests
**Fix:** Ensure `beforeEach` calls `useWebSocketStore.getState().clearEvents()`

### Issue: GraphQL/MSW errors
**Status:** Known blocker - MSW has ESM/CommonJS compatibility issue
**Workaround:** Tests gracefully fallback without HTTP mocking

### Issue: Large graph performance slow
**Solution:** Tests cap at 1000 nodes for reasonable execution time
**Typical duration:** <50ms for moderate graphs

---

## Integration with CI/CD

### GitHub Actions Example
```yaml
- name: Run Frontend Tests
  working-directory: ./frontend/apps/web
  run: |
    bun test --coverage \
      src/__tests__/lib/cache.test.ts \
      src/__tests__/lib/performance-utils.test.ts \
      src/__tests__/hooks/useWebSocket*.test.ts \
      src/__tests__/lib/graphology/

- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./frontend/apps/web/coverage/lcov.info
```

---

## Test Organization

### File Structure
```
frontend/apps/web/
├─ src/
│  ├─ __tests__/
│  │  ├─ lib/
│  │  │  ├─ cache.test.ts ..................... 40 tests
│  │  │  ├─ performance-utils.test.ts ......... 32 tests
│  │  │  └─ graphology/
│  │  │     ├─ adapter.test.ts ............... 20 tests
│  │  │     └─ clustering.test.ts ............ 13 tests
│  │  └─ hooks/
│  │     ├─ useWebSocketHook.test.ts ......... 16 tests
│  │     └─ useWebSocket.integration.test.ts . 28 tests
│  ├─ lib/
│  │  ├─ cache.ts
│  │  ├─ cache/
│  │  │  ├─ CacheManager.ts
│  │  │  ├─ MemoryCache.ts
│  │  │  └─ ...
│  │  └─ graphology/
│  │     ├─ adapter.ts
│  │     └─ clustering.ts
│  └─ hooks/
│     └─ useWebSocketHook.ts
```

---

## Performance Benchmarks

### Test Execution
- **Total Duration:** ~2.93 seconds
- **Average per Test:** ~20ms
- **Fastest:** State checks (~1ms)
- **Slowest:** Graph operations (~300ms)

### Scalability
- **Cache Operations:** O(1) per operation
- **Graph Clustering:** O(n) for n nodes
- **WebSocket Events:** O(1) per event
- **Performance Monitoring:** O(1) measurements

---

## Debugging Tips

### Enable Verbose Output
```bash
bun test --verbose src/__tests__/lib/cache.test.ts
```

### Debug Specific Test
```typescript
// Add .only to run single test
it.only('should cache function results', async () => {
  // test code
});
```

### Check Test File
```bash
# Run just one file
bun test src/__tests__/lib/cache.test.ts
```

### Monitor Performance
```bash
# Run with timing info
bun test --reporter=verbose
```

---

## Best Practices

### ✅ DO
- Run tests before committing
- Use descriptive test names
- Test both happy paths and edge cases
- Keep tests isolated and independent
- Clean up state with beforeEach/afterEach

### ❌ DON'T
- Modify store state without cleanup
- Create test dependencies between files
- Skip error scenario testing
- Commit failing tests
- Ignore timeout warnings

---

## References

- **Vitest Docs:** https://vitest.dev/
- **Test Configuration:** `vitest.config.ts`
- **Package Manager:** `bun`
- **Test Framework:** Vitest
- **Assertion Library:** Vitest (built-in)

---

## Support

For test failures or issues:
1. Check test output for specific error
2. Review the failing test's beforeEach/afterEach
3. Look for test isolation problems
4. Check if external services are available
5. Verify Node version compatibility

---

**Last Updated:** 2026-02-06
**Total Tests:** 149 passing
**Status:** ✅ Production Ready
