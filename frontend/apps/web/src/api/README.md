# API Hooks Documentation

This directory contains React Query hooks for interacting with the TraceRTM backend APIs. All hooks follow consistent patterns for querying and mutating data.

## Files Overview

### Core API Files

- **queries.ts** - Base query hooks for projects, items, links, and mutations
- **endpoints.ts** - Raw API client functions (graph, search, export/import)
- **client.ts** - API client configuration and response handling
- **types.ts** - TypeScript type definitions

### Feature-Specific Hooks

#### equivalence.ts
Hooks for managing equivalence detection and confirmation between items.

**Query Hooks:**
- `useEquivalenceLinks(projectId, status?)` - List equivalence links with optional status filter
- `useEquivalenceLink(equivalenceId)` - Get a single equivalence link

**Mutation Hooks:**
- `useDetectEquivalences()` - Trigger automatic equivalence detection
- `useConfirmEquivalence()` - Confirm an equivalence link
- `useRejectEquivalence()` - Reject an equivalence link
- `useBatchConfirmEquivalences()` - Batch confirm multiple equivalences
- `useBatchRejectEquivalences()` - Batch reject multiple equivalences

**Types:**
- `EquivalenceLink` - Represents an equivalence relationship between two items
- `DetectEquivalencesInput` - Input for detection with threshold configuration
- `ConfirmEquivalenceInput` - Input for confirming an equivalence
- `RejectEquivalenceInput` - Input for rejecting an equivalence

#### canonical.ts
Hooks for managing canonical concepts and their item projections.

**Query Hooks:**
- `useCanonicalConcepts(projectId)` - List all canonical concepts in a project
- `useCanonicalConcept(conceptId)` - Get a single canonical concept
- `useCanonicalProjections(conceptId)` - Get all items mapped to a concept
- `usePivotTargets(itemId)` - Get available pivot targets for an item

**Mutation Hooks:**
- `useCreateCanonicalConcept()` - Create a new canonical concept
- `useUpdateCanonicalConcept()` - Update concept metadata
- `useDeleteCanonicalConcept()` - Delete a canonical concept
- `useCreateCanonicalProjection()` - Map an item to a concept
- `useDeleteCanonicalProjection()` - Remove item-concept mapping
- `usePivotItem()` - Pivot an item to a canonical concept

**Types:**
- `CanonicalConcept` - Represents a canonical concept with properties and metadata
- `CanonicalProjection` - Maps an item to a concept with confidence score
- `PivotTarget` - Target information for pivoting items
- `CreateCanonicalConceptInput` - Input for creating concepts
- `UpdateCanonicalConceptInput` - Input for updating concepts

#### journeys.ts
Hooks for managing user/system journeys and workflows.

**Query Hooks:**
- `useDerivedJourneys(projectId, type?)` - List journeys with optional type filtering
- `useJourney(journeyId)` - Get a single journey with all details
- `useJourneySteps(journeyId)` - Get ordered steps within a journey

**Mutation Hooks:**
- `useDetectJourneys()` - Automatically detect journeys based on flow patterns
- `useCreateJourney()` - Manually create a new journey
- `useUpdateJourney()` - Update journey metadata and items
- `useDeleteJourney()` - Delete a journey
- `useAddJourneyStep()` - Add an item to a journey at specified position
- `useRemoveJourneyStep()` - Remove an item from a journey

**Types:**
- `Journey` - Represents a complete workflow or journey
- `JourneyStep` - Represents a single step in a journey
- `CreateJourneyInput` - Input for journey creation
- `UpdateJourneyInput` - Input for journey updates
- `DetectJourneysInput` - Configuration for journey detection

#### componentLibrary.ts
Hooks for managing component libraries and design systems.

**Query Hooks:**
- `useComponentLibraries(projectId)` - List all component libraries in a project
- `useComponentLibrary(libraryId)` - Get library details
- `useLibraryComponents(libraryId)` - List all components in a library
- `useLibraryComponent(componentId)` - Get single component details
- `useComponentUsage(componentId)` - Get usage statistics for a component
- `useDesignTokens(libraryId)` - Get all design tokens in a library

**Mutation Hooks:**
- `useCreateComponentLibrary()` - Create a new component library
- `useUpdateComponentLibrary()` - Update library metadata
- `useDeleteComponentLibrary()` - Delete a library
- `useCreateLibraryComponent()` - Add component to library
- `useUpdateLibraryComponent()` - Update component properties
- `useDeleteLibraryComponent()` - Remove component from library
- `useCreateDesignToken()` - Create a design token
- `useUpdateDesignToken()` - Update token value
- `useDeleteDesignToken()` - Delete a token

**Types:**
- `ComponentLibrary` - Represents a component library/design system
- `LibraryComponent` - Individual component in a library
- `ComponentUsage` - Usage statistics for a component
- `DesignToken` - Design token (color, spacing, typography, etc.)

