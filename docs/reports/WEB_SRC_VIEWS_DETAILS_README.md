# Type-Specific Detail Pages Foundation

This directory contains the foundation components for type-specific detail pages across all item types in TraceRTM.

## Architecture

### Base Components

1. **BaseDetailView** (`BaseDetailView.tsx`)
   - Shared layout structure for all detail pages
   - Responsive header, tab navigation, action toolbar
   - Mobile-optimized with Tailwind CSS
   - Accessibility features (ARIA labels, keyboard navigation)

2. **DetailHeader** (`DetailHeader.tsx`)
   - Consistent header with breadcrumb navigation
   - Item title, type icon, status/priority badges
   - Action buttons: Edit, Delete, Clone, Share
   - Uses `itemTypeConfig` for type-specific styling

### Shared Tab Components

Located in `tabs/`:

1. **OverviewTab** (`tabs/OverviewTab.tsx`)
   - Generic overview information
   - Status, priority, owner, version
   - Creation and update timestamps
   - Identifiers and metadata

2. **LinksTab** (`tabs/LinksTab.tsx`)
   - Upstream dependencies
   - Downstream impacts
   - Relationship visualization
   - Link type badges and navigation

3. **HistoryTab** (`tabs/HistoryTab.tsx`)
   - Audit trail with timeline
   - Version history
   - Change events
   - Metadata display

4. **CommentsTab** (`tabs/CommentsTab.tsx`)
   - Comment thread display
   - Add new comments
   - User avatars and timestamps
   - Discussion guidelines

## Usage

### Basic Implementation

```tsx
import { BaseDetailView, OverviewTab, LinksTab, HistoryTab } from '@/views/details';
import type { TypedItem } from '@tracertm/types';

function MyItemDetailView({ item }: { item: TypedItem }) {
  const tabs = [
    {
      id: 'overview',
      label: 'Overview',
      content: <OverviewTab item={item} />,
    },
    {
      id: 'links',
      label: 'Links',
      content: <LinksTab item={item} sourceLinks={[]} targetLinks={[]} />,
      badge: 5,
    },
    {
      id: 'history',
      label: 'History',
      content: <HistoryTab item={item} />,
    },
  ];

  return <BaseDetailView item={item} tabs={tabs} defaultTab='overview' />;
}
```

### Adding Custom Actions

```tsx
const actions = [
  {
    label: 'Run Tests',
    icon: PlayIcon,
    onClick: () => runTests(item.id),
    variant: 'default' as const,
  },
  {
    label: 'Export',
    icon: DownloadIcon,
    onClick: () => exportItem(item),
    variant: 'outline' as const,
  },
];

<BaseDetailView item={item} tabs={tabs} actions={actions} />;
```

### Custom Tab Content

```tsx
{
  id: "custom",
  label: "Custom Section",
  content: (
    <div className="space-y-4">
      <h2>Custom Content</h2>
      <p>Add your type-specific logic here</p>
    </div>
  ),
  badge: "NEW",
  ariaLabel: "Custom section for special features",
}
```

## Type-Specific Implementations

### RequirementDetailView

Advanced requirement detail page with:

- EARS pattern visualization
- Quality metrics (ISO 29148)
- Risk assessment
- Verification status
- Traceability links (ADR, contracts)

### TestDetailView

Comprehensive test detail page with:

- Test specification details
- Execution status and history
- Coverage metrics
- Flakiness detection
- Safety level indicators
- DO-178C compliance

## Styling Guidelines

### Type-Specific Colors

Use `getItemTypeConfig()` from `/lib/itemTypeConfig.ts` for consistent colors:

```tsx
import { getItemTypeConfig } from '@/lib/itemTypeConfig';

const typeConfig = getItemTypeConfig(item.type);
const color = typeConfig.color; // e.g., "#9333ea" for requirement
```

### Status and Priority Badges

```tsx
const statusColors = {
  done: 'bg-emerald-500/15 text-emerald-700 border-emerald-500/30',
  in_progress: 'bg-sky-500/15 text-sky-700 border-sky-500/30',
  todo: 'bg-slate-500/10 text-slate-600 border-slate-500/20',
  blocked: 'bg-rose-500/15 text-rose-700 border-rose-500/30',
};

const priorityColors = {
  critical: 'bg-rose-500 text-white',
  high: 'bg-orange-500 text-white',
  medium: 'bg-indigo-500 text-white',
  low: 'bg-emerald-500 text-white',
};
```

## Accessibility Features

All components include:

- ARIA labels for screen readers
- Keyboard navigation support
- Focus management
- Semantic HTML structure
- High contrast mode compatibility

## Mobile Responsiveness

- Responsive grid layouts (1 column mobile, 2-3 desktop)
- Touch-friendly button sizes (min 44px)
- Horizontal scroll for tabs on mobile
- Collapsible sections for small screens

## Best Practices

1. **Always use TypedItem**: Leverage the discriminated union types for type safety
2. **Type guards**: Use type guards (e.g., `isRequirementItem()`) before accessing type-specific properties
3. **Consistent styling**: Use shared color constants and UI components
4. **Accessibility first**: Include ARIA labels and keyboard navigation
5. **Mobile-friendly**: Test on mobile viewports

## File Structure

```
details/
├── BaseDetailView.tsx         # Base layout component
├── DetailHeader.tsx            # Shared header component
├── index.ts                    # Public exports
├── RequirementDetailView.tsx   # Requirement-specific view
├── TestDetailView.tsx          # Test-specific view
├── tabs/
│   ├── CommentsTab.tsx        # Comments/discussions
│   ├── HistoryTab.tsx         # Audit trail
│   ├── LinksTab.tsx           # Relationships
│   └── OverviewTab.tsx        # Basic info
└── README.md                   # This file
```

## Next Steps

To create a new type-specific detail view:

1. Create `{Type}DetailView.tsx` in this directory
2. Import base components: `BaseDetailView`, shared tabs
3. Add type-specific tabs as needed
4. Use type guards to ensure type safety
5. Export from `index.ts`

## References

- Item Types: `/frontend/packages/types/src/index.ts`
- Type Config: `/frontend/apps/web/src/lib/itemTypeConfig.ts`
- UI Components: `/frontend/packages/ui/src/components/`
- Hooks: `/frontend/apps/web/src/hooks/`
