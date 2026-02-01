# View Specialization: Quick Start Guide

**For:** New developers implementing specialized views
**Reading Time:** 10-15 minutes
**Complements:** VIEW_SPECIALIZATION_STRATEGY.md, VIEW_SPECIALIZATION_TECHNICAL_GUIDE.md

---

## 30-Second Summary

TraceRTM is transforming 15+ generic `ItemsTableView` components into specialized, domain-optimized views (API explorer, Code browser, Database ERD, etc.). This guide gets you started implementing a specialized view in 2-3 days.

---

## Step 1: Understand Your View (1 hour)

### Read the Strategy Document
1. Go to `/docs/guides/VIEW_SPECIALIZATION_STRATEGY.md`
2. Find your view in the "Domain-Specific View Specifications" section (e.g., "API View: Endpoint Explorer")
3. Read: Target Experience, Key Components, Data Requirements, API Endpoints

**Example:** For API View, you'll see it needs:
- EndpointBrowser component
- RequestBuilder component
- ResponsePreview component
- OpenAPI spec fetching

### Ask These Questions
- [ ] What is the PRIMARY use case for this view?
- [ ] What data entities does it show?
- [ ] What are the 3-5 most common user interactions?
- [ ] Does it use a visualization (graph, timeline, matrix)?
- [ ] What backend APIs already exist? What's missing?

---

## Step 2: Set Up the File Structure (30 minutes)

### Create View Component File
```bash
# Create the view route component
touch frontend/apps/web/src/pages/projects/views/[YourView]View.tsx

# Create the data hook
touch frontend/apps/web/src/hooks/use[YourView]ViewData.ts

# Create specialized components directory
mkdir -p frontend/apps/web/src/components/specialized/[yourview]
```

### Create Basic View Structure
```tsx
// frontend/apps/web/src/pages/projects/views/[YourView]View.tsx

import { useParams } from "@tanstack/react-router";
import { use[YourView]ViewData } from "@/hooks/use[YourView]ViewData";

export function [YourView]View() {
  const { projectId } = useParams({ from: "/projects/$projectId" });
  const viewData = use[YourView]ViewData(projectId);

  if (viewData.isLoading) return <div>Loading...</div>;
  if (viewData.error) return <div>Error: {viewData.error.message}</div>;

  return (
    <div className="flex-1 p-6 space-y-6">
      <h1 className="text-3xl font-bold">[Your View Title]</h1>
      {/* Main content here */}
    </div>
  );
}

export const [YOUR_VIEW] = [YourView]View;
```

### Create Data Hook
```tsx
// frontend/apps/web/src/hooks/use[YourView]ViewData.ts

import { useQuery } from "@tanstack/react-query";
import { useState, useCallback, useMemo } from "react";
import * as api from "@/api/client";

export function use[YourView]ViewData(projectId: string) {
  const [filters, setFilters] = useState({});
  const [selected, setSelected] = useState<string | null>(null);

  // Fetch data
  const { data: rawData, isLoading, error } = useQuery({
    queryKey: ["[yourview]", projectId, filters],
    queryFn: () => api.get[YourViewItems](projectId, filters),
  });

  // Transform data
  const transformedData = useMemo(() => {
    if (!rawData) return null;
    return processDataForView(rawData);
  }, [rawData]);

  return {
    data: transformedData,
    selected,
    setSelected,
    filters,
    setFilters,
    isLoading,
    error,
  };
}
```

---

## Step 3: Create Specialized Components (1-2 days)

### Identify Your Components
From the strategy doc for your view, list the key components:

**Example for API View:**
```
- EndpointBrowser (shows list of endpoints)
- RequestBuilder (build request to test)
- ResponsePreview (shows response)
- ApiSchemaViewer (shows request/response schema)
```

### Build Each Component
```tsx
// frontend/apps/web/src/components/specialized/api/EndpointBrowser.tsx

interface EndpointBrowserProps {
  endpoints: ApiEndpoint[];
  selected?: string;
  onSelect: (id: string) => void;
}

export function EndpointBrowser({
  endpoints,
  selected,
  onSelect,
}: EndpointBrowserProps) {
  return (
    <div className="space-y-2">
      {endpoints.map(endpoint => (
        <button
          key={endpoint.id}
          onClick={() => onSelect(endpoint.id)}
          className={`w-full text-left px-3 py-2 rounded
            ${selected === endpoint.id ? 'bg-blue-100' : 'hover:bg-gray-100'}
          `}
        >
          <span className="font-mono text-sm font-bold">{endpoint.method}</span>
          {' '}
          <span>{endpoint.path}</span>
        </button>
      ))}
    </div>
  );
}
```

### Use Shared Components Where Possible

Instead of building everything from scratch, use shared components:

