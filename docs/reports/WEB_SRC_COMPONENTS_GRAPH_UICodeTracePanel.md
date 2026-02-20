# UICodeTracePanel Component

## Overview

The `UICodeTracePanel` component visualizes the complete traceability chain from UI components through code implementation to business requirements. It shows how a user-facing UI element traces back to the canonical concept it represents, providing a comprehensive view of the multi-dimensional traceability model.

## Purpose

This component helps teams understand:

- How UI components map to code implementations
- How code implementations satisfy requirements
- The confidence level at each level of the trace
- The detection strategy used for each equivalence link
- The canonical concept that unifies all perspectives

## Features

### Core Traceability Display

- **Vertical Flow Diagram**: Shows UI → Code → Requirement → Concept progression
- **Multiple Perspectives**: Displays perspective context (UI, Technical, Business)
- **Confidence Scores**: Shows confidence percentage and visual indicators for each level
- **Strategy Labels**: Indicates how the equivalence was detected (manual, explicit, semantic, etc.)

### Level-Specific Details

#### UI Level

- Component name and path
- Screenshot/thumbnail (if available)
- Quick navigation to component editor
- Interactive affordances

#### Code Level

- Symbol name and type (function, class, component, etc.)
- File path with line numbers
- Function signature
- Programming language
- Commit SHA and repository link

#### Requirement Level

- Requirement ID and title
- Business value statement
- Link to requirement detail view
- Connection to epic/story

#### Canonical Concept Level

- Concept name and description
- Domain classification
- Related tags
- Projection count (how many perspectives link to it)
- Confidence metric

### Canonical Concept Card

- Shows the abstract concept unifying all perspectives
- Displays projections count and confidence
- Indicates confidence through visual progress bar
- Lists related tags and domain information

### Interactive Features

- **Open Code**: Navigate to code editor with specific file/line
- **View Requirement**: Link to requirement detail view
- **Open Component**: Jump to component implementation
- **Refresh Trace**: Regenerate trace chain with latest data

### Visual Indicators

- Color-coded confidence levels (green for high, yellow for medium, orange for low)
- Type-specific icons (component, code, document, concept)
- Confirmation badges for user-verified links
- Strategy information in tooltips

## Props

```typescript
interface UICodeTracePanelProps {
  // The trace chain to display
  traceChain: UICodeTraceChain | null;

  // Loading state
  isLoading?: boolean;

  // Callbacks
  onOpenCode?: (codeRef: CodeReference) => void;
  onOpenRequirement?: (requirementId: string) => void;
  onNavigateToUI?: (componentPath: string) => void;
  onRefreshTrace?: () => void;
}
```

## Types

### UICodeTraceChain

Represents a complete trace from UI to requirements:

```typescript
interface UICodeTraceChain {
  id: string;
  name: string;
  description?: string;
  levels: TraceLevel[];
  overallConfidence: number;
  canonicalConcept?: CanonicalConcept;
  projections?: CanonicalProjection[];
  lastUpdated: string;
}
```

### TraceLevel

Represents a single level in the traceability chain:

```typescript
interface TraceLevel {
  id: string;
  type: 'ui' | 'code' | 'requirement' | 'concept';
  title: string;
  description?: string;
  perspective?: string;

  // Type-specific fields
  componentName?: string;
  componentPath?: string;
  screenshot?: string;
  codeRef?: CodeReference;
  requirementId?: string;
  businessValue?: string;
  canonicalId?: string;

  // Metadata
  confidence: number;
  strategy?: EquivalenceStrategy;
  isConfirmed?: boolean;
}
```

## Usage Examples

### Basic Usage

```typescript
import { UICodeTracePanel } from '@/components/graph/UICodeTracePanel';

function MyView() {
  const [traceChain, setTraceChain] = useState<UICodeTraceChain | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleOpenCode = (codeRef: CodeReference) => {
    // Navigate to code editor
    window.open(`vscode://open?${codeRef.filePath}:${codeRef.startLine}`);
  };

  const handleOpenRequirement = (requirementId: string) => {
    // Navigate to requirement detail
    navigate(`/items/${requirementId}`);
  };

  const handleRefresh = async () => {
    setIsLoading(true);
    try {
      const trace = await fetchTraceChain();
      setTraceChain(trace);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <UICodeTracePanel
      traceChain={traceChain}
      isLoading={isLoading}
      onOpenCode={handleOpenCode}
      onOpenRequirement={handleOpenRequirement}
      onRefreshTrace={handleRefresh}
    />
  );
}
```

### With Canonical Concept

```typescript
const traceChain: UICodeTraceChain = {
  id: "trace-1",
  name: "User Login Flow",
  description: "Complete trace from login UI to auth requirement",
  levels: [
    {
      id: "ui-1",
      type: "ui",
      title: "Login Form",
      componentName: "LoginForm",
      componentPath: "src/components/auth/LoginForm.tsx",
      confidence: 1.0,
      strategy: "explicit_annotation",
    },
    {
      id: "code-1",
      type: "code",
      title: "LoginForm Implementation",
      codeRef: {
        filePath: "src/components/auth/LoginForm.tsx",
        startLine: 42,
        endLine: 128,
        symbolName: "LoginForm",
        symbolType: "component",
      },
      confidence: 0.95,
      strategy: "manual_link",
    },
    {
      id: "req-1",
      type: "requirement",
      title: "User Authentication",
      requirementId: "REQ-AUTH-001",
      businessValue: "Enable users to securely access the platform",
      confidence: 0.9,
      strategy: "shared_canonical",
    },
  ],
  overallConfidence: 0.95,
  canonicalConcept: {
    id: "concept-auth",
    name: "User Authentication",
    description: "User login and authentication process",
    domain: "security",
    confidence: 0.95,
    projectionCount: 3,
    // ... other fields
  },
  lastUpdated: new Date().toISOString(),
};

