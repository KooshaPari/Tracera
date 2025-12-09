# TraceRTM Design CLI - Complete Guide

Complete guide to using TraceRTM's design integration commands for managing Storybook and Figma workflows.

## Overview

The `rtm design` commands provide a complete integration layer between your codebase, Storybook stories, and Figma designs. This enables:

- **Component Registry**: Track all UI components in `.trace/.meta/components.yaml`
- **Figma Linking**: Map components to Figma design nodes
- **Story Generation**: Auto-generate Storybook stories from components
- **Bidirectional Sync**: Keep Storybook and Figma in sync
- **Design Export**: Export Storybook stories to Figma

## Prerequisites

1. TraceRTM project initialized (`rtm init`)
2. Figma account with API access
3. Figma file key (from your Figma URL)
4. Figma access token ([get one here](https://www.figma.com/developers/api#access-tokens))

## Quick Start

### 1. Initialize Design Integration

```bash
# Interactive initialization (prompts for credentials)
rtm design init

# Or provide credentials directly
rtm design init \
  --figma-key YOUR_FIGMA_FILE_KEY \
  --figma-token YOUR_FIGMA_ACCESS_TOKEN
```

**What it creates:**
- `.trace/.meta/designs.yaml` - Figma configuration
- `.trace/.meta/components.yaml` - Component registry

### 2. Link Components to Figma

```bash
# Link a component to a Figma design
rtm design link Button https://www.figma.com/file/ABC123/Design-System?node-id=1-2

# Link with explicit component path
rtm design link Card \
  https://www.figma.com/file/XYZ789/Components \
  --component-path src/components/Card/Card.tsx
```

**What it does:**
- Validates Figma URL format
- Extracts file key and node ID
- Updates `designs.yaml` and `components.yaml`
- Marks component as linked but unsynced

### 3. View Design Status

```bash
# Show overall design sync status
rtm design status
```

**Output:**
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
│           Design Status                      │
├──────────────────────────────────────────────┤
│ Figma file:       ABC123XYZ789               │
│ Last sync:        2025-11-30 14:30           │
│ Total components: 15                         │
│ Synced:           12                         │
│ Unsynced:         3                          │
│ With stories:     10                         │
└──────────────────────────────────────────────┘
```

### 4. List All Component Links

```bash
# List all linked components
rtm design list

# Filter by sync status
rtm design list --status unsynced

# Show full Figma URLs
rtm design list --urls
```

**Output:**
```
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
│ Component │ Path                   │ Story │ Status  │ Last Synced    │
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ Button    │ src/components/Button  │ ✓     │ Synced  │ 2025-11-30     │
│ Card      │ src/components/Card    │ ✓     │ Synced  │ 2025-11-30     │
│ Modal     │ src/components/Modal   │ ✗     │ Unsynced│ Never          │
└───────────┴────────────────────────┴───────┴─────────┴────────────────┘
```

### 5. Generate Storybook Stories

```bash
# Generate stories for all components
rtm design generate --all

# Generate for specific component
rtm design generate --component Button

# Use CSF3 template
rtm design generate --all --template csf3

# Use MDX template with documentation
rtm design generate --all --template mdx
```

**What it does:**
- Creates `.stories.tsx` files for each component
- Uses specified template (CSF 2.0, CSF 3.0, or MDX)
- Updates `components.yaml` to mark components as having stories

### 6. Sync Designs

```bash
# Full bidirectional sync
rtm design sync

# Push stories to Figma
rtm design sync --direction push

# Pull designs from Figma
rtm design sync --direction pull

# Preview changes without making them
rtm design sync --dry-run
```

**What it does:**
- **Pull**: Fetches design metadata from Figma API
- **Push**: Exports Storybook stories to Figma
- **Both**: Bidirectional sync (default)
- Updates sync timestamps in metadata

### 7. Export to Figma

```bash
# Export all components to Figma
rtm design export --all

# Export specific component
rtm design export --component Button
```

**What it does:**
- Uses story.to.design pattern
- Generates screenshots from Storybook
- Imports screenshots into Figma
- Creates Figma components from stories

## File Structure

After initialization, your `.trace/.meta/` directory will contain:

```
.trace/
└── .meta/
    ├── designs.yaml      # Figma configuration
    └── components.yaml   # Component registry
```

### designs.yaml

```yaml
figma:
  file_key: "ABC123XYZ789"
  access_token: "secret_token_here"
  base_url: "https://api.figma.com/v1"

storybook:
  stories_path: "src/components/**/*.stories.{ts,tsx,js,jsx}"
  output_dir: "src/components"

components:
  Button:
    figma_file_key: "ABC123XYZ789"
    figma_node_id: "1:2"
    figma_url: "https://www.figma.com/file/ABC123/...?node-id=1-2"
    linked_at: "2025-11-30T14:30:00"

  Card:
    figma_file_key: "ABC123XYZ789"
    figma_node_id: "3:4"
    figma_url: "https://www.figma.com/file/ABC123/...?node-id=3-4"
    linked_at: "2025-11-30T14:35:00"

last_sync: "2025-11-30T15:00:00"
```

### components.yaml

```yaml
components:
  - name: Button
    path: src/components/Button
    figma_url: "https://www.figma.com/file/ABC123/...?node-id=1-2"
    figma_node_id: "1:2"
    has_story: true
    sync_status: synced
    last_synced: "2025-11-30T15:00:00"

  - name: Card
    path: src/components/Card
    figma_url: "https://www.figma.com/file/ABC123/...?node-id=3-4"
    figma_node_id: "3:4"
    has_story: true
    sync_status: synced
    last_synced: "2025-11-30T15:00:00"

  - name: Modal
    path: src/components/Modal
    figma_url: "https://www.figma.com/file/ABC123/...?node-id=5-6"
    figma_node_id: "5:6"
    has_story: false
    sync_status: unsynced
    last_synced: null

metadata:
  created_at: "2025-11-30T14:00:00"
  last_updated: "2025-11-30T15:00:00"
  total_components: 3
```

## Complete Workflow Example

Here's a complete workflow for a new design system component:

```bash
# 1. Initialize design integration (first time only)
rtm design init

# 2. Create a new component (outside TraceRTM)
# File: src/components/Badge/Badge.tsx

# 3. Link component to Figma design
rtm design link Badge \
  https://www.figma.com/file/ABC123/Design-System?node-id=10-20 \
  --component-path src/components/Badge/Badge.tsx

# 4. Generate Storybook story
rtm design generate --component Badge --template csf3

# 5. Check status
rtm design status

# 6. Sync with Figma
rtm design sync

# 7. View all linked components
rtm design list

# 8. Export to Figma (if needed)
rtm design export --component Badge
```

## Advanced Usage

### Batch Linking Components

```bash
# Link multiple components in a script
for component in Button Card Modal Badge Alert; do
  rtm design link $component https://www.figma.com/file/ABC123/Design?node-id=$node_id
done
```

### Filtering and Querying

```bash
# Show only components that need stories
rtm design list | grep "✗"

# Show only unsynced components
rtm design list --status unsynced

# Export only synced components
rtm design export --all  # Will skip components without stories
```

### Integration with CI/CD

```bash
#!/bin/bash
# .github/workflows/design-sync.yml

# Check design sync status
rtm design status

# Fail if components are unsynced
unsynced=$(rtm design list --status unsynced | wc -l)
if [ $unsynced -gt 0 ]; then
  echo "Error: $unsynced components need to be synced"
  exit 1
fi

# Generate missing stories
rtm design generate --all

# Sync with Figma
rtm design sync --direction push
```

## TypeScript Integration Points

The CLI commands call TypeScript tools for actual sync operations. Here's what needs to be implemented:

### Required npm Scripts

Add these to your `package.json`:

```json
{
  "scripts": {
    "figma:pull": "bun run scripts/figma/pull.ts",
    "figma:push": "bun run scripts/figma/push.ts",
    "figma:export": "bun run scripts/figma/export.ts",
    "storybook:generate": "bun run scripts/storybook/generate.ts"
  }
}
```

### Required TypeScript Tools

1. **scripts/figma/pull.ts** - Fetch design metadata from Figma API
2. **scripts/figma/push.ts** - Push Storybook stories to Figma
3. **scripts/figma/export.ts** - Export stories using story.to.design
4. **scripts/storybook/generate.ts** - Generate Storybook stories from templates

See [FIGMA_SYNC_TOOLS.md](./FIGMA_SYNC_TOOLS.md) for implementation details.

## Troubleshooting

### Error: No .trace/ directory found

```bash
# Initialize TraceRTM first
rtm init
```

### Error: Design integration not initialized

```bash
# Initialize design integration
rtm design init
```

### Error: Invalid Figma URL

Make sure your Figma URL follows this format:
```
https://www.figma.com/file/FILE_KEY/Design-Name?node-id=NODE_ID
```

### Error: Component not found

```bash
# Check registered components
rtm design list

# Link the component first
rtm design link MyComponent https://figma.com/file/...
```

## Best Practices

1. **Version Control**: Commit both `designs.yaml` and `components.yaml` to git
2. **Secrets**: Consider using environment variables for Figma tokens
3. **Sync Frequently**: Run `rtm design sync` regularly to keep designs in sync
4. **Story Generation**: Use templates consistently across your component library
5. **Documentation**: Use MDX template for components that need extensive docs

## Related Commands

- `rtm init` - Initialize TraceRTM project
- `rtm project` - Manage projects
- `rtm item` - Manage requirements/items
- `rtm sync` - Sync with remote TraceRTM backend

## API Reference

All commands support `--path` option to specify a custom `.trace/` directory location.

### Command Summary

| Command | Purpose | Required Args | Optional Args |
|---------|---------|---------------|---------------|
| `init` | Initialize design integration | - | `--figma-key`, `--figma-token`, `--path` |
| `link` | Link component to Figma | `component`, `figma_url` | `--component-path`, `--path` |
| `sync` | Sync designs | - | `--direction`, `--dry-run`, `--path` |
| `generate` | Generate stories | - | `--component`, `--all`, `--template`, `--path` |
| `status` | Show sync status | - | `--path` |
| `list` | List component links | - | `--status`, `--urls`, `--path` |
| `export` | Export to Figma | - | `--component`, `--all`, `--path` |

## Next Steps

1. Set up TypeScript sync tools (see [FIGMA_SYNC_TOOLS.md](./FIGMA_SYNC_TOOLS.md))
2. Configure Storybook in your project
3. Create story templates for your design system
4. Set up CI/CD integration for automatic syncs
5. Document your component library in Storybook

---

**Need help?** Run any command with `--help` for detailed usage information.
