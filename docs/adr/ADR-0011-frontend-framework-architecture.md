# ADR-0011: Frontend Framework & Architecture

**Status:** Accepted
**Date:** 2026-02-06
**Deciders:** Development Team
**Supersedes:** N/A

---

## Context

TraceRTM frontend requires:

1. **Rich interactivity:** Graph visualizations, drag-and-drop, real-time updates
2. **Performance:** Handle 1000+ requirement graph, 60 FPS animations
3. **Developer experience:** Fast builds, hot reload, type safety
4. **State management:** Complex client state (traceability graph, filters, selections)
5. **Routing:** SPA with deep linking (/projects/:id/requirements/:reqId)

Technology constraints:
- **React ecosystem:** Established patterns, component libraries (Radix UI, shadcn/ui)
- **Build tool:** Fast builds (<5s), HMR (<100ms)
- **Type safety:** TypeScript strict mode
- **Bundle size:** <500KB initial bundle (gzipped)

## Decision

We will use:
- **Framework:** React 19 (with React Compiler)
- **Build tool:** Vite 8
- **Routing:** TanStack Router v1 (type-safe routing)
- **Data fetching:** TanStack Query v5 (server state)
- **State management:** Zustand (client state)
- **UI components:** Radix UI + shadcn/ui + Tailwind CSS

## Rationale

### Technology Stack (frontend/package.json)

```json
{
  "dependencies": {
    "react": "^19.2.0",                      // React 19 with compiler
    "react-dom": "^19.2.0",
    "@tanstack/react-router": "^1.158.1",    // Type-safe routing
    "@tanstack/react-query": "^5.90.14",     // Server state
    "@tanstack/react-table": "^8.21.3",      // Data tables
    "@tanstack/react-virtual": "^3.13.12",   // Virtualization
    "vite": "^8.0.0-beta.11",                // Build tool
    "tailwindcss": "^4.0.0",                 // Styling
    "zod": "4.3.6",                          // Validation
    "@radix-ui/react-*": "latest",           // Headless UI components
  },
  "devDependencies": {
    "@vitejs/plugin-react-swc": "^4.2.2",    // SWC (faster than Babel)
    "typescript": "5.9.3",                    // Type checking
    "vitest": "^4.0.18",                     // Testing
    "oxlint": "1.43.0",                      // Linting
  }
}
```

### Architecture

```
frontend/
├── apps/
│   ├── web/                    # Main SPA
│   │   ├── src/
│   │   │   ├── routes/         # TanStack Router routes
│   │   │   │   ├── __root.tsx
│   │   │   │   ├── index.tsx
│   │   │   │   └── projects/
│   │   │   │       ├── $projectId.tsx
│   │   │   │       └── $projectId.requirements.$reqId.tsx
│   │   │   ├── components/     # UI components
│   │   │   ├── hooks/          # Custom React hooks
│   │   │   ├── stores/         # Zustand stores
│   │   │   └── api/            # TanStack Query hooks
│   │   └── vite.config.ts
│   ├── docs/                   # Documentation site (separate app)
│   └── storybook/              # Component showcase
└── packages/
    ├── ui/                     # Shared UI components
    ├── graph-viz/              # Graph visualization (React Flow)
    ├── hooks/                  # Shared hooks
    └── utils/                  # Shared utilities
```

### Why These Choices

**React 19:**
- **React Compiler:** Auto-memoization (no manual `useMemo`, `useCallback`)
- **Concurrent features:** Suspense, transitions (smooth UX)
- **Actions:** Form handling with `useActionState`, `useFormStatus`

**Vite 8:**
- **Speed:** <2s cold start, <100ms HMR
- **Native ESM:** No bundling in dev (instant updates)
- **Build optimization:** Rollup-based (tree-shaking, code splitting)

**TanStack Router v1:**
```typescript
// Type-safe routing with params validation
import { createFileRoute } from '@tanstack/react-router'
import { z } from 'zod'

const projectParamsSchema = z.object({
  projectId: z.string().uuid(),
  reqId: z.string().uuid().optional(),
})

export const Route = createFileRoute('/projects/$projectId/requirements/$reqId')({
  params: {
    parse: (params) => projectParamsSchema.parse(params),
    stringify: (params) => params,
  },
  loader: async ({ params }) => {
    // Type-safe params.projectId, params.reqId
    return fetchRequirement(params.projectId, params.reqId)
  },
})

function RequirementPage() {
  const { projectId, reqId } = Route.useParams()  // Fully typed!
  const requirement = Route.useLoaderData()
  return <RequirementView data={requirement} />
}
```

