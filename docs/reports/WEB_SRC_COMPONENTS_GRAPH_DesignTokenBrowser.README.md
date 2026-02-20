# DesignTokenBrowser Component

A comprehensive React component for browsing, searching, and managing design tokens from your design system. Displays tokens organized by category with previews, component usage tracking, and Figma integration.

## Features

### Core Features

- **Token Organization**: Automatically groups tokens by type (colors, typography, spacing, shadows, borders, etc.)
- **Advanced Search**: Filter tokens by name, path, value, or tags
- **Category Expansion**: Expand/collapse token categories with individual or bulk controls
- **Token Preview**: Visual previews for colors, shadows, and border tokens
- **Detailed View**: Expand token details to see description, references, and component usage

### Integration Features

- **Figma Sync**: Display and link tokens to Figma styles
- **Component Usage Tracking**: Show which components use each token
- **Token References**: Display token-to-token references and dependencies
- **Copy to Clipboard**: Quick copy token values with visual feedback

### UX Features

- **Real-time Search**: Instant filtering as you type
- **Statistics Dashboard**: Token count, usage, sync status at a glance
- **Visual Indicators**: Icons and badges for token types, usage, and sync status
- **Responsive Design**: Works on all screen sizes
- **Keyboard Navigation**: Full keyboard support with semantic HTML

## Usage

### Basic Example

```tsx
import { DesignTokenBrowser } from '@/components/graph';
import type { DesignToken } from '@tracertm/types';

const MyTokenBrowser = () => {
  const tokens: DesignToken[] = [
    {
      id: 'color-primary',
      libraryId: 'lib-1',
      projectId: 'proj-1',
      name: 'primary',
      path: ['colors', 'primary', '500'],
      description: 'Primary brand color',
      type: 'color',
      value: '#3B82F6',
      resolvedValue: '#3B82F6',
      usageCount: 12,
      usedByComponentIds: ['btn-1', 'link-1'],
      tags: ['brand', 'interactive'],
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-01T00:00:00Z',
    },
  ];

  return <DesignTokenBrowser tokens={tokens} />;
};
```

### With Callbacks

```tsx
const MyTokenBrowser = () => {
  const [selectedToken, setSelectedToken] = useState<string | null>(null);

  const handleSelectToken = (tokenId: string) => {
    setSelectedToken(tokenId);
    console.log(`Selected token: ${tokenId}`);
  };

  const handleLinkToFigma = (tokenId: string) => {
    // Call your Figma linking API
    api.linkTokenToFigma(tokenId);
  };

  return (
    <DesignTokenBrowser
      tokens={tokens}
      selectedTokenId={selectedToken}
      onSelectToken={handleSelectToken}
      onLinkToFigma={handleLinkToFigma}
    />
  );
};
```

### With Component Usage Tracking

```tsx
const MyTokenBrowser = () => {
  // Map component IDs to human-readable names
  const componentMap = new Map([
    ['btn-1', 'Button Primary'],
    ['link-1', 'Link Text'],
    ['card-1', 'Card Header'],
  ]);

  return (
    <DesignTokenBrowser tokens={tokens} showComponentUsage={true} componentMap={componentMap} />
  );
};
```

## API Reference

### Props

```typescript
interface DesignTokenBrowserProps {
  /** Design tokens to display */
  tokens: DesignToken[];

  /** Callback when a token is selected */
  onSelectToken?: (tokenId: string) => void;

  /** Currently selected token ID */
  selectedTokenId?: string | null;

  /** Callback to link token to Figma style */
  onLinkToFigma?: (tokenId: string) => void;

  /** Show component usage details */
  showComponentUsage?: boolean;

  /** Map component IDs to human-readable names */
  componentMap?: Map<string, string>;
}
```

### Token Type

