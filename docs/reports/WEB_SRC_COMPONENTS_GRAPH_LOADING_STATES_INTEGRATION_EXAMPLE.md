# Loading States Integration Guide

This guide shows how to integrate the loading state components into graph views.

## Components

### GraphSkeleton

Shows a placeholder graph while data is loading.

```tsx
import { GraphSkeleton } from '@/components/graph/GraphSkeleton';

<GraphSkeleton nodeCount={20} edgeCount={30} />;
```

### ErrorState

Displays error messages with optional retry functionality.

```tsx
import { ErrorState } from '@/components/graph/ErrorState';

<ErrorState
  title='Failed to load graph'
  message='An error occurred while loading the graph data.'
  onRetry={() => refetch()}
/>;
```

### LoadingTransition

Smoothly transitions between loading skeleton and content.

```tsx
import { LoadingTransition } from '@/components/graph/LoadingTransition';

<LoadingTransition isLoading={isLoading}>
  <GraphContent />
</LoadingTransition>;
```

### LoadingProgress

Shows progressive loading with node count.

```tsx
import { LoadingProgress } from '@/components/graph/LoadingProgress';

<LoadingProgress loaded={loadedNodes} total={totalNodes} />;
```

## Integration Example

Here's how to integrate loading states into a graph component:

```tsx
import { GraphSkeleton } from '@/components/graph/GraphSkeleton';
import { ErrorState } from '@/components/graph/ErrorState';
import { LoadingProgress } from '@/components/graph/LoadingProgress';

interface GraphViewProps {
  items: Item[];
  links: Link[];
}

function GraphView({ items, links }: GraphViewProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [loadProgress, setLoadProgress] = useState({ loaded: 0, total: 0 });

  // Simulate data loading
  useEffect(() => {
    const loadData = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Simulate progressive loading
        const total = 100;
        for (let i = 0; i <= total; i += 10) {
          setLoadProgress({ loaded: i, total });
          await new Promise((resolve) => setTimeout(resolve, 100));
        }

        setIsLoading(false);
      } catch (err) {
        setError(err as Error);
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

  const handleRetry = () => {
    setError(null);
    setIsLoading(true);
    // Restart loading logic
  };

  // Error state
  if (error) {
    return (
      <ErrorState title='Failed to load graph' message={error.message} onRetry={handleRetry} />
    );
  }

  // Initial loading state
  if (isLoading && loadProgress.loaded === 0) {
    return <GraphSkeleton nodeCount={25} edgeCount={40} />;
  }

  // Progressive loading with skeleton
  if (isLoading) {
    return (
      <div className='relative h-full'>
        <GraphSkeleton nodeCount={25} edgeCount={40} />
        <LoadingProgress
          loaded={loadProgress.loaded}
          total={loadProgress.total}
          label='Loading graph data'
        />
      </div>
    );
  }

  // Content loaded
  return <FlowGraphViewInner items={items} links={links} />;
}
```

## With React Query

If using React Query for data fetching:

```tsx
import { useQuery } from '@tanstack/react-query';
import { GraphSkeleton } from '@/components/graph/GraphSkeleton';
import { ErrorState } from '@/components/graph/ErrorState';
import { LoadingTransition } from '@/components/graph/LoadingTransition';

function GraphView({ projectId }: { projectId: string }) {
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['graph', projectId],
    queryFn: () => fetchGraphData(projectId),
  });

  if (isError) {
    return (
      <ErrorState
        title='Failed to load graph'
        message={error?.message || 'Unknown error'}
        onRetry={() => refetch()}
      />
    );
  }

  return (
    <LoadingTransition isLoading={isLoading}>
      {data && <FlowGraphViewInner items={data.items} links={data.links} />}
    </LoadingTransition>
  );
}
```

## Best Practices

1. **Show skeleton immediately**: Display `GraphSkeleton` as soon as loading starts
2. **Use progress for large datasets**: Show `LoadingProgress` when loading > 1000 nodes
3. **Smooth transitions**: Use `LoadingTransition` for fade effects (300ms default)
4. **Always provide retry**: Include `onRetry` callback in error states
5. **Match skeleton to content**: Use similar node count in skeleton as expected data
6. **Handle edge cases**: Empty states, zero progress, network errors

## Empty State

For empty graphs (no data):

```tsx
if (!isLoading && items.length === 0) {
  return (
    <div className='flex flex-col items-center justify-center h-full min-h-[280px] text-center p-6 text-muted-foreground'>
      <p className='text-sm font-medium'>No nodes to display</p>
      <p className='text-xs mt-1'>Add items or links in this project to see the graph.</p>
    </div>
  );
}
```

## Testing

All loading state components have comprehensive tests:

```bash
bunx vitest run src/__tests__/components/LoadingStates.test.tsx
```

## Storybook

View interactive examples in Storybook:

```bash
bun run storybook
```

Then navigate to "Graph/Loading States" in the sidebar.
