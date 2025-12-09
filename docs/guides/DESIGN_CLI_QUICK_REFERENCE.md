# Design CLI - Quick Reference

## Commands

### `rtm design init`
Initialize design integration (creates `.trace/.meta/designs.yaml` and `components.yaml`)

```bash
rtm design init                                    # Interactive
rtm design init -k FILE_KEY -t TOKEN              # With credentials
```

### `rtm design link`
Link a component to a Figma design

```bash
rtm design link Button https://figma.com/file/ABC123?node-id=1-2
rtm design link Card https://figma.com/file/XYZ -c src/components/Card.tsx
```

### `rtm design sync`
Sync designs between Storybook and Figma

```bash
rtm design sync                    # Bidirectional sync
rtm design sync -d push           # Push to Figma
rtm design sync -d pull           # Pull from Figma
rtm design sync --dry-run         # Preview changes
```

### `rtm design generate`
Generate Storybook stories from components

```bash
rtm design generate --all                         # All components
rtm design generate -c Button                    # Specific component
rtm design generate --all -t csf3               # Use CSF3 template
rtm design generate --all -t mdx                # Use MDX template
```

### `rtm design status`
Show design sync status

```bash
rtm design status
```

### `rtm design list`
List all component → design links

```bash
rtm design list                    # All components
rtm design list -s unsynced       # Filter by status
rtm design list --urls            # Show full Figma URLs
```

### `rtm design export`
Export designs to Figma (story.to.design pattern)

```bash
rtm design export --all           # Export all
rtm design export -c Button       # Export specific component
```

## Common Workflows

### First-time Setup
```bash
rtm init                          # Initialize TraceRTM
rtm design init                   # Initialize design integration
```

### Add New Component
```bash
rtm design link NewComponent https://figma.com/file/...
rtm design generate -c NewComponent
rtm design sync
```

### Batch Update All Components
```bash
rtm design generate --all
rtm design sync
rtm design list
```

### Check Sync Status
```bash
rtm design status
rtm design list -s unsynced
```

## File Locations

- **Design config**: `.trace/.meta/designs.yaml`
- **Component registry**: `.trace/.meta/components.yaml`

## Options Reference

| Option | Short | Description | Commands |
|--------|-------|-------------|----------|
| `--figma-key` | `-k` | Figma file key | init |
| `--figma-token` | `-t` | Figma access token | init |
| `--path` | `-p` | Path to .trace/ | all |
| `--component-path` | `-c` | Component file path | link |
| `--direction` | `-d` | Sync direction (push/pull/both) | sync |
| `--dry-run` | - | Preview changes | sync |
| `--component` | `-c` | Specific component | generate, export |
| `--all` | `-a` | All components | generate, export |
| `--template` | `-t` | Story template (default/csf3/mdx) | generate |
| `--status` | `-s` | Filter by status | list |
| `--urls` | `-u` | Show full URLs | list |

## Story Templates

| Template | Description | Use Case |
|----------|-------------|----------|
| `default` | CSF 2.0 stories | Standard components |
| `csf3` | CSF 3.0 stories | Modern Storybook |
| `mdx` | MDX documentation | Components with docs |

## Sync Directions

| Direction | Description | Use Case |
|-----------|-------------|----------|
| `both` | Bidirectional (default) | Full sync |
| `push` | Storybook → Figma | Export stories |
| `pull` | Figma → Storybook | Import designs |

## Sync Status Values

| Status | Description |
|--------|-------------|
| `synced` | Component is in sync |
| `unsynced` | Component needs sync |

## Error Messages

| Error | Solution |
|-------|----------|
| No .trace/ directory found | Run `rtm init` |
| Design integration not initialized | Run `rtm design init` |
| Invalid Figma URL | Check URL format |
| Component not found | Run `rtm design link` first |

## Examples

### Complete New Component Workflow
```bash
# 1. Create component (outside CLI)
# 2. Link to Figma
rtm design link MyComponent https://figma.com/file/ABC?node-id=1-2

# 3. Generate story
rtm design generate -c MyComponent -t csf3

# 4. Sync
rtm design sync

# 5. Verify
rtm design list
```

### Batch Operations
```bash
# Link multiple components
for comp in Button Card Modal; do
  rtm design link $comp https://figma.com/file/ABC?node-id=$id
done

# Generate all stories
rtm design generate --all

# Check status
rtm design status
```

### CI/CD Integration
```bash
# Pre-commit hook
rtm design status || exit 1
rtm design list -s unsynced | wc -l | grep -q "^0$" || exit 1

# Post-deploy
rtm design sync -d push
```

## Tips

1. Use `--dry-run` with sync to preview changes
2. Commit `designs.yaml` and `components.yaml` to git
3. Use environment variables for Figma tokens in CI/CD
4. Run `rtm design status` regularly to check sync health
5. Generate stories before syncing for best results

## Related Commands

- `rtm init` - Initialize TraceRTM project
- `rtm sync` - Sync with remote backend
- `rtm item` - Manage requirements

---

Run any command with `--help` for detailed usage.
