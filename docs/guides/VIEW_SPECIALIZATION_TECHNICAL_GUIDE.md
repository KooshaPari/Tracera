# TraceRTM View Specialization: Technical Implementation Guide

**Document Version:** 1.0
**Created:** January 31, 2026
**Target Audience:** Frontend & Backend Engineers

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Component Patterns](#component-patterns)
3. [Data Flow Architecture](#data-flow-architecture)
4. [Shared Component Library](#shared-component-library)
5. [Performance Patterns](#performance-patterns)
6. [Testing Strategies](#testing-strategies)
7. [Backend Integration](#backend-integration)
8. [Code Examples](#code-examples)

---

## Architecture Overview

### Layered View Architecture

```
┌─────────────────────────────────────────────────┐
│         View Container (Route Component)        │
│  Handles: routing, auth, layout, error handling │
└──────────────────────┬──────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────┐
│      View Component (e.g., ApiView)            │
│  Handles: data fetching, state mgmt, composition │
└──────────────────────┬──────────────────────────┘
                       ↓
    ┌──────────────────┴──────────────────┐
    ↓                                     ↓
┌──────────────────┐          ┌──────────────────┐
│ View-Specific    │          │  Shared/Generic  │
│ Components       │          │  Components      │
├──────────────────┤          ├──────────────────┤
│ ApiSchemaViewer  │          │ Visualization    │
│ EndpointBrowser  │          │ SearchFilter     │
│ RequestBuilder   │          │ DetailsPanel     │
│ ResponsePreview  │          │ DiffViewer       │
│ DependencyGraph  │          │ MetricsPanel     │
└──────────────────┘          │ HierarchicalTree │
                              │ Timeline         │
                              │ MatrixView       │
                              └──────────────────┘
                       ↓
┌─────────────────────────────────────────────────┐
│      Domain/Utility Components                  │
│  (@tracertm/ui, lucide-react, custom utils)    │
└─────────────────────────────────────────────────┘
```

### Directory Structure

```
frontend/apps/web/src/
├── pages/projects/views/           # Route-level view components
│   ├── ApiView.tsx                 # NEW specialized view
│   ├── CodeView.tsx                # NEW specialized view
│   ├── DatabaseView.tsx            # NEW specialized view
│   ├── DomainView.tsx              # NEW specialized view
│   ├── FeatureView.tsx             # Enhanced existing
│   ├── TestCaseView.tsx            # Already specialized
│   └── QADashboardView.tsx         # Already specialized
│
├── components/specialized/         # NEW: View-specific components
│   ├── api/
│   │   ├── EndpointBrowser.tsx
│   │   ├── RequestBuilder.tsx
│   │   ├── ResponsePreview.tsx
│   │   └── ApiSchemaViewer.tsx
│   ├── code/
│   │   ├── FileTreeExplorer.tsx
│   │   ├── CodeBrowser.tsx
│   │   ├── SymbolIndex.tsx
│   │   └── CodeMetrics.tsx
│   ├── database/
│   │   ├── ERDDiagram.tsx
│   │   ├── TableBrowser.tsx
│   │   ├── QueryBuilder.tsx
│   │   └── SchemaViewer.tsx
│   ├── domain/
│   │   ├── DomainModelDiagram.tsx
│   │   ├── BoundedContextExplorer.tsx
│   │   ├── AggregateViewer.tsx
│   │   └── UbiquitousLanguageGlossary.tsx
│   └── ...other views...
│
├── components/shared/              # NEW: Reusable view components
│   ├── visualization/
│   │   ├── DomainVisualization.tsx (wrapper)
│   │   ├── CytoscapeVisualization.tsx
│   │   ├── D3Visualization.tsx
│   │   └── VisualizationControls.tsx
│   ├── panels/
│   │   ├── DetailsInspector.tsx
│   │   ├── MetricsPanel.tsx
│   │   ├── SearchFilterPanel.tsx
│   │   └── TimelinePanel.tsx
│   ├── browsers/
│   │   ├── HierarchicalTree.tsx
│   │   ├── DataBrowser.tsx
│   │   └── VirtualizedList.tsx
│   ├── editors/
│   │   ├── DiffViewer.tsx
│   │   ├── QueryEditor.tsx
│   │   └── FormBuilder.tsx
│   └── matrix/
│       ├── MatrixView.tsx
│       └── MatrixCell.tsx
│
├── hooks/                          # NEW: View-specific hooks
│   ├── useApiViewData.ts
│   ├── useCodeViewData.ts
│   ├── useDatabaseViewData.ts
│   ├── useDomainViewData.ts
│   ├── useFeatureViewData.ts
│   └── ...more hooks...
│
├── lib/visualization/              # NEW: Visualization utilities
│   ├── cytoscapeLayouts.ts
│   ├── elkLayouts.ts
│   ├── d3Utils.ts
│   ├── colorScales.ts
│   └── geometryUtils.ts
│
└── types/views/                    # NEW: View-specific types
    ├── api.types.ts
    ├── code.types.ts
    ├── database.types.ts
    └── ...more types...
```

---

## Component Patterns

### Pattern 1: Container Component + Hooks Pattern

**Best for:** Separating logic from presentation, testability

```tsx
// hooks/useApiViewData.ts
export interface UseApiViewDataOptions {
  projectId: string;
  filters?: ApiFilters;
}

export function useApiViewData(options: UseApiViewDataOptions) {
  const { projectId, filters = {} } = options;

  // Fetch raw data
  const { data: spec, isLoading: specLoading, error: specError } = useQuery({
    queryKey: ['openapi-spec', projectId],
    queryFn: () => api.getOpenApiSpec(projectId),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Local state
  const [selectedEndpointId, setSelectedEndpointId] = useState<string | null>(null);
  const [requestState, setRequestState] = useState<RequestBuilderState>({
    method: 'GET',
    headers: {},
    body: null,
  });

  // Computed data
  const endpoints = useMemo(() => {
    if (!spec) return [];
    return filterAndMapEndpoints(spec.endpoints, filters);
  }, [spec, filters]);

  const selectedEndpoint = useMemo(() => {
    return endpoints.find(e => e.id === selectedEndpointId);
  }, [endpoints, selectedEndpointId]);

  // Actions
  const setFilters = useCallback((newFilters: ApiFilters) => {
    // Update URL or local state
    updateSearchParams(newFilters);
  }, []);

  const executeRequest = useCallback(async () => {
    if (!selectedEndpoint) return;
    const response = await api.testApiEndpoint(projectId, {
      endpoint: selectedEndpoint,
      request: requestState,
    });
    return response;
  }, [projectId, selectedEndpoint, requestState]);

  return {
    // Data
    endpoints,
    selectedEndpoint,
    spec,

    // State
    selectedEndpointId,
    requestState,

    // Actions
    setSelectedEndpointId,
    setRequestState,
    setFilters,
    executeRequest,

    // Meta
    isLoading: specLoading,
    error: specError,
  };
}

// pages/projects/views/ApiView.tsx
export function ApiView({ projectId }: ApiViewProps) {
  const viewData = useApiViewData({ projectId });

  if (viewData.isLoading) return <LoadingState />;
  if (viewData.error) return <ErrorState error={viewData.error} />;

  return (
    <div className="grid grid-cols-3 gap-4">
      <EndpointBrowser
        endpoints={viewData.endpoints}
        selected={viewData.selectedEndpointId}
        onSelect={viewData.setSelectedEndpointId}
      />
      <RequestBuilder
        endpoint={viewData.selectedEndpoint}
        state={viewData.requestState}
        onChange={viewData.setRequestState}
        onExecute={viewData.executeRequest}
      />
      <ResponsePreview endpoint={viewData.selectedEndpoint} />
    </div>
  );
}
```

### Pattern 2: Visualization Abstraction

**Best for:** Reusing visualization logic across views with different visualization libraries

```tsx
// components/shared/visualization/DomainVisualization.tsx
export interface DomainVisualizationProps<T = any> {
  data: GraphData<T>;
  type: 'graph' | 'hierarchy' | 'timeline' | 'matrix';

  // Appearance
  layout?: LayoutConfig;
  colorScale?: ColorScaleConfig;
  nodeSize?: 'fixed' | 'dynamic';

  // Interaction
  interactive?: boolean;
  onNodeSelect?: (nodeId: string) => void;
  onNodeDblClick?: (nodeId: string) => void;
  onNodeHover?: (nodeId: string | null) => void;
  onEdgeClick?: (edgeId: string) => void;

  // Controls
  showZoomControls?: boolean;
  showPanControls?: boolean;
  showLegend?: boolean;

  // Highlighting
  highlightedNodeIds?: Set<string>;
  highlightedPathIds?: Set<string>;
  highlightRules?: HighlightRule[];
}

export function DomainVisualization<T>({
  data,
  type,
  layout,
  interactive = true,
  onNodeSelect,
  ...props
}: DomainVisualizationProps<T>) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [vizInstance, setVizInstance] = useState<VizInstance | null>(null);

  // Choose visualization engine based on type
  useEffect(() => {
    if (!containerRef.current) return;

    const visualizer = selectVisualizationEngine(type);
    const instance = visualizer.create(containerRef.current, {
      data,
      layout,
      interactive,
      ...props,
    });

    instance.on('node:select', (nodeId) => onNodeSelect?.(nodeId));

    setVizInstance(instance);

    return () => instance.dispose();
  }, [type, data, layout, interactive, onNodeSelect]);

  return (
    <div ref={containerRef} className="w-full h-full">
      {vizInstance && (
        <VisualizationControls
          instance={vizInstance}
          showZoom={props.showZoomControls}
          showPan={props.showPanControls}
        />
      )}
    </div>
  );
}

// Utility to select the right visualization engine
function selectVisualizationEngine(type: string) {
  switch (type) {
    case 'graph':
      return CytoscapeVisualization;
    case 'hierarchy':
      return D3Hierarchy;
    case 'timeline':
      return D3Timeline;
    case 'matrix':
      return ReactMatrixView;
    default:
      throw new Error(`Unknown visualization type: ${type}`);
  }
}
```

### Pattern 3: Custom Hook for Shared Logic

**Best for:** Data transformations, filtering, sorting logic

```tsx
// hooks/useTreeHierarchy.ts
export function useTreeHierarchy<T extends { id: string; children?: T[] }>(
  items: T[],
  options: TreeHierarchyOptions = {}
) {
  const { initialExpanded = new Set(), sortBy } = options;

  const [expandedIds, setExpandedIds] = useState<Set<string>>(initialExpanded);

  // Toggle expand/collapse
  const toggleExpanded = useCallback((id: string) => {
    setExpandedIds(prev => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }, []);

  // Get visible items (respecting expanded state)
  const visibleItems = useMemo(() => {
    return flattenHierarchy(items, expandedIds);
  }, [items, expandedIds]);

  // Get tree statistics
  const stats = useMemo(() => {
    return {
      totalNodes: countNodes(items),
      expandedCount: expandedIds.size,
      visibleCount: visibleItems.length,
      maxDepth: getMaxDepth(items),
    };
  }, [items, expandedIds, visibleItems]);

  return {
    expandedIds,
    toggleExpanded,
    expandAll: () => setExpandedIds(new Set(getAllIds(items))),
    collapseAll: () => setExpandedIds(new Set()),
    visibleItems,
    stats,
  };
}

// Usage
function FeatureView({ projectId }: FeatureViewProps) {
  const { features } = useFeatureViewData({ projectId });
  const {
    expandedIds,
    toggleExpanded,
    visibleItems,
    expandAll,
    collapseAll,
  } = useTreeHierarchy(features, { initialExpanded: new Set(['epic-1']) });

  return (
    <div>
      <div className="flex gap-2">
        <button onClick={expandAll}>Expand All</button>
        <button onClick={collapseAll}>Collapse All</button>
      </div>

      <HierarchicalTree
        items={visibleItems}
        expandedIds={expandedIds}
        onToggleExpand={toggleExpanded}
      />
    </div>
  );
}
```

### Pattern 4: Provider Pattern for View Context

**Best for:** Sharing state across multiple components in a view

```tsx
// contexts/ApiViewContext.tsx
export interface ApiViewContextType {
  projectId: string;
  selectedEndpointId: string | null;
  requestState: RequestBuilderState;
  responseData: ResponseData | null;

  setSelectedEndpointId: (id: string | null) => void;
  setRequestState: (state: RequestBuilderState) => void;
  setResponseData: (data: ResponseData | null) => void;
}

const ApiViewContext = createContext<ApiViewContextType | null>(null);

export function ApiViewProvider({ projectId, children }: PropsWithChildren) {
  const [selectedEndpointId, setSelectedEndpointId] = useState<string | null>(null);
  const [requestState, setRequestState] = useState<RequestBuilderState>({
    method: 'GET',
    headers: {},
  });
  const [responseData, setResponseData] = useState<ResponseData | null>(null);

  const value: ApiViewContextType = {
    projectId,
    selectedEndpointId,
    requestState,
    responseData,
    setSelectedEndpointId,
    setRequestState,
    setResponseData,
  };

  return (
    <ApiViewContext.Provider value={value}>
      {children}
    </ApiViewContext.Provider>
  );
}

export function useApiViewContext() {
  const context = useContext(ApiViewContext);
  if (!context) {
    throw new Error('useApiViewContext must be used within ApiViewProvider');
  }
  return context;
}

// Usage
export function ApiView({ projectId }: ApiViewProps) {
  return (
    <ApiViewProvider projectId={projectId}>
      <div className="grid grid-cols-3 gap-4">
        <EndpointBrowser />
        <RequestBuilder />
        <ResponsePreview />
      </div>
    </ApiViewProvider>
  );
}

function EndpointBrowser() {
  const { selectedEndpointId, setSelectedEndpointId } = useApiViewContext();
  // ...
}
```

---

## Data Flow Architecture

### Unidirectional Data Flow

```
User Input (click, type, scroll)
    ↓
Event Handler
    ↓
State Update
    ↓
Re-render with new state
    ↓
Side Effect (API call, analytics)
```

### Example: Complete Data Flow for API View

```tsx
// 1. User clicks endpoint in list
<EndpointBrowser
  endpoints={endpoints}
  onSelect={(id) => {
    // Event handler
    setSelectedEndpointId(id);
    // Track analytics
    analytics.track('api_endpoint_selected', { endpointId: id });
  }}
/>

// 2. State updates, component re-renders
const selectedEndpoint = useMemo(() => {
  return endpoints.find(e => e.id === selectedEndpointId);
}, [endpoints, selectedEndpointId]);

// 3. Dependent components receive new props
<RequestBuilder endpoint={selectedEndpoint} />

// 4. Side effects execute (optional)
useEffect(() => {
  if (!selectedEndpoint) return;

  // Fetch additional data about the endpoint
  api.getEndpointDetails(selectedEndpoint.id)
    .then(details => {
      // Update another piece of state if needed
      updateEndpointDetails(details);
    });
}, [selectedEndpoint]);
```

### Data Fetching Pattern

```tsx
// Fetch data with React Query
const { data: items, isLoading, error } = useQuery({
  queryKey: ['items', projectId, filters],
  queryFn: () => api.getItems({ projectId, ...filters }),
  staleTime: 5 * 60 * 1000, // 5 min
  gcTime: 10 * 60 * 1000,   // 10 min (formerly cacheTime)
  retry: 2,
  retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
});

// Transform data (memoized)
const transformedData = useMemo(() => {
  if (!items) return null;
  return transformItemsForView(items);
}, [items]);

// Render
if (isLoading) return <LoadingState />;
if (error) return <ErrorState error={error} />;
return <ViewComponent data={transformedData} />;
```

---

## Shared Component Library

### Component: DomainVisualization (Wrapper)

**File:** `/components/shared/visualization/DomainVisualization.tsx`

Provides a unified interface to different visualization engines. Automatically selects the best engine for the data type.

```tsx
export interface GraphData<T = any> {
  nodes: VisualizationNode<T>[];
  edges: VisualizationEdge[];
  metadata?: {
    title?: string;
    description?: string;
  };
}

export interface VisualizationNode<T = any> {
  id: string;
  label: string;
  type?: string;
  data?: T;
  style?: NodeStyle;
  metadata?: Record<string, any>;
}

export interface VisualizationEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  type?: 'directed' | 'undirected';
  style?: EdgeStyle;
}

// Usage across views:
// API View - Dependency graph
<DomainVisualization
  type="graph"
  data={endpointDependencyGraph}
  layout={{ type: 'hierarchical' }}
  onNodeSelect={handleEndpointSelect}
/>

// Database View - ER Diagram
<DomainVisualization
  type="graph"
  data={erDiagramData}
  layout={{ type: 'force', strength: 0.5 }}
  colorScale={tableTypeColorScale}
/>

// Domain View - Aggregate graph
<DomainVisualization
  type="graph"
  data={domainModelGraph}
  layout={{ type: 'force' }}
  highlightRules={[
    { type: 'aggregate', color: 'blue' },
    { type: 'entity', color: 'green' },
    { type: 'value-object', color: 'purple' },
  ]}
/>
```

### Component: HierarchicalTree

**File:** `/components/shared/browsers/HierarchicalTree.tsx`

Renders tree structures with optional virtualization.

```tsx
export interface HierarchicalTreeProps<T> {
  items: T[];
  childrenKey?: string; // defaults to 'children'
  renderItem: (item: T, level: number) => ReactNode;
  expandedIds?: Set<string>;
  onToggleExpand?: (id: string) => void;
  virtualized?: boolean; // Use react-window for large trees
  getItemId?: (item: T) => string;
  isChildrenLoading?: (itemId: string) => boolean; // For async loading
  onLoadChildren?: (parentId: string) => Promise<void>;
}

// Usage in FEATURE view
<HierarchicalTree
  items={epics}
  childrenKey="features"
  renderItem={(item, level) => (
    <EpicRow epic={item} level={level} />
  )}
  expandedIds={expandedIds}
  onToggleExpand={toggleExpanded}
  virtualized={true}
/>

// Usage in CONFIGURATION view
<HierarchicalTree
  items={configGroups}
  renderItem={(item) => (
    <ConfigurationRow config={item} />
  )}
  onLoadChildren={async (parentId) => {
    const children = await api.getConfigChildren(parentId);
    addToCache(parentId, children);
  }}
/>
```

### Component: DetailsInspector

**File:** `/components/shared/panels/DetailsInspector.tsx`

Displays detailed information about a selected item with customizable sections.

```tsx
export interface DetailsInspectorProps {
  item: any;
  sections: InspectorSection[];
  readOnly?: boolean;
  onPropertyChange?: (property: string, value: any) => void;
  expandedSections?: Set<string>;
  onToggleSection?: (sectionId: string) => void;
}

export interface InspectorSection {
  id: string;
  title: string;
  icon?: ReactNode;
  properties: InspectorProperty[];
}

export interface InspectorProperty {
  key: string;
  label: string;
  type: 'string' | 'number' | 'boolean' | 'date' | 'select' | 'custom';
  value: any;
  readOnly?: boolean;
  options?: Array<{ label: string; value: any }>;
  render?: (value: any) => ReactNode;
}

// Usage in API view
<DetailsInspector
  item={selectedEndpoint}
  sections={[
    {
      id: 'basic',
      title: 'Basic Info',
      properties: [
        { key: 'method', label: 'HTTP Method', type: 'string' },
        { key: 'path', label: 'Path', type: 'string' },
        { key: 'description', label: 'Description', type: 'string' },
      ],
    },
    {
      id: 'request',
      title: 'Request Schema',
      properties: [
        {
          key: 'requestBody',
          label: 'Body',
          type: 'custom',
          render: (value) => <JsonViewer data={value} />,
        },
      ],
    },
  ]}
  readOnly={true}
/>
```

### Component: SearchFilterPanel

**File:** `/components/shared/panels/SearchFilterPanel.tsx`

Unified search and filter UI for all views.

```tsx
export interface SearchFilterPanelProps {
  searchPlaceholder?: string;
  filters: FilterDefinition[];
  onSearch?: (query: string) => void;
  onFilterChange?: (filters: FilterState) => void;
  savedSearches?: SavedSearch[];
  onSavedSearch?: (searchId: string) => void;
  searchDebounceMs?: number;
}

export interface FilterDefinition {
  id: string;
  label: string;
  type: 'select' | 'multi-select' | 'range' | 'date' | 'text';
  options?: Array<{ label: string; value: any }>;
  defaultValue?: any;
}

// Usage across all views
<SearchFilterPanel
  searchPlaceholder="Search endpoints..."
  filters={[
    {
      id: 'method',
      label: 'HTTP Method',
      type: 'multi-select',
      options: [
        { label: 'GET', value: 'GET' },
        { label: 'POST', value: 'POST' },
        // ...
      ],
    },
    {
      id: 'status',
      label: 'Status',
      type: 'select',
      options: [
        { label: 'Implemented', value: 'implemented' },
        { label: 'Planned', value: 'planned' },
      ],
    },
  ]}
  onSearch={setSearchQuery}
  onFilterChange={setFilters}
/>
```

### Component: MetricsPanel

**File:** `/components/shared/panels/MetricsPanel.tsx`

Display KPIs and metrics in various formats.

```tsx
export interface MetricsPanelProps {
  metrics: Metric[];
  layout?: 'grid' | 'stacked' | 'sparkline';
  columns?: number;
  compareMode?: boolean;
  onMetricClick?: (metric: Metric) => void;
  timeRange?: TimeRange;
  onTimeRangeChange?: (range: TimeRange) => void;
}

export interface Metric {
  id: string;
  label: string;
  value: number;
  unit?: string;
  format?: 'number' | 'percent' | 'bytes' | 'duration';
  trend?: 'up' | 'down' | 'neutral';
  trendPercent?: number;
  benchmark?: number;
  status?: 'good' | 'warning' | 'critical';
  onClick?: () => void;
}

// Usage in QA view
<MetricsPanel
  metrics={[
    { id: 'pass-rate', label: 'Pass Rate', value: 92.5, unit: '%', format: 'percent' },
    { id: 'avg-duration', label: 'Avg Duration', value: 2.3, unit: 's' },
    { id: 'flaky-tests', label: 'Flaky Tests', value: 3, status: 'warning' },
  ]}
  layout="grid"
  columns={3}
/>
```

### Component: DiffViewer

**File:** `/components/shared/editors/DiffViewer.tsx`

Visual diff for comparing versions.

```tsx
export interface DiffViewerProps {
  oldData: any;
  newData: any;
  fieldMap?: Record<string, string>; // Map field paths to display names
  highlightLevel?: 'field' | 'value' | 'character';
  format?: 'unified' | 'split';
  ignoreFields?: string[];
}

// Usage in CONFIGURATION view
<DiffViewer
  oldData={configV1}
  newData={configV2}
  format="split"
  highlightLevel="value"
/>
```

---

## Performance Patterns

### Pattern 1: Memoization Strategy

```tsx
// Memoize expensive computations
const expensiveResult = useMemo(() => {
  return performExpensiveComputation(inputData);
}, [inputData]); // Only recompute when inputData changes

// Memoize callback functions
const handleSelect = useCallback((id: string) => {
  setSelected(id);
  analytics.track('item_selected', { id });
}, []);

// Memoize components that don't need to re-render
const EndpointItem = memo(function EndpointItem({ endpoint, selected }: Props) {
  return <div>{endpoint.name}</div>;
}, (prev, next) => {
  // Custom comparison: only re-render if critical props change
  return prev.endpoint.id === next.endpoint.id &&
         prev.selected === next.selected;
});
```

### Pattern 2: Virtualization for Large Lists

```tsx
import { useVirtualizer } from '@tanstack/react-virtual';

function LargeListView({ items }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => containerRef.current,
    estimateSize: useCallback(() => 35, []), // row height
    overscan: 10, // render 10 items outside viewport
  });

  const virtualItems = virtualizer.getVirtualItems();
  const totalSize = virtualizer.getTotalSize();

  return (
    <div ref={containerRef} className="overflow-auto h-96">
      <div style={{ height: `${totalSize}px` }}>
        {virtualItems.map(virtualItem => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualItem.size}px`,
              transform: `translateY(${virtualItem.start}px)`,
            }}
          >
            <ItemRow item={items[virtualItem.index]} />
          </div>
        ))}
      </div>
    </div>
  );
}
```

### Pattern 3: Lazy Loading Images & Assets

```tsx
function AsyncImageViewer({ imageUrl }: Props) {
  const [imageSrc, setImageSrc] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const img = new Image();
    img.onload = () => {
      setImageSrc(img.src);
      setIsLoading(false);
    };
    img.onerror = () => setIsLoading(false);
    img.src = imageUrl;
  }, [imageUrl]);

  if (isLoading) return <ImagePlaceholder />;
  if (!imageSrc) return <ImageError />;
  return <img src={imageSrc} alt="preview" />;
}
```

### Pattern 4: Code-Splitting by View

```tsx
// routes/projects.$projectId.views.api.tsx
import { lazy, Suspense } from 'react';
import { LoadingFallback } from '@/components/LoadingFallback';

