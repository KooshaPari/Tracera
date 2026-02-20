# Loading States Quick Reference

Quick reference for using loading state components in graph views.

## Import

```tsx
import {
  GraphSkeleton,
  ErrorState,
  LoadingTransition,
  LoadingProgress
} from '@/components/graph';
```

## Components

### GraphSkeleton

```tsx
<GraphSkeleton nodeCount={20} edgeCount={30} />
```

**Props:**
- `nodeCount?: number` - Number of skeleton nodes (default: 20)
- `edgeCount?: number` - Number of skeleton edges (default: 30)

### ErrorState

```tsx
<ErrorState
  title="Failed to load graph"
  message="An error occurred while loading the graph data."
  onRetry={() => refetch()}
/>
```

**Props:**
- `title?: string` - Error title (default: "Failed to load graph")
- `message?: string` - Error message (default: "An error occurred...")
- `onRetry?: () => void` - Optional retry callback

### LoadingTransition

```tsx
<LoadingTransition isLoading={isLoading} minDisplayTime={300}>
  <GraphContent />
</LoadingTransition>
```

**Props:**
- `isLoading: boolean` - Whether to show loading state
- `children: React.ReactNode` - Content to show when loaded
- `minDisplayTime?: number` - Minimum skeleton display time in ms (default: 300)

### LoadingProgress

```tsx
<LoadingProgress
  loaded={50}
  total={100}
  label="Loading graph data"
/>
```

**Props:**
- `loaded: number` - Number of items loaded
- `total: number` - Total number of items
- `label?: string` - Progress label (default: "Loading graph data")

## Common Patterns

### Basic Loading

```tsx
if (isLoading) {
  return <GraphSkeleton />;
}
return <GraphContent />;
```

### With Error Handling

```tsx
if (error) {
  return <ErrorState onRetry={refetch} />;
}
if (isLoading) {
  return <GraphSkeleton />;
}
return <GraphContent />;
```

### Smooth Transitions

```tsx
<LoadingTransition isLoading={isLoading}>
  <GraphContent />
</LoadingTransition>
```

### Progressive Loading

```tsx
{isLoading && (
  <div className="relative h-full">
    <GraphSkeleton />
    <LoadingProgress loaded={progress.loaded} total={progress.total} />
  </div>
)}
```

## With React Query

```tsx
const { data, isLoading, error, refetch } = useQuery({
  queryKey: ['graph', projectId],
  queryFn: () => fetchGraphData(projectId),
});

if (error) {
  return <ErrorState onRetry={refetch} />;
}

return (
  <LoadingTransition isLoading={isLoading}>
    {data && <GraphContent data={data} />}
  </LoadingTransition>
);
```

## Testing

Run tests:
```bash
bunx vitest run src/__tests__/components/LoadingStates.test.tsx
```

## Storybook

View examples:
```bash
bun run storybook
# Navigate to: Graph/Loading States
```

## Files

- Components: `/frontend/apps/web/src/components/graph/`
- Tests: `/frontend/apps/web/src/__tests__/components/LoadingStates.test.tsx`
- Stories: `/frontend/apps/web/src/components/graph/__stories__/LoadingStates.stories.tsx`
- Guide: `/frontend/apps/web/src/components/graph/LOADING_STATES_INTEGRATION_EXAMPLE.md`
