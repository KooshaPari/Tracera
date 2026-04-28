# FigmaSyncPanel Component - Usage Examples

## Example 1: Basic Usage

```typescript
import { FigmaSyncPanel } from "@/components/graph";
import type { FigmaSyncState, LibraryComponent } from "@tracertm/types";

export function LibraryManagerPage() {
  const [syncState, setSyncState] = useState<FigmaSyncState | null>(null);
  const [components, setComponents] = useState<LibraryComponent[]>([]);

  useEffect(() => {
    // Load sync state and components
    fetchLibraryData();
  }, []);

  return (
    <div className="p-6">
      <FigmaSyncPanel
        syncState={syncState}
        components={components}
      />
    </div>
  );
}
```

## Example 2: With React Query Integration

```typescript
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { FigmaSyncPanel } from "@/components/graph";
import { api } from "@/lib/trpc";

export function FigmaLibrarySyncPanel({ libraryId }: { libraryId: string }) {
  const queryClient = useQueryClient();

  // Fetch sync state
  const { data: syncState } = useQuery({
    queryKey: ["figma-sync-state", libraryId],
    queryFn: () => api.getLibraryFigmaSyncState.query({ libraryId }),
  });

  // Fetch components
  const { data: components = [] } = useQuery({
    queryKey: ["library-components", libraryId],
    queryFn: () => api.getLibraryComponents.query({ libraryId }),
  });

  // Sync mutation
  const syncMutation = useMutation({
    mutationFn: () =>
      api.syncLibraryFromFigma.mutate({ libraryId }),
    onSuccess: () => {
      // Invalidate related queries
      queryClient.invalidateQueries({
        queryKey: ["figma-sync-state", libraryId],
      });
      queryClient.invalidateQueries({
        queryKey: ["library-components", libraryId],
      });
    },
  });

  // Unlink mutation
  const unlinkMutation = useMutation({
    mutationFn: (componentId: string) =>
      api.unlinkComponentFromFigma.mutate({ componentId }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["library-components", libraryId],
      });
    },
  });

  return (
    <FigmaSyncPanel
      syncState={syncState ?? null}
      components={components}
      isSyncing={syncMutation.isPending}
      onSync={() => syncMutation.mutateAsync()}
      onOpenInFigma={(componentId) => {
        const component = components.find((c) => c.id === componentId);
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

## Example 3: With Tabs Layout

```typescript
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@tracertm/ui/components/Tabs";
import { FigmaSyncPanel } from "@/components/graph";

export function LibrarySettingsPage() {
  return (
    <Tabs defaultValue="sync" className="w-full">
      <TabsList>
        <TabsTrigger value="sync">Figma Sync</TabsTrigger>
        <TabsTrigger value="components">Components</TabsTrigger>
        <TabsTrigger value="settings">Settings</TabsTrigger>
      </TabsList>

      <TabsContent value="sync" className="mt-6">
        <FigmaSyncPanel
          syncState={syncState}
          components={components}
          isSyncing={isSyncing}
          onSync={handleSync}
          onOpenInFigma={handleOpenInFigma}
          onUnlink={handleUnlink}
        />
      </TabsContent>

      <TabsContent value="components">{/* ... */}</TabsContent>
      <TabsContent value="settings">{/* ... */}</TabsContent>
    </Tabs>
  );
}
```

## Example 4: With Error Boundary

```typescript
import { ErrorBoundary } from "@/components/layout/ErrorBoundary";
import { FigmaSyncPanel } from "@/components/graph";

export function SafeFigmaSyncPanel(props: FigmaSyncPanelProps) {
  return (
    <ErrorBoundary
      fallback={
        <div className="p-4 bg-red-50 rounded border border-red-200">
          <p className="text-red-800">
            Failed to load Figma sync panel. Please refresh the page.
          </p>
        </div>
      }
    >
      <FigmaSyncPanel {...props} />
    </ErrorBoundary>
  );
}
```

## Example 5: With Toast Notifications

```typescript
import { useToast } from "@/hooks/useToast";
import { FigmaSyncPanel } from "@/components/graph";

