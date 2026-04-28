# Design Integration Architecture

## System Overview

The TraceRTM Design CLI provides a complete integration layer between your codebase, Storybook, and Figma. This document describes the architecture, data flow, and integration points.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         TraceRTM Design CLI                         │
│                         (Python + Typer)                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │   init   │  │   link   │  │   sync   │  │ generate │           │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘           │
│       │             │              │             │                  │
│       └─────────────┴──────────────┴─────────────┘                  │
│                        │                                            │
│                        ▼                                            │
│              ┌──────────────────┐                                   │
│              │  Configuration   │                                   │
│              │   Management     │                                   │
│              └────────┬─────────┘                                   │
│                       │                                             │
│         ┌─────────────┴─────────────┐                               │
│         ▼                           ▼                               │
│  ┌─────────────┐           ┌─────────────┐                         │
│  │ designs.yaml│           │components.  │                         │
│  │             │           │    yaml     │                         │
│  └─────────────┘           └─────────────┘                         │
│                                                                      │
└───────────────────────┬──────────────────────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────────┐
        │     TypeScript Integration Layer      │
        │          (To be implemented)          │
        └───────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Figma API  │ │  Storybook   │ │   Component  │
│              │ │   Stories    │ │   Codebase   │
└──────────────┘ └──────────────┘ └──────────────┘
```

## Data Flow

### 1. Initialization Flow (`rtm design init`)

```
User Command
    │
    ▼
┌─────────────────────────┐
│ Prompt for Credentials  │
│ - Figma file key        │
│ - Figma access token    │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Create .trace/.meta/    │
│ - designs.yaml          │
│ - components.yaml       │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Display Success Tree    │
└─────────────────────────┘
```

### 2. Component Linking Flow (`rtm design link`)

```
User Command: rtm design link Button https://figma.com/file/ABC?node-id=1-2
    │
    ▼
┌─────────────────────────┐
│ Validate Figma URL      │
│ - Extract file key      │
│ - Extract node ID       │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Update designs.yaml     │
│ - Add component entry   │
│ - Store Figma metadata  │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Update components.yaml  │
│ - Add/update component  │
│ - Mark as unsynced      │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Display Success Message │
└─────────────────────────┘
```

### 3. Sync Flow (`rtm design sync`)

```
User Command: rtm design sync
    │
    ▼
┌─────────────────────────┐
│ Load Configuration      │
│ - designs.yaml          │
│ - components.yaml       │
└───────────┬─────────────┘
            │
    ┌───────┴───────┐
    ▼               ▼
┌────────┐      ┌────────┐
│  Pull  │      │  Push  │
│ (Figma │      │(Figma) │
│   ↓)   │      │   ↑    │
└────┬───┘      └───┬────┘
     │              │
     └──────┬───────┘
            │
            ▼
┌─────────────────────────┐
│ Call TypeScript Tools   │
│ - bun run figma:pull    │
│ - bun run figma:push    │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Update Metadata         │
│ - Sync timestamps       │
│ - Component status      │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Display Results         │
│ - Progress bars         │
│ - Success/error stats   │
└─────────────────────────┘
```

### 4. Story Generation Flow (`rtm design generate`)

```
User Command: rtm design generate --all --template csf3
    │
    ▼
┌─────────────────────────┐
│ Load components.yaml    │
│ Filter components       │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ For Each Component:     │
│                         │
│  ┌──────────────────┐   │
│  │ Call TypeScript  │   │
│  │ Story Generator  │   │
│  └──────────────────┘   │
│                         │
│  ┌──────────────────┐   │
│  │ Update Registry  │   │
│  │ has_story: true  │   │
│  └──────────────────┘   │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Display Generated Files │
└─────────────────────────┘
```

### 5. Export Flow (`rtm design export`)

```
User Command: rtm design export --all
    │
    ▼
┌─────────────────────────┐
│ Load Configuration      │
│ Filter components       │
│ (must have stories)     │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ For Each Component:     │
│                         │
│  ┌──────────────────┐   │
│  │ Capture Story    │   │
│  │ Screenshots      │   │
│  └──────────────────┘   │
│                         │
│  ┌──────────────────┐   │
│  │ Upload to Figma  │   │
│  │ via API          │   │
│  └──────────────────┘   │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Display Figma Link      │
└─────────────────────────┘
```

## Component Registry Architecture

### designs.yaml Schema

```yaml
# Figma connection configuration
figma:
  file_key: string              # Primary Figma file
  access_token: string          # API authentication
  base_url: string             # API endpoint

