# FigmaSyncPanel Component

A comprehensive React component for managing and displaying Figma integration status for component libraries.

## Overview

The FigmaSyncPanel displays:
- Figma file information and direct links
- Sync status (synced, outdated, error, unlinked)
- Last sync timestamp and version
- Sync statistics (components, tokens, styles)
- Component-level sync status with diff indicators
- Manual sync triggers
- Quick actions (open in Figma, unlink component)

## Features

### Status Indicators
- **Synced**: Component is linked to Figma and up-to-date
- **Outdated**: Figma has newer changes not yet synced
- **Unlinked**: Component has no Figma connection
- **Error**: Sync failed with descriptive error message

### Component Details
Each component in the list shows:
- Display name and category
- Sync status badge
- Diff count when design changes are detected
- Expandable details with:
  - Description
  - Figma node ID
  - Status-specific messages
  - Quick action buttons

### Statistics
Displays aggregated sync data:
- Total components synced
- Design tokens synced
- Styles synced

### Actions
- **Sync Button**: Manual trigger to sync with Figma
- **Open in Figma**: Navigate to component in Figma (requires figmaUrl)
- **Unlink**: Remove component from Figma integration

## Usage

### Basic Example

```tsx
import { FigmaSyncPanel, type FigmaSyncPanelProps } from "@/components/graph";
import type { FigmaSyncState, LibraryComponent } from "@tracertm/types";

function MyComponent() {
  const [syncState, setSyncState] = useState<FigmaSyncState | null>(null);
  const [components, setComponents] = useState<LibraryComponent[]>([]);
  const [isSyncing, setIsSyncing] = useState(false);

  const handleSync = async () => {
    setIsSyncing(true);
    try {
      // Call your sync API
      await api.syncFigmaLibrary(syncState.libraryId);
      // Update sync state...
    } finally {
      setIsSyncing(false);
    }
  };

  return (
    <FigmaSyncPanel
      syncState={syncState}
      components={components}
      isSyncing={isSyncing}
      onSync={handleSync}
    />
  );
}
```

### With All Callbacks

```tsx
<FigmaSyncPanel
  syncState={syncState}
  components={components}
  isSyncing={isSyncing}
  onSync={handleSync}
  onOpenInFigma={(componentId) => {
    const component = components.find(c => c.id === componentId);
    if (component?.figmaUrl) {
      window.open(component.figmaUrl, "_blank");
    }
  }}
  onUnlink={(componentId) => {
    // Call your unlink API
    api.unlinkComponentFromFigma(componentId);
  }}
  className="w-full max-w-2xl"
/>
```

## Props

### FigmaSyncPanelProps

```typescript
interface FigmaSyncPanelProps {
  /** Figma sync state for the library */
  syncState: FigmaSyncState | null;

  /** Library components with Figma integration */
  components: LibraryComponent[];

  /** Whether sync is in progress */
  isSyncing?: boolean;

  /** Callback to trigger manual sync */
  onSync?: () => Promise<void>;

  /** Callback to open component in Figma */
  onOpenInFigma?: (componentId: string) => void;

  /** Callback to unlink component from Figma */
  onUnlink?: (componentId: string) => void;

  /** CSS class name */
  className?: string;
}
```

## Type Dependencies

The component uses these types from `@tracertm/types`:

### FigmaSyncState
```typescript
interface FigmaSyncState {
  id: string;
  libraryId: string;
  projectId: string;

  // Figma file info
  figmaFileKey: string;
  figmaFileName: string;
  figmaFileUrl: string;

  // Sync status
  lastSyncedAt?: string;
  lastSyncVersion?: string;
  syncStatus: "synced" | "syncing" | "error" | "outdated";
  syncError?: string;

  // Stats
  componentsSynced: number;
  tokensSynced: number;
  stylesSynced: number;

  createdAt: string;
  updatedAt: string;
}
```

