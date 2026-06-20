# Journey Explorer Component Guide

## Overview

The Journey Explorer is a comprehensive UI component for visualizing, managing, and analyzing derived journeys in traceability graphs. It supports multiple journey types including user flows, data paths, call chains, and test traces.

## Features

### 1. Journey Visualization

- **Journey Cards**: Individual cards displaying journey metadata and flow visualization
- **Flow Visualization**: Horizontal flow showing node sequence with connections
- **Metadata Display**: Node count, link count, and coverage metrics
- **Type-specific Styling**: Color-coded journey types with descriptive labels

### 2. Journey Type Support

Four distinct journey types with dedicated configurations:

#### User Flow (`user_flow`)

- Color: Purple (#9333ea)
- Represents user interaction paths through the system
- Typically flow: Page → Component → API → Database

#### Data Path (`data_path`)

- Color: Blue (#3b82f6)
- Shows data flow between components and databases
- Focuses on data transformation and storage interactions

#### Call Chain (`call_chain`)

- Color: Amber (#f59e0b)
- Represents function/method invocation sequences
- Shows execution flow through code layers

#### Test Trace (`test_trace`)

- Color: Green (#22c55e)
- Shows test execution flows and coverage paths
- Connects test cases to components and APIs

### 3. Filtering Capabilities

- **Search**: Full-text search by journey name and type
- **Type Filtering**: Filter by specific journey type
- **Combined Filters**: Search and type filters work together
- **Clear Filters**: One-click filter reset

### 4. Coverage Metrics

Shows comprehensive coverage analysis for selected journeys:

- **Nodes in Journeys**: Count of unique items across selected journeys
- **Total Nodes**: Total items in the graph
- **Coverage %**: Percentage of graph covered by journeys
- **Visual Progress**: Coverage progress bar for quick reference

### 5. Journey Management

- **Create**: Manual journey creation with type selection
- **Delete**: Remove journeys from collection
- **Update**: Modify journey properties (name, color, etc.)
- **Select**: Select multiple journeys for analysis

### 6. Overlay Functionality

- **Enable/Disable**: Toggle journey overlay on main graph
- **Multi-Journey**: Overlay multiple journeys simultaneously
- **Visual Distinction**: Color-coded journeys for clarity

### 7. Export Capabilities

Three export formats for documentation and integration:

- **JSON**: Complete journey structure for programmatic access
- **CSV**: Tabular format for spreadsheet analysis
- **SVG**: Vector visualization for presentations and docs

## Component Structure

### Props

```typescript
interface JourneyExplorerProps {
  // Core data
  items: Item[];
  links: Link[];
  journeys: DerivedJourney[];

  // Callbacks
  onJourneySelect?: (journey: DerivedJourney) => void;
  onJourneyOverlay?: (journeyIds: string[]) => void;
  onJourneyCreate?: (journey: Omit<DerivedJourney, 'id'>) => void;
  onJourneyDelete?: (journeyId: string) => void;
  onJourneyUpdate?: (journeyId: string, updates: Partial<DerivedJourney>) => void;
  onExport?: (format: 'json' | 'csv' | 'svg') => void;

  // UI state
  selectedJourneyIds?: string[];
  isLoading?: boolean;
  compact?: boolean;
}
```

### Journey Type

```typescript
interface DerivedJourney {
  id: string;
  name: string;
  type: 'user_flow' | 'data_path' | 'call_chain' | 'test_trace';
  nodeIds: string[];
  links: { sourceId: string; targetId: string; type: string }[];
  color?: string;
}
```

## Usage Examples

### Basic Integration

```tsx
import { JourneyExplorer } from '@/components/graph/JourneyExplorer';

function GraphViewWithJourneys() {
  const [selectedJourneyIds, setSelectedJourneyIds] = useState<string[]>([]);

  const handleJourneySelect = (journey: DerivedJourney) => {
    setSelectedJourneyIds([journey.id]);
  };

  return (
    <JourneyExplorer
      items={items}
      links={links}
      journeys={journeys}
      selectedJourneyIds={selectedJourneyIds}
      onJourneySelect={handleJourneySelect}
    />
  );
}
```

### With All Callbacks

```tsx
function FullFeaturedJourneyExplorer() {
  const [journeys, setJourneys] = useState<DerivedJourney[]>([]);

  const handleCreate = (journey: Omit<DerivedJourney, 'id'>) => {
    const newJourney: DerivedJourney = {
      ...journey,
      id: `journey-${Date.now()}`,
    };
    setJourneys([...journeys, newJourney]);
  };

  const handleDelete = (journeyId: string) => {
    setJourneys(journeys.filter((j) => j.id !== journeyId));
  };

  const handleExport = (format: 'json' | 'csv' | 'svg') => {
    // Implement export logic
    console.log(`Exporting as ${format}`);
  };

  return (
    <JourneyExplorer
      items={items}
      links={links}
      journeys={journeys}
      onJourneyCreate={handleCreate}
      onJourneyDelete={handleDelete}
      onJourneyUpdate={(id, updates) => {
        setJourneys(journeys.map((j) => (j.id === id ? { ...j, ...updates } : j)));
      }}
      onExport={handleExport}
    />
  );
}
```

### Compact Mode

```tsx
<JourneyExplorer items={items} links={links} journeys={journeys} compact={true} />
```

## Metrics Calculation

### Node Count

Total number of items in the journey.

### Link Count

Total number of connections (relationships) between items in the journey.

### Coverage

Percentage calculation:

```
Coverage % = (Nodes in Journey / Total Graph Nodes) × 100
```

For multiple selected journeys:

```
Coverage % = (Unique Nodes Across Journeys / Total Graph Nodes) × 100
```

## Journey Flow Visualization

The component displays journey flows as sequential node chains with connectors:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Login Page   │  →  │  Auth API    │  →  │ Users Table  │
└──────────────┘     └──────────────┘     └──────────────┘
```

Features:

- Shows up to 7 nodes in expanded view, 3 in compact view
- Truncates with "+N more" indicator for longer journeys
- Displays link types in badges
- Expandable/collapsible for detailed view

## Search and Filter Algorithm

### Search

Full-text matching on:

- Journey name (case-insensitive)
- Journey type (case-insensitive)

### Type Filter

Exact match on journey type field.

### Combined Filtering

Journey must match BOTH search term AND type filter.

## Color Palette

Default journey colors (randomized on creation):

- Purple: #9333ea
- Blue: #3b82f6
- Amber: #f59e0b
- Green: #22c55e
- Red: #ef4444
- Pink: #ec4899
- Emerald: #10b981
- Cyan: #06b6d4

## Integration with UnifiedGraphView

### Linking Journeys to Graph

```tsx
const [selectedJourneys, setSelectedJourneys] = useState<string[]>([]);

<JourneyExplorer
  journeys={journeys}
  selectedJourneyIds={selectedJourneys}
  onJourneySelect={(journey) => setSelectedJourneys([journey.id])}
  onJourneyOverlay={(ids) => {
    // Highlight selected journeys on graph
    highlightJourneyPaths(ids);
  }}
/>

<UnifiedGraphView
  items={items}
  links={links}
  highlightedPaths={selectedJourneys}
/>
```

## Performance Considerations

### Rendering

- Uses React memo for journey cards to prevent unnecessary re-renders
- Scroll area implementation for efficient handling of large lists
- Progressive rendering of journey details on expand

### Filtering

- Real-time filtering with debounce
- Efficient string matching algorithms
- Memoized filtered results

### Metrics Calculation

- Memoized metric calculations prevent recalculation on re-render
- Efficient set operations for coverage aggregation
- Linear time complexity for node counting

### Scalability

Tested and optimized for:

- 50+ journeys with minimal performance impact
- 100+ nodes per journey
- Complex filtering operations on large datasets

## Accessibility Features

### Keyboard Navigation

- Tab through journey cards
- Enter to select/expand
- Delete/Backspace to remove (with confirmation)
- Escape to close dialogs

### ARIA Labels

- Semantic HTML structure
- Card landmarks with proper headings
- Button roles and descriptions
- Tooltip helpers for icon buttons

### Visual Indicators

- Color coding for journey types
- Status badges for selection state
- Focus outlines on interactive elements
- High contrast text colors

## Testing

### Unit Tests

Located in `/src/__tests__/components/JourneyExplorer.test.tsx`:

- Rendering and display
- Filtering and search
- Coverage metrics
- Interactions (select, delete, expand)
- Create/update/delete operations
- Export functionality
- Loading states

### Integration Tests

Located in `/src/__tests__/components/JourneyExplorer.integration.test.tsx`:

- Journey detection workflows
- Multi-journey selection
- Lifecycle management
- Export workflows
- Performance at scale
- Error handling

Run tests with:

```bash
bun run test:components
```

## Best Practices

### Journey Creation

1. Keep journey names descriptive and unique
2. Use appropriate type for clarity
3. Ensure all referenced node IDs exist in items array
4. Validate link types match your data model

### Coverage Analysis

1. Select related journeys for comprehensive coverage
2. Look for gaps in coverage to identify untested areas
3. Use coverage metrics to track implementation progress

### Export and Documentation

1. Use JSON exports for programmatic processing
2. Use CSV for spreadsheet analysis and reporting
3. Use SVG for presentations and documentation

### Performance

1. Limit displayed journeys to 50-100 for smooth interaction
2. Use search filters to reduce visible set
3. Virtualize long lists for better performance
4. Debounce search input for large datasets

## Common Patterns

### Filter by Test Coverage

```tsx
const testJourneys = journeys.filter((j) => j.type === 'test_trace');
```

### Calculate Total Coverage

```tsx
const totalCoverage = useMemo(() => {
  const nodeSet = new Set<string>();
  journeys.forEach((j) => j.nodeIds.forEach((id) => nodeSet.add(id)));
  return (nodeSet.size / items.length) * 100;
}, [journeys, items]);
```

### Group Journeys by Type

```tsx
const journeysByType = useMemo(
  () =>
    journeys.reduce(
      (acc, j) => {
        if (!acc[j.type]) acc[j.type] = [];
        acc[j.type].push(j);
        return acc;
      },
      {} as Record<DerivedJourney['type'], DerivedJourney[]>,
    ),
  [journeys],
);
```

## Troubleshooting

### Journeys Not Displaying

- Verify `journeys` array is passed and not empty
- Check item IDs in `nodeIds` exist in `items` array
- Ensure journey type is valid

### Coverage Showing 0%

- Verify items array contains all referenced items
- Check that allNodeIds Set is properly populated
- Ensure journey nodeIds reference valid item IDs

### Export Not Working

- Implement `onExport` callback
- Verify callback receives correct format parameter
- Check export format is one of: "json", "csv", "svg"

### Performance Issues

- Reduce number of displayed journeys using filters
- Implement virtualization for large lists
- Memoize heavy calculations
- Use React DevTools to identify re-render causes

## Future Enhancements

Planned features for upcoming releases:

1. **Journey Templates**: Pre-built journey patterns
2. **AI Detection**: Automatic journey discovery from graph
3. **Comparison View**: Compare multiple journeys side-by-side
4. **Animation**: Animated journey playback/walkthrough
5. **Integration**: Direct GitHub/Jira issue linking
6. **Analytics**: Journey usage and coverage statistics
7. **Sharing**: Shareable journey links and reports

## Contributing

When contributing to Journey Explorer:

1. Follow existing code style and patterns
2. Add tests for new features
3. Update this documentation
4. Test with various journey types and sizes
5. Ensure accessibility standards are met
6. Performance test with 50+ journeys

## Related Components

- **UnifiedGraphView**: Main graph visualization component
- **GraphSearch**: Search functionality for graph nodes
- **NodeDetailPanel**: Detailed information about selected nodes
- **EditAffordances**: Editing capabilities for graph elements

## API Reference

### Functions

#### `calculateJourneyMetrics`

```typescript
function calculateJourneyMetrics(
  journey: DerivedJourney,
  items: Item[],
  links: Link[],
  allNodeIds: string[],
): JourneyMetrics;
```

Calculates node count, link count, coverage %, and confidence score.

#### `getJourneyNodeNames`

```typescript
function getJourneyNodeNames(journey: DerivedJourney, items: Item[]): Map<string, string>;
```

Maps node IDs to display names for visualization.

## Support

For issues or questions:

1. Check this documentation
2. Review test files for usage examples
3. Create an issue with detailed reproduction steps
4. Include journey data structure in bug reports
