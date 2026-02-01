# TracerTM Graph Enhancement Plan

## Executive Summary

This plan addresses two core requirements:

1. **Rich Node Expansion & Entity System** - Click-to-expand nodes with progressive disclosure (collapsed → preview → panel → full page), deep hierarchy support (page → layout → section → component → element), and robust entity/link models

2. **DAG-Like Data & Layouts** - Realistic mock data with proper directed acyclic graph relationships, intuitive layout names, screenshot generation for UI nodes, and aggregation to reduce visual complexity

---

## Part 1: Entity & Link System Enhancement

### 1.1 Enhanced Entity Type Taxonomy

**UI/Visual Hierarchy** (Physical map of site/app):
```
site → page → layout → section → subsection → component → subcomponent → element
                                              ↳ modal, popup, toast, drawer
```

**Product/Requirements Hierarchy**:
```
initiative → epic → feature → user_story → acceptance_criteria
                           ↳ task → subtask
```

**Technical Hierarchy**:
```
service → module → class → function
       ↳ api_endpoint
       ↳ database_table → database_field
```

**Test Hierarchy**:
```
test_suite → test_case → test_step → assertion
          ↳ fixture, mock
```

### 1.2 Enhanced Link Types (19 types)

| Category | Link Types |
|----------|------------|
| **Hierarchical** | `parent_of`, `contains`, `part_of` |
| **Traceability** | `implements`, `tests`, `verifies`, `satisfies`, `derives_from`, `refines` |
| **Dependencies** | `depends_on`, `uses`, `imports`, `calls`, `blocks` |
| **UI Flow** | `navigates_to`, `triggers`, `opens`, `closes`, `renders`, `includes` |
| **Semantic** | `related_to`, `similar_to`, `conflicts_with`, `alternative_to`, `duplicates` |

Each link includes metadata:
- `confidence`: high | medium | low
- `coverage`: 0-100% (for implements/tests)
- `dependency_type`: required | optional | conditional
- `is_aggregated`: boolean (for visual simplification)

### 1.3 Aggregation Node System

To avoid 1000 connections to common components (error handlers, shared modals):

```typescript
interface AggregationNode {
  id: string;
  type: "aggregation";
  label: string;                    // "Error Handlers (47)"
  aggregatedType: EntityType;       // What's being aggregated
  aggregatedCount: number;          // 47
  aggregatedIds: string[];          // Actual item IDs
  criteria: {
    type: "common_parent" | "same_type" | "shared_dependency" | "custom";
    threshold: number;              // Min items to trigger aggregation (default: 5)
  };
  collapsed: boolean;               // Expand to see children
}
```

**Aggregation strategies**:
1. **Type-based**: Group all buttons, all forms, all error modals
2. **Shared dependency**: Items sharing same parent/dependency
3. **Threshold-based**: Auto-aggregate when edge count > N
4. **Community detection**: Use Louvain algorithm for data-driven clustering

---

## Part 2: Rich Node Expansion System

### 2.1 Progressive Disclosure (4 Levels)

| Level | Trigger | Content | Size |
|-------|---------|---------|------|
| **Collapsed** | Default | Icon + name + child count badge | 140x40px |
| **Preview** | Click | + type badge, description, stats, thumbnail | 280x200px |
| **Panel** | Double-click or "Expand" | + full metadata, relationships, actions, breadcrumbs | 360x400px |
| **Full Page** | "Open" button | Complete entity view with editing, history, related items | Full screen |

### 2.2 Node Component Structure

```typescript
interface ExpandableNodeData {
  // Identity
  item: Item;
  label: string;
  type: EntityType;

  // Hierarchy
  depth: number;
  path: string[];                   // Breadcrumb: ["site-1", "page-2", "layout-3"]
  hasChildren: boolean;
  childCount: number;
  parentId?: string;

  // Preview
  thumbnailUrl?: string;            // Screenshot thumbnail
  screenshotUrl?: string;           // Full screenshot
  interactiveUrl?: string;          // Live widget URL

  // Edit capabilities
  canEdit: boolean;
  editType: "instant" | "agent_required" | "manual";

  // State
  expansionState: "collapsed" | "preview" | "panel";
}
```

### 2.3 Edit Affordances