**TanStack Query v5:**
```typescript
// Server state management (data fetching, caching)
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

function useRequirement(id: string) {
  return useQuery({
    queryKey: ['requirements', id],
    queryFn: () => api.getRequirement(id),
    staleTime: 5 * 60 * 1000,  // Cache 5 minutes
  })
}

function useUpdateRequirement() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (req: Requirement) => api.updateRequirement(req),
    onSuccess: (updated) => {
      // Optimistic update
      queryClient.setQueryData(['requirements', updated.id], updated)
    },
  })
}

function RequirementEditor({ id }: { id: string }) {
  const { data: requirement, isLoading } = useRequirement(id)
  const updateMutation = useUpdateRequirement()

  if (isLoading) return <Skeleton />

  return (
    <form onSubmit={(e) => {
      e.preventDefault()
      updateMutation.mutate(requirement)
    }}>
      <input value={requirement.title} onChange={(e) => {
        requirement.title = e.target.value
      }} />
    </form>
  )
}
```

**Zustand (Client State):**
```typescript
// Lightweight state management (no boilerplate)
import { create } from 'zustand'

interface GraphState {
  selectedNodes: string[]
  selectNode: (id: string) => void
  clearSelection: () => void
}

const useGraphStore = create<GraphState>((set) => ({
  selectedNodes: [],
  selectNode: (id) => set((state) => ({
    selectedNodes: [...state.selectedNodes, id]
  })),
  clearSelection: () => set({ selectedNodes: [] }),
}))

function GraphView() {
  const selectedNodes = useGraphStore((state) => state.selectedNodes)
  const selectNode = useGraphStore((state) => state.selectNode)

  return <ReactFlow nodes={nodes} onNodeClick={(node) => selectNode(node.id)} />
}
```

### Performance Optimizations

**React Virtualization:**
```typescript
import { useVirtualizer } from '@tanstack/react-virtual'

function RequirementList({ requirements }: { requirements: Requirement[] }) {
  const parentRef = useRef<HTMLDivElement>(null)

  const virtualizer = useVirtualizer({
    count: requirements.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 100,  // Estimated row height
  })

  return (
    <div ref={parentRef} style={{ height: '600px', overflow: 'auto' }}>
      <div style={{ height: `${virtualizer.getTotalSize()}px` }}>
        {virtualizer.getVirtualItems().map((virtualRow) => (
          <RequirementRow
            key={virtualRow.key}
            requirement={requirements[virtualRow.index]}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualRow.size}px`,
              transform: `translateY(${virtualRow.start}px)`,
            }}
          />
        ))}
      </div>
    </div>
  )
}
```

**Code Splitting:**
```typescript
// Route-based code splitting (automatic with Vite)
const ProjectPage = lazy(() => import('./routes/projects/$projectId'))
const GraphPage = lazy(() => import('./routes/graph'))

// Suspense fallback
<Suspense fallback={<LoadingSpinner />}>
  <ProjectPage />
