# Figma Generator - Examples

Real-world examples of using the Figma design generator with TracerTM.

## Example 1: Button Component

### React Component (Input)

```typescript
// packages/ui/src/components/Button.tsx
import { cva, type VariantProps } from 'class-variance-authority';

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-lg font-medium transition-colors',
  {
    variants: {
      variant: {
        primary: 'bg-primary-600 text-white hover:bg-primary-700',
        secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300',
        outline: 'border-2 border-primary-600 text-primary-600 hover:bg-primary-50',
      },
      size: {
        sm: 'px-3 py-1.5 text-sm',
        md: 'px-4 py-2 text-base',
        lg: 'px-6 py-3 text-lg',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  children: React.ReactNode;
}

export function Button({ variant, size, children, className, ...props }: ButtonProps) {
  return (
    <button className={buttonVariants({ variant, size, className })} {...props}>
      {children}
    </button>
  );
}
```

### Generated Figma Structure (Output)

```json
{
  "id": "component-button",
  "name": "Button",
  "type": "COMPONENT_SET",
  "children": [
    {
      "id": "variant-primary-md",
      "name": "variant=primary, size=md",
      "type": "COMPONENT",
      "properties": {
        "width": "auto",
        "height": 40
      },
      "styles": {
        "fills": [{ "type": "SOLID", "color": "#2563eb", "opacity": 1 }],
        "cornerRadius": 8,
        "padding": { "top": 8, "right": 16, "bottom": 8, "left": 16 },
        "layoutMode": "HORIZONTAL",
        "primaryAxisAlignItems": "CENTER",
        "counterAxisAlignItems": "CENTER",
        "typography": {
          "fontFamily": "Inter",
          "fontSize": 16,
          "fontWeight": 500,
          "lineHeight": 24,
          "color": "#ffffff"
        }
      }
    },
    {
      "id": "variant-secondary-md",
      "name": "variant=secondary, size=md",
      "type": "COMPONENT",
      "styles": {
        "fills": [{ "type": "SOLID", "color": "#e5e7eb" }],
        "typography": {
          "color": "#111827"
        }
      }
    }
  ]
}
```

### Generated Storybook Story (Output)

```typescript
// .figma-output/stories/Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from '@tracertm/ui';

const meta: Meta<typeof Button> = {
  title: 'Components/Button',
  component: Button,
  parameters: {
    layout: 'centered',
    design: {
      type: 'figma',
      url: 'https://www.figma.com/file/ABC123/Design-System?node-id=1:234',
    },
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'outline'],
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg'],
    },
  },
};

export default meta;
type Story = StoryObj<typeof Button>;

export const Primary: Story = {
  args: {
    variant: 'primary',
    size: 'md',
    children: 'Primary Button',
  },
};

export const Secondary: Story = {
  args: {
    variant: 'secondary',
    size: 'md',
    children: 'Secondary Button',
  },
};

export const Small: Story = {
  args: {
    variant: 'primary',
    size: 'sm',
    children: 'Small Button',
  },
};

export const Large: Story = {
  args: {
    variant: 'primary',
    size: 'lg',
    children: 'Large Button',
  },
};
```

## Example 2: Card Component

### React Component

```typescript
// packages/ui/src/components/Card.tsx
export interface CardProps {
  title: string;
  description: string;
  image?: string;
  actions?: React.ReactNode;
}

export function Card({ title, description, image, actions }: CardProps) {
  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden">
      {image && (
        <div className="h-48 bg-gray-200">
          <img src={image} alt={title} className="w-full h-full object-cover" />
        </div>
      )}
      <div className="p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-2">{title}</h3>
        <p className="text-gray-600 text-sm mb-4">{description}</p>
        {actions && <div className="flex gap-2">{actions}</div>}
      </div>
    </div>
  );
}
```

### Tailwind → Figma Conversion

```javascript
// Input classes → Output Figma properties

'bg-white'           → fills: [{ type: 'SOLID', color: '#ffffff' }]
'rounded-xl'         → cornerRadius: 12
'shadow-lg'          → effects: [{ type: 'DROP_SHADOW', radius: 15, ... }]
'overflow-hidden'    → clipsContent: true

'h-48'               → height: 192
'bg-gray-200'        → fills: [{ type: 'SOLID', color: '#e5e7eb' }]

'p-6'                → padding: { top: 24, right: 24, bottom: 24, left: 24 }
'text-xl'            → typography: { fontSize: 20 }
'font-bold'          → typography: { fontWeight: 700 }
'text-gray-900'      → typography: { color: '#111827' }
'mb-2'               → marginBottom: 8

'flex'               → layoutMode: 'HORIZONTAL'
'gap-2'              → itemSpacing: 8
```

## Example 3: Design Token Extraction

### Figma Design Tokens (Input)

Figma file contains:

- Color styles: "Primary/500", "Gray/900", etc.
- Text styles: "Heading/Large", "Body/Medium", etc.
- Effect styles: "Shadow/Large", etc.

### Extracted TypeScript (Output)

