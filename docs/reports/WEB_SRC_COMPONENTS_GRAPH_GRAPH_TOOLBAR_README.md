# Graph Toolbar Components

Professional, polished toolbar controls for graph visualization with zoom, layout, filter, and export capabilities.

## Components

### GraphToolbar

Main toolbar component providing comprehensive graph controls.

**Features:**

- Layout selection (Flow Chart, Tree, Radial, etc.)
- Advanced filtering (by perspective, node type, status)
- Export controls (PNG, SVG, JSON, CSV)
- Zoom controls (in, out, fit, actual size)
- View controls (fullscreen, detail panel)
- Performance stats display
- Keyboard shortcuts
- Three variants: full, compact, minimal

**Usage:**

```tsx
import { GraphToolbar } from '@/components/graph';
import { useState } from 'react';

function MyGraphView() {
  const [layout, setLayout] = useState('flow-chart');
  const [perspective, setPerspective] = useState('all');
  const [showDetailPanel, setShowDetailPanel] = useState(true);

  return (
    <GraphToolbar
      layout={layout}
      onLayoutChange={setLayout}
      perspective={perspective}
      onPerspectiveChange={setPerspective}
      showDetailPanel={showDetailPanel}
      onToggleDetailPanel={() => setShowDetailPanel(!showDetailPanel)}
      isFullscreen={false}
      onToggleFullscreen={handleFullscreen}
      totalNodes={150}
      visibleNodes={120}
      totalEdges={300}
      visibleEdges={250}
      variant='full'
    />
  );
}
```

### FilterControls

Advanced filtering UI for graph nodes and edges.

**Features:**

- Perspective selection (Product, Technical, UI, Security, etc.)
- Multi-select node type filtering
- Status filtering
- Active filter badges
- Clear all filters
- Visual color coding

**Usage:**

```tsx
import { FilterControls } from '@/components/graph';

function MyFilters() {
  const [perspective, setPerspective] = useState('all');
  const [selectedTypes, setSelectedTypes] = useState([]);

  return (
    <FilterControls
      perspective={perspective}
      onPerspectiveChange={setPerspective}
      nodeTypes={['requirement', 'feature', 'task', 'bug']}
      selectedNodeTypes={selectedTypes}
      onNodeTypeFilterChange={setSelectedTypes}
    />
  );
}
```

### ExportControls

Export graph visualization in multiple formats.

**Features:**

- PNG export (raster image, 2x quality)
- SVG export (vector format)
- JSON export (graph data with metadata)
- CSV export (node and edge lists)
- Loading states
- Error handling

**Usage:**

```tsx
import { ExportControls } from '@/components/graph';

function MyExport() {
  const handleExport = (format) => {
    console.log(`Exporting as ${format}`);
    // Export logic is handled internally
  };

  return <ExportControls onExport={handleExport} disabled={false} />;
}
```

## Keyboard Shortcuts

All keyboard shortcuts are available via `useGraphKeyboardShortcuts` hook:

### Zoom Controls

- **Cmd/Ctrl + Plus** - Zoom in
- **Cmd/Ctrl + Minus** - Zoom out
- **Cmd/Ctrl + 0** - Fit view
- **Cmd/Ctrl + 1** - Actual size (1:1)

### View Controls

- **F** - Toggle fullscreen
- **P** - Toggle detail panel
- **M** - Toggle mini-map

### Actions

- **Cmd/Ctrl + E** - Open export menu
- **Cmd/Ctrl + F** - Toggle filters
- **Cmd/Ctrl + Shift + R** - Reset view

## Integration Examples

### Full Integration

```tsx
import { ReactFlowProvider } from '@xyflow/react';
import { GraphToolbar, FlowGraphViewInner } from '@/components/graph';

function FullGraphView({ items, links }) {
  const [layout, setLayout] = useState('flow-chart');
  const [perspective, setPerspective] = useState('all');
  const [showDetailPanel, setShowDetailPanel] = useState(true);

  return (
    <ReactFlowProvider>
      <div className='h-full flex flex-col'>
        {/* Toolbar */}
        <GraphToolbar
          layout={layout}
          onLayoutChange={setLayout}
          perspective={perspective}
          onPerspectiveChange={setPerspective}
          showDetailPanel={showDetailPanel}
          onToggleDetailPanel={() => setShowDetailPanel(!showDetailPanel)}
          isFullscreen={false}
          onToggleFullscreen={handleFullscreen}
          totalNodes={items.length}
          visibleNodes={items.length}
          totalEdges={links.length}
          visibleEdges={links.length}
          variant='full'
        />

        {/* Graph */}
        <div className='flex-1 mt-3'>
          <FlowGraphViewInner
            items={items}
            links={links}
            perspective={perspective}
            defaultLayout={layout}
            showControls={false} // Toolbar provides controls
          />
        </div>
      </div>
    </ReactFlowProvider>
  );
}
```

