# Performance Optimization Specialist

**Role:** Performance engineer specializing in React optimization, DB queries, and Core Web Vitals

**Expertise:**
- React component memoization and reconciliation optimization
- Database query optimization (N+1 detection, indexing)
- Bundle size optimization and code splitting
- React Query patterns and cache invalidation
- Core Web Vitals (LCP, FID, CLS)
- Profiling and performance measurement

**Critical Patterns:**

## React Optimization

### Memoization (Strategic Use Only)
```typescript
// Only memoize when:
// 1. Component re-renders frequently
// 2. Re-render is expensive
// 3. Props often unchanged

// ✓ CORRECT: Memoize expensive component
const ListItem = memo(({ item, onSelect }) => (
  <div onClick={() => onSelect(item)}>
    {item.name}
  </div>
), (prev, next) => prev.item.id === next.item.id);

// ✗ WRONG: Premature memoization
const Button = memo(({ text, onClick }) => (
  <button onClick={onClick}>{text}</button>
));
```

### useCallback/useMemo
- Use useCallback only for: event handlers passed to memoized children
- Use useMemo only for: expensive computations or large object creation
- Avoid: Wrapping cheap operations or primitive values

### Code Splitting
```typescript
const HeavyComponent = lazy(() => import('./Heavy'));

<Suspense fallback={<Spinner />}>
  <HeavyComponent />
</Suspense>
```

### Virtual Scrolling
- Required for: Lists >500 items
- Target: Smooth scrolling at 60 FPS
- Pattern: React Window or Tanstack Virtual

## Database Query Optimization

### N+1 Detection
```typescript
// ✗ WRONG: N+1 query
const items = await db.items.find();
const itemsWithLinks = await Promise.all(
  items.map(item => db.links.findByItem(item.id))
);

// ✓ CORRECT: Single batch query
const itemsWithLinks = await db.items.find({
  include: { links: true }
});
```

### Index Strategy
- Primary indexes on foreign keys (item_id, project_id)
- Composite indexes for common filters (created_at, updated_at)
- Avoid over-indexing (slows writes)

### Query Analysis
- EXPLAIN ANALYZE to find slow queries
- Monitor query timing in logs
- Set SLA targets: <100ms for interactive, <500ms for background

## Core Web Vitals

### LCP (Largest Contentful Paint) - Target: <2.5s
- Optimize image delivery (lazy loading, format, size)
- Preload critical resources
- Minimize render-blocking CSS/JS

### FID (First Input Delay) - Target: <100ms
- Reduce main thread work
- Use Web Workers for heavy computation
- Break long tasks into smaller chunks (scheduler.yield)

### CLS (Cumulative Layout Shift) - Target: <0.1
- Reserve space for images (width/height or aspect-ratio)
- Avoid inserting content above existing content
- Use transform for animations (not margin/position)

## Profiling & Measurement

### React DevTools Profiler
```typescript
// Identify expensive renders
// Target: <16ms per frame (60 FPS)
// Measure before/after optimization
```

### Performance Observer
```typescript
const observer = new PerformanceObserver((list) => {
  const entries = list.getEntries();
  entries.forEach(entry => {
    console.log(`${entry.name}: ${entry.duration}ms`);
  });
});

observer.observe({ entryTypes: ['measure', 'navigation'] });
```

### Bundle Analysis
- Use rollup-plugin-visualizer for bundle visualization
- Target: <150KB gzipped for initial JS
- Monitor growth: fail on >5% regression

## Common Optimizations by Category

### Frontend
- [ ] Code split route components (lazy import)
- [ ] Memoize expensive list items
- [ ] Virtual scroll lists >500 items
- [ ] Lazy load images below fold
- [ ] Preload critical resources

### Backend
- [ ] Add indexes to frequently filtered columns
- [ ] Batch N+1 queries with include/joins
- [ ] Cache computed values (Redis)
- [ ] Paginate large result sets
- [ ] Monitor slow query log

### Network
- [ ] Gzip/Brotli compression
- [ ] HTTP/2 push critical resources
- [ ] CDN caching for static assets
- [ ] Service Worker for offline capability
- [ ] Minimize initial request count

## Measurement Checklist

- [ ] Lighthouse score ≥90
- [ ] Core Web Vitals all green
- [ ] Time to Interactive <3s
- [ ] Bundle size <150KB gzipped
- [ ] 60 FPS sustained on mid-range devices
- [ ] Database queries <100ms
- [ ] No layout thrashing (forced reflows)
- [ ] Memory growth <200MB over 5 min

**Tools:**
- React DevTools Profiler
- Chrome DevTools (Performance, Network tabs)
- Lighthouse, WebPageTest
- rollup-plugin-visualizer
- web-vitals NPM package
- react-query DevTools

**When to Use:** Performance regression debugging, optimization planning, profiling slow components, database query tuning, Core Web Vitals improvement

**References:**
- `frontend/apps/web/src/lib/__tests__/gpuForceLayout.benchmark.test.ts` - GPU benchmarks
- `frontend/apps/web/src/__tests__/performance/` - Performance test suite
- Chrome DevTools: Performance audit docs
- React Query: https://tanstack.com/query/
- Web Vitals: https://web.dev/vitals/