| Edit Type | Visual | Behavior |
|-----------|--------|----------|
| **Instant** | Lightning icon | Inline edit, saves immediately |
| **Agent Required** | Bot/sparkle icon | Opens agent dialog, "Ask Claude to..." |
| **Manual** | Pencil icon | Opens form/modal for complex edits |

---

## Part 3: Layout System Overhaul

### 3.1 Intuitive Layout Names

| Technical Name | User-Friendly Name | Best For | Icon |
|----------------|-------------------|----------|------|
| `dagre-TB` | **Flow Chart** | Requirements traceability, linear flows | ↓ |
| `dagre-LR` | **Timeline** | Process flows, left-to-right progression | → |
| `elk-layered` | **Hierarchical** | Deep org charts, component trees | 🌳 |
| `d3-force` | **Organic Network** | Exploratory analysis, relationships | 🌐 |
| `d3-radial` | **Mind Map** | Brainstorming, centered exploration | 🧠 |
| `d3-tree` | **Tree** | Single-root hierarchies, file systems | 📂 |
| `grid` | **Gallery** | Quick overview, many items | ⊞ |
| `circular` | **Wheel** | Cyclic processes, stakeholder maps | ⭕ |

### 3.2 Layout Recommendations by View

| Perspective | Recommended Layout | Reason |
|-------------|-------------------|--------|
| **Traceability** | Flow Chart | Shows requirements → implementation flow |
| **UI/Components** | Tree / Hierarchical | Natural component hierarchy |
| **Page Flow** | Timeline | User journey left-to-right |
| **Technical** | Hierarchical | Service → module → function |
| **Product** | Flow Chart | Epic → story → task |
| **All** | Organic Network | Exploratory, reveals clusters |

### 3.3 DAG Layout Algorithm (Dagre/ELK)

```typescript
// Proper hierarchical DAG layout
import dagre from '@dagrejs/dagre';

function applyDAGLayout(nodes: Node[], edges: Edge[]): Node[] {
  const g = new dagre.graphlib.Graph();
  g.setGraph({
    rankdir: 'TB',      // Top-to-bottom
    ranksep: 120,       // Space between ranks
    nodesep: 80,        // Space between nodes
    marginx: 40,
    marginy: 40
  });

  nodes.forEach(node => g.setNode(node.id, { width: 200, height: 80 }));
  edges.forEach(edge => g.setEdge(edge.source, edge.target));

  dagre.layout(g);

  return nodes.map(node => ({
    ...node,
    position: {
      x: g.node(node.id).x - 100,
      y: g.node(node.id).y - 40
    }
  }));
}
```

---

## Part 4: Screenshot Generation System

### 4.1 Two-Tier Architecture

**Tier 1: Component Screenshots (Storybook + Playwright)**
- Capture all component states from Storybook
- Run on build/CI pipeline
- Store as immutable versioned assets

**Tier 2: Live Page Screenshots (On-Demand + Cached)**
- Capture full pages/views when requested
- Background job queue with caching
- 7-day TTL with stale-while-revalidate

### 4.2 Version Tracking

| Stage | Version | Source | Screenshot Type |
|-------|---------|--------|-----------------|
| **Design** | v0 | Figma API | Design mockup |
| **Draft** | v0.1 | HTML render | Initial implementation |
| **Review** | v0.x | HTML render | Iteration screenshots |
| **Release** | v1 | HTML render | Production-ready |

### 4.3 Implementation

```typescript
// Item metadata structure
interface ItemMetadata {
  screenshots?: {
    [version: string]: {
      url: string;              // S3/CDN URL
      thumbnail: string;        // 150x150 thumbnail
      timestamp: string;
      capturedAt: "design" | "draft" | "review" | "release";
    };
  };
  screenshotUrl?: string;       // Current canonical
  thumbnailUrl?: string;        // Current thumbnail
}

// Capture pipeline
async function captureScreenshot(item: Item) {
  // 1. Render component/page with Playwright
  const screenshot = await playwright.screenshot(item.componentPath);

  // 2. Generate thumbnails (150x150, 300x300)
  const thumbnails = await generateThumbnails(screenshot);

  // 3. Upload to S3 with versioning
  const urls = await uploadToS3(screenshot, thumbnails, item.id, item.version);

  // 4. Update item metadata
  await updateItemMetadata(item.id, {
    screenshotUrl: urls.full,
    thumbnailUrl: urls.thumbnail
  });
}
```