return <UICodeTracePanel traceChain={traceChain} />;
```

### Minimal Usage (Display Only)

```typescript
// Just display the trace without callbacks
<UICodeTracePanel traceChain={traceChain} />
```

## Styling

The component uses Tailwind CSS classes with shadcn/ui components. Customize appearance through:

1. **Color Configuration**: Adjust `CONFIDENCE_COLOR` function
2. **Layout**: Modify card padding and spacing classes
3. **Responsive**: Component is responsive and works on mobile/tablet

## Confidence Levels and Colors

| Confidence | Color  | Icon        | Meaning             |
| ---------- | ------ | ----------- | ------------------- |
| 90-100%    | Green  | CheckCircle | High confidence     |
| 70-89%     | Blue   | Zap         | Good confidence     |
| 50-69%     | Yellow | Sparkles    | Moderate confidence |
| <50%       | Orange | Sparkles    | Low confidence      |

## Equivalence Strategies

Each trace level shows how the equivalence was detected:

| Strategy            | Confidence | Description                              |
| ------------------- | ---------- | ---------------------------------------- |
| explicit_annotation | 1.0        | Explicitly marked with @trace annotation |
| manual_link         | 1.0        | User manually created the link           |
| api_contract        | 0.9        | Frontend fetch matches backend route     |
| shared_canonical    | 0.9        | Both items share the same concept        |
| naming_pattern      | 0.7        | CamelCase/snake_case pattern matching    |
| semantic_similarity | 0.6        | Embedding similarity score               |
| structural          | 0.5        | Similar structure/hierarchy              |
| temporal            | 0.4        | Created/modified at similar times        |
| co_occurrence       | 0.3        | Frequently appear together               |

## Accessibility Features

- Semantic HTML with proper heading hierarchy
- ARIA labels for icon buttons
- Keyboard accessible tooltips
- Color-independent confidence indicators (uses icons + color)
- Screen reader friendly badge labels
- Proper form labels and descriptions

## Performance Considerations

- Uses `memo()` for optimization
- Lazy renders only visible trace levels
- Efficient scrolling with ScrollArea component
- Minimal re-renders through proper prop memoization

## Integration Points

### With tRPC Queries

```typescript
// Fetch trace chain from API
const { data: traceChain, isLoading } = trpc.traces.getUICodeTrace.useQuery({
  componentId,
});

return (
  <UICodeTracePanel
    traceChain={traceChain}
    isLoading={isLoading}
  />
);
```

### With Navigation

```typescript
// Handle navigation callbacks
const navigate = useNavigate();

const handleOpenRequirement = (id: string) => {
  navigate(`/items/${id}`);
};

const handleOpenCode = (codeRef: CodeReference) => {
  // Open in VS Code via extension
  window.open(`vscode://open?${codeRef.filePath}:${codeRef.startLine}`);
};
```

### With State Management

```typescript
const [selectedTrace, setSelectedTrace] = useAtom(selectedTraceAtom);

return (
  <UICodeTracePanel
    traceChain={selectedTrace}
    onRefreshTrace={() => {
      // Refetch and update atom
      const fresh = await api.getTrace(selectedTrace.id);
      setSelectedTrace(fresh);
    }}
  />
);
```

## Testing

The component includes comprehensive test coverage:

- Rendering of all trace levels
- Confidence score display and colors
- User interactions (button clicks)
- Tooltip information
- Edge cases (no concept, long paths, low confidence)
- Accessibility features
- Data display and formatting

Run tests:

```bash
bun run test:components -- UICodeTracePanel
```

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Related Components

- `EquivalencePanel`: Show equivalence relationships between items
- `NodeDetailPanel`: Display detailed item information
- `GraphView`: Visualize full traceability graph
- `CanonicalConceptCard`: Show concept information

## Troubleshooting

### Trace chain not updating

- Check that `onRefreshTrace` callback is implemented
- Verify API is returning new data
- Check for caching issues

### Confidence scores incorrect

- Verify strategy detection logic
- Check equivalence detection algorithms
- Review confidence weighting formula

### UI Level not rendering

- Ensure `componentPath` and `componentName` are provided
- Check screenshot URL is accessible
- Verify component exists

### Code Level details missing

- Check CodeReference object is fully populated
- Verify file path matches repository structure
- Ensure line numbers are correct

## Future Enhancements

- Code diff visualization for code changes
- Requirement change history
- Interactive trace editing
- Custom confidence weighting
- Trace chain branching (multiple implementations)
- Trace chain metrics and statistics
- Integration with code search
- Real-time collaboration features
