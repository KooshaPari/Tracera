# API Hooks Quick Reference

## Files Overview

| File                | Location | Size   | Hooks    |
| ------------------- | -------- | ------ | -------- |
| equivalence.ts      | src/api/ | 4.8 KB | 7 hooks  |
| canonical.ts        | src/api/ | 6.6 KB | 11 hooks |
| journeys.ts         | src/api/ | 6.3 KB | 10 hooks |
| componentLibrary.ts | src/api/ | 10 KB  | 20 hooks |

Total: 27.7 KB across 4 files with 48 hooks + 4 query key factories

## Quick Import Guide

```typescript
// Equivalence hooks
import {
  useEquivalenceLinks,
  useDetectEquivalences,
  useConfirmEquivalence,
  useRejectEquivalence,
  equivalenceQueryKeys,
} from '@/api/equivalence';

// Canonical hooks
import {
  useCanonicalConcepts,
  useCreateCanonicalConcept,
  usePivotItem,
  canonicalQueryKeys,
} from '@/api/canonical';

// Journey hooks
import {
  useDerivedJourneys,
  useCreateJourney,
  useDetectJourneys,
  journeyQueryKeys,
} from '@/api/journeys';

// Component Library hooks
import {
  useComponentLibraries,
  useDesignTokens,
  useCreateLibraryComponent,
  componentLibraryQueryKeys,
} from '@/api/componentLibrary';
```

## Hook Categories by Type

### Equivalence (equivalence.ts)

**Queries:**

- `useEquivalenceLinks(projectId, status?)` - List equivalences
- `useEquivalenceLink(equivalenceId)` - Single equivalence

**Mutations:**

- `useDetectEquivalences()` - Auto-detect
- `useConfirmEquivalence()` - Confirm one
- `useRejectEquivalence()` - Reject one
- `useBatchConfirmEquivalences()` - Batch confirm
- `useBatchRejectEquivalences()` - Batch reject

### Canonical (canonical.ts)

**Queries:**

- `useCanonicalConcepts(projectId)` - All concepts
- `useCanonicalConcept(conceptId)` - Single concept
- `useCanonicalProjections(conceptId)` - Items for concept
- `usePivotTargets(itemId)` - Pivot options

**Mutations:**

- `useCreateCanonicalConcept()` - Create
- `useUpdateCanonicalConcept()` - Update
- `useDeleteCanonicalConcept()` - Delete
- `useCreateCanonicalProjection()` - Add item
- `useDeleteCanonicalProjection()` - Remove item
- `usePivotItem()` - Pivot item

### Journeys (journeys.ts)

**Queries:**

- `useDerivedJourneys(projectId, type?)` - List journeys
- `useJourney(journeyId)` - Single journey
- `useJourneySteps(journeyId)` - Journey steps

**Mutations:**

- `useDetectJourneys()` - Auto-detect
- `useCreateJourney()` - Create
- `useUpdateJourney()` - Update
- `useDeleteJourney()` - Delete
- `useAddJourneyStep()` - Add step
- `useRemoveJourneyStep()` - Remove step

### Component Library (componentLibrary.ts)

**Queries:**

- `useComponentLibraries(projectId)` - All libraries
- `useComponentLibrary(libraryId)` - Single library
- `useLibraryComponents(libraryId)` - Components in library
- `useLibraryComponent(componentId)` - Single component
- `useComponentUsage(componentId)` - Usage stats
- `useDesignTokens(libraryId)` - Tokens in library

**Mutations:**

- `useCreateComponentLibrary()` - Create library
- `useUpdateComponentLibrary()` - Update library
- `useDeleteComponentLibrary()` - Delete library
- `useCreateLibraryComponent()` - Add component
- `useUpdateLibraryComponent()` - Update component
- `useDeleteLibraryComponent()` - Remove component
- `useCreateDesignToken()` - Create token
- `useUpdateDesignToken()` - Update token
- `useDeleteDesignToken()` - Delete token

## Common Patterns

### Query with Loading State

```typescript
const { data, isLoading, error } = useCanonicalConcepts(projectId);

if (isLoading) return <Spinner />;
if (error) return <ErrorAlert error={error} />;
return <ConceptList concepts={data} />;
```

### Mutation with Success Callback

```typescript
const { mutate, isPending } = useCreateJourney({
  onSuccess: (data) => {
    toast.success(`Created journey: ${data.name}`);
    navigate(`/journeys/${data.id}`);
  },
});

const handleCreate = (formData) =>
  mutate({
    projectId,
    name: formData.name,
    type: 'user',
    itemIds: formData.items,
  });
```

### Conditional Query

```typescript
const { data } = useDerivedJourneys(projectId, undefined, {
  enabled: !!projectId, // Only run if projectId exists
});
```

### Cache Invalidation (Automatic)

```typescript
// Automatically invalidates useCanonicalConcepts(projectId) query
const { mutate } = useCreateCanonicalConcept();

mutate({ projectId, name: 'New Concept' });
// No manual invalidation needed!
```

