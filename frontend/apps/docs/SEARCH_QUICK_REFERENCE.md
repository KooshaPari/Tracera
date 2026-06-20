# Search Performance - Quick Reference

## Quick Start

### Build Search Index

```bash
bun run search:index
```

### Run Benchmark

```bash
bun run search:benchmark
```

### Run E2E Tests

```bash
bun run test:e2e search-performance
```

## Usage

### Basic Search Hook

```tsx
import { useSearchWorker } from '@/lib/use-search-worker';

function MyComponent() {
  const { search, results, isReady, isSearching, performance } = useSearchWorker();

  useEffect(() => {
    if (isReady) {
      search('my query', 20);
    }
  }, [isReady]);

  return (
    <div>
      {isSearching && <p>Searching...</p>}
      {results.map((result) => (
        <div key={result.item.id}>
          <h3>{result.item.title}</h3>
          <p>{result.item.description}</p>
        </div>
      ))}
      <p>Search took: {performance.searchDuration}ms</p>
    </div>
  );
}
```

### Full Search UI

```tsx
import { InstantSearch } from '@/components/instant-search';

function App() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button onClick={() => setIsOpen(true)}>Search</button>
      <InstantSearch
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        placeholder='Search docs...'
        maxResults={20}
      />
    </>
  );
}
```

## Configuration

### Search Weights

Edit `lib/search-config.ts`:

```ts
export const searchConfig = {
  weights: {
    title: 10, // Most important
    description: 5, // Very relevant
    heading: 3, // Moderately important
    content: 1, // Baseline
  },
  priorityPages: ['/docs', '/docs/getting-started'],
  minQueryLength: 2,
  maxResults: 50,
};
```

### Fuse.js Options

Edit `scripts/build-search-index.ts`:

```ts
const fuseOptions = {
  threshold: 0.35, // Lower = stricter matching
  distance: 80, // Max char distance for fuzzy
  ignoreLocation: false, // Prefer matches at start
  keys: [
    { name: 'title', weight: 10 },
    { name: 'description', weight: 5 },
    { name: 'headings', weight: 3 },
  ],
};
```

## Performance Tuning

### If searches are too slow (>100ms)

1. **Reduce content length**

   ```ts
   content: content.slice(0, 500), // Reduce from 1000
   ```

2. **Remove search keys**

   ```ts
   keys: [
     { name: 'title', weight: 10 },
     // Remove description and headings
   ],
   ```

3. **Decrease distance**

   ```ts
   distance: 50, // Reduce from 80
   ```

4. **Limit results**
   ```ts
   const results = fuse.search(query, { limit: 10 }); // Reduce from 20
   ```

### If index is too large (>200KB)

1. **Reduce content per page**

   ```ts
   content: content.slice(0, 500),
   ```

2. **Limit headings**

   ```ts
   headings: headings.slice(0, 5),
   ```

3. **Remove fields**
   ```ts
   // Don't index content field
   ```

### If relevance is poor

1. **Increase threshold**

   ```ts
   threshold: 0.4, // More lenient fuzzy matching
   ```

2. **Adjust weights**

   ```ts
   weights: {
     title: 20,      // Even more important
     description: 3,
   },
   ```

3. **Enable location**
   ```ts
   ignoreLocation: false,
   location: 0, // Prefer matches at beginning
   ```

## Keyboard Shortcuts

| Key                | Action                |
| ------------------ | --------------------- |
| `Cmd+K` / `Ctrl+K` | Open search           |
| `↑` / `↓`          | Navigate results      |
| `Enter`            | Go to selected result |
| `Esc`              | Close search          |

## File Reference

| File                             | Purpose                            |
| -------------------------------- | ---------------------------------- |
| `scripts/build-search-index.ts`  | Build search index at compile time |
| `scripts/benchmark-search.ts`    | Performance benchmarking           |
| `lib/search.worker.ts`           | Web worker for background search   |
| `lib/use-search-worker.ts`       | React hook for search              |
| `lib/search-config.ts`           | Search configuration               |
| `components/instant-search.tsx`  | Search UI component                |
| `public/search-index.json`       | Generated search index             |
| `e2e/search-performance.spec.ts` | E2E tests                          |

## Benchmarks

### Expected Performance

```
Average: 8.75ms
Min: 0.80ms
Max: 46.39ms
P95: 46.39ms
Under 100ms: 100%
```

### Test Queries

```ts
const queries = [
  'api', // Short
  'getting started', // Medium
  'authentication and authorization', // Long
  'proj', // Partial
];
```

## Troubleshooting

### Worker not loading

```bash
# Rebuild search index
bun run search:index

# Check file exists
ls -la public/search-index.json

# Check browser console for errors
```

### Slow performance

```bash
# Run benchmark to identify slow queries
bun run search:benchmark

# Check index size
du -h public/search-index.json

# Optimize configuration (see above)
```

### No results

1. Check query length (min 2 chars)
2. Try broader search terms
3. Check index contains expected pages
4. Reduce threshold for stricter matching

## Scripts

### package.json

```json
{
  "scripts": {
    "prebuild": "bun run scripts/build-search-index.ts",
    "search:index": "bun run scripts/build-search-index.ts",
    "search:benchmark": "bun run scripts/benchmark-search.ts"
  }
}
```

## Dependencies

```json
{
  "dependencies": {
    "fuse.js": "^7.1.0",
    "@tanstack/react-virtual": "^3.13.18"
  }
}
```

## Success Metrics

- [x] Average search time <50ms (achieved: 8.75ms)
- [x] P95 search time <100ms (achieved: 46.39ms)
- [x] 100% success rate on benchmarks
- [x] Index size <200KB (achieved: 37KB)
- [x] Virtual scrolling for results
- [x] Web worker implementation
- [x] Keyboard navigation
- [x] Match highlighting

## Next Steps

1. Integrate `<InstantSearch />` into main app layout
2. Add search analytics tracking
3. Implement debounced search (150ms)
4. Add search result click tracking
5. Create search suggestions feature
