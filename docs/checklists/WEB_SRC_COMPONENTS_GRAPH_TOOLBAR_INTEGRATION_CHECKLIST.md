# Graph Toolbar Integration Checklist

Quick reference for integrating the GraphToolbar into your views.

## Prerequisites

- [ ] `@xyflow/react` installed and configured
- [ ] `html-to-image` dependency added (for export)
- [ ] ReactFlowProvider wrapping your component
- [ ] Graph data (items and links) available

## Basic Integration Steps

### 1. Import Components

```tsx
import { ReactFlowProvider } from '@xyflow/react';
import { GraphToolbar, FlowGraphViewInner, useGraphKeyboardShortcuts } from '@/components/graph';
```

### 2. Set Up State

```tsx
const [layout, setLayout] = useState<LayoutType>('flow-chart');
const [perspective, setPerspective] = useState<GraphPerspective>('all');
const [showDetailPanel, setShowDetailPanel] = useState(true);
const [isFullscreen, setIsFullscreen] = useState(false);
const [selectedNodeTypes, setSelectedNodeTypes] = useState<string[]>([]);
```

### 3. Create Fullscreen Handler

```tsx
const containerRef = useRef<HTMLDivElement>(null);

const handleFullscreenToggle = useCallback(async () => {
  if (!containerRef.current) return;

  try {
    if (document.fullscreenElement) {
      await document.exitFullscreen();
    } else {
      await containerRef.current.requestFullscreen();
    }
  } catch {
    // Fullscreen not supported
  }
}, []);

useEffect(() => {
  const onFullscreenChange = () => setIsFullscreen(!!document.fullscreenElement);

  document.addEventListener('fullscreenchange', onFullscreenChange);
  return () => document.removeEventListener('fullscreenchange', onFullscreenChange);
}, []);
```

### 4. Set Up Keyboard Shortcuts

```tsx
useGraphKeyboardShortcuts({
  onFullscreen: handleFullscreenToggle,
  onToggleDetailPanel: () => setShowDetailPanel((prev) => !prev),
  enabled: true,
});
```

### 5. Render Toolbar and Graph

```tsx
return (
  <ReactFlowProvider>
    <div ref={containerRef} className='h-full flex flex-col'>
      <GraphToolbar
        layout={layout}
        onLayoutChange={setLayout}
        perspective={perspective}
        onPerspectiveChange={setPerspective}
        showDetailPanel={showDetailPanel}
        onToggleDetailPanel={() => setShowDetailPanel(!showDetailPanel)}
        isFullscreen={isFullscreen}
        onToggleFullscreen={handleFullscreenToggle}
        totalNodes={items.length}
        visibleNodes={filteredItems.length}
        variant='full'
      />

      <div className='flex-1 mt-3'>
        <FlowGraphViewInner
          items={filteredItems}
          links={links}
          perspective={perspective}
          defaultLayout={layout}
          showControls={false}
        />
      </div>
    </div>
  </ReactFlowProvider>
);
```

## Feature Checklist

### Essential Features (Required)

- [ ] Layout selection working
- [ ] Zoom controls functional
- [ ] Detail panel toggle working
- [ ] Fullscreen toggle working
- [ ] Stats display showing correct counts

### Advanced Features (Optional)

- [ ] Filter controls integrated
- [ ] Perspective filtering working
- [ ] Node type filtering working
- [ ] Export controls functional
- [ ] Keyboard shortcuts enabled
- [ ] Custom export handler (if needed)
- [ ] Status filtering (if applicable)

## Testing Checklist

### Visual Tests

- [ ] Toolbar renders correctly in default state
- [ ] All buttons have icons
- [ ] Tooltips appear on hover
- [ ] Active filters display correctly
- [ ] Stats update when filtering
- [ ] Responsive on mobile (compact/minimal variant)

### Functional Tests

- [ ] Layout changes apply to graph
- [ ] Zoom in/out works
- [ ] Fit view centers graph
- [ ] Fullscreen toggle works
- [ ] Detail panel shows/hides
- [ ] Filters reduce visible nodes
- [ ] Export downloads files
- [ ] Clear filters resets view

### Keyboard Tests

- [ ] Cmd/Ctrl + Plus zooms in
- [ ] Cmd/Ctrl + Minus zooms out
- [ ] Cmd/Ctrl + 0 fits view
- [ ] F toggles fullscreen
- [ ] P toggles detail panel
- [ ] Cmd/Ctrl + E opens export

### Accessibility Tests

- [ ] Tab navigation works
- [ ] Focus indicators visible
- [ ] ARIA labels present
- [ ] Keyboard shortcuts don't conflict with inputs
- [ ] Screen reader announces controls

## Common Issues

### Issue: Export not working

**Solution:** Ensure React Flow container has `className="react-flow"`

