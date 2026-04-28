# Cross-Perspective Search Guide

## Overview

The Cross-Perspective Search functionality enables powerful multi-dimensional searching across all perspectives in the traceability system. Users can search items simultaneously across Feature, Code, Test, API, Database, and other perspectives, with results grouped and colored by perspective and equivalence relationships highlighted.

## Features

### 1. Multi-Perspective Search

- Search across all items in all perspectives simultaneously
- Results grouped by perspective with distinct color coding
- Count summary showing results per perspective
- Alphabetically sorted perspective groups

### 2. Equivalence Discovery

- Automatic detection of equivalent items across perspectives
- Display confidence scores for equivalence relationships
- Show all equivalent items for each result
- Visual representation with colored badges

### 3. Advanced Filtering

- Filter by item type
- Filter by item status (todo, in_progress, done, blocked, cancelled)
- Filter by specific perspectives
- Combine multiple filters

### 4. Smart Matching

- Title matches score highest
- Prefix matches rank above substring matches
- Description and type matching supported
- Case-insensitive search

### 5. Search History

- Automatic history tracking (up to 10 recent searches)
- Quick access buttons for re-running searches
- History cleared on demand

### 6. Keyboard Navigation

- Arrow keys to navigate results
- Enter to select result
- Escape to clear search
- Full keyboard accessibility

## Component Usage

### Basic Implementation

```tsx
import { CrossPerspectiveSearch } from "@/components/graph";
import type { Item, Link } from "@tracertm/types";

function MyComponent() {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const items: Item[] = [...]; // Your items
  const links: Link[] = [...]; // Your links

  return (
    <CrossPerspectiveSearch
      items={items}
      links={links}
      onSelect={(itemId) => setSelectedId(itemId)}
      onHighlight={(itemId) => console.log("Highlight:", itemId)}
    />
  );
}
```

### Compact Mode

For inline search in toolbars or compact layouts:

```tsx
<CrossPerspectiveSearch
  items={items}
  links={links}
  onSelect={handleSelect}
  onHighlight={handleHighlight}
  compact={true}
/>
```

### With Custom Max Results

```tsx
<CrossPerspectiveSearch
  items={items}
  links={links}
  onSelect={handleSelect}
  onHighlight={handleHighlight}
  maxResultsPerPerspective={3}
/>
```

## Hook Usage

Use the `useCrossPerspectiveSearch` hook for programmatic search functionality:

```tsx
import { useCrossPerspectiveSearch } from '@/components/graph';

function MySearchUI() {
  const { performSearch, debouncedSearch, addToHistory, getHistory } = useCrossPerspectiveSearch();

  // Perform synchronous search
  const results = performSearch(items, links, 'auth');

  // Or use debounced version (300ms default)
  const handleSearch = (query: string) => {
    debouncedSearch(items, links, query, filters, (results) => {
      console.log('Results:', results);
    });
  };

  // Add to history
  const handleSubmit = (query: string) => {
    addToHistory(query);
    const history = getHistory(); // ["query1", "query2", ...]
  };
}
```

## Data Types

### CrossPerspectiveSearchResult

```typescript
interface CrossPerspectiveSearchResult {
  item: Item;
  perspective: string;
  matchType: 'title' | 'description' | 'type' | 'dimension';
  score: number;
  matchedText?: string;
  equivalences: EquivalenceInfo[];
}
```

### EquivalenceInfo

```typescript
interface EquivalenceInfo {
  equivalentItemId: string;
  equivalentPerspective: string;
  linkId?: string;
  confidence: number;
  linkType: 'same_as' | 'represents' | 'manifests_as';
}
```

### GroupedSearchResults

```typescript
interface GroupedSearchResults {
  perspective: string;
  results: CrossPerspectiveSearchResult[];
  count: number;
}
```

### SearchFilters

```typescript
interface SearchFilters {
  type?: string;
  status?: string;
  perspectives?: string[];
  dimensionKey?: string;
  dimensionValue?: string;
}
```

## Search Behavior

### Scoring Algorithm

Results are ranked by relevance score:

| Match Type            | Score | Condition                       |
| --------------------- | ----- | ------------------------------- |
| Exact title match     | 100   | Title equals query exactly      |
| Title prefix match    | 75    | Title starts with query         |
| Title substring match | 50    | Query found in title            |
| Description match     | 25    | Query found in description      |
| Type exact match      | 50    | Type equals query exactly       |
| Type substring match  | 25    | Query found in type             |
| Dimension match       | 15    | Query found in dimension values |

### Match Detection

Results are grouped by match type:

- **title**: Highest priority, found in item title
- **description**: Found in item description
- **type**: Found in item type
- **dimension**: Found in dimension values

### Equivalence Detection

Equivalences are discovered from two sources:

1. **Explicit IDs**: Items with `equivalentItemIds` array
2. **Links**: Items connected via `same_as`, `represents`, or `manifests_as` links

Equivalences are deduplicated and sorted by confidence score (highest first).

## Perspective Colors

Each perspective has a distinct color for visual identification:

