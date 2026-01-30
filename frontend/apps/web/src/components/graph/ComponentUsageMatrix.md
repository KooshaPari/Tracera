# ComponentUsageMatrix

A comprehensive matrix view component that visualizes component library usage across pages and views. Shows which design system components are used where, their usage counts, variants, and deprecation status.

## Features

### Core Functionality
- **Component Library Matrix**: Display all components in a table-like matrix view
- **Category Grouping**: Automatically groups components by category (atoms, molecules, organisms, etc.)
- **Usage Tracking**: Shows total usage count and per-page breakdown
- **Variant Tracking**: Displays which variants are used where
- **Props Display**: Lists component props when expanded
- **Deprecation Warnings**: Highlights deprecated components with special styling
- **Unused Detection**: Identifies components with zero usage

### Filtering & Search
- **Text Search**: Search components by name, display name, or description
- **Category Filter**: Filter components by atomic design category
- **Filter Display**: Shows active filters with clear badges

### Customization
- **Custom Page Labels**: Map file paths to human-readable page names
- **Status Badges**: Shows component status (Stable, Beta, Deprecated, Experimental)
- **Expandable Rows**: Click to expand component rows for detailed information
- **Collapsible Categories**: Collapse/expand entire category sections

### Visual Features
- **Color-Coded Status**: Different colors for different component statuses
- **Deprecation Highlighting**: Highlights unused and deprecated components
- **Statistics Dashboard**: Shows total components, usage counts, and metrics
- **Responsive Layout**: Adapts to different screen sizes

## Props

### Required Props
- `components`: `LibraryComponent[]` - Array of library components to display

### Optional Props

#### Data
- `usage?`: `ComponentUsage[]` - Component usage tracking data
- `pages?`: `string[]` - List of pages where components are used

#### Selection & Callbacks
- `selectedCategory?`: `ComponentCategory | "all"` - Currently selected category filter (default: "all")
- `onCategoryChange?`: `(category: ComponentCategory | "all") => void` - Callback when category changes
- `onSelectComponent?`: `(componentId: string) => void` - Callback when a component is selected
- `onViewInCode?`: `(componentId: string) => void` - Callback to view component in code

#### Display Options
- `isLoading?`: `boolean` - Show loading state (default: false)
- `enableFiltering?`: `boolean` - Enable/disable search and filter controls (default: true)
- `highlightUnused?`: `boolean` - Highlight unused and deprecated components (default: true)
- `showVariants?`: `boolean` - Show variant information when expanded (default: true)
- `showProps?`: `boolean` - Show props information when expanded (default: true)

#### Customization
- `pageLabels?`: `Record<string, string>` - Map file paths to human-readable names

## Usage Examples

### Basic Usage
```typescript
import { ComponentUsageMatrix } from '@/components/graph'
import type { LibraryComponent, ComponentUsage } from '@tracertm/types'

function MyComponent() {
  const components: LibraryComponent[] = [
    {
      id: 'btn-1',
      name: 'Button',
      displayName: 'Primary Button',
      category: 'atom',
      status: 'stable',
      usageCount: 24,
      // ... other props
    },
  ]

  const usage: ComponentUsage[] = [
    {
      id: 'usage-1',
      componentId: 'btn-1',
      usedInFilePath: 'pages/dashboard.tsx',
      variantUsed: 'Primary',
      // ... other props
    },
  ]

  return (
    <ComponentUsageMatrix
      components={components}
      usage={usage}
      enableFiltering={true}
      highlightUnused={true}
    />
  )
}
```

### With Custom Page Labels
```typescript
<ComponentUsageMatrix
  components={components}
  usage={usage}
  pageLabels={{
    'pages/dashboard.tsx': 'Dashboard',
    'pages/settings.tsx': 'Settings',
    'pages/profile.tsx': 'User Profile',
  }}
/>
```

### With Callbacks
```typescript
<ComponentUsageMatrix
  components={components}
  usage={usage}
  selectedCategory="atom"
  onCategoryChange={(category) => {
    console.log('Selected category:', category)
  }}
  onSelectComponent={(componentId) => {
    console.log('Selected component:', componentId)
  }}
  onViewInCode={(componentId) => {
    window.open(`/code/${componentId}`, '_blank')
  }}
/>
```

### With Controlled Filtering
```typescript
const [selectedCategory, setSelectedCategory] = useState<ComponentCategory>('atom')

<ComponentUsageMatrix
  components={components}
  usage={usage}
  selectedCategory={selectedCategory}
  onCategoryChange={(category) => {
    setSelectedCategory(category as ComponentCategory)
  }}
  enableFiltering={true}
/>
```

