# FigmaSyncPanel - Quick Start Guide

## Import the Component

```typescript
import { FigmaSyncPanel } from "@/components/graph";
import type { FigmaSyncPanelProps } from "@/components/graph";
```

## Minimal Setup

```typescript
<FigmaSyncPanel
  syncState={syncState}
  components={components}
/>
```

## Full Setup with All Features

```typescript
<FigmaSyncPanel
  syncState={syncState}
  components={components}
  isSyncing={isSyncing}
  onSync={handleSync}
  onOpenInFigma={handleOpenInFigma}
  onUnlink={handleUnlink}
  className="w-full max-w-2xl"
/>
```

## Required Data

### syncState: FigmaSyncState | null

```typescript
{
  id: "sync-1",
  libraryId: "lib-1",
  projectId: "proj-1",
  figmaFileKey: "abc123xyz",
  figmaFileName: "Design System",
  figmaFileUrl: "https://figma.com/file/abc123xyz/Design-System",
  lastSyncedAt: "2026-01-29T12:00:00Z",
  lastSyncVersion: "1.0.0",
  syncStatus: "synced", // or "syncing" | "error" | "outdated"
  syncError: null,
  componentsSynced: 24,
  tokensSynced: 156,
  stylesSynced: 42,
  createdAt: "2026-01-20T00:00:00Z",
  updatedAt: "2026-01-29T12:00:00Z"
}
```

### components: LibraryComponent[]

```typescript
[
  {
    id: "comp-1",
    libraryId: "lib-1",
    projectId: "proj-1",
    name: "button",
    displayName: "Button",
    description: "Primary action button",
    category: "atom",
    figmaNodeId: "node-123", // Set to link to Figma
    figmaUrl: "https://figma.com/file/...", // Direct link
    status: "stable",
    usageCount: 42,
    createdAt: "2026-01-20T00:00:00Z",
    updatedAt: "2026-01-29T12:00:00Z"
  },
  // ... more components
]
```

## Callback Handlers

### onSync: () => Promise<void>

Called when user clicks the sync button.

```typescript
const handleSync = async () => {
  try {
    await api.syncFigmaLibrary(libraryId);
    // Refetch data if needed
  } catch (error) {
    console.error("Sync failed:", error);
  }
};
```

### onOpenInFigma: (componentId: string) => void

Called when user clicks "Open in Figma" button.

```typescript
const handleOpenInFigma = (componentId: string) => {
  const component = components.find(c => c.id === componentId);
  if (component?.figmaUrl) {
    window.open(component.figmaUrl, "_blank");
  }
};
```

### onUnlink: (componentId: string) => void

Called when user clicks unlink button.

```typescript
const handleUnlink = (componentId: string) => {
  api.unlinkComponentFromFigma(componentId)
    .then(() => {
      // Refetch components list
      refetchComponents();
    });
};
```

## Common Integration Pattern

```typescript
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { FigmaSyncPanel } from "@/components/graph";
import { api } from "@/lib/trpc";

function FigmaSyncManager({ libraryId }: { libraryId: string }) {
  const queryClient = useQueryClient();

  // Fetch data
  const { data: syncState } = useQuery({
    queryKey: ["figma-sync", libraryId],
    queryFn: () => api.getLibraryFigmaSyncState.query({ libraryId }),
  });

  const { data: components = [] } = useQuery({
    queryKey: ["components", libraryId],
    queryFn: () => api.getLibraryComponents.query({ libraryId }),
  });

  // Mutations
  const syncMutation = useMutation({
    mutationFn: () => api.syncLibraryFromFigma.mutate({ libraryId }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["figma-sync", libraryId],
      });
    },
  });

  const unlinkMutation = useMutation({
    mutationFn: (componentId: string) =>
      api.unlinkComponentFromFigma.mutate({ componentId }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["components", libraryId],
      });
    },
  });

  // Render
  return (
    <FigmaSyncPanel
      syncState={syncState ?? null}
      components={components}
      isSyncing={syncMutation.isPending}
      onSync={() => syncMutation.mutateAsync()}
      onOpenInFigma={(componentId) => {
        const component = components.find(c => c.id === componentId);
        if (component?.figmaUrl) {
          window.open(component.figmaUrl, "_blank");
        }
      }}
      onUnlink={(componentId) => {
        unlinkMutation.mutate(componentId);
      }}
    />
  );
}
```

