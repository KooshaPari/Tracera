# DesignTokenBrowser - Quick Start Guide

## 5-Minute Setup

### 1. Import the Component

```tsx
import { DesignTokenBrowser } from '@/components/graph';
import type { DesignToken } from '@tracertm/types';
```

### 2. Prepare Your Tokens

```tsx
const tokens: DesignToken[] = [
  {
    id: 'color-primary',
    libraryId: 'lib-1',
    projectId: 'proj-1',
    name: 'primary',
    path: ['colors', 'primary', '500'],
    type: 'color',
    value: '#3B82F6',
    resolvedValue: '#3B82F6',
    usageCount: 12,
    usedByComponentIds: ['btn-1'],
    tags: ['brand'],
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
  },
  // ... more tokens
];
```

### 3. Render the Component

```tsx
export function MyTokenBrowser() {
  return <DesignTokenBrowser tokens={tokens} />;
}
```

## Common Tasks

### Show Component Usage

```tsx
const componentMap = new Map([
  ['btn-1', 'Button Primary'],
  ['link-1', 'Link Text'],
]);

<DesignTokenBrowser
  tokens={tokens}
  showComponentUsage={true}
  componentMap={componentMap}
/>
```

### Handle Token Selection

```tsx
const [selectedTokenId, setSelectedTokenId] = useState<string | null>(null);

<DesignTokenBrowser
  tokens={tokens}
  selectedTokenId={selectedTokenId}
  onSelectToken={setSelectedTokenId}
/>
```

### Link to Figma

```tsx
<DesignTokenBrowser
  tokens={tokens}
  onLinkToFigma={async (tokenId) => {
    await api.linkTokenToFigma(tokenId);
  }}
/>
```

## Feature Checklist

- [x] Display tokens organized by type
- [x] Search by name, path, value, or tags
- [x] Expand/collapse token categories
- [x] View token details (description, references, usage)
- [x] Copy token value to clipboard
- [x] Show which components use each token
- [x] Display token references
- [x] Figma integration support
- [x] Responsive design
- [x] Keyboard accessible
- [x] Mobile friendly

## Supported Token Types

- Color
- Spacing
- Typography
- Shadow
- Border
- Border Radius
- Opacity
- Z-Index
- Breakpoint
- Animation
- Custom

## File Locations

| File | Purpose |
|------|---------|
| `src/components/graph/DesignTokenBrowser.tsx` | Main component |
| `src/components/graph/DesignTokenBrowser.README.md` | Full documentation |
| `src/components/graph/DesignTokenBrowser.example.tsx` | Usage examples |
| `src/__tests__/components/graph/DesignTokenBrowser.test.tsx` | Test suite |

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Tab | Navigate between tokens |
| Enter | Expand/collapse or select token |
| Space | Activate buttons |
| Ctrl/Cmd+F | Focus search input |

## Props Quick Reference

```typescript
interface DesignTokenBrowserProps {
  // Required
  tokens: DesignToken[];

  // Optional: Callbacks
  onSelectToken?: (tokenId: string) => void;
  onLinkToFigma?: (tokenId: string) => void;

  // Optional: State
  selectedTokenId?: string | null;

  // Optional: Configuration
  showComponentUsage?: boolean;           // default: true
  componentMap?: Map<string, string>;
}
```

## Styling

The component inherits your app's theming:

- Primary color: Used for selection highlights
- Muted colors: Used for secondary text
- Tailwind CSS: All styling uses utility classes
- shadcn/ui: Consistent with existing components

No additional CSS required!

## Performance Tips

### For Large Token Sets (1000+)

```tsx
// Consider pagination
const tokensPerPage = 50;
const displayedTokens = tokens.slice(
  page * tokensPerPage,
  (page + 1) * tokensPerPage
);

<DesignTokenBrowser tokens={displayedTokens} />
```

### Optimize Token Map

```tsx
// Memoize the component map to prevent recreations
const componentMap = useMemo(() => new Map([
  ['btn-1', 'Button Primary'],
  ['btn-2', 'Button Secondary'],
]), []);
```

## Testing

```bash
# Run component tests
bun run test -- DesignTokenBrowser.test.tsx

# Run with coverage
bun run test -- --coverage DesignTokenBrowser.test.tsx

# Run all tests
bun run test
```

## Troubleshooting

### Tokens Not Showing?

1. Check token array is not empty
2. Verify each token has required fields: `id`, `name`, `type`, `value`
3. Ensure token type is valid (see Supported Token Types)
4. Check token libraryId matches expected library

### Search Not Working?

1. Verify tokens have text-based properties (name, path, value)
2. Check tags are strings in array
3. Try expanding a category first

### Component Usage Not Showing?

1. Verify `showComponentUsage={true}`
2. Check `componentMap` is provided
3. Ensure token has `usedByComponentIds` array populated
4. Component IDs in token must match componentMap keys

## Examples

### Minimal Example

```tsx
<DesignTokenBrowser tokens={colorTokens} />
```

### Full-Featured Example

```tsx
<DesignTokenBrowser
  tokens={allTokens}
  selectedTokenId={selected}
  onSelectToken={setSelected}
  onLinkToFigma={linkToFigma}
  showComponentUsage={true}
  componentMap={componentNames}
/>
```

### In a Page Layout

```tsx
export function DesignSystemPage() {
  const { tokens } = useDesignSystem();

  return (
    <div className="grid grid-cols-[1fr_400px] gap-4 h-screen">
      <div className="p-4">
        {/* Page content */}
      </div>
      <DesignTokenBrowser
        tokens={tokens}
        showComponentUsage={true}
        componentMap={componentNameMap}
      />
    </div>
  );
}
```

## Next Steps

1. **Read Full Documentation**: See `DesignTokenBrowser.README.md`
2. **Explore Examples**: Check `DesignTokenBrowser.example.tsx`
3. **Run Tests**: `bun run test -- DesignTokenBrowser.test.tsx`
4. **Integrate**: Add to your design system pages

## Support

For issues or questions:

1. Check the README for detailed documentation
2. Review examples for usage patterns
3. Check test file for test scenarios
4. Refer to troubleshooting section above

## Related Components

- **ComponentLibraryExplorer**: Browse components
- **FigmaSyncPanel**: Manage Figma sync
- **ComponentUsageMatrix**: View usage relationships

---

**Component Status**: Production Ready ✅

**Last Updated**: January 2024
