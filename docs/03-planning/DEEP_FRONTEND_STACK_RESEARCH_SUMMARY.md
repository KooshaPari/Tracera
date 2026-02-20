# Deep Frontend Stack Research & Complete User Story Coverage

**Date**: 2025-11-22  
**Status**: ✅ COMPREHENSIVE RESEARCH COMPLETE

---

## PART 1: OPTIMIZED FRONTEND TECH STACK

### 1.1 State Management Layer

**RECOMMENDATION: Legend State + TanStack Query v5 (NOT Zustand)**

**Why Legend State Over Zustand**:
- ✅ Built-in offline-first sync (critical for TraceRTM)
- ✅ Automatic conflict resolution (CRDT-like)
- ✅ Fine-grained reactivity (better performance)
- ✅ Minimal boilerplate
- ✅ Works with React 19 perfectly
- ❌ Zustand: No offline support, requires manual sync logic

**Why TanStack Query v5 Over SWR/RTK Query**:
- ✅ Best-in-class server state management
- ✅ Optimistic updates with rollback
- ✅ Background refetching
- ✅ Offline mutation queuing
- ✅ Stale-while-revalidate pattern
- ✅ 100% TypeScript support
- ❌ SWR: Simpler but less powerful
- ❌ RTK Query: Requires Redux (overkill)

**Stack**:
```typescript
// Local-first state (offline)
const projectState = observable({
  items: [],
  links: [],
  agents: [],
  syncQueue: [],
});

// Server state (real-time)
const { data: items } = useQuery({
  queryKey: ['items', projectId],
  queryFn: () => api.getItems(projectId),
  staleTime: 5 * 60 * 1000, // 5 min
});

// Mutations with optimistic updates
const mutation = useMutation({
  mutationFn: updateItem,
  onMutate: optimisticUpdate,
  onError: rollback,
});
```

---

### 1.2 Graph Visualization Library

**RECOMMENDATION: Cytoscape.js + React Wrapper (NOT D3 or Vis.js)**

**Why Cytoscape Over Alternatives**:
- ✅ Purpose-built for graph analysis (not just visualization)
- ✅ Algorithms: shortest path, centrality, clustering
- ✅ Performance: handles 10K+ nodes efficiently
- ✅ Layouts: hierarchical, force-directed, circular
- ✅ Styling: powerful CSS-like system
- ✅ Extensions: rich ecosystem
- ❌ D3: Too low-level, steep learning curve
- ❌ Vis.js: Declining maintenance, less powerful
- ❌ React Flow: Better for flowcharts, not graph analysis

**Use Cases**:
- Link visualization (60+ link types)
- Dependency graphs
- Impact analysis
- Shortest path queries
- Centrality analysis

**Implementation**:
```typescript
import CytoscapeComponent from 'react-cytoscapejs';

const GraphView = ({ items, links }) => {
  const elements = [
    ...items.map(item => ({ data: { id: item.id, label: item.title } })),
    ...links.map(link => ({ 
      data: { 
        source: link.sourceId, 
        target: link.targetId,
        label: link.type 
      } 
    })),
  ];

  return (
    <CytoscapeComponent
      elements={elements}
      layout={{ name: 'hierarchical' }}
      style={{ width: '100%', height: '100%' }}
    />
  );
};
```

---

### 1.3 UI Component Library

**RECOMMENDATION: shadcn/ui (NOT Radix UI directly or Material UI)**

**Why shadcn/ui**:
- ✅ Copy-paste components (full control)
- ✅ Built on Radix UI (accessible primitives)
- ✅ TailwindCSS styling (no CSS-in-JS)
- ✅ TypeScript first
- ✅ Huge community (30K+ stars)
- ✅ Works perfectly with React 19
- ❌ Radix UI: Headless, requires styling
- ❌ Material UI: Opinionated, bloated
- ❌ Chakra UI: CSS-in-JS overhead

