# Frontend P2 Priority Tests - Quick Reference
**Last Updated:** 2026-02-06

## Test Files Added/Modified

### Primary Test Files
| File | Original | Enhanced | Tests Added | Coverage Target |
|------|----------|----------|------------|-----------------|
| `src/__tests__/hooks/useProjects.test.ts` | 181 lines | 559 lines | 19 | 90%+ |
| `src/__tests__/hooks/useLinks.test.ts` | 202 lines | 628 lines | 22 | 90%+ |

## Quick Commands

```bash
# Run specific hook tests
cd frontend/apps/web
bun test src/__tests__/hooks/useProjects.test.ts
bun test src/__tests__/hooks/useLinks.test.ts

# Run both with coverage
bun test --coverage src/__tests__/hooks/useProjects.test.ts src/__tests__/hooks/useLinks.test.ts

# Watch mode for development
bun test --watch src/__tests__/hooks/useProjects.test.ts

# Verbose output
bun test --run --reporter=verbose src/__tests__/hooks/useLinks.test.ts
```

## Test Structure Overview

### useProjects.test.ts
```
describe('useProjects', 6 tests)
describe('useProject', 5 tests)
describe('useCreateProject', 5 tests)
describe('useUpdateProject', 3 tests)
describe('useDeleteProject', 3 tests)
```

### useLinks.test.ts
```
describe('useLinks', 11 tests)
describe('useCreateLink', 5 tests)
describe('useDeleteLink', 3 tests)
describe('useTraceabilityGraph', 3 tests)
```

## Key Test Categories

### Error Path Testing
- **HTTP 4xx errors**: 400, 403, 404
- **HTTP 5xx errors**: 500
- **Error message extraction**: From response.text()

### Data Transformation Testing
- **Input transformation**: camelCase → snake_case in request bodies
- **Output transformation**: snake_case → camelCase in responses
- **Field mapping**: created_at/updated_at timestamp handling

### Query & Filter Testing
- **Single filters**: sourceId, targetId, projectId, type
- **Filter combinations**: Multiple filters together
- **Pagination**: limit, offset parameters
- **Advanced filters**: excludeTypes array joining

### Edge Cases
- Empty arrays vs object responses
- Missing optional fields
- Empty ID/project IDs (fetch disabled)
- Large datasets (1000+ edges)
- Progressive loading behavior

## Coverage Focus Areas

### Authentication
✓ Token in Authorization header
✓ Bearer prefix construction
✓ Empty/missing token handling

### Headers
✓ X-Bulk-Operation: 'true' on bulk endpoints
✓ Content-Type: application/json on POST/PATCH
✓ Authorization header on all authenticated requests

### Query Cache
✓ Invalidation on mutations
✓ Query key composition
✓ Enabled/disabled conditions

### Response Handling
✓ Array format responses
✓ Object with data property
✓ Nested property access
✓ Total count extraction

## Test Patterns Reference

### Fetch Mock Setup
```typescript
const mockFetch = vi.fn();
globalThis.fetch = mockFetch as unknown as typeof fetch;

beforeEach(() => {
  vi.clearAllMocks();
});
```

### QueryClient Wrapper
```typescript
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      mutations: { retry: false },
      queries: { retry: false },
    },
  });
  return ({ children }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
};
```

### Error Response Mock
```typescript
mockFetch.mockResolvedValueOnce({
  ok: false,
  status: 404,
  text: async () => 'Not found',
});
```

### Async Assertion
```typescript
await waitFor(() => {
  expect(result.current.isSuccess).toBeTruthy();
});
```

## Coverage Metrics

| Aspect | Before | After | Target |
|--------|--------|-------|--------|
| useProjects tests | 3 | 21 | 20+ |
| useLinks tests | 3 | 22 | 20+ |
| Error scenarios | 2 | 12 | 10+ |
| Filter combinations | 0 | 11 | 8+ |
| Data transformation | 1 | 8 | 6+ |

## Notes

### Environment
- Uses vitest with jsdom environment
- fetch mocked at globalThis level
- React Query QueryClient per test
- Fetch mocks cleared between tests

### Performance
- Individual test files run in <2 seconds
- Full suite (both files) runs in <5 seconds
- No network calls (all mocked)

### Dependencies
- @tanstack/react-query v5+
- @testing-library/react
- vitest

## Debugging Tips

### Check fetch calls
```typescript
expect(mockFetch).toHaveBeenCalledWith(
  expect.stringContaining('/api/v1/projects'),
  expect.objectContaining({ method: 'POST' })
);
```

### Inspect response transformation
```typescript
expect(result.current.data).toEqual(expectedTransformedData);
```

### Verify query state
```typescript
expect(result.current.isLoading).toBeFalsy();
expect(result.current.isSuccess).toBeTruthy();
expect(result.current.error).toBeNull();
```

## Related Files

- Source hooks: `src/hooks/useProjects.ts`, `src/hooks/useLinks.ts`
- Setup: `src/__tests__/setup.ts`
- Config: `vitest.config.ts`
- API client: `src/api/client.ts`
- Auth store: `src/stores/authStore.ts`

---

**Status:** Complete - 43 tests across 2 files
**Estimated Coverage:** 85-95% on tested functions