| Task | Shared Component | Location |
|------|-----------------|----------|
| Show visualizations | `DomainVisualization` | `/components/shared/visualization/` |
| Display item details | `DetailsInspector` | `/components/shared/panels/` |
| Search & filter | `SearchFilterPanel` | `/components/shared/panels/` |
| Show metrics | `MetricsPanel` | `/components/shared/panels/` |
| Tree structures | `HierarchicalTree` | `/components/shared/browsers/` |
| Compare two versions | `DiffViewer` | `/components/shared/editors/` |

**Example:**
```tsx
// Instead of building search from scratch
<SearchFilterPanel
  filters={[
    {
      id: 'method',
      label: 'HTTP Method',
      type: 'multi-select',
      options: [
        { label: 'GET', value: 'GET' },
        { label: 'POST', value: 'POST' },
      ],
    },
  ]}
  onFilterChange={setFilters}
/>
```

---

## Step 4: Handle Visualizations (if needed)

### If Your View Shows a Graph/Diagram

1. **Use `DomainVisualization`** wrapper component (handles Cytoscape, D3, etc.)

```tsx
import { DomainVisualization } from "@/components/shared/visualization/DomainVisualization";

// Transform your data to GraphData format
const graphData: GraphData = {
  nodes: [
    { id: '1', label: 'Endpoint 1', type: 'endpoint' },
    { id: '2', label: 'Endpoint 2', type: 'endpoint' },
  ],
  edges: [
    { id: 'e1', source: '1', target: '2', label: 'calls' },
  ],
};

return (
  <DomainVisualization
    type="graph"
    data={graphData}
    layout={{ type: 'hierarchical' }}
    onNodeSelect={(id) => setSelected(id)}
  />
);
```

2. **Choose layout type** for your domain:
   - `hierarchical` - Org charts, feature hierarchies, class hierarchies
   - `force` - Dependencies, relationships where layout is flexible
   - `dag` - Directed acyclic graphs (pipelines, workflows)
   - `custom` - Implement custom layout algorithm

### If Your View Shows a Tree

Use `HierarchicalTree`:
```tsx
import { HierarchicalTree } from "@/components/shared/browsers/HierarchicalTree";

<HierarchicalTree
  items={features}
  childrenKey="features"
  renderItem={(item, level) => (
    <div style={{ paddingLeft: `${level * 20}px` }}>
      {item.title}
    </div>
  )}
  expandedIds={expandedIds}
  onToggleExpand={toggleExpanded}
  virtualized={true} // For large lists
/>
```

---

## Step 5: Connect to Backend APIs (1 day)

### Check What APIs Exist
```bash
# Search for existing endpoints in backend handlers
grep -r "GET /api" backend/internal/handlers/ | grep -i "[yourview]"

# Check types
grep -r "type.*Items" backend/internal/models/ | head -20
```

### If APIs Exist
Use them directly in your hook:
```tsx
const { data } = useQuery({
  queryKey: ["api-endpoints", projectId],
  queryFn: () => fetch(`/api/v1/projects/${projectId}/items?view=api`),
});
```

### If APIs Need Enhancement
Document what you need and coordinate with backend team:
```markdown
## Needed APIs for [YourView] View

### GET /api/v1/projects/{projectId}/[yourview]/data
- Purpose: Fetch view-specific data
- Required response fields: [list them]
- Example: [show example response]
- Estimated effort: [hours]
```

---

## Step 6: Write Tests (4-6 hours)

### Unit Test: Component
```tsx
// frontend/apps/web/src/components/specialized/api/EndpointBrowser.test.tsx
import { render, screen } from "@testing-library/react";
import { EndpointBrowser } from "./EndpointBrowser";

describe("EndpointBrowser", () => {
  it("renders endpoints", () => {
    const endpoints = [
      { id: "1", method: "GET", path: "/users" },
    ];

    render(
      <EndpointBrowser
        endpoints={endpoints}
        onSelect={jest.fn()}
      />
    );

    expect(screen.getByText("/users")).toBeInTheDocument();
  });
});
```

### Integration Test: View
```tsx
// frontend/apps/web/src/pages/projects/views/ApiView.test.tsx
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClientProvider } from "@tanstack/react-query";
import { ApiView } from "./ApiView";

jest.mock("@/api/client");

describe("ApiView", () => {
  it("loads and displays endpoints", async () => {
    (api.getEndpoints as jest.Mock).mockResolvedValue([
      { id: "1", method: "GET", path: "/users" },
    ]);

    render(
      <QueryClientProvider client={testQueryClient}>
        <ApiView projectId="test-project" />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText("/users")).toBeInTheDocument();
    });
  });
});
```

---

## Step 7: Optimize & Document (1-2 days)

### Performance Checklist
- [ ] Is data fetching memoized with `useMemo`?
- [ ] Are event handlers wrapped with `useCallback`?
- [ ] Are large lists virtualized (100+ items)?
- [ ] Are heavy components code-split with `lazy`?
- [ ] Are visualizations using efficient rendering (Cytoscape, not D3 for large graphs)?

### Documentation Checklist
- [ ] Added component storybook stories
- [ ] Documented component props with JSDoc
- [ ] Added inline comments for complex logic
- [ ] Documented required backend APIs
- [ ] Added usage examples in component