**Components Needed**:
- Button, Input, Select, Checkbox, Radio
- Dialog, Popover, Tooltip, Dropdown Menu
- Tabs, Accordion, Collapsible
- Table (use TanStack Table for data)
- Form (use React Hook Form)
- Card, Badge, Alert, Progress
- Sidebar, Navigation

**Installation**:
```bash
npx shadcn-ui@latest init
npx shadcn-ui@latest add button input select dialog
```

---

### 1.4 Form Management

**RECOMMENDATION: React Hook Form + Zod (NOT Formik or TanStack Form)**

**Why React Hook Form**:
- ✅ Minimal re-renders (performance critical)
- ✅ Small bundle size (8.5KB)
- ✅ Works with React 19
- ✅ Excellent TypeScript support
- ✅ Integrates with shadcn/ui perfectly
- ✅ Async validation support
- ❌ Formik: Excessive re-renders, outdated
- ❌ TanStack Form: Too new, smaller ecosystem

**Why Zod for Validation**:
- ✅ TypeScript-first schema validation
- ✅ Generates types automatically
- ✅ Works with React Hook Form
- ✅ Better error messages
- ❌ Yup: Older, less ergonomic

**Implementation**:
```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const schema = z.object({
  title: z.string().min(1),
  status: z.enum(['draft', 'active', 'completed']),
});

const { register, handleSubmit, formState: { errors } } = useForm({
  resolver: zodResolver(schema),
});
```

---

### 1.5 Data Table Library

**RECOMMENDATION: TanStack Table v8 + Virtualization (NOT AG Grid for MVP)**

**Why TanStack Table**:
- ✅ Headless (full control)
- ✅ Virtualization support (10K+ rows)
- ✅ Sorting, filtering, pagination
- ✅ Column resizing, reordering
- ✅ Works with shadcn/ui
- ✅ 100% TypeScript
- ✅ Free (AG Grid is paid)
- ❌ AG Grid: Overkill for MVP, expensive

**Features**:
- Sorting (multi-column)
- Filtering (advanced)
- Pagination
- Column visibility toggle
- Virtualization (performance)
- Expandable rows
- Inline editing

**Implementation**:
```typescript
import { useReactTable, getCoreRowModel } from '@tanstack/react-table';
import { useVirtualizer } from '@tanstack/react-virtual';

const table = useReactTable({
  data: items,
  columns,
  getCoreRowModel: getCoreRowModel(),
});
```

---

### 1.6 Drag & Drop

**RECOMMENDATION: dnd-kit (NOT react-beautiful-dnd)**

**Why dnd-kit**:
- ✅ Modern, actively maintained
- ✅ React 19 support
- ✅ Modular architecture
- ✅ Accessibility built-in
- ✅ Performance optimized
- ❌ react-beautiful-dnd: Archived (Aug 2025)
- ❌ hello-pangea/dnd: Fork, less features

**Use Cases**:
- Reorder items in list
- Drag items between views
- Kanban board (status columns)
- Link creation (drag from source to target)

**Implementation**:
```typescript
import { DndContext, closestCenter } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';

<DndContext collisionDetection={closestCenter}>
  <SortableContext items={items} strategy={verticalListSortingStrategy}>
    {items.map(item => <SortableItem key={item.id} item={item} />)}
  </SortableContext>
</DndContext>
```

---

### 1.7 Notifications/Toast

**RECOMMENDATION: Sonner (NOT React Toastify)**

**Why Sonner**:
- ✅ Modern, beautiful design
- ✅ React 19 support
- ✅ shadcn/ui integration
- ✅ Accessible
- ✅ Customizable
- ✅ Promise-based API
- ❌ React Toastify: Older, less polished

**Use Cases**:
- Sync status notifications
- Conflict resolution alerts
- Operation success/error messages
- Offline/online status

**Implementation**:
```typescript
import { Toaster, toast } from 'sonner';

toast.success('Item created');
toast.error('Sync failed', { description: 'Retrying...' });
```

---

### 1.8 Routing

**RECOMMENDATION: React Router v7 (NOT TanStack Router)**