## Component Structure

### Main Sections

1. **Header**
   - Component title and statistics
   - Filter controls (search, category select)
   - Active filter badges

2. **Content**
   - Category sections (collapsible)
   - Component rows within each category
   - Expandable details panel per component

3. **Footer**
   - Showing X of Y components
   - Overall usage percentage

### Expandable Component Details

When expanded, each component row shows:
- **Props**: List of available props with required indicator
- **Variants**: Available component variants with usage counts
- **Page Usage**: List of pages where the component is used
- **Description**: Component description text
- **Deprecation Message**: If the component is deprecated

## Category Types

The component supports all atomic design categories:
- `atom` - Basic building blocks (Button, Input, Icon)
- `molecule` - Simple combinations (SearchBar, FormField)
- `organism` - Complex combinations (Header, Card, Form)
- `template` - Page layouts
- `page` - Full page components
- `utility` - Utility components
- `layout` - Layout components
- `navigation` - Navigation components
- `feedback` - Feedback components (Alert, Toast)
- `overlay` - Overlay components (Modal, Drawer)
- `data-display` - Data display (Table, List)
- `data-entry` - Data entry (Form, Select)
- `other` - Other components

## Component Status

Supported component statuses with color coding:
- `stable` - Green (production-ready)
- `beta` - Blue (feature-complete, testing)
- `deprecated` - Red (not recommended)
- `experimental` - Purple (early development)

## Testing

The component includes comprehensive test coverage:

```bash
# Run tests
bun run test ComponentUsageMatrix.test.tsx --run

# Watch mode
bun run test ComponentUsageMatrix.test.tsx

# With UI
bun run test ComponentUsageMatrix.test.tsx --ui
```

Test coverage includes:
- Component rendering and display
- Filtering and search functionality
- Expandable rows and details
- Callback invocation
- Empty and loading states
- Category grouping and statistics
- Deprecation and unused highlighting

## Storybook Stories

The component has comprehensive Storybook stories available:

```bash
bun run build  # Build Storybook
```

Available stories:
- **Default** - Full-featured matrix view
- **WithSearch** - With filtering enabled
- **HighlightUnused** - Highlighting deprecated/unused components
- **WithVariantsAndProps** - Showing variant and props details
- **CustomPageLabels** - Using custom page names
- **NoFiltering** - Without filter controls
- **LoadingState** - Loading indicator
- **Empty** - Empty state
- **OnlyAtoms** - Pre-filtered to atom category
- **WithCallbacks** - Demonstrating callback functions

## Styling

The component uses:
- **Tailwind CSS** for styling
- **Shadcn/UI** components for base UI elements
- **Lucide React** icons for visual indicators

All styling is responsive and follows the design system.

## Type Definitions

```typescript
interface ComponentUsageMatrixProps {
  components: LibraryComponent[]
  usage?: ComponentUsage[]
  pages?: string[]
  selectedCategory?: ComponentCategory | 'all'
  onCategoryChange?: (category: ComponentCategory | 'all') => void
  onSelectComponent?: (componentId: string) => void
  onViewInCode?: (componentId: string) => void
  isLoading?: boolean
  enableFiltering?: boolean
  highlightUnused?: boolean
  showVariants?: boolean
  showProps?: boolean
  pageLabels?: Record<string, string>
}
```

## Performance Considerations

- **Memoization**: Uses React.memo for category and row components
- **useMemo**: Caches computed values (statistics, filtered components, grouping)
- **Lazy Rendering**: Components are rendered on demand when expanded
- **Efficient Filtering**: Uses memoized filter functions

## Accessibility

- **Semantic HTML**: Uses proper heading and button elements
- **ARIA Labels**: Provides tooltips and descriptions
- **Keyboard Navigation**: Fully keyboard accessible
- **Color Contrast**: Meets WCAG standards

## Related Components

- `ComponentLibraryExplorer` - Browse component libraries with detailed information
- `NodeDetailPanel` - Display detailed information about selected items
- `Badge` - Status indicator badges
- `Collapsible` - Expandable sections

## Files

- `/src/components/graph/ComponentUsageMatrix.tsx` - Main component
- `/src/__tests__/components/ComponentUsageMatrix.test.tsx` - Test suite
- `/src/components/graph/__stories__/ComponentUsageMatrix.stories.tsx` - Storybook stories
