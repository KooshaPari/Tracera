# Quick Start Guide - Figma Design Generator

Get started with TracerTM Figma design sync in 5 minutes.

## Prerequisites

- Figma account with API access
- TracerTM frontend project setup
- Bun package manager installed

## Step 1: Get Figma Credentials

### Personal Access Token

1. Go to [Figma Account Settings](https://www.figma.com/settings)
2. Scroll to **Personal Access Tokens**
3. Click **Generate new token**
4. Name it "TracerTM Design Sync"
5. Copy the token (starts with `figd_`)

### File Key

1. Open your design file in Figma
2. Copy the file key from the URL:
   ```
   https://www.figma.com/file/ABC123XYZ/Design-System
                            ^^^^^^^^^ <- This is your file key
   ```

## Step 2: Configure Environment

Create `.env.local` in the `frontend` directory:

```bash
cd frontend
cp .env.figma.example .env.local
```

Edit `.env.local` and add your credentials:

```bash
FIGMA_ACCESS_TOKEN=figd_your_token_here
FIGMA_FILE_KEY=your_file_key_here
```

## Step 3: Install Dependencies

```bash
bun install
```

This installs:

- `figma-api` - Figma REST API client
- `yaml` - YAML parser for metadata
- `glob` - File pattern matching
- `typescript` - TypeScript support

## Step 4: Run Your First Sync

### Pull Design Tokens

Extract colors, typography, and spacing from Figma:

```bash
bun run figma:pull
```

This creates:

- `.trace/.meta/designs.yaml` - Sync metadata with tokens
- Design tokens imported from your Figma file

### Export to TypeScript

Generate a TypeScript file with your design tokens:

```bash
bun run figma:export-tokens src/design-tokens.ts
```

Now you can use tokens in your code:

```typescript
import { colors, typography } from './design-tokens';

const Button = styled.button`
  background: ${colors['primary-500']};
  font-size: ${typography['text-md'].fontSize}px;
`;
```

### Generate Figma Plugin

Create a Figma plugin from your React components:

```bash
bun run figma:export
```

This generates:

- `.figma-output/manifest.json` - Plugin manifest
- `.figma-output/code.js` - Plugin logic
- `.figma-output/ui.html` - Plugin UI
- `.figma-output/figma-plugin.json` - Component data

### Import Plugin to Figma

1. Open Figma
2. Go to `Plugins → Development → Import plugin from manifest`
3. Select `.figma-output/manifest.json`
4. Run the plugin to import your components

## Step 5: Sync Both Ways

### Push Local Changes

After updating components locally:

```bash
bun run figma:push
```

### Pull Figma Updates

After making changes in Figma:

```bash
bun run figma:pull
```

### Two-Way Sync

Do both at once:

```bash
bun run figma:sync
```

## Common Tasks

### Check for Conflicts

Before syncing, check if there are conflicts:

```bash
bun run figma:conflicts
```

If conflicts exist, resolve them manually or use:

```bash
# Keep local changes
FIGMA_CONFLICT_RESOLUTION=local bun run figma:sync

# Keep Figma changes
FIGMA_CONFLICT_RESOLUTION=remote bun run figma:sync
```

### Export Specific Component

Edit `config.ts` to target specific components:

```typescript
components: {
  paths: [
    'packages/ui/src/components/Button.tsx',
    'packages/ui/src/components/Card.tsx',
  ],
}
```

Then run:

```bash
bun run figma:export
```

### Auto-Generate Storybook Stories

Generate stories with Figma links:

```bash
bun run figma:export
```

Stories are created in `.figma-output/stories/`:

```typescript
// .figma-output/stories/Button.stories.tsx
import { Button } from '@tracertm/ui';

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

## Workflow Integration

### Git Hooks

Add pre-commit hook to sync on commit:

```bash
# .husky/pre-commit
#!/bin/sh
bun run figma:sync
git add .trace/.meta/designs.yaml
```

### GitHub Actions

Auto-sync on push:

```yaml
# .github/workflows/figma-sync.yml
name: Sync Figma Designs

on:
  push:
    branches: [main]

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: oven-sh/setup-bun@v1
      - run: bun install
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

### VS Code Tasks

Add to `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Figma: Sync",
      "type": "shell",
      "command": "bun run figma:sync",
      "group": "build",
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Figma: Export",
      "type": "shell",
      "command": "bun run figma:export",
      "group": "build"
    }
  ]
}
```

Now use `Cmd+Shift+P` → `Tasks: Run Task` → `Figma: Sync`

## Troubleshooting

### "Access token invalid"

Your token may have expired. Generate a new one:

1. Go to Figma Account Settings
2. Delete old token
3. Generate new token
4. Update `.env.local`

### "File not found"

Check your file key is correct:

1. Open file in Figma
2. Copy URL
3. Extract key: `https://www.figma.com/file/KEY/...`
4. Update `FIGMA_FILE_KEY` in `.env.local`

### "Rate limit exceeded"

You're making too many API calls. Adjust rate limit:

```bash
# .env.local
FIGMA_RATE_LIMIT_REQUESTS=50
FIGMA_RATE_LIMIT_MS=60000
```

### Components not found

Make sure your component paths are correct in `config.ts`:

```typescript
components: {
  paths: [
    'packages/ui/src/components/**/*.tsx',  // ✓ Correct
    'packages/ui/components/**/*.tsx',       // ✗ Wrong path
  ],
}
```

## Next Steps

- [Full Documentation](./README.md)
- [Configuration Guide](./config.ts)
- [API Reference](./index.ts)
- [Type Definitions](./types.ts)

## Support

For issues or questions:

1. Check [README.md](./README.md) for detailed docs
2. Review [types.ts](./types.ts) for API types
3. Examine [config.ts](./config.ts) for configuration options

## Example Project Structure

After setup, you should have:

```
frontend/
├── .env.local                          # Your credentials (gitignored)
├── .env.figma.example                  # Template
├── package.json                        # Updated with figma:* scripts
├── tools/
│   └── figma-generator/
│       ├── README.md                   # Full docs
│       ├── QUICK_START.md             # This file
│       ├── config.ts                   # Configuration
│       ├── figma-api-client.ts        # API wrapper
│       ├── code-to-design.ts          # Converter
│       ├── generate-figma.ts          # Generator
│       ├── sync-designs.ts            # Sync tool
│       ├── types.ts                    # Type definitions
│       └── index.ts                    # Main exports
├── .figma-output/                      # Generated files (gitignored)
│   ├── manifest.json
│   ├── code.js
│   ├── ui.html
│   ├── figma-plugin.json
│   └── stories/
│       └── *.stories.tsx
└── .trace/.meta/
    └── designs.yaml                    # Sync metadata (committed)
```

Happy designing! 🎨