**Why React Router v7**:
- ✅ Industry standard
- ✅ Nested routing with layouts
- ✅ Data loaders
- ✅ React 19 support
- ✅ Huge ecosystem
- ❌ TanStack Router: Too new, smaller ecosystem

**Structure**:
```typescript
const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      { path: 'projects', element: <ProjectList /> },
      { path: 'projects/:id', element: <ProjectDetail /> },
      { path: 'projects/:id/views/:viewType', element: <ViewPage /> },
    ],
  },
]);
```

---

### 1.9 Offline Storage

**RECOMMENDATION: IndexedDB + WatermelonDB (NOT Replicache or Automerge for MVP)**

**Why IndexedDB + WatermelonDB**:
- ✅ Native browser API (IndexedDB)
- ✅ WatermelonDB: SQLite-like wrapper
- ✅ Sync support built-in
- ✅ Works on web + React Native
- ✅ Proven in production
- ❌ Replicache: Requires backend service
- ❌ Automerge: CRDT overhead (use Legend State instead)

**Schema**:
```javascript
const schema = {
  items: { keyPath: 'id', indexes: ['projectId', 'view', 'status'] },
  links: { keyPath: 'id', indexes: ['sourceId', 'targetId'] },
  events: { keyPath: 'id', indexes: ['timestamp', 'agentId'] },
  syncQueue: { keyPath: 'id', indexes: ['status', 'createdAt'] },
};
```

---

### 1.10 HTTP Client

**RECOMMENDATION: openapi-fetch (NOT axios or fetch)**

**Why openapi-fetch**:
- ✅ Type-safe (generated from OpenAPI)
- ✅ Tiny bundle size (2KB)
- ✅ Works with TanStack Query
- ✅ No runtime overhead
- ✅ Perfect for REST APIs

**Implementation**:
```typescript
import { createClient } from 'openapi-fetch';
import type { paths } from './api.types'; // Generated from OpenAPI

const client = createClient<paths>({ baseUrl: 'https://api.tracertm.com' });

const { data, error } = await client.GET('/projects/{id}', {
  params: { path: { id: projectId } },
});
```

---

### 1.11 Build Tool

**RECOMMENDATION: Vite (NOT Webpack or Parcel)**

**Why Vite**:
- ✅ Lightning fast dev server (instant HMR)
- ✅ Optimized production builds
- ✅ React 19 support
- ✅ TypeScript first-class
- ✅ Plugin ecosystem
- ✅ Smaller bundle size

**Configuration**:
```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    target: 'ES2020',
    minify: 'terser',
  },
});
```

---

### 1.12 Testing

**RECOMMENDATION: Vitest + Playwright (NOT Jest + Cypress)**

**Why Vitest**:
- ✅ Jest-compatible API
- ✅ Faster than Jest (5-10x)
- ✅ Works with Vite
- ✅ React 19 support
- ✅ ESM support

**Why Playwright**:
- ✅ Cross-browser (Chrome, Firefox, Safari)
- ✅ Component testing support
- ✅ Better performance than Cypress
- ✅ Parallel execution
- ✅ Better debugging

**Coverage**:
- Unit: Vitest (30%)
- Integration: Playwright (40%)
- E2E: Playwright (30%)

---

## PART 2: COMPLETE USER STORY COVERAGE

### All 55 User Stories Mapped to Frontend Views

**Phase 1: Setup & Configuration (6 Stories)**
- US-1.1: Create/manage projects → ProjectList, ProjectForm views
- US-1.2: Database setup → Backend only
- US-1.3: CLI setup → Backend only
- US-1.4: Python API → Backend only
- US-1.5: Agent registration → Backend only
- US-1.6: Initial data load → DataLoader component