const ApiViewLazy = lazy(() =>
  import('@/pages/projects/views/ApiView').then(m => ({
    default: m.ApiView,
  }))
);

export function ApiRoute() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <ApiViewLazy projectId={projectId} />
    </Suspense>
  );
}
```

### Pattern 5: Debouncing Search/Filter

```tsx
import { useDeferredValue, useState } from 'react';

function SearchableView({ items }: Props) {
  const [searchQuery, setSearchQuery] = useState('');

  // Defer the search query update to prevent too frequent filtering
  const deferredQuery = useDeferredValue(searchQuery);

  const filtered = useMemo(() => {
    return items.filter(item =>
      item.name.toLowerCase().includes(deferredQuery.toLowerCase())
    );
  }, [items, deferredQuery]);

  return (
    <>
      <input
        type="search"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        placeholder="Search..."
      />
      <ItemList items={filtered} />
    </>
  );
}
```

---

## Testing Strategies

### Unit Tests: Component Testing

```tsx
// components/specialized/api/EndpointBrowser.test.tsx
import { render, screen } from '@testing-library/react';
import { EndpointBrowser } from './EndpointBrowser';

describe('EndpointBrowser', () => {
  it('renders endpoints', () => {
    const endpoints = [
      { id: '1', method: 'GET', path: '/users', description: 'List users' },
    ];

    render(
      <EndpointBrowser
        endpoints={endpoints}
        selected={null}
        onSelect={jest.fn()}
      />
    );

    expect(screen.getByText('/users')).toBeInTheDocument();
  });

  it('calls onSelect when endpoint is clicked', () => {
    const onSelect = jest.fn();
    const endpoints = [{ id: '1', method: 'GET', path: '/users' }];

    const { getByText } = render(
      <EndpointBrowser
        endpoints={endpoints}
        selected={null}
        onSelect={onSelect}
      />
    );

    fireEvent.click(getByText('/users'));
    expect(onSelect).toHaveBeenCalledWith('1');
  });
});
```

### Integration Tests: Data Flow Testing

```tsx
// pages/projects/views/ApiView.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClientProvider } from '@tanstack/react-query';
import { ApiView } from './ApiView';
import * as api from '@/api/client';