export function FigmaSyncWithNotifications({
  libraryId,
}: {
  libraryId: string;
}) {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const syncMutation = useMutation({
    mutationFn: () => api.syncLibraryFromFigma.mutate({ libraryId }),
    onSuccess: () => {
      toast({
        title: "Success",
        description: "Library synced from Figma successfully",
        variant: "default",
      });
      queryClient.invalidateQueries({
        queryKey: ["figma-sync-state", libraryId],
      });
    },
    onError: (error) => {
      toast({
        title: "Sync Failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  return (
    <FigmaSyncPanel
      syncState={syncState}
      components={components}
      isSyncing={syncMutation.isPending}
      onSync={() => syncMutation.mutateAsync()}
      onUnlink={(componentId) => {
        // Show confirmation
        if (confirm("Unlink this component from Figma?")) {
          unlinkMutation.mutate(componentId);
          toast({
            title: "Component Unlinked",
            description: "This component is no longer synced from Figma",
          });
        }
      }}
    />
  );
}
```

## Example 6: With Status Polling

```typescript
import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { FigmaSyncPanel } from "@/components/graph";

export function FigmaSyncWithPolling({ libraryId }: { libraryId: string }) {
  const { data: syncState, refetch } = useQuery({
    queryKey: ["figma-sync-state", libraryId],
    queryFn: () => api.getLibraryFigmaSyncState.query({ libraryId }),
    // Poll every 30 seconds if syncing
    refetchInterval: (data) =>
      data?.syncState?.syncStatus === "syncing" ? 30000 : false,
  });

  return (
    <FigmaSyncPanel
      syncState={syncState?.syncState ?? null}
      components={components}
      isSyncing={syncState?.syncState?.syncStatus === "syncing"}
      onSync={async () => {
        await api.syncLibraryFromFigma.mutate({ libraryId });
        // Refetch immediately
        refetch();
      }}
    />
  );
}
```

## Example 7: Responsive Grid Layout

```typescript
import { Grid, GridItem } from "@tracertm/ui/components/Grid";
import { FigmaSyncPanel } from "@/components/graph";

export function LibrariesDashboard() {
  const [libraries, setLibraries] = useState<Array<{
    id: string;
    name: string;
    syncState: FigmaSyncState | null;
    components: LibraryComponent[];
  }>>([]);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Component Libraries</h1>

      <Grid cols={{ xs: 1, md: 2, lg: 3 }} gap="6">
        {libraries.map((library) => (
          <GridItem key={library.id}>
            <FigmaSyncPanel
              syncState={library.syncState}
              components={library.components}
              onSync={() => handleSync(library.id)}
              className="h-full"
            />
          </GridItem>
        ))}
      </Grid>
    </div>
  );
}
```

## Example 8: With Custom Status Colors

```typescript
import { cn } from "@tracertm/ui";
import { FigmaSyncPanel } from "@/components/graph";

export function ThemedFigmaSyncPanel(props: FigmaSyncPanelProps) {
  // Custom theme classes
  const customClass = cn(
    props.className,
    // Add custom background
    "bg-gradient-to-br from-slate-50 to-slate-100",
    // Custom border
    "border-2 border-slate-300",
    // Custom shadow
    "shadow-lg hover:shadow-xl transition-shadow"
  );

  return (
    <FigmaSyncPanel
      {...props}
      className={customClass}
    />
  );
}
```

## Example 9: Standalone Modal

```typescript
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@tracertm/ui/components/Dialog";
import { FigmaSyncPanel } from "@/components/graph";
import { useState } from "react";

export function FigmaSyncModal() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button onClick={() => setOpen(true)} className="...">
        Sync Figma
      </button>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Figma Library Sync</DialogTitle>
          </DialogHeader>

          <FigmaSyncPanel
            syncState={syncState}
            components={components}
            isSyncing={isSyncing}
            onSync={handleSync}
            className="max-h-[60vh]"
          />
        </DialogContent>
      </Dialog>
    </>
  );
}
```

## Example 10: With Animation on Sync

```typescript
import { useEffect, useState } from "react";
import { FigmaSyncPanel } from "@/components/graph";

export function AnimatedFigmaSyncPanel(props: FigmaSyncPanelProps) {
  const [showSuccess, setShowSuccess] = useState(false);

  const handleSync = async () => {
    if (!props.onSync) return;

    try {
      await props.onSync();
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 3000);
    } catch (error) {
      console.error("Sync failed:", error);
    }
  };

  return (
    <div className="relative">
      <FigmaSyncPanel
        {...props}
        onSync={handleSync}
        className={cn(
          "transition-opacity",
          showSuccess && "opacity-75"
        )}
      />

      {showSuccess && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/10 rounded">
          <div className="bg-green-500 text-white px-4 py-2 rounded animate-fade-in">
            Sync completed successfully!
          </div>
        </div>
      )}
    </div>
  );
}
```

## Integration Checklist

When integrating FigmaSyncPanel, ensure:

- [ ] FigmaSyncState data is fetched and passed
- [ ] LibraryComponent[] array is populated
- [ ] onSync callback connects to backend API
- [ ] onOpenInFigma callback opens correct Figma links
- [ ] onUnlink callback updates backend and refetches data
- [ ] Error states are handled with toast notifications
- [ ] Loading state (isSyncing) is managed
- [ ] Component is wrapped in error boundary
- [ ] Styling matches application theme
- [ ] Accessibility requirements are met

## Performance Tips

1. **Memoize components**: Already done with `memo()`
2. **Use React Query**: For automatic caching and refetching
3. **Debounce rapid syncs**: Prevent multiple simultaneous sync requests
4. **Lazy load details**: Already implemented (expandable)
5. **Pagination**: For very large component lists, consider pagination
6. **WebSocket updates**: For real-time sync status updates

## Common Patterns

### Sync on Mount
```typescript
useEffect(() => {
  syncMutation.mutate();
}, []);
```

### Sync on Library Selection
```typescript
useEffect(() => {
  queryClient.invalidateQueries({
    queryKey: ["figma-sync-state", libraryId],
  });
}, [libraryId]);
```

### Auto-refresh on Sync
```typescript
onSuccess: () => {
  refetch(); // React Query refetch
}
```