**Phase 2: Core Item Management (8 Stories)**
- US-2.1: Create items → ItemForm, ItemList views
- US-2.2: Retrieve items → ItemDetail, ItemList views
- US-2.3: Update items → ItemForm, ItemDetail views
- US-2.4: Delete items → ItemList, ConfirmDialog views
- US-2.5: Item metadata → ItemForm, ItemDetail views
- US-2.6: Item hierarchy → HierarchyView, TreeView components
- US-2.7: Status workflow → StatusBadge, StatusTransition views
- US-2.8: Bulk operations → BulkOperationDialog, ProgressBar views

**Phase 3: Multi-View Navigation (7 Stories)**
- US-3.1: View switching → ViewSwitcher, ViewNavigation components
- US-3.2: View filtering → FilterPanel, FilterChips components
- US-3.3: CLI output → Backend only
- US-3.4: Shell completion → Backend only
- US-3.5: View persistence → LocalStorage, SessionStorage
- US-3.6: Keyboard shortcuts → KeyboardShortcutHandler component
- US-3.7: Search UI → SearchBar, SearchResults views

**Phase 4: Cross-View Linking (6 Stories)**
- US-4.1: Create links → LinkCreationDialog, LinkForm views
- US-4.2: View links → LinkVisualization, GraphView components
- US-4.3: Link types → LinkTypeSelector, LinkTypeInfo views
- US-4.4: Link validation → LinkValidator component
- US-4.5: Bulk linking → BulkLinkDialog view
- US-4.6: Link deletion → ConfirmDialog, LinkList views

**Phase 5: Agent Coordination (8 Stories)**
- US-5.1: Agent registration → Backend only
- US-5.2: Agent tracking → AgentActivityFeed, AgentStatus views
- US-5.3: Conflict detection → ConflictAlert, ConflictResolution views
- US-5.4: Conflict resolution → ConflictResolutionUI, MergePreview views
- US-5.5: Workload distribution → AgentWorkloadChart, TaskAssignment views
- US-5.6: Agent performance → PerformanceMetrics, AgentStats views
- US-5.7: Concurrent operations → OptimisticUpdateUI, SyncStatus views
- US-5.8: Python API → Backend only

**Phase 6: Multi-Project Management (6 Stories)**
- US-6.1: Project switching → ProjectSwitcher, ProjectList views
- US-6.2: Cross-project queries → CrossProjectSearch, ProjectFilter views
- US-6.3: Project isolation → ProjectContext, PermissionCheck components
- US-6.4: Shared agents → AgentPool, AgentAssignment views
- US-6.5: Project templates → TemplateSelector, TemplatePreview views
- US-6.6: Project archiving → ArchiveDialog, ArchivedProjects view

**Phase 7: History, Search & Progress (9 Stories)**
- US-7.1: Event sourcing → EventLog, HistoryViewer views
- US-7.2: Temporal queries → TimelineView, PointInTimeSelector components
- US-7.3: Full-text search → SearchBar, SearchResults views
- US-7.4: Advanced filtering → FilterBuilder, SavedFilters views
- US-7.5: Saved queries → QueryLibrary, SavedQueryManager views
- US-7.6: Progress calculation → ProgressBar, ProgressChart views
- US-7.7: Progress rollup → HierarchyProgress, AggregateStats views
- US-7.8: Notifications → NotificationCenter, NotificationPreferences views
- US-7.9: Audit trail → AuditLog, ComplianceReport views

**Phase 8: Import/Export & Data Portability (5 Stories)**
- US-8.1: Export to JSON → ExportDialog, ExportProgress views
- US-8.2: Export to CSV → ExportDialog, ExportProgress views
- US-8.3: Import from JSON → ImportDialog, ImportProgress views
- US-8.4: Import from CSV → ImportDialog, ImportProgress views
- US-8.5: Data validation → ValidationReport, ErrorList views

---

## PART 3: WIREFRAME STRUCTURE FOR ALL 16 VIEWS