jest.mock('@/api/client');

describe('ApiView', () => {
  it('fetches and displays endpoints', async () => {
    (api.getOpenApiSpec as jest.Mock).mockResolvedValue({
      endpoints: [
        { id: '1', method: 'GET', path: '/users' },
      ],
    });

    render(
      <QueryClientProvider client={queryClient}>
        <ApiView projectId="test-project" />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('/users')).toBeInTheDocument();
    });
  });

  it('allows selecting and testing endpoints', async () => {
    // ... setup ...

    const endpoint = screen.getByText('/users');
    fireEvent.click(endpoint);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Execute Request' })).toBeEnabled();
    });
  });
});
```

### Visual Regression Tests

```tsx
// Use Chromatic for visual regression testing
import { Meta, StoryObj } from '@storybook/react';
import { ApiView } from './ApiView';

const meta: Meta<typeof ApiView> = {
  component: ApiView,
  parameters: {
    chromatic: { disableSnapshot: false },
  },
};

export const Default: StoryObj<typeof ApiView> = {
  args: { projectId: 'test-project' },
};

export const WithManyEndpoints: StoryObj<typeof ApiView> = {
  args: { projectId: 'test-project' },
  parameters: {
    // This snapshot will auto-capture visual changes
    data: { endpointCount: 100 },
  },
};
```

---

## Backend Integration

### API Contract Definition

```typescript
// types/api/views.ts - Shared between backend and frontend