### Compact Integration (Tablet)

```tsx
function CompactGraphView({ items, links }) {
  const [layout, setLayout] = useState('flow-chart');
  const [showDetailPanel, setShowDetailPanel] = useState(true);

  return (
    <ReactFlowProvider>
      <div className='h-full flex flex-col'>
        <GraphToolbar
          layout={layout}
          onLayoutChange={setLayout}
          showDetailPanel={showDetailPanel}
          onToggleDetailPanel={() => setShowDetailPanel(!showDetailPanel)}
          isFullscreen={false}
          onToggleFullscreen={() => {}}
          variant='compact'
        />
        <div className='flex-1 mt-2'>
          <FlowGraphViewInner
            items={items}
            links={links}
            defaultLayout={layout}
            showControls={false}
          />
        </div>
      </div>
    </ReactFlowProvider>
  );
}
```

### Minimal Integration (Mobile)

```tsx
function MobileGraphView({ items, links }) {
  return (
    <ReactFlowProvider>
      <div className='h-full flex flex-col'>
        <GraphToolbar
          layout='flow-chart'
          onLayoutChange={() => {}}
          showDetailPanel={false}
          onToggleDetailPanel={() => {}}
          isFullscreen={false}
          onToggleFullscreen={() => {}}
          variant='minimal'
        />
        <div className='flex-1 mt-1'>
          <FlowGraphViewInner items={items} links={links} showControls={false} />
        </div>
      </div>
    </ReactFlowProvider>
  );
}
```

## Variants

### Full Variant

- Complete toolbar with all features
- Layout selector, filters, export, zoom, view controls
- Performance stats
- Best for desktop views

### Compact Variant

- Essential controls only
- Layout selector in compact mode
- Zoom controls
- Detail panel toggle
- Good for tablet views

### Minimal Variant

- Zoom controls only
- Minimal footprint
- Ideal for mobile or embedded views

## Customization

### Custom Export Handler

```tsx
function MyGraph() {
  const handleExport = async (format) => {
    if (format === 'json') {
      // Custom JSON export logic
      const data = await customExportLogic();
      downloadFile(data, 'custom-export.json');
    }
  };

  return (
    <GraphToolbar
      onExport={handleExport}
      // ... other props
    />
  );
}
```

### Custom Filter Logic

```tsx
function MyGraph() {
  const [filters, setFilters] = useState({
    types: [],
    statuses: [],
    dateRange: null,
  });

  const handleTypeFilterChange = (types) => {
    setFilters((prev) => ({ ...prev, types }));
    // Apply custom filtering logic
  };

  return (
    <GraphToolbar
      selectedNodeTypes={filters.types}
      onNodeTypeFilterChange={handleTypeFilterChange}
      // ... other props
    />
  );
}
```

## Accessibility

All toolbar components follow WCAG 2.1 Level AA guidelines:

- **Keyboard Navigation**: Full keyboard support with shortcuts
- **ARIA Labels**: All buttons have descriptive labels
- **Focus Management**: Proper focus indicators
- **Screen Readers**: Semantic HTML and ARIA attributes
- **Color Contrast**: Meets contrast requirements

## Performance

The toolbar is optimized for performance:

- **Memoized callbacks**: Prevents unnecessary re-renders
- **Lazy loading**: Export controls loaded on demand
- **Debounced events**: Zoom and pan events are debounced
- **Stable refs**: Uses stable references for event handlers

## Dependencies

- `@xyflow/react` - For React Flow integration
- `html-to-image` - For PNG/SVG export
- `@tracertm/ui` - UI component library
- `lucide-react` - Icons

## Browser Support

- Chrome/Edge: 90+
- Firefox: 88+
- Safari: 14+
- Mobile browsers: iOS 14+, Android 90+

## Troubleshooting

### Export fails

```tsx
// Ensure React Flow container has a class
<div className="react-flow">
  <ReactFlow ... />
</div>
```

### Keyboard shortcuts not working

```tsx
// Ensure the graph container has focus
<div tabIndex={0} onFocus={() => setFocused(true)}>
  <GraphToolbar ... />
</div>
```

### Filters not applying

```tsx
// Ensure you're filtering items based on selected types
const filteredItems =
  selectedTypes.length > 0 ? items.filter((item) => selectedTypes.includes(item.type)) : items;
```

## Related Components

- `FlowGraphViewInner` - Core graph visualization
- `NodeDetailPanel` - Node details sidebar
- `LayoutSelector` - Layout algorithm selector
- `PerspectiveSelector` - Perspective switcher

## See Also

- [Graph Visualization Guide](./README.md)
- [Performance Optimization](./PERFORMANCE.md)
- [Keyboard Shortcuts](./KEYBOARD_SHORTCUTS.md)
- [Storybook Stories](./__stories__/GraphToolbar.stories.tsx)