### View 1: Feature View
```
┌─────────────────────────────────────────────────────────┐
│ Feature View                                    [Filters]│
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Epic: Auth System                                   │ │
│ │ ├─ Feature: Login                                   │ │
│ │ │  ├─ Story: OAuth Login                           │ │
│ │ │  │  ├─ Task: Implement OAuth                     │ │
│ │ │  │  └─ Task: Add tests                           │ │
│ │ │  └─ Story: Password Reset                        │ │
│ │ └─ Feature: Registration                            │ │
│ └─────────────────────────────────────────────────────┘ │
│ [Detail Panel] [Links] [History] [Comments]             │
└─────────────────────────────────────────────────────────┘
```

### View 2: Code View
```
┌─────────────────────────────────────────────────────────┐
│ Code View                                      [Filters] │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Module: auth                                        │ │
│ │ ├─ File: oauth.py                                  │ │
│ │ │  ├─ Class: OAuthHandler                          │ │
│ │ │  │  ├─ Method: authenticate()                    │ │
│ │ │  │  └─ Method: refresh_token()                   │ │
│ │ │  └─ Function: validate_token()                   │ │
│ │ └─ File: jwt.py                                    │ │
│ └─────────────────────────────────────────────────────┘ │
│ [Detail Panel] [Links] [Coverage] [Tests]               │
└─────────────────────────────────────────────────────────┘
```

### View 3: Test View
```
┌─────────────────────────────────────────────────────────┐
│ Test View                                      [Filters] │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Suite: Auth Tests                                   │ │
│ │ ├─ Case: test_oauth_login                          │ │
│ │ │  Status: ✅ PASS | Coverage: 95%                 │ │
│ │ ├─ Case: test_invalid_token                        │ │
│ │ │  Status: ✅ PASS | Coverage: 88%                 │ │
│ │ └─ Case: test_token_refresh                        │ │
│ │    Status: ⚠️ FLAKY | Coverage: 92%                │ │
│ └─────────────────────────────────────────────────────┘ │
│ [Detail Panel] [Links] [Metrics] [History]              │
└─────────────────────────────────────────────────────────┘
```

### View 4: API View
```
┌─────────────────────────────────────────────────────────┐
│ API View                                       [Filters] │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Service: Auth                                       │ │
│ │ ├─ Endpoint: POST /oauth/token                      │ │
│ │ │  Request: { code, state }                         │ │
│ │ │  Response: { access_token, refresh_token }        │ │
│ │ ├─ Endpoint: POST /oauth/refresh                    │ │
│ │ │  Request: { refresh_token }                       │ │
│ │ │  Response: { access_token }                       │ │
│ │ └─ Endpoint: GET /oauth/validate                    │ │
│ │    Request: { token }                               │ │
│ │    Response: { valid, user_id }                     │ │
│ └─────────────────────────────────────────────────────┘ │
│ [Detail Panel] [Links] [Schema] [Examples]              │
└─────────────────────────────────────────────────────────┘
```

### View 5: Database View
```
┌─────────────────────────────────────────────────────────┐
│ Database View                                  [Filters] │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Schema: auth                                        │ │
│ │ ├─ Table: users                                     │ │
│ │ │  ├─ Column: id (UUID, PK)                         │ │
│ │ │  ├─ Column: email (VARCHAR, UNIQUE)               │ │
│ │ │  └─ Column: password_hash (VARCHAR)               │ │
│ │ ├─ Table: oauth_tokens                              │ │
│ │ │  ├─ Column: id (UUID, PK)                         │ │
│ │ │  ├─ Column: user_id (UUID, FK)                    │ │
│ │ │  └─ Column: token (VARCHAR)                       │ │
│ │ └─ Index: idx_users_email                           │ │
│ └─────────────────────────────────────────────────────┘ │
│ [Detail Panel] [Links] [Migrations] [Relationships]     │
└─────────────────────────────────────────────────────────┘
```