// API View APIs
export interface OpenApiSpec {
  endpoints: ApiEndpoint[];
  version: string;
}

export interface ApiEndpoint {
  id: string;
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  path: string;
  description: string;
  requestSchema?: JsonSchema;
  responseSchema?: JsonSchema;
  parameters?: Parameter[];
  tags?: string[];
}

// Database View APIs
export interface DatabaseSchema {
  tables: Table[];
  views: View[];
  relationships: Relationship[];
}

export interface Table {
  id: string;
  name: string;
  schema: string;
  columns: Column[];
  primaryKey?: string[];
  indexes: Index[];
  constraints: Constraint[];
}

// Feature View APIs
export interface HierarchicalFeatures {
  epics: Epic[];
}

export interface Epic {
  id: string;
  title: string;
  status: 'todo' | 'in_progress' | 'done';
  features: Feature[];
  linkedDependencies?: string[]; // references to other items
}
```

### Endpoint Design

```
# OpenAPI spec endpoint
GET /api/v1/projects/{projectId}/openapi/spec
Response: OpenApiSpec

# Database schema endpoint
GET /api/v1/projects/{projectId}/database/schema
Response: DatabaseSchema

# Code file tree
GET /api/v1/projects/{projectId}/code/files?hierarchical=true
Response: CodeFileHierarchy

