# Bundle Optimization Quick Reference

## Key Files

### Configuration

- **vite.config.mjs** - Manual chunks, sourcemaps, optimizeDeps
- **BUNDLE_OPTIMIZATION.md** - Complete documentation

### Utilities

- **src/lib/lazy-loading.tsx** - Loading states, lazy component wrappers

### Routes Updated

- **src/routes/graph.index.tsx** - Improved loading state
- **src/routes/api-docs.swagger.tsx** - Improved loading state
- **src/routes/api-docs.redoc.tsx** - Improved loading state
- **src/routes/projects.$projectId.views.$viewType.tsx** - Improved loading state

## Using the Utilities

### Show Loading State

```typescript
import { ChunkLoadingSkeleton } from '@/lib/lazy-loading';

<Suspense fallback={<ChunkLoadingSkeleton message="Loading..." />}>
  <HeavyComponent />
</Suspense>
```

### Show Error State

```typescript
import { ChunkErrorFallback } from '@/lib/lazy-loading';

<ErrorBoundary fallback={({ error, retry }) => (
  <ChunkErrorFallback error={error} retry={retry} />
)}>
  <Component />
</ErrorBoundary>
```

### Lazy Load Component

```typescript
import { useLazyComponent } from '@/lib/lazy-loading';

const MyComponent = useLazyComponent(
  () => import('./HeavyComponent')
);

<MyComponent prop1="value" />
```

## Bundle Size Targets

### Initial Load (Critical Path)

- Target: <500KB gzipped
- Current: ~370KB gzipped
- Status: ✓ Met

### Total Bundle

- Target: <2.5MB gzipped
- Current: ~2.3MB gzipped
- Status: ✓ Met

## Measuring Performance

### Automated Analysis

```bash
cd frontend/apps/web
bash scripts/analyze-bundle.sh
```

### Manual Check

```bash
# Check specific chunk
ls -lh dist/assets/vendor-graph-elk-*.js

# Total size
du -sh dist/assets/*.js

# Gzipped estimate (divide by 3-4)
du -sh dist/assets/index-*.js
```

## Lazy Chunks

### Always Loaded

- vendor-react (~260KB)
- vendor-router (~110KB)
- vendor-radix (~150KB)
- Application code (~880KB)

### Loaded on Demand

| Chunk             | Size  | When Loaded        |
| ----------------- | ----- | ------------------ |
| vendor-api-docs   | 2.4MB | `/api-docs` routes |
| vendor-graph-elk  | 1.4MB | Graph views        |
| vendor-graph-core | 476KB | Graph views        |
| vendor-charts     | 424KB | Dashboard/Reports  |
| vendor-forms      | 128KB | Form-heavy pages   |
| vendor-monaco     | 12KB  | Code editor        |

## Build Time

- Before: 12-15s (with embedded sourcemaps)
- After: 9-12s (with hidden sourcemaps)
- Improvement: 2-3s faster

## Testing

### Verify Lazy Loading Works

```typescript
test('graph view lazy loads', async () => {
  render(<Suspense fallback={<div>Loading</div>}><GraphView /></Suspense>);

  // Shows loading first
  expect(screen.getByText('Loading')).toBeInTheDocument();

  // Eventually renders
  await waitFor(() => {
    expect(screen.getByTestId('graph-canvas')).toBeInTheDocument();
  });
});
```

### Check Chunk Separation

```bash
# Should see vendor-graph-elk chunk
ls dist/assets/vendor-graph-elk-*.js

# Should see vendor-api-docs chunk
ls dist/assets/vendor-api-docs-*.js

# Monaco should be tiny (~12KB)
ls -lh dist/assets/vendor-monaco-*.js
```

## Future Improvements

1. **Prefetching** - Preload likely next routes
2. **CSS Splitting** - Split CSS per route
3. **Dynamic Imports** - More granular code splitting
4. **Service Worker** - Cache chunks for offline
5. **Image Optimization** - Lazy load images
6. **Compression** - Brotli compression on CDN

## Troubleshooting

### Bundle Size Increased?

1. Check what changed: `git diff dist/assets`
2. Run analysis: `bash scripts/analyze-bundle.sh`
3. Identify new large imports
4. Consider lazy loading or excluding from pre-bundling

### Slow Load Times?

1. Check Network tab in DevTools
2. Look for chunks that should be lazy-loaded
3. Add prefetching for common next routes
4. Enable Brotli compression on CDN

### Chunk Not Separating?

1. Verify module path in vite.config.mjs manualChunks
2. Check that import is at top level
3. Rebuild: `bun run build`
4. Check dist/assets for chunk file

## CLI Commands

```bash
# Build
bun run build

# Type check
bun run typecheck

# Lint
bun run lint:fix

# Analyze bundle
bash scripts/analyze-bundle.sh

# Development with HMR
bun run dev
```

## Performance Goals

- Initial page load: <2s (on 3G)
- First Contentful Paint: <1s
- Largest Contentful Paint: <2s
- Cumulative Layout Shift: <0.1
- First Input Delay: <100ms

## More Info

See **BUNDLE_OPTIMIZATION.md** for comprehensive documentation including:

- Detailed bundle breakdown
- How each optimization works
- Testing strategies
- Monitoring setup
- Future improvements