</Suspense>
```

## Alternatives Rejected

### Alternative 1: Next.js (App Router)

- **Description:** React framework with SSR, file-based routing
- **Pros:** SEO-friendly, server components, built-in API routes
- **Cons:** Overkill for SPA (TraceRTM is auth-gated, no SEO), heavier runtime, Vercel-centric
- **Why Rejected:** TraceRTM is SPA (no SSR needed). TanStack Router provides better type safety without Next.js complexity.

### Alternative 2: Vue 3 (Composition API)

- **Description:** Alternative frontend framework
- **Pros:** Simpler learning curve, smaller bundle, built-in reactivity
- **Cons:** Smaller ecosystem (fewer graph libraries), less mature TypeScript support, team expertise in React
- **Why Rejected:** React ecosystem superior for complex UIs (React Flow, Radix UI). Team has React experience.

### Alternative 3: Svelte/SvelteKit

- **Description:** Compiled frontend framework (no virtual DOM)
- **Pros:** Smallest bundle, reactive by default, simple syntax
- **Cons:** Immature ecosystem (fewer libraries), smaller community, less TypeScript tooling
- **Why Rejected:** React Flow (graph viz) is React-only. Svelte ecosystem too small for complex traceability UI.

### Alternative 4: Angular

- **Description:** Full-featured framework (TypeScript-first)
- **Pros:** Batteries-included, strong TypeScript, enterprise support
- **Cons:** Heavy (1MB+ bundle), opinionated, slower DX, legacy patterns (RxJS, modules)
- **Why Rejected:** React 19 + Vite faster, lighter, better DX. Angular overkill for SPA.

## Consequences

### Positive

- **Developer experience:** <2s cold start (Vite), <100ms HMR, full TypeScript
- **Type safety:** TanStack Router params typed, TanStack Query inferred types
- **Performance:** React 19 compiler auto-optimizes, virtualization handles 10,000+ rows
- **Bundle size:** <300KB initial (gzipped), code splitting per route
- **Ecosystem:** Radix UI (accessible), shadcn/ui (beautiful), Tailwind CSS (rapid styling)

### Negative

- **React 19 maturity:** Compiler still new (beta in 2025), potential bugs
- **TanStack Router learning curve:** Type-safe routing requires understanding generics
- **Zustand vs Redux:** No Redux DevTools time-travel (less powerful debugging)
- **Vite 8 beta:** Vite 8 still beta (as of Feb 2026), may have edge case bugs

### Neutral

- **SPA vs MPA:** SPA chosen (no SSR), affects SEO (mitigated by auth-gated app)
- **CSS framework:** Tailwind chosen (utility-first), alternative: CSS Modules, styled-components
- **State management:** Zustand chosen (simple), alternative: Redux Toolkit, Jotai

## Implementation

### Affected Components

- `frontend/apps/web/` - Main SPA
- `frontend/packages/ui/` - Shared UI components
- `frontend/packages/graph-viz/` - React Flow wrappers
- `frontend/apps/web/src/routes/` - TanStack Router routes
- `frontend/apps/web/src/api/` - TanStack Query hooks

### Migration Strategy

**Phase 1: Vite + React 19 Setup (Week 1)**
- Initialize Vite project
- Configure React 19 (enable compiler)
- Add TypeScript strict mode
- Configure Tailwind CSS

**Phase 2: Routing (Week 2)**
- Install TanStack Router
- Create file-based routes
- Add params validation (Zod)
- Implement navigation guards (auth)

**Phase 3: Data Layer (Week 3)**
- Install TanStack Query
- Create API hooks (useProjects, useRequirements)
- Add optimistic updates
- Configure caching strategy

**Phase 4: UI Components (Week 4)**
- Install Radix UI, shadcn/ui
- Build component library (buttons, forms, modals)
- Add Storybook for component showcase

### Rollout Plan

- **Phase 1:** Scaffold (Vite + React)
- **Phase 2:** Basic routes (project list, requirement list)
- **Phase 3:** Data fetching (TanStack Query)
- **Phase 4:** Full UI (graph visualization, forms)

### Success Criteria

- [ ] <2s cold start (Vite dev server)
- [ ] <100ms HMR (hot module replacement)
- [ ] <300KB initial bundle (gzipped)
- [ ] 100/100 Lighthouse score (performance)
- [ ] Type-safe routing (TanStack Router)
- [ ] Render 10,000 requirements (virtualized)

## References

- [React 19 Documentation](https://react.dev/)
- [Vite Documentation](https://vite.dev/)
- [TanStack Router](https://tanstack.com/router)
- [TanStack Query](https://tanstack.com/query)
- [Zustand](https://github.com/pmndrs/zustand)
- [ADR-0004: Graph Visualization](ADR-0004-graph-visualization-library.md)

---

**Notes:**
- **React Compiler:** Enables auto-memoization (no manual `useMemo`, `useCallback` needed)
- **Vite 8:** Major upgrade from Vite 5 (rollup 5, faster builds)
- **TanStack Router:** Type-safe alternative to React Router
- **Bundle analysis:** Use `vite-bundle-visualizer` to monitor bundle size
- **Performance budget:** 300KB initial, 100KB per lazy chunk
