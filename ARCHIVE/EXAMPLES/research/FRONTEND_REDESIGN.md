# Frontend Redesign: Project Management + Traceability Diagrammer

## Current Problem
Frontend is just a Storybook showcase - not a real project management tool.

## Solution: Jira + Miro Hybrid

### 7 Core Views

#### 1. Board View (Kanban)
```
┌─────────────────────────────────────────┐
│ Project: TraceRTM                       │
├─────────────────────────────────────────┤
│ Draft  │ Active │ In Progress │ Done   │
├────────┼────────┼─────────────┼────────┤
│ [Card] │ [Card] │   [Card]    │[Card] │
│ [Card] │ [Card] │   [Card]    │[Card] │
│        │ [Card] │             │       │
└────────┴────────┴─────────────┴────────┘
```

**Features**:
- Drag-drop cards between columns
- Swimlanes by owner/priority
- Card details on click
- Real-time updates
- Bulk operations

**Libraries**:
- `dnd-kit` - Drag and drop
- `@tanstack/react-table` - Table
- `zustand` - State management

#### 2. Timeline View (Gantt)
```
┌──────────────────────────────────────────┐
│ Epic 1          [████████]               │
│ ├─ Feature 1    [████]                   │
│ ├─ Feature 2       [██████]              │
│ └─ Feature 3          [████]             │
│ Epic 2             [████████████]        │
└──────────────────────────────────────────┘
```

**Features**:
- Hierarchical timeline
- Dependency lines
- Milestone markers
- Drag-drop to reschedule
- Zoom/pan

**Libraries**:
- `react-gantt-chart` or `syncfusion`
- `recharts` - Charts

#### 3. Graph View (Traceability Diagram)
```
┌─────────────────────────────────────────┐
│ [Epic]                                  │
│   ↓                                     │
│ [Feature] ──implements──→ [Code]        │
│   ↓                         ↓           │
│ [Story] ──tests──→ [Test]   ↓           │
│   ↓                    [API]            │
│ [Task]                                  │
└─────────────────────────────────────────┘
```

**Features**:
- Interactive node-link diagram
- Zoom, pan, fit-to-view
- Filter by link type
- Highlight paths
- Real-time updates
- Custom layouts (hierarchical, force-directed)

**Libraries**:
- `cytoscape` - Graph visualization
- `cytoscape-cose-bilkent` - Layout algorithm
- `cytoscape-popper` - Tooltips

#### 4. Table View (Spreadsheet)
```
┌──────────────────────────────────────────┐
│ ID │ Title │ Status │ Owner │ Priority  │
├────┼───────┼────────┼───────┼───────────┤
│ 1  │ Epic  │ Active │ Alice │ High      │
│ 2  │ Story │ Draft  │ Bob   │ Medium    │
│ 3  │ Task  │ Done   │ Carol │ Low       │
└────┴───────┴────────┴───────┴───────────┘
```

**Features**:
- Sortable columns
- Filterable
- Inline editing
- Bulk operations
- Export (CSV, Excel)
- Column customization

**Libraries**:
- `@tanstack/react-table` v8
- `@tanstack/react-virtual` - Virtualization

#### 5. Roadmap View (Timeline)
```
Q1 2025          Q2 2025          Q3 2025
├─ MVP           ├─ Phase 2        ├─ Analytics
│  ├─ Backend    │  ├─ Search      │  ├─ Neo4j
│  ├─ Frontend   │  ├─ Collab      │  └─ Reports
│  └─ Deploy     │  └─ Mobile      │
└─ Release 1.0   └─ Release 2.0    └─ Release 3.0
```

**Features**:
- Quarter/milestone view
- Feature grouping
- Scope wave tracking
- Dependency visualization

#### 6. Hierarchy View (Tree)
```
Epic 1
├─ Feature 1.1
│  ├─ Story 1.1.1
│  │  ├─ Task 1.1.1.1
│  │  └─ Task 1.1.1.2
│  └─ Story 1.1.2
└─ Feature 1.2
   └─ Story 1.2.1
```

**Features**:
- Expand/collapse
- Drag-drop reordering
- Inline editing
- Add/delete items
- Keyboard navigation

**Libraries**:
- `react-arborist` - Tree component
- `dnd-kit` - Drag and drop