# Features with hierarchy
GET /api/v1/projects/{projectId}/items/features?hierarchical=true
Response: HierarchicalFeatures

# Metrics for any view
GET /api/v1/projects/{projectId}/metrics?view={viewType}&timeRange={range}
Response: MetricsData

# Relationships/dependencies
GET /api/v1/projects/{projectId}/relationships?itemId={id}&type={type}
Response: RelationshipGraph
```

---

## Code Examples

### Example 1: Complete API View Implementation

```tsx
// hooks/useApiViewData.ts
export function useApiViewData(projectId: string) {
  const [filters, setFilters] = useState<ApiFilters>({});
  const [selectedEndpointId, setSelectedEndpointId] = useState<string | null>(null);
  const [requestState, setRequestState] = useState<RequestBuilderState>({
    method: 'GET',
    headers: {},
  });

  const { data: spec, isLoading, error } = useQuery({
    queryKey: ['openapi-spec', projectId],
    queryFn: () => api.getOpenApiSpec(projectId),
    staleTime: 5 * 60 * 1000,
  });

  const endpoints = useMemo(() => {
    if (!spec) return [];
    return filterEndpoints(spec.endpoints, filters);
  }, [spec, filters]);

  const selectedEndpoint = useMemo(() => {
    return endpoints.find(e => e.id === selectedEndpointId);
  }, [endpoints, selectedEndpointId]);

  const executeRequest = useCallback(async () => {
    if (!selectedEndpoint) return null;
    try {
      const response = await api.testApiEndpoint(projectId, {
        endpointId: selectedEndpoint.id,
        request: requestState,
      });
      return response;
    } catch (error) {
      toast.error('Failed to execute request');
      return null;
    }
  }, [projectId, selectedEndpoint, requestState]);

  return {
    endpoints,
    selectedEndpoint,
    selectedEndpointId,
    requestState,
    filters,
    isLoading,
    error,
    setSelectedEndpointId,
    setRequestState,
    setFilters,
    executeRequest,
  };
}