### Batch Operations

```typescript
const { mutate } = useBatchConfirmEquivalences();

mutate(selectedEquivalenceIds, {
  onSuccess: () => {
    setSelectedIds([]);
    toast.success('Confirmed equivalences');
  },
});
```

## Type Quick Reference

### Equivalence

```typescript
type EquivalenceLink = {
  id: string;
  itemId1: string;
  itemId2: string;
  similarity: number; // 0-1
  confidence: number; // 0-1
  status: 'pending' | 'confirmed' | 'rejected';
  createdAt: string;
  confirmedAt?: string;
};
```

### Canonical

```typescript
type CanonicalConcept = {
  id: string;
  projectId: string;
  name: string;
  description?: string;
  category?: string;
  properties: Record<string, any>;
  itemCount: number;
  createdAt: string;
  updatedAt: string;
};

type CanonicalProjection = {
  id: string;
  conceptId: string;
  itemId: string;
  confidence: number;
  mappedProperties: Record<string, any>;
  createdAt: string;
};
```

### Journey

```typescript
type Journey = {
  id: string;
  projectId: string;
  name: string;
  type: 'user' | 'system' | 'business' | 'technical';
  itemIds: string[];
  sequence: number[];
  metadata?: Record<string, any>;
  createdAt: string;
  updatedAt: string;
};

type JourneyStep = {
  itemId: string;
  order: number;
  duration?: number;
};
```

### Component Library

```typescript
type ComponentLibrary = {
  id: string;
  projectId: string;
  name: string;
  version: string;
  itemCount: number;
  createdAt: string;
  updatedAt: string;
};

type LibraryComponent = {
  id: string;
  libraryId: string;
  name: string;
  category: string;
  properties: Record<string, any>;
  usageCount: number;
  createdAt: string;
  updatedAt: string;
};

type DesignToken = {
  id: string;
  libraryId: string;
  name: string;
  type: string;
  value: string | number | Record<string, any>;
  category: string;
  createdAt: string;
  updatedAt: string;
};
```

## Query Key Structure for Cache Management

```typescript
// Equivalence
['equivalences'][('equivalences', 'list')][('equivalences', 'list', projectId)][ // Root // All lists // Specific project
  ('equivalences', 'detail', equivalenceId)
][ // Specific item
  // Canonical
  ('canonical', 'list', projectId)
][('canonical', 'projections', conceptId)][('canonical', 'pivots', itemId)][ // Concepts in project // Items for concept // Pivot targets
  // Journeys
  ('journeys', 'list', projectId, type)
][('journeys', 'steps', journeyId)][ // Journeys // Steps
  // Component Library
  ('componentLibrary', 'list', projectId)
][('componentLibrary', 'components', libraryId)][('componentLibrary', 'tokens', libraryId)][ // Libraries // Components // Tokens
  ('componentLibrary', 'usage', componentId)
]; // Usage
```

## Testing Imports

```typescript
import { equivalenceQueryKeys } from '@/api/equivalence';
import { canonicalQueryKeys } from '@/api/canonical';
import { journeyQueryKeys } from '@/api/journeys';
import { componentLibraryQueryKeys } from '@/api/componentLibrary';

// Use in test assertions
expect(equivalenceQueryKeys.list(projectId)).toEqual([
  'equivalences',
  'list',
  projectId,
  undefined,
]);
```

## Error Handling Pattern

```typescript
const { mutate, error } = useConfirmEquivalence({
  onError: (error) => {
    const message = error instanceof Error
      ? error.message
      : "Unknown error";
    console.error("Failed to confirm:", message);
  },
});

// In component
if (error) {
  return <ErrorAlert message={error.message} />;
}
```

## Performance Tips

1. **Use `staleTime`** - Reduce unnecessary refetches

   ```typescript
   useCanonicalConcepts(projectId, {
     staleTime: 5 * 60 * 1000, // 5 minutes
   });
   ```

2. **Use `select`** - Transform data

   ```typescript
   useCanonicalConcepts(projectId, {
     select: (data) => data.filter((c) => c.itemCount > 0),
   });
   ```

3. **Batch queries** - Fetch related data efficiently

   ```typescript
   const concepts = useCanonicalConcepts(projectId);
   const journeys = useDerivedJourneys(projectId);
   ```

4. **Manual invalidation** - Only when needed

   ```typescript
   const queryClient = useQueryClient();

   onSuccess: () => {
     queryClient.invalidateQueries({
       queryKey: equivalenceQueryKeys.lists(),
     });
   };
   ```

## Support & Documentation

- Full docs: See `src/api/README.md`
- Implementation details: See `REACT_QUERY_HOOKS.md`
- Tests: Check `src/__tests__/api/*.test.ts`

## Test Coverage

All 4 modules fully tested:

- ✅ 61 tests passing
- ✅ Query key generation
- ✅ Type validation
- ✅ Input structures
- ✅ Cache hierarchies

Run tests: `bun run test -- src/__tests__/api/*.test.ts`