```typescript
// src/design-tokens.ts (auto-generated)

/**
 * Design Tokens
 * Auto-generated from Figma - Do not edit manually
 * Last updated: 2025-11-30T12:00:00Z
 */

export const colors = {
  // Primary colors
  'primary-50': '#eff6ff',
  'primary-500': '#3b82f6',
  'primary-600': '#2563eb',
  'primary-900': '#1e3a8a',

  // Gray scale
  'gray-50': '#f9fafb',
  'gray-500': '#6b7280',
  'gray-900': '#111827',

  // Semantic
  'success-500': '#10b981',
  'error-500': '#ef4444',
} as const;

export const typography = {
  'heading-large': {
    fontFamily: 'Inter',
    fontSize: 48,
    fontWeight: 700,
    lineHeight: 60,
    letterSpacing: -2,
  },
  'body-medium': {
    fontFamily: 'Inter',
    fontSize: 16,
    fontWeight: 400,
    lineHeight: 24,
  },
} as const;

export const spacing = {
  '0': 0,
  '4': 16,
  '8': 32,
} as const;

export const shadows = {
  'shadow-large': '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
} as const;

export type ColorToken = keyof typeof colors;
export type TypographyToken = keyof typeof typography;
```

### Usage in Components

```typescript
import { colors, typography } from './design-tokens';

const StyledButton = styled.button`
  background: ${colors['primary-500']};
  font-size: ${typography['body-medium'].fontSize}px;
  font-weight: ${typography['body-medium'].fontWeight};
  line-height: ${typography['body-medium'].lineHeight}px;
`;

// Or with Tailwind config
// tailwind.config.js
import { colors, spacing } from './src/design-tokens';

export default {
  theme: {
    colors,
    spacing,
  },
};
```

## Example 4: Sync Workflow

### Initial Pull

```bash
$ bun run figma:pull

🔄 Starting design sync...
⬇️  Pulling updates from Figma...
   Fetching file: ABC123
   Extracting 24 components
   Extracting design tokens:
   - 45 colors
   - 12 typography styles
   - 16 spacing values
   - 8 border radius values
   - 6 shadow effects
   Pulled 24 updates
💾 Saved metadata to .trace/.meta/designs.yaml
✅ Sync complete: 0 pushed, 24 pulled
```

### Metadata Created

```yaml
# .trace/.meta/designs.yaml
version: '1.0.0'
lastSync: '2025-11-30T12:00:00Z'
figmaFileKey: 'ABC123'

components:
  - name: Button
    componentId: button
    figmaNodeId: '1:234'
    filePath: packages/ui/src/components/Button.tsx
    lastModified: '2025-11-30T11:00:00Z'
    syncStatus: synced

  - name: Card
    componentId: card
    figmaNodeId: '1:567'
    filePath: packages/ui/src/components/Card.tsx
    lastModified: '2025-11-30T11:30:00Z'
    syncStatus: synced

tokens:
  colors:
    primary-500: '#3b82f6'
  # ... more tokens
```

### Push Changes

```bash
# Make changes to Button.tsx
# Then push to Figma

$ bun run figma:push

🔄 Starting design sync...
⬆️  Pushing changes to Figma...
📁 Found 25 component files
🔍 Parsed 25 components
   Generating plugin output
   Generating Storybook stories
   Updated metadata for 25 components
   Pushed 25 components
✅ Plugin output generated
💾 Saved metadata to .trace/.meta/designs.yaml
✅ Sync complete: 25 pushed, 0 pulled
```

### Conflict Detection

```bash
# Button.tsx modified locally
# Button component also updated in Figma

$ bun run figma:conflicts

⚠️  Conflicts detected:
   - Button: Modified locally after last sync with Figma
   - Card: Deleted from Figma
   - Modal: Exists in Figma but not found locally

# Resolve conflicts
$ FIGMA_CONFLICT_RESOLUTION=local bun run figma:sync
# or
$ FIGMA_CONFLICT_RESOLUTION=remote bun run figma:sync
```

## Example 5: CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/figma-sync.yml
name: Sync Figma Designs

on:
  push:
    branches: [main]
    paths:
      - 'frontend/packages/ui/src/components/**'
  schedule:
    - cron: '0 */6 * * *' # Every 6 hours
  workflow_dispatch: # Manual trigger

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Setup Bun
        uses: oven-sh/setup-bun@v1

      - name: Install dependencies
        run: |
          cd frontend
          bun install

      - name: Check for conflicts
        env:
          FIGMA_ACCESS_TOKEN: ${{ secrets.FIGMA_ACCESS_TOKEN }}
          FIGMA_FILE_KEY: ${{ secrets.FIGMA_FILE_KEY }}
        run: |
          cd frontend
          bun run figma:conflicts || echo "Conflicts detected"

      - name: Sync designs
        env:
          FIGMA_ACCESS_TOKEN: ${{ secrets.FIGMA_ACCESS_TOKEN }}
          FIGMA_FILE_KEY: ${{ secrets.FIGMA_FILE_KEY }}
          FIGMA_CONFLICT_RESOLUTION: local
        run: |
          cd frontend
          bun run figma:sync

      - name: Commit changes
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add frontend/.trace/.meta/designs.yaml
          git diff --staged --quiet || git commit -m "chore: sync Figma designs [skip ci]"
          git push
