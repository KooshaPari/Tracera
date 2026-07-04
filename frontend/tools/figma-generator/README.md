# Figma Design Generator

Automated bidirectional sync between TracerTM React components and Figma designs.

## Features

- **Code → Figma**: Generate Figma components from React code
- **Figma → Code**: Extract design tokens from Figma
- **Bidirectional Sync**: Keep designs and code in sync
- **Multiple Outputs**: Figma plugin format and story.to.design integration
- **Design Tokens**: Automated extraction and code generation
- **Storybook Integration**: Auto-generate stories with Figma links

## Quick Start

### 1. Setup

Create a `.env.local` file in the frontend root:

```bash
# Get your access token from https://www.figma.com/developers/api
FIGMA_ACCESS_TOKEN=your_token_here

# Get file key from Figma URL: https://www.figma.com/file/ABC123/...
FIGMA_FILE_KEY=ABC123
```

### 2. Install Dependencies

```bash
cd frontend
bun install figma-api typescript yaml glob
```

### 3. Run Commands

```bash
# Full bidirectional sync
bun run figma:sync

# Only push changes to Figma
bun run figma:sync push

# Only pull from Figma
bun run figma:sync pull

# Export components to Figma plugin format
bun run figma:export

# Export design tokens to TypeScript
bun run figma:export-tokens

# Detect conflicts
bun run figma:conflicts
```

## Architecture

### Files

```
tools/figma-generator/
├── config.ts              # Configuration and tokens
├── figma-api-client.ts    # Figma API wrapper
├── code-to-design.ts      # React → Figma converter
├── generate-figma.ts      # Main generator
├── sync-designs.ts        # Bidirectional sync
└── README.md              # This file
```

### Data Flow

```
┌─────────────────┐
│ React Components│
│  (*.tsx files)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Component Parser│
│  (TypeScript)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│ Tailwind → Figma│◄─────┤ Design Tokens│
│   Converter     │      └──────────────┘
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Figma Client   │◄────► Figma API
│   (REST API)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ .figma-output/  │
│ - plugin format │
│ - stories       │
│ - metadata      │
└─────────────────┘
```

## Usage Examples

### Generate Figma Plugin

```bash
bun run figma:export
```

This creates:

- `.figma-output/figma-plugin.json` - Component data
- `.figma-output/manifest.json` - Plugin manifest
- `.figma-output/code.js` - Plugin logic
- `.figma-output/ui.html` - Plugin UI

Load in Figma: `Plugins → Development → Import plugin from manifest`

### Sync with Figma

```bash
# Two-way sync
bun run figma:sync

# Push local changes only
bun run figma:sync push

# Pull Figma updates only
bun run figma:sync pull
```

Creates/updates:

- `.trace/.meta/designs.yaml` - Sync metadata
- `.figma-output/stories/*.stories.tsx` - Storybook stories

### Export Design Tokens

```bash
bun run figma:export-tokens src/design-tokens.ts
```

Generates TypeScript file with:

```typescript
export const colors = {
  'primary-500': '#3b82f6',
  // ... all colors from Figma
} as const;

export const typography = {
  'text-lg': {
    fontFamily: 'Inter',
    fontSize: 18,
    fontWeight: 400,
    lineHeight: 28,
  },
  // ... all text styles
} as const;
```

### Detect Conflicts

```bash
bun run figma:conflicts
```

Reports:

- Components modified locally after last sync
- Components deleted from Figma
- Components only in Figma (not in code)

## Configuration

### Environment Variables

```bash
# Required
FIGMA_ACCESS_TOKEN=figd_...
FIGMA_FILE_KEY=ABC123

# Optional
STORY_TO_DESIGN_URL=https://api.story.to.design/v1/sync
STORY_TO_DESIGN_ENABLED=true
FIGMA_OUTPUT_DIR=.figma-output
FIGMA_OUTPUT_FORMAT=both  # plugin | story-to-design | both
FIGMA_AUTO_SYNC=false
FIGMA_CONFLICT_RESOLUTION=manual  # local | remote | manual
```

### Component Paths

Edit `config.ts` to customize component discovery:

```typescript
components: {
  paths: [
    'packages/ui/src/components/**/*.tsx',
    'apps/web/src/components/**/*.tsx',
  ],
  exclude: [
    '**/node_modules/**',
    '**/*.test.tsx',
  ],
}
```

### Design Tokens

Customize default tokens in `config.ts`:

```typescript
tokens: {
  colors: {
    'primary-500': '#3b82f6',
    // ... your colors
  },
  spacing: {
    '4': 16,
    // ... your spacing
  },
  // ...
}
```

## Tailwind → Figma Mapping

The converter automatically maps Tailwind classes to Figma properties:

| Tailwind      | Figma                    |
| ------------- | ------------------------ |
| `bg-blue-500` | Fill color               |
| `p-4`         | Padding: 16px all        |
| `px-4`        | Padding: 16px left/right |
| `gap-4`       | Item spacing: 16px       |
| `rounded-lg`  | Corner radius: 12px      |
| `flex`        | Auto layout: horizontal  |
| `flex-col`    | Auto layout: vertical    |
| `text-lg`     | Typography: large        |
| `font-bold`   | Font weight: 700         |
| `shadow-md`   | Drop shadow effect       |

## Figma Plugin Usage

1. **Generate plugin**:

   ```bash
   bun run figma:export
   ```

2. **Import to Figma**:
   - Open Figma
   - Go to `Plugins → Development → Import plugin from manifest`
   - Select `.figma-output/manifest.json`

3. **Use plugin**:
   - Run plugin from Figma
   - Click "Import Components"
   - Components appear as Figma components

## story.to.design Integration

### Setup

1. Configure URL in `.env.local`:

   ```bash
   STORY_TO_DESIGN_URL=https://api.story.to.design/v1/sync
   STORY_TO_DESIGN_ENABLED=true
   ```

2. Generate and upload:
   ```bash
   bun run figma:sync upload
   ```

### Storybook Integration

Generated stories include Figma links:

```typescript
export default {
  title: 'Components/Button',
  component: Button,
  parameters: {
    design: {
      type: 'figma',
      url: 'https://www.figma.com/file/ABC123/...',
    },
  },
};
```

Install addon in Storybook:

```bash
bun add -d @storybook/addon-designs
```

## Metadata Format

`.trace/.meta/designs.yaml` structure:

```yaml
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

tokens:
  colors:
    primary-500: '#3b82f6'
  typography:
    text-lg:
      fontFamily: Inter
      fontSize: 18
      fontWeight: 400
      lineHeight: 28
```

## Troubleshooting

### "Access token required"

Set `FIGMA_ACCESS_TOKEN` in `.env.local`. Get token from:
https://www.figma.com/developers/api#authentication

### "File key required"

Set `FIGMA_FILE_KEY` in `.env.local`. Extract from Figma URL:
`https://www.figma.com/file/ABC123/...` → key is `ABC123`

### "Rate limit exceeded"

Adjust rate limiting in `.env.local`:

```bash
FIGMA_RATE_LIMIT_REQUESTS=50
FIGMA_RATE_LIMIT_MS=60000
```

### Conflicts detected

Use conflict resolution:

```bash
# Keep local changes
FIGMA_CONFLICT_RESOLUTION=local bun run figma:sync

# Keep Figma changes
FIGMA_CONFLICT_RESOLUTION=remote bun run figma:sync

# Manually review (default)
FIGMA_CONFLICT_RESOLUTION=manual bun run figma:conflicts
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Sync Figma Designs

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 0 * * *' # Daily at midnight

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: oven-sh/setup-bun@v1
      - name: Install dependencies
        run: bun install
      - name: Sync designs
        env:
          FIGMA_ACCESS_TOKEN: ${{ secrets.FIGMA_ACCESS_TOKEN }}
          FIGMA_FILE_KEY: ${{ secrets.FIGMA_FILE_KEY }}
        run: bun run figma:sync
      - name: Commit changes
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add .trace/.meta/designs.yaml
          git commit -m "chore: sync Figma designs" || true
          git push
```

## API Reference

### FigmaClient

```typescript
import { createFigmaClient } from './figma-api-client';

const client = createFigmaClient({
  personalAccessToken: 'your_token',
});

// Get file data
const file = await client.getFile('file_key');

// Get components
const components = await client.getComponents('file_key');

// Export images
const images = await client.exportImages('file_key', ['node_id_1']);

// Get design tokens
const variables = await client.getVariables('file_key');
```

### FigmaGenerator

```typescript
import { FigmaGenerator } from './generate-figma';

const generator = new FigmaGenerator({
  componentPaths: ['src/**/*.tsx'],
  outputDir: '.figma-output',
  outputFormat: 'both',
});

await generator.generate();
```

### DesignSync

```typescript
import { DesignSync } from './sync-designs';

const sync = new DesignSync({
  figmaAccessToken: 'token',
  figmaFileKey: 'key',
  componentPaths: ['src/**/*.tsx'],
  metaFilePath: '.trace/.meta/designs.yaml',
  outputDir: '.figma-output',
});

// Two-way sync
await sync.sync('both');

// Detect conflicts
const conflicts = await sync.detectConflicts();

// Export tokens
await sync.exportTokens('src/tokens.ts');
```

## License

Part of the TracerTM project. See main LICENSE file.