```tsx
<ReactFlow className="react-flow" ... />
```

### Issue: Keyboard shortcuts not working

**Solution:** Ensure hook is called and component has focus

```tsx
useGraphKeyboardShortcuts({ enabled: true });

// Make container focusable
<div tabIndex={0}>
  <GraphToolbar ... />
</div>
```

### Issue: Filters not applying

**Solution:** Filter items before passing to graph

```tsx
const filteredItems = selectedNodeTypes.length > 0
  ? items.filter(item => selectedNodeTypes.includes(item.type))
  : items;

<FlowGraphViewInner items={filteredItems} ... />
```

### Issue: Stats showing wrong counts

**Solution:** Pass filtered counts, not total counts

```tsx
<GraphToolbar
  totalNodes={items.length}
  visibleNodes={filteredItems.length} // ← Use filtered
  totalEdges={links.length}
  visibleEdges={filteredLinks.length} // ← Use filtered
/>
```

### Issue: Fullscreen exit not updating state

**Solution:** Listen to fullscreenchange event

```tsx
useEffect(() => {
  const onFullscreenChange = () => setIsFullscreen(!!document.fullscreenElement);
  document.addEventListener('fullscreenchange', onFullscreenChange);
  return () => document.removeEventListener('fullscreenchange', onFullscreenChange);
}, []);
```

## Variants Guide

### When to Use Each Variant

**Full Variant**

- ✅ Desktop views (≥1024px)
- ✅ Dashboard pages
- ✅ Main graph views
- ❌ Mobile views
- ❌ Embedded graphs

**Compact Variant**

- ✅ Tablet views (768-1023px)
- ✅ Side panels
- ✅ Modal dialogs
- ❌ Mobile phones
- ❌ Very small containers

**Minimal Variant**

- ✅ Mobile views (<768px)
- ✅ Embedded graphs
- ✅ Preview cards
- ✅ Print views
- ❌ Interactive dashboards

### Responsive Example

```tsx
function ResponsiveGraphView() {
  const [isMobile, setIsMobile] = useState(false);
  const [isTablet, setIsTablet] = useState(false);

  useEffect(() => {
    const checkSize = () => {
      setIsMobile(window.innerWidth < 768);
      setIsTablet(window.innerWidth >= 768 && window.innerWidth < 1024);
    };

    checkSize();
    window.addEventListener("resize", checkSize);
    return () => window.removeEventListener("resize", checkSize);
  }, []);

  const variant = isMobile ? "minimal" : isTablet ? "compact" : "full";

  return (
    <GraphToolbar variant={variant} ... />
  );
}
```

## Performance Tips

### 1. Memoize Callbacks

```tsx
const handleLayoutChange = useCallback((layout: LayoutType) => {
  setLayout(layout);
}, []);
```

### 2. Debounce Filter Changes

```tsx
const debouncedFilterChange = useMemo(
  () =>
    debounce((types: string[]) => {
      setSelectedNodeTypes(types);
    }, 300),
  [],
);
```

### 3. Lazy Load Export

Export controls are already lazy - they only render when the export button is clicked.

### 4. Limit Stats Updates

```tsx
const stats = useMemo(() => ({
  totalNodes: items.length,
  visibleNodes: filteredItems.length,
  totalEdges: links.length,
  visibleEdges: filteredLinks.length,
}), [items.length, filteredItems.length, links.length, filteredLinks.length]);

<GraphToolbar {...stats} ... />
```

## Best Practices

### ✅ Do

- Use the correct variant for your viewport size
- Enable keyboard shortcuts for better UX
- Show stats to give users visibility
- Handle fullscreen exit events
- Filter items before passing to graph
- Memoize expensive computations
- Test on multiple screen sizes

### ❌ Don't

- Don't use `any` types
- Don't forget to wrap in ReactFlowProvider
- Don't disable keyboard shortcuts without reason
- Don't show all features on mobile
- Don't forget accessibility
- Don't skip error handling for export
- Don't mutate state directly

## Complete Example

See `GraphToolbar.example.tsx` for complete integration examples:

- Full integration with all features
- Compact variant for tablets
- Minimal variant for mobile
- Custom filter logic
- Custom export handlers

## Documentation

- **API Reference**: `GRAPH_TOOLBAR_README.md`
- **Visual Guide**: `TOOLBAR_VISUAL_GUIDE.md`
- **Implementation**: `TOOLBAR_IMPLEMENTATION_SUMMARY.md`
- **Storybook**: `__stories__/GraphToolbar.stories.tsx`

## Support

If you encounter issues:

1. Check this checklist
2. Review the documentation files
3. Check Storybook examples
4. Look at `GraphToolbar.example.tsx`
5. Review TypeScript types for prop requirements