```typescript
interface DesignToken {
  id: string;
  libraryId: string;
  projectId: string;

  // Identity
  name: string; // e.g., "colors.primary.500"
  path: string[]; // e.g., ["colors", "primary", "500"]
  description?: string;

  // Value
  type: DesignTokenType; // color | spacing | typography | shadow | border | radius | opacity | z-index | breakpoint | animation | custom
  value: string; // Raw value
  resolvedValue?: string; // Resolved value (if references other tokens)

  // References
  referencesTokenId?: string; // If this token references another
  referencedByIds?: string[]; // Tokens that reference this one

  // Figma integration
  figmaStyleId?: string; // Linked to Figma style
  figmaVariableId?: string;

  // Usage
  usageCount: number;
  usedByComponentIds?: string[]; // Components using this token

  // Metadata
  tags?: string[];
  metadata?: Record<string, unknown>;

  // Timestamps
  createdAt: string;
  updatedAt: string;
}
```

## Supported Token Types

| Type         | Icon        | Use Cases                          | Preview        |
| ------------ | ----------- | ---------------------------------- | -------------- |
| `color`      | 🎨 Palette  | Brand colors, semantic colors      | Color box      |
| `spacing`    | # Hash      | Padding, margins, gaps             | Code icon      |
| `typography` | 📄 FileCode | Font sizes, line heights, families | Code icon      |
| `shadow`     | ⚡ Zap      | Box shadows, drop shadows          | Shadow preview |
| `border`     | 🔗 Link     | Border styles, widths              | Border preview |
| `radius`     | ⚪ Circle   | Border radius values               | Radius preview |
| `opacity`    | 👁️ Eye      | Transparency values                | Code icon      |
| `z-index`    | 📚 Layers   | Stacking context values            | Code icon      |
| `breakpoint` | 📐 Maximize | Media query breakpoints            | Code icon      |
| `animation`  | ▶️ Play     | Animation durations, easing        | Code icon      |
| `custom`     | 💻 Code     | Custom token types                 | Code icon      |

## Features in Detail

### Search and Filtering

The search input supports multiple search strategies:

```tsx
// Search by token name
'primary';

// Search by path
'colors / primary';

// Search by value
'#3B82F6';

// Search by tag
'brand';
```

### Category Management

Organize tokens by type with expand/collapse controls:

```tsx
// Individual category toggle
onClick={() => toggleCategory('color')}

// Expand all categories
<Button onClick={expandAllCategories}>Expand All</Button>

// Collapse all categories
<Button onClick={collapseAllCategories}>Collapse All</Button>
```

### Token Details Panel

Click the expand icon on any token to see:

- **Description**: Token purpose and usage guidelines
- **References**: Tokens this token references
- **Referenced By**: Other tokens that reference this token
- **Component Usage**: Which components use this token
- **Figma Link**: Direct link to Figma style (if synced)
- **Tags**: Categorization tags

### Figma Integration

Show sync status and link tokens to Figma:

```tsx
// Display Figma icon for synced tokens
{
  token.figmaStyleId && <Figma className='h-3.5 w-3.5' />;
}

// Link token to Figma style
<Button onClick={() => onLinkToFigma(token.id)}>Link to Figma</Button>;
```

### Component Usage Tracking

Display which components use each token:

```tsx
const componentMap = new Map([
  ['btn-1', 'Button Primary'],
  ['btn-2', 'Button Secondary'],
  ['link-1', 'Link Text'],
]);

<DesignTokenBrowser tokens={tokens} showComponentUsage={true} componentMap={componentMap} />;
```

## Statistics Dashboard

The header displays key metrics:

- **Total tokens**: Count of all tokens in the library
- **Tokens in use**: Tokens with usageCount > 0
- **Synced tokens**: Tokens linked to Figma styles
- **Linked tokens**: Tokens that reference other tokens

## Styling and Customization

The component uses `shadcn/ui` components and follows your app's theming:

- Primary color for selection and highlights
- Muted colors for secondary text
- Responsive design with Tailwind utilities
- Semantic HTML for accessibility

### CSS Classes

Main components use these classes:

- `.h-full` - Full height container
- `.flex flex-col` - Vertical flex layout
- `.space-y-*` - Vertical spacing
- `.gap-*` - Gap between items
- `.text-xs`, `.text-sm` - Text sizes
- `.font-mono` - Code font for token values

## Accessibility

- **Keyboard Navigation**: Full keyboard support
- **ARIA Labels**: Semantic HTML with proper roles
- **Color Contrast**: WCAG AA compliant colors
- **Focus Management**: Visible focus indicators
- **Screen Reader Support**: Descriptive labels and aria-labels