// pages/projects/views/ApiView.tsx
export function ApiView({ projectId }: { projectId: string }) {
  const viewData = useApiViewData(projectId);

  if (viewData.isLoading) return <LoadingState />;
  if (viewData.error) return <ErrorState error={viewData.error} />;

  return (
    <div className="grid grid-cols-3 gap-4 h-full">
      <div className="border-r overflow-y-auto">
        <SearchFilterPanel
          filters={[
            {
              id: 'method',
              label: 'Method',
              type: 'multi-select',
              options: [
                { label: 'GET', value: 'GET' },
                { label: 'POST', value: 'POST' },
                { label: 'PUT', value: 'PUT' },
                { label: 'PATCH', value: 'PATCH' },
                { label: 'DELETE', value: 'DELETE' },
              ],
            },
          ]}
          onFilterChange={viewData.setFilters}
        />

        <div className="space-y-1">
          {viewData.endpoints.map(endpoint => (
            <button
              key={endpoint.id}
              onClick={() => viewData.setSelectedEndpointId(endpoint.id)}
              className={cn(
                'w-full text-left px-3 py-2 text-sm',
                viewData.selectedEndpointId === endpoint.id && 'bg-blue-500/20'
              )}
            >
              <span className="font-mono text-xs">{endpoint.method}</span>
              {' '}
              {endpoint.path}
            </button>
          ))}
        </div>
      </div>

      <div className="border-r overflow-y-auto">
        {viewData.selectedEndpoint ? (
          <RequestBuilder
            endpoint={viewData.selectedEndpoint}
            state={viewData.requestState}
            onChange={viewData.setRequestState}
            onExecute={viewData.executeRequest}
          />
        ) : (
          <div className="text-center text-muted-foreground py-8">
            Select an endpoint to view details
          </div>
        )}
      </div>

      <div className="overflow-y-auto">
        {viewData.selectedEndpoint ? (
          <ResponsePreview endpoint={viewData.selectedEndpoint} />
        ) : null}
      </div>
    </div>
  );
}
```

### Example 2: Database View with ERD

```tsx
// hooks/useDatabaseViewData.ts
export function useDatabaseViewData(projectId: string) {
  const [selectedTableId, setSelectedTableId] = useState<string | null>(null);

  const { data: schema, isLoading, error } = useQuery({
    queryKey: ['database-schema', projectId],
    queryFn: () => api.getDatabaseSchema(projectId),
  });

  const graphData = useMemo(() => {
    if (!schema) return null;
    return transformSchemaToGraph(schema);
  }, [schema]);

  return {
    schema,
    graphData,
    selectedTableId,
    setSelectedTableId,
    isLoading,
    error,
  };
}