---

## Common Patterns You'll Use

### Pattern 1: Fetch & Transform Data
```tsx
const { data: raw } = useQuery(...);
const transformed = useMemo(() => {
  if (!raw) return null;
  return raw.map(item => ({
    ...item,
    computed_field: expensive_computation(item),
  }));
}, [raw]);
```

### Pattern 2: Selection State
```tsx
const [selectedId, setSelectedId] = useState<string | null>(null);
const selected = useMemo(() => {
  return data?.find(item => item.id === selectedId);
}, [data, selectedId]);
```

### Pattern 3: Filters
```tsx
const [filters, setFilters] = useState<Filters>({});
const filtered = useMemo(() => {
  return applyFilters(data, filters);
}, [data, filters]);
```

### Pattern 4: Modal/Detail View
```tsx
const [detailId, setDetailId] = useState<string | null>(null);

if (detailId) {
  return <DetailView id={detailId} onClose={() => setDetailId(null)} />;
}

return <MainView onSelectItem={(id) => setDetailId(id)} />;
```

---

## Implementation Checklist

### Week 1: Foundation
- [ ] Read strategy doc for your view
- [ ] Create basic view structure
- [ ] Implement data hook with sample data
- [ ] Create 1-2 primary components
- [ ] Set up tests infrastructure

### Week 2: Core Features
- [ ] Complete all components
- [ ] Integrate with backend APIs
- [ ] Handle errors and loading states
- [ ] Implement search/filter (or use SearchFilterPanel)
- [ ] Add unit tests

### Week 3: Polish & Launch
- [ ] Performance optimization
- [ ] Accessibility audit (run axe-core)
- [ ] Visual regression tests (Chromatic)
- [ ] Documentation & storybook
- [ ] Code review & QA
- [ ] Feature flag setup for rollout

---

## Common Mistakes to Avoid

| Mistake | Problem | Solution |
|---------|---------|----------|
| Not memoizing expensive computations | Unnecessary re-renders, performance issues | Use `useMemo` for derived data |
| Fetching data in components | Race conditions, duplicate requests | Use React Query in custom hook |
| Building everything from scratch | Wasted time, inconsistent patterns | Reuse shared components |
| Not handling loading/error states | Confusing UX | Always show loading spinner and error message |
| Large component files | Unmaintainable code | Split into smaller components in subdirectory |
| No type definitions | Unsafe code, poor DX | Use TypeScript interfaces throughout |
| Missing tests | Regressions, low confidence | Aim for 70%+ test coverage |

---

## Getting Help

### Documentation
- **Overall strategy** → `docs/guides/VIEW_SPECIALIZATION_STRATEGY.md`
- **Technical deep dive** → `docs/guides/VIEW_SPECIALIZATION_TECHNICAL_GUIDE.md`
- **Component library** → Check `/components/shared/` README files
- **Similar implementations** → Look at `TestCaseView` or `QADashboardView` (already specialized)

### Shared Components Reference
```
Search/Filter → SearchFilterPanel in /components/shared/panels/
Details panel → DetailsInspector in /components/shared/panels/
Graphs → DomainVisualization in /components/shared/visualization/
Metrics → MetricsPanel in /components/shared/panels/
Trees → HierarchicalTree in /components/shared/browsers/
Diffs → DiffViewer in /components/shared/editors/
```

### Code Examples
Check the "Code Examples" section in `VIEW_SPECIALIZATION_TECHNICAL_GUIDE.md` for complete working examples of:
- API View implementation
- Database View with ERD
- Feature View with hierarchy

---

## Timeline Estimate

| Task | Time | Notes |
|------|------|-------|
| Understand requirements | 1-2 hours | Read strategy doc |
| Set up structure | 30 min | Create files and directory structure |
| Build components | 1-2 days | Main implementation effort |
| Backend integration | 1 day | Connect to APIs |
| Tests | 1 day | Unit + integration tests |
| Optimization | 1 day | Performance & accessibility |
| Documentation | 1 day | Stories, docs, comments |
| **Total** | **4-5 days** | Single developer, moderate complexity |

**Variations:**
- **Simple view** (Configuration, CRUD) → **2-3 days**
- **Complex view with visualization** (Database, Architecture) → **1-2 weeks**
- **Very complex with multiple visualizations** (Code view) → **2-3 weeks**

---

## Next: What to Read

1. **Before starting:** Read your view spec in `VIEW_SPECIALIZATION_STRATEGY.md` (pages 5-50)
2. **During implementation:** Reference `VIEW_SPECIALIZATION_TECHNICAL_GUIDE.md` for patterns
3. **For shared components:** Check specific component READMEs in `/components/shared/`
4. **For questions:** Look at similar existing views (`TestCaseView`, `QADashboardView`)

---

## Questions?

If you're stuck:
1. Check if a similar component already exists
2. Look at test cases for usage examples
3. Check component Storybook stories
4. Ask on team chat with what you've tried so far

Good luck! 🚀