# Storybook configuration
storybook:
  stories_path: string         # Glob for story files
  output_dir: string           # Story generation target

# Component-to-design mappings
components:
  ComponentName:
    figma_file_key: string     # Can differ from primary file
    figma_node_id: string      # Specific design node
    figma_url: string          # Full URL for reference
    linked_at: timestamp       # When link was created

# Sync tracking
last_sync: timestamp           # Last successful sync
```

### components.yaml Schema

```yaml
# Component registry
components:
  - name: string               # Component name
    path: string               # File path in codebase
    figma_url: string          # Figma design link
    figma_node_id: string      # Figma node identifier
    has_story: boolean         # Story exists?
    sync_status: enum          # synced | unsynced
    last_synced: timestamp     # Last sync time

# Registry metadata
metadata:
  created_at: timestamp
  last_updated: timestamp
  total_components: integer
```

## Integration Points

### TypeScript Tools (To Be Implemented)

#### 1. Figma Pull Tool (`scripts/figma/pull.ts`)

**Purpose**: Fetch design metadata from Figma API

**Input**:
- Figma file key (from designs.yaml)
- Figma access token
- Component node IDs

**Process**:
1. Authenticate with Figma API
2. Fetch file metadata
3. For each component node:
   - Get node details
   - Extract design tokens
   - Download assets if needed
4. Update local cache

**Output**:
- Design metadata JSON
- Updated component registry
- Downloaded assets

**API Calls**:
```typescript
GET https://api.figma.com/v1/files/:file_key
GET https://api.figma.com/v1/files/:file_key/nodes?ids=:node_ids
GET https://api.figma.com/v1/images/:file_key
```

#### 2. Figma Push Tool (`scripts/figma/push.ts`)

**Purpose**: Push Storybook metadata to Figma

**Input**:
- Storybook story files
- Component metadata
- Figma credentials

**Process**:
1. Parse Storybook stories
2. Extract component variants
3. Generate design tokens
4. Update Figma via API
5. Sync component descriptions

**Output**:
- Updated Figma components
- Sync confirmation
- Error reports

**API Calls**:
```typescript
POST https://api.figma.com/v1/files/:file_key/comments
PUT https://api.figma.com/v1/files/:file_key
```

#### 3. Figma Export Tool (`scripts/figma/export.ts`)

**Purpose**: Export Storybook stories to Figma (story.to.design pattern)

**Input**:
- Component stories
- Storybook URL
- Figma credentials

**Process**:
1. Build Storybook
2. For each story:
   - Navigate to story URL
   - Capture screenshot
   - Resize to Figma frame
3. Upload to Figma:
   - Create frame
   - Import screenshot
   - Add metadata

**Output**:
- Figma components created
- Screenshot cache
- Import report

**Technologies**:
- Puppeteer/Playwright for screenshots
- Figma API for import

#### 4. Storybook Generator (`scripts/storybook/generate.ts`)

**Purpose**: Generate Storybook story files from components

**Input**:
- Component file path
- Template name (default/csf3/mdx)
- Component metadata

**Process**:
1. Parse component file
2. Extract props using TypeScript AST
3. Generate story based on template
4. Write .stories.tsx file
5. Update component registry

**Output**:
- Generated .stories.tsx file
- Updated component metadata

**Templates**:
```typescript
// CSF 2.0
export default { title: 'Components/Button', component: Button }
export const Primary = () => <Button>Click</Button>

// CSF 3.0
export default { component: Button }
export const Primary = { args: { children: 'Click' } }