// pages/projects/views/DatabaseView.tsx
export function DatabaseView({ projectId }: { projectId: string }) {
  const viewData = useDatabaseViewData(projectId);

  if (viewData.isLoading) return <LoadingState />;

  return (
    <div className="grid grid-cols-3 gap-4 h-full">
      {/* ERD Diagram */}
      <div className="col-span-2 border-r">
        {viewData.graphData && (
          <DomainVisualization
            type="graph"
            data={viewData.graphData}
            layout={{ type: 'hierarchical' }}
            colorScale={tableTypeColorScale}
            onNodeSelect={viewData.setSelectedTableId}
          />
        )}
      </div>

      {/* Table Details */}
      <div className="overflow-y-auto">
        {viewData.selectedTableId && (
          <DetailsInspector
            item={viewData.schema?.tables.find(t => t.id === viewData.selectedTableId)}
            sections={[
              {
                id: 'columns',
                title: 'Columns',
                properties: viewData.schema?.tables
                  .find(t => t.id === viewData.selectedTableId)
                  ?.columns.map(col => ({
                    key: col.name,
                    label: col.name,
                    type: 'string' as const,
                    value: `${col.type}${col.nullable ? ' (nullable)' : ''}`,
                  })) || [],
              },
            ]}
            readOnly={true}
          />
        )}
      </div>
    </div>
  );
}
```

---

## Conclusion

This technical guide provides the foundational patterns and practices for implementing TraceRTM's domain-optimized views. Key principles:

1. **Separation of Concerns** - Hooks for data, components for presentation
2. **Reusable Abstractions** - Shared components across views
3. **Performance First** - Memoization, virtualization, lazy loading
4. **Type Safety** - Strong TypeScript types throughout
5. **Testability** - Unit tests, integration tests, visual regression tests

The patterns demonstrated here should be applied consistently across all new view implementations to ensure maintainability and performance.