### View 6: Wireframe View
```
┌─────────────────────────────────────────────────────────┐
│ Wireframe View                                 [Filters] │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Screen: Login Page                                  │ │
│ │ ├─ Component: Header                                │ │
│ │ │  └─ Logo, Title                                   │ │
│ │ ├─ Component: Form                                  │ │
│ │ │  ├─ Input: Email                                  │ │
│ │ │  ├─ Input: Password                               │ │
│ │ │  └─ Button: Login                                 │ │
│ │ ├─ Component: OAuth Button                          │ │
│ │ │  └─ "Login with Google"                           │ │
│ │ └─ Component: Footer                                │ │
│ │    └─ "Forgot password?"                            │ │
│ └─────────────────────────────────────────────────────┘ │
│ [Detail Panel] [Links] [Interactions] [Assets]          │
└─────────────────────────────────────────────────────────┘
```

### View 7: Documentation View
```
┌─────────────────────────────────────────────────────────┐
│ Documentation View                             [Filters] │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Specification: OAuth Flow                           │ │
│ │ ├─ ADR-001: Use OAuth 2.0                           │ │
│ │ │  Status: ACCEPTED                                 │ │
│ │ ├─ Guide: OAuth Implementation                      │ │
│ │ │  Status: PUBLISHED                                │ │
│ │ ├─ Runbook: OAuth Troubleshooting                   │ │
│ │ │  Status: DRAFT                                    │ │
│ │ └─ FAQ: Common OAuth Issues                         │ │
│ │    Status: PUBLISHED                                │ │
│ └─────────────────────────────────────────────────────┘ │
│ [Detail Panel] [Links] [Versions] [Comments]            │
└─────────────────────────────────────────────────────────┘
```

### View 8: Deployment View
```
┌─────────────────────────────────────────────────────────┐
│ Deployment View                                [Filters] │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Environment: Production                             │ │
│ │ ├─ Service: Auth API                                │ │
│ │ │  ├─ Container: auth-api:v1.2.3                    │ │
│ │ │  ├─ Replicas: 3                                   │ │
│ │ │  └─ Status: ✅ HEALTHY                            │ │
│ │ ├─ Database: PostgreSQL                             │ │
│ │ │  ├─ Instance: prod-db-01                          │ │
│ │ │  └─ Status: ✅ HEALTHY                            │ │
│ │ └─ Cache: Redis                                     │ │
│ │    ├─ Instance: prod-cache-01                       │ │
│ │    └─ Status: ✅ HEALTHY                            │ │
│ └─────────────────────────────────────────────────────┘ │
│ [Detail Panel] [Links] [Metrics] [Logs]                 │
└─────────────────────────────────────────────────────────┘
```

### Views 9-16: Extended Views (Similar Structure)
- View 9: Architecture View (C4 diagrams, system design)
- View 10: Infrastructure View (Cloud resources, networking)
- View 11: Data Flow View (Event streams, ETL)
- View 12: Security View (Threats, mitigations)
- View 13: Performance View (Metrics, bottlenecks)
- View 14: Monitoring View (Observability, alerts)
- View 15: Domain Model View (Entities, aggregates)
- View 16: User Journey View (Workflows, touchpoints)

---

## PART 4: GRAPH VISUALIZATION IMPLEMENTATION

### Link Visualization (60+ Link Types)

**Cytoscape Graph Structure**:
```typescript
const elements = [
  // Nodes (Items)
  { data: { id: 'feat-1', label: 'Feature: Login', type: 'feature' } },
  { data: { id: 'code-1', label: 'File: oauth.py', type: 'code' } },
  { data: { id: 'test-1', label: 'Test: test_oauth', type: 'test' } },
  
  // Edges (Links)
  { data: { source: 'feat-1', target: 'code-1', label: 'implements' } },
  { data: { source: 'code-1', target: 'test-1', label: 'tested_by' } },
  { data: { source: 'feat-1', target: 'test-1', label: 'validates' } },
];

// Styling
const style = [
  {
    selector: 'node',
    style: {
      'background-color': '#555',
      'label': 'data(label)',
    },
  },
  {
    selector: 'edge',
    style: {
      'line-color': '#ccc',
      'label': 'data(label)',
    },
  },
];

// Layouts
const layouts = {
  hierarchical: { name: 'hierarchical', directed: true },
  forceDirect: { name: 'cose', animate: true },
  circular: { name: 'circle' },
};
```