### Keyboard Shortcuts

- `Tab` / `Shift+Tab` - Navigate between tokens
- `Enter` - Expand/collapse category or select token
- `Space` - Activate buttons
- `Ctrl+F` / `Cmd+F` - Focus search input

## Performance Optimization

The component is optimized for large token libraries:

- **Memoization**: Sub-components use `React.memo`
- **Lazy Rendering**: ScrollArea for efficient rendering
- **Efficient Filtering**: useMemo for search operations
- **No Unnecessary Re-renders**: Proper dependency tracking

### For Large Libraries (1000+ tokens)

```tsx
// Lazy load tokens with pagination
const [page, setPage] = useState(0);
const tokensPerPage = 50;
const displayedTokens = tokens.slice(page * tokensPerPage, (page + 1) * tokensPerPage);

<DesignTokenBrowser tokens={displayedTokens} />;
```

## Common Use Cases

### 1. Design System Documentation

Embed in a design system documentation page:

```tsx
const DesignSystemDocs = () => {
  const { tokens } = useDesignSystem();

  return (
    <div className='grid grid-cols-[1fr_400px]'>
      <div>{/* documentation content */}</div>
      <DesignTokenBrowser tokens={tokens} showComponentUsage={true} />
    </div>
  );
};
```

### 2. Component Variant Selector

Use to preview token applications:

```tsx
const TokenPreview = () => {
  const [selectedToken, setSelectedToken] = useState<string | null>(null);
  const tokens = useTokens();

  return (
    <div className='grid grid-cols-2 gap-4'>
      <DesignTokenBrowser
        tokens={tokens}
        selectedTokenId={selectedToken}
        onSelectToken={setSelectedToken}
      />
      <TokenPreviewPane tokenId={selectedToken} />
    </div>
  );
};
```

### 3. Token Management Dashboard

Full-featured token editor/manager:

```tsx
const TokenManager = () => {
  const { tokens, linkTokenToFigma } = useTokens();

  return (
    <DesignTokenBrowser
      tokens={tokens}
      showComponentUsage={true}
      componentMap={componentNameMap}
      onLinkToFigma={linkTokenToFigma}
    />
  );
};
```

## Troubleshooting

### Tokens Not Displaying

Check that:

- Tokens array is not empty
- Each token has required fields (id, name, type, value)
- Token type is valid (see Supported Token Types)

### Search Not Working

Ensure:

- Search query contains valid text
- Token properties (name, path, value) are strings
- Tags are properly formatted in token metadata

### Figma Integration Not Working

Verify:

- `figmaStyleId` is set on the token
- `onLinkToFigma` callback is provided
- Figma API token has correct permissions

### Performance Issues

Try:

- Implementing pagination for large token sets
- Using lazy loading with virtualization
- Filtering tokens before passing to component
- Memoizing component parent to prevent unnecessary re-renders

## Best Practices

1. **Keep Token Names Consistent**: Use dot notation for hierarchical names

   ```
   ✅ colors.primary.500
   ❌ primary-color
   ```

2. **Provide Descriptions**: Help users understand token purpose

   ```tsx
   description: 'Primary brand color used in interactive elements';
   ```

3. **Track Component Usage**: Maintain usageCount and usedByComponentIds

   ```tsx
   usageCount: 12,
   usedByComponentIds: ['btn-1', 'link-1', 'card-1']
   ```

4. **Use Figma Integration**: Link tokens to Figma styles for sync

   ```tsx
   figmaStyleId: 'abc123xyz789';
   ```

5. **Organize with Tags**: Use tags for categorization and filtering
   ```tsx
   tags: ['brand', 'interactive', 'primary'];
   ```

## Related Components

- `ComponentLibraryExplorer` - Browse components in your library
- `FigmaSyncPanel` - Manage Figma synchronization
- `ComponentUsageMatrix` - View component-to-token relationships

## Contributing

When adding features:

1. Update component props interface
2. Add tests in `DesignTokenBrowser.test.tsx`
3. Update this README with new features
4. Ensure accessibility compliance
5. Performance test with large token sets

## License

Part of the Atoms.tech design system framework.