```
- Feature: Blue (#3b82f6)
- Code: Purple (#8b5cf6)
- Test: Green (#10b981)
- API: Amber (#f59e0b)
- Database: Pink (#ec4899)
- Wireframe: Cyan (#06b6d4)
- Documentation: Indigo (#6366f1)
- Deployment: Teal (#14b8a6)
- Architecture: Orange (#f97316)
- Configuration: Purple (#a855f7)
- DataFlow: Sky (#0ea5e9)
- Dependency: Red (#ef4444)
- Domain: Rose (#f43f5e)
- Infrastructure: Lime (#84cc16)
- Journey: Fuchsia (#d946ef)
- Monitoring: Orange (#fb923c)
- Performance: Green (#22c55e)
- Security: Purple (#8b5cf6)
```

## Keyboard Shortcuts

| Key    | Action                    |
| ------ | ------------------------- |
| ↑      | Move to previous result   |
| ↓      | Move to next result       |
| Enter  | Select highlighted result |
| Escape | Clear search and close    |

## Examples

### Search for Authentication

```
Query: "auth"
Results across:
- Feature: "User Authentication System"
- Code: "AuthenticationService", "LoginForm"
- Test: "Authentication Integration Tests"
- API: "POST /api/auth/login", "POST /api/auth/refresh"
- Database: "users_table", "sessions_table"
- Security: "Authentication Security Hardening"
```

### Search with Filters

```tsx
const results = performSearch(items, links, 'login', {
  type: 'Component',
  status: 'done',
  perspectives: ['code', 'wireframe'],
});
```

### Search History

```tsx
// Add to history
addToHistory('authentication');
addToHistory('user login');

// Retrieve history
const history = getHistory();
// ["user login", "authentication"]

// Clear history
clearHistory();
```

## Performance Characteristics

- **Search Time**: O(n) where n = number of items
- **Grouping**: O(m log m) where m = matching items
- **Equivalence Discovery**: O(m \* k) where k = average equivalences per item
- **Debounce Delay**: 300ms (customizable)

For 1000 items: ~30-50ms search time
For 10000 items: ~200-300ms search time

## Accessibility

- Full keyboard navigation support
- ARIA labels on interactive elements
- High contrast colors for visual distinction
- Clear focus indicators
- Status messages for screen readers

## Best Practices

### 1. Use Compact Mode for Toolbars

```tsx
<CrossPerspectiveSearch {...props} compact={true} />
```

### 2. Provide Visual Feedback

```tsx
const [selectedId, setSelectedId] = useState<string | null>(null);

<CrossPerspectiveSearch
  onSelect={(id) => {
    setSelectedId(id);
    scrollToItem(id); // Highlight in graph
  }}
/>;
```

### 3. Limit Results for Performance

```tsx
<CrossPerspectiveSearch {...props} maxResultsPerPerspective={3} />
```

### 4. Use Filters to Narrow Results

```tsx
const [filters, setFilters] = useState<SearchFilters>({
  status: 'done',
  perspectives: ['code', 'api'],
});
```

### 5. Handle Empty States

```tsx
if (results.length === 0 && query) {
  return <EmptyStateUI />;
}
```

## Testing

### Unit Tests

Test the hook with `vitest`:

```bash
bun run test:run -- useCrossPerspectiveSearch.test.ts
```

### Component Tests

Test components with Playwright:

```bash
bun run test:components
```

### E2E Tests

Test full workflows:

```bash
bun run test:workflows
```

### Storybook

View component stories:

```bash
bun run storybook
```

## Troubleshooting

### Results Not Showing

- Check items have `perspective` or `view` field
- Ensure query string is not empty or whitespace
- Verify items match the search query

### Equivalences Not Displayed

- Check items have `equivalentItemIds` array or equivalent links
- Verify links have correct `type` (same_as, represents, manifests_as)
- Ensure linked items exist in the items array

### Performance Issues

- Reduce `maxResultsPerPerspective`
- Use debounced search with longer delay
- Filter items by perspective before searching
- Consider pagination for very large datasets

### Keyboard Navigation Not Working

- Ensure component has focus
- Check for event handler conflicts
- Verify no parent elements are stopping propagation

## Future Enhancements

- [ ] Fuzzy matching for typo tolerance
- [ ] Search within specific perspectives
- [ ] Saved search filters
- [ ] Search result statistics
- [ ] Advanced query syntax (AND, OR, NOT)
- [ ] Search suggestions/autocomplete
- [ ] Search result export
- [ ] Search analytics

## Related Components

- `GraphSearch`: Single-perspective search
- `GraphViewContainer`: Main graph view
- `PerspectiveSelector`: Perspective switching
- `EquivalencePanel`: Equivalence relationship viewer
- `PivotNavigation`: Cross-perspective navigation

## API Reference

### CrossPerspectiveSearch Props

```typescript
interface CrossPerspectiveSearchProps {
  items: Item[];
  links: Link[];
  onSelect: (itemId: string) => void;
  onHighlight: (itemId: string | null) => void;
  compact?: boolean;
  className?: string;
  maxResultsPerPerspective?: number;
}
```

### useCrossPerspectiveSearch Return

```typescript
{
  performSearch: (
    items: Item[],
    links: Link[],
    query: string,
    filters?: SearchFilters
  ) => GroupedSearchResults[];

  debouncedSearch: (
    items: Item[],
    links: Link[],
    query: string,
    filters: SearchFilters | undefined,
    onResults: (results: GroupedSearchResults[]) => void,
    delay?: number
  ) => void;

  addToHistory: (query: string) => void;
  getHistory: () => string[];
  clearHistory: () => void;
}
```