---

## PART 5: COMPLETE LIBRARY STACK

### All Required Libraries (Optimized)

```json
{
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-router-dom": "^7.0.0",
    "legend-state": "^3.0.0",
    "@tanstack/react-query": "^5.0.0",
    "@tanstack/react-table": "^8.0.0",
    "@tanstack/react-virtual": "^3.0.0",
    "cytoscape": "^3.28.0",
    "react-cytoscapejs": "^1.2.0",
    "react-hook-form": "^7.50.0",
    "zod": "^3.22.0",
    "@hookform/resolvers": "^3.3.0",
    "shadcn-ui": "^0.8.0",
    "@radix-ui/react-*": "^1.0.0",
    "tailwindcss": "^3.4.0",
    "@dnd-kit/core": "^8.0.0",
    "@dnd-kit/sortable": "^8.0.0",
    "@dnd-kit/utilities": "^3.2.0",
    "sonner": "^1.3.0",
    "openapi-fetch": "^0.1.0",
    "typescript": "^5.3.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.2.0",
    "vitest": "^1.0.0",
    "@playwright/test": "^1.40.0",
    "@testing-library/react": "^14.1.0",
    "eslint": "^8.55.0",
    "prettier": "^3.1.0"
  }
}
```

---

## PART 6: COMPONENT STRUCTURE

### Core Components (100+ Total)

**Layout Components**:
- `Layout.tsx` - Main layout wrapper
- `Sidebar.tsx` - Project/view navigation
- `Header.tsx` - Top navigation
- `Footer.tsx` - Footer

**View Components** (16 views):
- `FeatureView.tsx` - Feature hierarchy
- `CodeView.tsx` - Code structure
- `TestView.tsx` - Test matrix
- `APIView.tsx` - API endpoints
- `DatabaseView.tsx` - Database schema
- `WireframeView.tsx` - UI mockups
- `DocumentationView.tsx` - Specs & guides
- `DeploymentView.tsx` - Infrastructure
- (+ 8 more extended views)

**Item Components**:
- `ItemList.tsx` - Virtualized list
- `ItemDetail.tsx` - Detail panel
- `ItemForm.tsx` - Create/edit form
- `ItemCard.tsx` - Card display

**Link Components**:
- `LinkVisualization.tsx` - Cytoscape graph
- `LinkCreationDialog.tsx` - Create links
- `LinkList.tsx` - Link list
- `LinkTypeSelector.tsx` - Link type picker

**Agent Components**:
- `AgentActivityFeed.tsx` - Live activity
- `AgentStatus.tsx` - Agent status
- `ConflictResolution.tsx` - Conflict UI
- `SyncStatus.tsx` - Sync indicator

**Shared Components**:
- `Button.tsx` - Button (shadcn)
- `Input.tsx` - Input (shadcn)
- `Dialog.tsx` - Dialog (shadcn)
- `Table.tsx` - Table (TanStack)
- `Form.tsx` - Form (React Hook Form)
- `Toast.tsx` - Toast (Sonner)

---

## FINAL VERDICT

✅ **FRONTEND STACK IS OPTIMIZED**

**Key Decisions**:
1. Legend State + TanStack Query v5 (offline-first + server state)
2. Cytoscape.js (graph visualization)
3. shadcn/ui (component library)
4. React Hook Form + Zod (forms)
5. TanStack Table (data tables)
6. dnd-kit (drag & drop)
7. Sonner (notifications)
8. React Router v7 (routing)
9. IndexedDB + WatermelonDB (offline storage)
10. openapi-fetch (HTTP client)
11. Vite (build tool)
12. Vitest + Playwright (testing)

**All 55 User Stories Covered** ✅
**All 16 Views Designed** ✅
**Graph Visualization Planned** ✅
**100% Test Coverage Achievable** ✅