---

## Part 5: Mock Data Enhancement

### 5.1 Current Problem

- Only 8 items with 4 links
- Flat hierarchy, no DAG structure
- No cross-view connections
- No realistic relationships

### 5.2 Enhanced Mock Data Structure

**Project: "E-Commerce Platform"**

```
Site (1)
├── Pages (8)
│   ├── Home Page
│   │   ├── Layout: Hero Section
│   │   │   ├── Component: Hero Banner
│   │   │   ├── Component: CTA Button (→ shared)
│   │   │   └── Component: Search Bar
│   │   └── Layout: Featured Products
│   │       ├── Component: Product Card (×6)
│   │       └── Component: View All Button
│   ├── Product Detail Page
│   │   ├── Layout: Product Info
│   │   │   ├── Component: Image Gallery
│   │   │   ├── Component: Price Display
│   │   │   └── Component: Add to Cart Button
│   │   └── Layout: Reviews Section
│   │       └── Component: Review Card (×N)
│   ├── Cart Page
│   ├── Checkout Page
│   ├── User Profile Page
│   ├── Order History Page
│   ├── Login Page
│   └── Register Page
├── Shared Components (12)
│   ├── Error Modal (used by 15 items) → AGGREGATE
│   ├── Loading Spinner (used by 20 items) → AGGREGATE
│   ├── Toast Notification (used by 25 items) → AGGREGATE
│   ├── Navigation Header
│   ├── Footer
│   ├── Button (Primary, Secondary, Danger)
│   └── Form Input
├── Epics (3)
│   ├── Epic: User Authentication
│   │   ├── Story: User can register
│   │   │   ├── Task: Create register form
│   │   │   ├── Task: Implement validation
│   │   │   └── Task: Connect to API
│   │   └── Story: User can login
│   ├── Epic: Shopping Cart
│   └── Epic: Checkout Flow
├── API Endpoints (6)
│   ├── POST /auth/register
│   ├── POST /auth/login
│   ├── GET /products
│   ├── GET /products/:id
│   ├── POST /cart/add
│   └── POST /checkout
└── Tests (15)
    ├── Test Suite: Authentication
    │   ├── Test: Register with valid data
    │   ├── Test: Register with invalid email
    │   └── Test: Login with correct credentials
    └── Test Suite: Cart
```

### 5.3 DAG Relationships

```
Epic: User Authentication
  ├── implements → POST /auth/register
  ├── implements → POST /auth/login
  └── tests → Test Suite: Authentication

Story: User can register
  ├── parent_of → Task: Create register form
  ├── derives_from → Epic: User Authentication
  └── traces_to → Register Page

Register Page
  ├── contains → Layout: Register Form
  ├── uses → Error Modal (aggregated)
  ├── uses → Loading Spinner (aggregated)
  └── navigates_to → Login Page

Component: Register Form
  ├── implements → Story: User can register
  ├── calls → POST /auth/register
  └── renders → Form Input (×4)

POST /auth/register
  ├── depends_on → Database: users table
  └── tests → Test: Register with valid data
```

---

## Part 6: Implementation Roadmap

### Phase 1: Foundation (Week 1-2)

| Task | Effort | Priority |
|------|--------|----------|
| Create `entity-hierarchy.ts` types | 4h | P0 |
| Enhance mock data (50+ items, 80+ links) | 6h | P0 |
| Implement Dagre layout algorithm | 4h | P0 |
| Add intuitive layout selector | 2h | P0 |
| Fix node-link connections in views | 4h | P0 |

**Deliverable**: Working DAG visualization with realistic data

### Phase 2: Node Expansion (Week 3-4)

| Task | Effort | Priority |
|------|--------|----------|
| Create ExpandableNode component | 8h | P0 |
| Implement 4-level progressive disclosure | 6h | P0 |
| Add breadcrumb navigation | 4h | P1 |
| Create NodeDetailPanel enhancements | 4h | P1 |
| Add keyboard navigation (arrow keys) | 3h | P1 |

**Deliverable**: Rich node expansion with preview/panel/full-page modes

### Phase 3: Screenshot System (Week 5-6)

| Task | Effort | Priority |
|------|--------|----------|
| Set up S3 bucket + CloudFront | 2h | P1 |
| Create Playwright screenshot utility | 4h | P1 |
| Implement thumbnail generation | 3h | P1 |
| Add screenshot metadata to items | 2h | P1 |
| Create background job queue | 6h | P2 |