### LibraryComponent
Component needs these fields:
- `id`: Unique identifier
- `libraryId`: Parent library
- `projectId`: Parent project
- `name`: Component name
- `displayName`: Display name for UI
- `description?`: Component description
- `category`: Component category (atom, molecule, etc.)
- `figmaNodeId?`: Figma node ID (indicates linked status)
- `figmaUrl?`: Direct URL to Figma component

## Styling

The component uses Tailwind CSS and shadcn/ui components:
- `@tracertm/ui/components/Badge` - Status badges
- `@tracertm/ui/components/Button` - Action buttons
- `@tracertm/ui/components/Card` - Container
- `@tracertm/ui/components/Tooltip` - Hover hints
- `@tracertm/ui/components/Separator` - Dividers
- `@tracertm/ui/components/ScrollArea` - Scrollable list

Custom styling uses Tailwind utility classes and CSS variables from the UI theme.

## Status Colors

### Sync Status
- **Synced**: Green (text-green-600, bg-green-50)
- **Syncing**: Blue (text-blue-600, bg-blue-50)
- **Outdated**: Amber (text-amber-600, bg-amber-50)
- **Error**: Red (text-red-600, bg-red-50)

### Component Status
- **Synced**: Green badge
- **Outdated**: Amber with diff count indicator
- **Unlinked**: Gray badge

## Empty States

### No Integration
When `syncState` is null, displays a message prompting to configure Figma integration.

### No Components
When components list is empty, displays a helpful message.

## Accessibility

- Semantic HTML structure
- ARIA labels and roles
- Keyboard navigation support
- Focus management for interactive elements
- Proper color contrast ratios
- Icon descriptions via lucide-react built-in labels

## Performance Considerations

- Uses `memo` to prevent unnecessary re-renders
- Component details are expanded on-demand
- ScrollArea handles large component lists efficiently
- Callbacks are wrapped in useCallback to maintain referential equality

## Testing

Full test coverage including:
- Rendering with various sync states
- User interactions (expand, click, sync)
- Callback invocations
- Edge cases (empty list, null state, error handling)
- Accessibility features

Run tests:
```bash
bun run test -- src/__tests__/components/FigmaSyncPanel.test.tsx
```

## Integration Patterns

### With TanStack Query (React Query)

```tsx
function FigmaLibrarySync({ libraryId }: { libraryId: string }) {
  const { data: syncState, isLoading: isSyncStateLoading } =
    useQuery({
      queryKey: ["figma-sync", libraryId],
      queryFn: () => api.getFigmaSyncState(libraryId),
    });

  const { data: components } = useQuery({
    queryKey: ["library-components", libraryId],
    queryFn: () => api.getLibraryComponents(libraryId),
  });

  const syncMutation = useMutation({
    mutationFn: () => api.syncFigmaLibrary(libraryId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["figma-sync", libraryId]
      });
    },
  });

  return (
    <FigmaSyncPanel
      syncState={syncState ?? null}
      components={components ?? []}
      isSyncing={syncMutation.isPending}
      onSync={() => syncMutation.mutateAsync()}
    />
  );
}
```

### With Error Boundaries

```tsx
<ErrorBoundary fallback={<div>Failed to load Figma sync</div>}>
  <FigmaSyncPanel {...props} />
</ErrorBoundary>
```

## Future Enhancements

- Batch diff preview for components
- Direct component property sync visualization
- Version history and rollback
- Selective component sync (sync specific components)
- Figma design token mapping visualization
- Real-time sync status updates via WebSocket
- Component variant sync tracking
- Design system metrics dashboard

## Related Components

- `ComponentLibraryExplorer` - Browse all library components
- `NodeDetailPanel` - Detailed item information
- `EquivalencePanel` - Cross-perspective relationships
- `ComponentUsageMatrix` - Component usage tracking

## Files

- `/src/components/graph/FigmaSyncPanel.tsx` - Component implementation
- `/src/__tests__/components/FigmaSyncPanel.test.tsx` - Test suite
- `/src/components/graph/index.ts` - Component export