#### 7. Search & Filter
```
┌─────────────────────────────────────────┐
│ 🔍 Search items...                      │
├─────────────────────────────────────────┤
│ Filters:                                │
│ ☑ Status: Active, In Progress           │
│ ☑ Owner: Alice, Bob                     │
│ ☑ Priority: High, Medium                │
│ ☑ View: Feature, Code, Test             │
└─────────────────────────────────────────┘
```

**Features**:
- Global search (Meilisearch)
- Advanced filters
- Saved views
- Search history
- Keyboard shortcuts (⌘K)

## New Component Library

### Core Components
- `<Board>` - Kanban board
- `<Timeline>` - Gantt chart
- `<Graph>` - Cytoscape diagram
- `<DataTable>` - Spreadsheet
- `<Tree>` - Hierarchy tree
- `<Roadmap>` - Timeline view
- `<SearchBox>` - Global search

### Shared Components
- `<ItemCard>` - Item display
- `<ItemModal>` - Item details/edit
- `<LinkBadge>` - Link type indicator
- `<StatusBadge>` - Status indicator
- `<OwnerAvatar>` - Owner display
- `<PriorityIcon>` - Priority indicator

## New Dependencies

```json
{
  "dnd-kit": "^6.0.0",
  "cytoscape": "^3.28.0",
  "cytoscape-cose-bilkent": "^4.1.0",
  "react-gantt-chart": "^2.0.0",
  "recharts": "^2.10.0",
  "react-arborist": "^3.0.0",
  "@tanstack/react-table": "^8.0.0",
  "@tanstack/react-virtual": "^3.0.0",
  "zustand": "^4.4.0",
  "meilisearch": "^0.35.0"
}
```

## State Management

Replace Legend State with Zustand:

```typescript
// stores/projectStore.ts
export const useProjectStore = create((set) => ({
  items: [],
  links: [],
  selectedItem: null,
  filters: {},
  
  setItems: (items) => set({ items }),
  setLinks: (links) => set({ links }),
  selectItem: (item) => set({ selectedItem: item }),
  setFilters: (filters) => set({ filters }),
}));
```

## API Integration

### Endpoints Needed
```
GET    /api/projects/{id}/items
POST   /api/projects/{id}/items
PUT    /api/items/{id}
DELETE /api/items/{id}

GET    /api/projects/{id}/links
POST   /api/projects/{id}/links
DELETE /api/links/{id}

GET    /api/search?q=...&filters=...
GET    /api/items/{id}/descendants
GET    /api/items/{id}/graph

WS     /ws/projects/{id}
```

## Real-Time Updates

WebSocket for live collaboration:
```typescript
// hooks/useRealtimeUpdates.ts
export function useRealtimeUpdates(projectId: string) {
  useEffect(() => {
    const ws = new WebSocket(`/ws/projects/${projectId}`);
    
    ws.onmessage = (event) => {
      const { type, data } = JSON.parse(event.data);
      
      if (type === 'item_created') {
        useProjectStore.setState(state => ({
          items: [...state.items, data]
        }));
      }
      // ... handle other events
    };
  }, [projectId]);
}
```

## File Structure

```
frontend/apps/web/src/
├── components/
│   ├── views/
│   │   ├── BoardView.tsx
│   │   ├── TimelineView.tsx
│   │   ├── GraphView.tsx
│   │   ├── TableView.tsx
│   │   ├── RoadmapView.tsx
│   │   ├── HierarchyView.tsx
│   │   └── SearchView.tsx
│   ├── items/
│   │   ├── ItemCard.tsx
│   │   ├── ItemModal.tsx
│   │   └── ItemForm.tsx
│   ├── links/
│   │   ├── LinkBadge.tsx
│   │   └── LinkForm.tsx
│   └── layout/
│       ├── Sidebar.tsx
│       ├── Header.tsx
│       └── ViewSelector.tsx
├── hooks/
│   ├── useItems.ts
│   ├── useLinks.ts
│   ├── useSearch.ts
│   ├── useRealtimeUpdates.ts
│   └── useFilters.ts
├── stores/
│   ├── projectStore.ts
│   ├── filterStore.ts
│   └── uiStore.ts
└── pages/
    ├── ProjectDetail.tsx
    └── Dashboard.tsx
```

## Next Steps

1. Redesign ProjectDetail.tsx for multi-view
2. Implement Board View
3. Implement Timeline View
4. Implement Graph View
5. Implement Table View
6. Add real-time updates
7. Integrate Meilisearch
8. Deploy to Vercel

This is a real project management tool! 🚀