// MDX
import { Meta, Story } from '@storybook/blocks'
# Button
<Meta component={Button} />
<Story name="Primary">...</Story>
```

## Error Handling Strategy

### Python CLI Layer

1. **Configuration Errors**
   - Missing .trace/ directory → Suggest `rtm init`
   - Missing design config → Suggest `rtm design init`
   - Invalid YAML → Show parse error with line number

2. **Validation Errors**
   - Invalid Figma URL → Show expected format
   - Missing component → Show available components
   - Missing credentials → Prompt for input

3. **Runtime Errors**
   - Network errors → Show offline-friendly message
   - TypeScript tool errors → Display stderr output
   - Permission errors → Check file permissions

### TypeScript Tool Layer

1. **API Errors**
   - Authentication failed → Check token validity
   - Rate limiting → Implement exponential backoff
   - Invalid node ID → Verify Figma URL

2. **Generation Errors**
   - Component parse failed → Show syntax error
   - Template error → Show template validation
   - File write failed → Check permissions

## Security Considerations

### 1. Credential Storage

**Current Approach**:
- Stored in `.trace/.meta/designs.yaml`
- Not gitignored by default
- Plain text storage

**Recommendations**:
1. Add `.trace/.meta/designs.yaml` to `.gitignore`
2. Support environment variables:
   ```bash
   FIGMA_ACCESS_TOKEN=secret rtm design sync
   ```
3. Use system keychain integration (future)

### 2. API Token Security

**Best Practices**:
1. Never commit tokens to git
2. Use read-only tokens when possible
3. Rotate tokens regularly
4. Use project-scoped tokens

**Implementation**:
```python
# Support env var fallback
figma_token = os.getenv('FIGMA_ACCESS_TOKEN') or config.get('figma.access_token')
```

## Performance Optimization

### 1. Caching Strategy

**Local Cache**:
- Design metadata cache (`.trace/.cache/figma/`)
- Component screenshots cache
- API response cache with TTL

**Benefits**:
- Reduced API calls
- Faster sync operations
- Offline capability

### 2. Batch Operations

**Optimization**:
- Batch API requests for multiple components
- Parallel TypeScript tool execution
- Progress tracking for long operations

**Implementation**:
```python
# Use Rich progress bars
with Progress() as progress:
    for component in components:
        process_component(component)
```

## Future Enhancements

### 1. Design Token Support

**Concept**: Import/export design tokens (colors, spacing, typography)

**Flow**:
```
Figma Styles → JSON → CSS Variables → Component Props
```

### 2. Component Variants

**Concept**: Map Figma variants to Storybook args

**Example**:
```typescript
// Figma variants: size (small, medium, large)
// Storybook args:
export default {
  argTypes: {
    size: { options: ['small', 'medium', 'large'] }
  }
}
```

### 3. Visual Regression Testing

**Concept**: Compare Figma designs with Storybook screenshots

**Tools**:
- Chromatic integration
- Percy integration
- Custom diff algorithm

### 4. Auto-detection

**Concept**: Scan codebase for components and auto-link

**Process**:
1. Find all React components
2. Search Figma for matching names
3. Suggest links to user
4. Auto-create with confirmation

## Deployment Considerations

### CI/CD Integration

**Pre-commit Hook**:
```bash
#!/bin/bash
# .git/hooks/pre-commit

rtm design status || exit 1

# Fail if components are unsynced
unsynced=$(rtm design list -s unsynced | wc -l)
if [ $unsynced -gt 0 ]; then
  echo "Error: $unsynced components need sync"
  exit 1
fi
```

**GitHub Actions**:
```yaml
name: Design Sync
on: [push]
jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: rtm design sync -d push
        env:
          FIGMA_ACCESS_TOKEN: ${{ secrets.FIGMA_TOKEN }}
```

### Monitoring

**Metrics to Track**:
- Sync frequency
- Component coverage (% with stories)
- Sync errors
- API usage
- Generation time

**Implementation**:
```python
# Log metrics to file or service
metrics = {
    'sync_duration': duration,
    'components_synced': count,
    'errors': len(errors),
}
```

## Conclusion

This architecture provides a comprehensive foundation for design system integration in TraceRTM. The Python CLI layer handles configuration, validation, and user interaction, while TypeScript tools handle the heavy lifting of Figma API operations and Storybook generation.

The design is extensible, maintainable, and follows TraceRTM patterns while providing clear integration points for future enhancements.

---

**Next Steps**:
1. Implement TypeScript tools
2. Test with real Figma projects
3. Add caching layer
4. Implement security best practices
5. Create CI/CD examples