## Usage Patterns

### Basic Query

```typescript
import canonicalApi from "@/api/canonical";

const { useCanonicalConcepts } = canonicalApi;

function ConceptList({ projectId }: { projectId: string }) {
  const { data: concepts, isLoading, error } = useCanonicalConcepts(projectId);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <ul>
      {concepts?.map((concept) => (
        <li key={concept.id}>{concept.name}</li>
      ))}
    </ul>
  );
}
```

### Mutation with Invalidation

```typescript
import { useConfirmEquivalence } from "@/api/equivalence";

function ConfirmButton({ equivalenceId }: { equivalenceId: string }) {
  const { mutate, isPending } = useConfirmEquivalence();

  return (
    <button
      onClick={() => mutate({ equivalenceId, comment: "Confirmed" })}
      disabled={isPending}
    >
      {isPending ? "Confirming..." : "Confirm"}
    </button>
  );
}
```

### Combined Query and Mutation

```typescript
import { useDerivedJourneys, useCreateJourney } from "@/api/journeys";
import { useQueryClient } from "@tanstack/react-query";

function JourneyManager({ projectId }: { projectId: string }) {
  const queryClient = useQueryClient();
  const { data: journeys } = useDerivedJourneys(projectId);
  const { mutateAsync: createJourney } = useCreateJourney();

  const handleCreate = async (name: string, itemIds: string[]) => {
    await createJourney({
      projectId,
      name,
      type: "user",
      itemIds,
    });

    // Auto-invalidation happens, but can also manually invalidate:
    // queryClient.invalidateQueries({
    //   queryKey: journeyQueryKeys.list(projectId),
    // });
  };

  return (
    <div>
      <h2>Journeys ({journeys?.length ?? 0})</h2>
      <button onClick={() => handleCreate("New Journey", [])}>Create</button>
    </div>
  );
}
```

## Query Key Structure

All hooks organize query keys in a hierarchical structure for proper cache invalidation:

```typescript
// Equivalence keys
["equivalences"] // all
["equivalences", "list"] // all lists
["equivalences", "list", projectId, status] // specific list
["equivalences", "detail", equivalenceId] // specific equivalence

// Canonical keys
["canonical"] // all
["canonical", "list", projectId] // concepts in project
["canonical", "detail", conceptId] // specific concept
["canonical", "projections", conceptId] // items for concept
["canonical", "pivots", itemId] // pivot targets for item

// Journey keys
["journeys"] // all
["journeys", "list", projectId, type] // filtered journeys
["journeys", "detail", journeyId] // specific journey
["journeys", "steps", journeyId] // journey steps

// Component library keys
["componentLibrary"] // all
["componentLibrary", "list", projectId] // libraries in project
["componentLibrary", "components", libraryId] // components in library
["componentLibrary", "tokens", libraryId] // tokens in library
["componentLibrary", "usage", componentId] // component usage
```

## Best Practices

### 1. Error Handling

```typescript
const { mutate, isError, error } = useConfirmEquivalence({
  onError: (error) => {
    console.error("Failed to confirm:", error.message);
  },
});
```

### 2. Loading States

```typescript
const { isPending, isLoading, data } = useCanonicalConcepts(projectId);

// isPending: true during mutation
// isLoading: true during initial query load
```

### 3. Conditional Queries

```typescript
// Hook only runs if projectId is defined
const { data } = useDerivedJourneys(projectId, undefined, {
  enabled: !!projectId,
});
```

### 4. Stale Data Management

```typescript
const { data } = useComponentLibraries(projectId, {
  staleTime: 5 * 60 * 1000, // 5 minutes
  gcTime: 10 * 60 * 1000, // 10 minutes
});
```

### 5. Batch Operations

```typescript
const { mutate: batchConfirm } = useBatchConfirmEquivalences();

batchConfirm(equivalenceIds, {
  onSuccess: () => {
    toast.success(`Confirmed ${equivalenceIds.length} equivalences`);
  },
});
```

## Testing

All hooks include comprehensive unit tests in `src/__tests__/api/`:

- `equivalence.test.ts` - Query key generation and type validation
- `canonical.test.ts` - Concept, projection, and pivot types
- `journeys.test.ts` - Journey structure and type validation
- `componentLibrary.test.ts` - Library, component, and token types

Run tests with:
```bash
bun run test -- src/__tests__/api/*.test.ts
```

## Migration Notes

When integrating these hooks into components:

1. Replace direct API calls with hooks
2. Update cache invalidation to use proper query keys
3. Implement loading and error states
4. Add optimistic updates where appropriate
5. Handle side effects with `onSuccess`/`onError` callbacks

## Related Documentation

- React Query: https://tanstack.com/query/latest
- API Response Types: `/src/api/types.ts`
- API Client: `/src/api/client.ts`
- Example Usage: `/src/hooks/*.ts`