## Styling

### Default Width
The component works best with a defined width:

```typescript
<FigmaSyncPanel
  {...props}
  className="w-full max-w-2xl"
/>
```

### Responsive
```typescript
<FigmaSyncPanel
  {...props}
  className="w-full md:w-3/4 lg:w-2/3"
/>
```

### In a Container
```typescript
<div className="p-6 bg-white rounded-lg">
  <FigmaSyncPanel {...props} />
</div>
```

## Status States

The component automatically displays appropriate status based on syncState.syncStatus:

### Synced (Green)
```typescript
syncStatus: "synced"
```

### Syncing (Blue with Spinner)
```typescript
isSyncing: true
```

### Outdated (Amber)
```typescript
syncStatus: "outdated"
```

### Error (Red with Message)
```typescript
syncStatus: "error"
syncError: "Failed to connect to Figma API"
```

### Not Configured (Gray)
```typescript
syncState: null
```

## Component Status Display

### Synced (has figmaNodeId)
- Green badge with checkmark
- Shows "Synced" label
- Open in Figma button available

### Unlinked (no figmaNodeId)
- Gray badge
- Shows "Unlinked" label
- Helpful message to link component

### Outdated (with diff count)
- Amber badge
- Shows "Outdated" label
- Displays number of diffs detected
- Explains design has changed

## Empty States

### No Figma Integration
When syncState is null:
```
No Figma integration configured
```

### No Components
When components array is empty:
```
No components to display
```

## Accessibility Features

- Semantic HTML (buttons, links, headings)
- ARIA labels for status badges
- Keyboard navigable
- Focus visible on interactive elements
- Color not only indicator
- Icon descriptions

## Testing the Component

Run tests:
```bash
bun run test -- src/__tests__/components/FigmaSyncPanel.test.tsx
```

Results:
```
Test Files: 1 passed (1)
Tests: 18 passed (18)
```

## Common Issues

### Component not rendering

Make sure syncState is properly typed:
```typescript
syncState: FigmaSyncState | null  // Not just FigmaSyncState
```

### Callbacks not firing

Ensure callbacks don't have errors:
```typescript
const handleSync = async () => {
  console.log("Sync started");
  // Your logic here
};
```

### Styling issues

Import Tailwind CSS in your component:
```typescript
import "@/index.css"; // or wherever Tailwind is imported
```

### Type errors

Install latest @tracertm/types:
```bash
bun install @tracertm/types
```

## Performance Tips

1. Use React Query for data fetching
2. Wrap callbacks in useCallback
3. Memoize parent components
4. Avoid inline object creation for props

## Next Steps

1. Add to your page/component
2. Connect to your data source
3. Implement API callbacks
4. Test with real Figma data
5. Gather user feedback

## API Reference

### Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| syncState | FigmaSyncState \| null | Yes | Figma sync metadata |
| components | LibraryComponent[] | Yes | Library components |
| isSyncing | boolean | No | Loading state (default: false) |
| onSync | () => Promise<void> | No | Manual sync callback |
| onOpenInFigma | (id: string) => void | No | Open in Figma callback |
| onUnlink | (id: string) => void | No | Unlink callback |
| className | string | No | CSS class name |

### Status Values

| Status | Color | Icon | Meaning |
|--------|-------|------|---------|
| synced | Green | CheckCircle2 | Up to date |
| syncing | Blue | Loader2 | In progress |
| outdated | Amber | AlertTriangle | Has changes |
| error | Red | AlertCircle | Failed to sync |
| null | Gray | Link2 | Not configured |

## Support

For questions or issues:
1. Check FigmaSyncPanel.README.md for detailed documentation
2. See FIGMA_SYNC_PANEL_EXAMPLES.md for integration patterns
3. Review test file for usage examples
4. Check types in @tracertm/types

## License

Part of the Trace project. All rights reserved.