```

### Pre-commit Hook

```bash
#!/bin/sh
# .husky/pre-commit

echo "🔄 Syncing Figma designs..."

cd frontend

# Check for conflicts
if ! bun run figma:conflicts > /dev/null 2>&1; then
  echo "⚠️  Figma sync conflicts detected"
  echo "Run: bun run figma:conflicts"
  exit 1
fi

# Sync
bun run figma:sync

# Add metadata if changed
git add .trace/.meta/designs.yaml

echo "✅ Figma sync complete"
```

## Example 6: Component Library

### Batch Export

```bash
# Export all components to Figma
$ bun run figma:export

🎨 Starting Figma generation...
📁 Found 42 component files
🔍 Parsed 42 components
✅ Plugin output generated
✅ Story to Design output generated
🎉 Generation complete!

# Output structure
.figma-output/
├── manifest.json
├── code.js
├── ui.html
├── figma-plugin.json
├── story-to-design.json
└── stories/
    ├── Button.stories.tsx
    ├── Card.stories.tsx
    ├── Modal.stories.tsx
    ├── Input.stories.tsx
    ├── Select.stories.tsx
    └── ... (42 total)
```

### Import to Figma

```bash
# In Figma:
# 1. Plugins → Development → Import plugin from manifest
# 2. Select .figma-output/manifest.json
# 3. Run "TracerTM Design Sync" plugin
# 4. Click "Import Components"

# Result:
# - 42 components created in Figma
# - Organized by component name
# - Full structure preserved
# - Styles applied from Tailwind classes
```

## Example 7: Design Token Sync

### Full Token Export

```bash
$ bun run figma:export-tokens src/design-tokens.ts

📝 Exported design tokens to src/design-tokens.ts

# Generated file:
// src/design-tokens.ts
export const colors = { ... }
export const typography = { ... }
export const spacing = { ... }
export const borderRadius = { ... }
export const shadows = { ... }
```

### CSS Variables

```bash
$ bun run figma:export-tokens src/design-tokens.css

# Generated file:
/* src/design-tokens.css */
:root {
  --color-primary-50: #eff6ff;
  --color-primary-500: #3b82f6;
  --color-primary-900: #1e3a8a;

  --font-size-sm: 14px;
  --font-size-base: 16px;
  --font-size-lg: 18px;

  --spacing-4: 16px;
  --spacing-8: 32px;

  --radius-sm: 4px;
  --radius-lg: 8px;

  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 20px 25px rgba(0, 0, 0, 0.1);
}
```

## Example 8: story.to.design Integration

### Upload to story.to.design

```bash
$ bun run figma:upload

📤 Uploading to story.to.design...
🎨 Starting Figma generation...
📁 Found 42 component files
🔍 Parsed 42 components
✅ Story to Design output generated
📤 Uploading to https://api.story.to.design/v1/sync
✅ Successfully uploaded to story.to.design

# Result:
# - Storybook stories linked to Figma
# - Design specs visible in Storybook
# - Two-way sync enabled
```

### Storybook Addon

```typescript
// .storybook/main.ts
export default {
  addons: [
    '@storybook/addon-essentials',
    '@storybook/addon-designs', // Enable Figma integration
  ],
  features: {
    storyStoreV7: true,
  },
};

// Stories now show Figma designs:
// [Storybook UI]
//   ┌─────────────────────────────┐
//   │ Button Story                │
//   ├─────────────────────────────┤
//   │ [Canvas]  [Docs]  [Design] │ ← Design tab shows Figma
//   │                             │
//   │  [Primary Button Preview]   │
//   │                             │
//   └─────────────────────────────┘
```

## Example 9: Custom Token Schema

### Override Default Tokens

```typescript
// tools/figma-generator/config.ts
import { loadFigmaConfig } from './config';

const customConfig = loadFigmaConfig();

// Add custom tokens
customConfig.tokens.colors = {
  ...customConfig.tokens.colors,
  'brand-purple': '#8b5cf6',
  'brand-orange': '#f97316',
};

customConfig.tokens.typography = {
  ...customConfig.tokens.typography,
  'mono-sm': {
    fontFamily: 'Fira Code',
    fontSize: 14,
    fontWeight: 400,
    lineHeight: 20,
  },
};
```

## Example 10: Error Handling

### Invalid Token

```bash
$ FIGMA_ACCESS_TOKEN=invalid bun run figma:sync

❌ Sync failed: Access token invalid
Error: Failed to fetch file ABC123: 403 Forbidden

Fix: Generate a new token at https://www.figma.com/settings
```

### Rate Limit

```bash
$ bun run figma:sync

⚠️  Rate limit approaching (95/100 requests)
🔄 Waiting 5 seconds...
✅ Sync complete
```

### File Not Found

```bash
$ FIGMA_FILE_KEY=INVALID bun run figma:sync

❌ Sync failed: File not found
Error: Failed to fetch file INVALID: 404 Not Found

Fix: Check your file key in .env.local
Correct format: https://www.figma.com/file/KEY/...
```

---

These examples demonstrate the complete workflow from React components to Figma and back, with real-world scenarios and error handling.