**Deliverable**: Automated screenshot capture with thumbnails in graph

### Phase 4: Aggregation (Week 7-8)

| Task | Effort | Priority |
|------|--------|----------|
| Implement type-based aggregation | 4h | P1 |
| Create AggregateGroupNode component | 6h | P1 |
| Add expand/collapse animation | 2h | P2 |
| Implement threshold-based auto-aggregation | 4h | P2 |
| Add edge bundling for dense connections | 4h | P2 |

**Deliverable**: Clean graphs with 40-60% fewer visible nodes

### Phase 5: Polish (Week 9-10)

| Task | Effort | Priority |
|------|--------|----------|
| Add edit affordances (instant/agent/manual) | 4h | P1 |
| Implement drill-down navigation | 4h | P1 |
| Add graph search/filter | 4h | P2 |
| Performance optimization (virtual scrolling) | 6h | P2 |
| Mobile responsive improvements | 4h | P2 |

**Deliverable**: Production-ready graph with full feature set

---

## Part 7: Technical Architecture

### 7.1 Component Structure

```
/components/graph/
├── nodes/
│   ├── ExpandableNode.tsx         # Main rich node
│   ├── AggregateGroupNode.tsx     # Collapsed group
│   ├── CollapsedNodeView.tsx      # Minimal state
│   ├── PreviewNodeView.tsx        # Medium state
│   └── PanelNodeView.tsx          # Full control panel
├── edges/
│   ├── SmartEdge.tsx              # Auto-routing edge
│   └── BundledEdge.tsx            # For aggregated connections
├── layouts/
│   ├── useDAGLayout.ts            # Dagre implementation
│   ├── useForceLayout.ts          # D3-force simulation
│   └── useTreeLayout.ts           # D3-hierarchy
├── panels/
│   ├── NodeDetailPanel.tsx        # Right sidebar
│   ├── BreadcrumbTrail.tsx        # Path navigation
│   └── EditCapabilityBadge.tsx    # Edit type indicator
├── utils/
│   ├── aggregation.ts             # Grouping algorithms
│   ├── typeStyles.ts              # Type → icon/color
│   └── layoutPresets.ts           # Layout configurations
└── FlowGraphViewInner.tsx         # Main container
```

### 7.2 State Management

```typescript
interface GraphState {
  // View
  layout: LayoutType;
  perspective: GraphPerspective;

  // Selection
  selectedNodeId: string | null;
  expandedNodes: Set<string>;       // Panel-expanded nodes

  // Aggregation
  aggregatedGroups: AggregationNode[];
  expandedAggregates: Set<string>;

  // Navigation
  breadcrumbPath: string[];
  focusedNodeId: string | null;

  // Filters
  visibleTypes: EntityType[];
  searchQuery: string;
}
```

### 7.3 Data Flow

```
API (Items + Links)
  ↓
useItems() + useLinks() hooks
  ↓
Transform to HierarchicalEntity[]
  ↓
Apply aggregation rules
  ↓
Filter by perspective/search
  ↓
Calculate layout positions
  ↓
Convert to React Flow nodes/edges
  ↓
Render with ExpandableNode components
```

---

## Part 8: Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Items in mock data | 8 | 100+ |
| Links in mock data | 4 | 150+ |
| Node expansion levels | 1 | 4 |
| Layout options | 4 (broken) | 8 (working) |
| Screenshot support | None | Full pipeline |
| Aggregation | None | 40-60% reduction |
| Keyboard navigation | None | Full WAI-ARIA |
| Mobile support | Poor | Responsive |

---

## Appendix: Research Sources

All research documents saved to project root:

1. `GRAPH_LAYOUT_RESEARCH.md` - Layout algorithms (32 KB)
2. `GRAPH_NODE_EXPANSION_RESEARCH.md` - Node interaction patterns (35 KB)
3. `NODE_AGGREGATION_RESEARCH.md` - Aggregation strategies (40 KB)
4. `AGGREGATION_IMPLEMENTATION_GUIDE.md` - Code patterns (24 KB)
5. Screenshot generation research (internal agent summary)
6. atoms.tech codebase analysis (internal agent summary)

**Total research: ~150 KB of documentation ready for implementation**
