# Wireframe Integration with Figma

TraceRTM supports wireframes as first-class items with deep Figma integration for design-to-code traceability.

## Overview

Wireframes allow you to:
- Link design artifacts to requirements (stories/epics)
- Track which components are used in designs
- Maintain traceability from design → code
- Auto-sync with Figma using the Figma API

## Wireframe Item Type

Wireframes are stored in `.trace/wireframes/` with the following structure:

### Frontmatter Fields

```yaml
---
id: "uuid"                    # Internal UUID
external_id: "WF-001"         # Human-readable ID
type: wireframe               # Item type
status: approved              # draft, review, approved, implemented
priority: high                # Priority level
owner: "@designer"            # Designer/owner

# Figma integration
figma_url: "https://www.figma.com/file/abc123/Project?node-id=1:42"
figma_file_key: "abc123"      # Extracted from URL
figma_node_id: "1:42"         # Node/frame ID in Figma

# Design metadata
components:                   # UI components used
  - Button
  - InputField
  - Card
screens:                      # Screen names
  - LoginScreen
  - SignupScreen
implements:                   # Stories/epics this design implements
  - STORY-001
  - STORY-002

tags:
  - authentication
  - ui
---
```

### Markdown Body

```markdown
# Login Screen Wireframe

## Description
Wireframe for the user authentication flow...

## Figma Preview
![Figma Preview](figma://abc123/1:42)
[View in Figma](https://www.figma.com/file/abc123/Project?node-id=1:42)

## Components Used
- Button (primary variant)
- InputField (email, password)

## Screens
- LoginScreen
- SignupScreen

## Acceptance Criteria
- [ ] All form fields are properly labeled
- [ ] Error states are clearly visible
- [x] Responsive design for mobile and desktop

## Notes
Design follows Material Design guidelines...
```

## Link Types

Wireframes support the following traceability links:

### wireframe_for
**Wireframe → Story/Epic**

Links a wireframe to the requirements it implements.

```bash
rtm link wireframe WF-001 --story STORY-001
```

Stored in `.trace/.meta/links.yaml`:
```yaml
- source: WF-001
  target: STORY-001
  type: wireframe_for
  created: 2024-01-15T10:30:00Z
```

### designed_by
**Component → Wireframe**

Links a component (in code) to the wireframe that designed it.

```bash
rtm link component Button --wireframe WF-001
```

### implemented_in
**Wireframe → Code file**

Links a wireframe to the code files that implement it.

```bash
rtm link wireframe WF-001 --file src/components/LoginForm.tsx
```

## CLI Commands

### Create Wireframe

```bash
# Basic creation
rtm create wireframe "Login Screen"

# With Figma URL
rtm create wireframe "Login Screen" \
  --figma-url "https://www.figma.com/file/abc123/Project?node-id=1:42"

# Full creation with metadata
rtm create wireframe "Login Screen" \
  --figma-url "https://www.figma.com/file/abc123/Project?node-id=1:42" \
  --components "Button,InputField,Card" \
  --screens "LoginScreen,SignupScreen" \
  --owner "@designer" \
  --status draft
```

The CLI automatically extracts:
- `figma_file_key` from the URL
- `figma_node_id` from the `node-id` parameter

### Link Wireframe to Story

```bash
# Link to single story
rtm link wireframe WF-001 --story STORY-001

# Link to multiple stories
rtm link wireframe WF-001 --stories STORY-001,STORY-002

# Link to epic
rtm link wireframe WF-001 --epic EPIC-001
```

### List Wireframes

```bash
# List all wireframes
rtm list --type wireframe

# Filter by status
rtm list --type wireframe --status approved

# Show wireframes for a story
rtm list wireframes --for-story STORY-001
```

### Sync with Figma

```bash
# Fetch latest from Figma (requires FIGMA_ACCESS_TOKEN)
rtm figma sync WF-001

# Update wireframe metadata from Figma
rtm figma update WF-001

# Export Figma frame as image
rtm figma export WF-001 --format png
```

## Figma Integration

### Setup

1. Get a Figma access token from https://www.figma.com/developers/api#access-tokens
2. Set the environment variable:
   ```bash
   export FIGMA_ACCESS_TOKEN="your-token-here"
   ```
3. Enable Figma integration in `.trace/project.yaml`:
   ```yaml
   figma:
     team_id: "your-team-id"
     access_token_env: "FIGMA_ACCESS_TOKEN"
     auto_sync: true
   ```

### Auto-sync

When `auto_sync: true`, TraceRTM will:
- Poll Figma API for changes to watched files
- Update wireframe metadata when designs change
- Create new wireframes when new frames are added
- Notify team when designs are updated

### Figma URL Format

TraceRTM supports the standard Figma URL format:

```
https://www.figma.com/file/{file_key}/{file_name}?node-id={node_id}
```

Example:
```
https://www.figma.com/file/abc123xyz/MyProject?node-id=1:42
                         ^^^^^^^^^ file_key    ^^^^ node_id
```

### Figma Image Protocol

Wireframes can embed Figma previews using the custom protocol:

```markdown
![Preview](figma://abc123xyz/1:42)
```

When rendered in the TUI/Desktop app, this fetches the image from Figma's API and displays it inline.

## Traceability Matrix

Wireframes appear in the traceability matrix:

```
Epic-001: User Authentication
├── Story-001: Login Page
│   ├── WF-001: Login Screen Wireframe (wireframe_for)
│   │   ├── src/components/LoginForm.tsx (implemented_in)
│   │   └── src/components/Button.tsx (designed_by)
│   └── TEST-001: Login Form Tests (tested_by)
└── Story-002: Signup Page
    └── WF-001: Login Screen Wireframe (wireframe_for)
```

## Workflow Example

### 1. Designer creates wireframe in Figma
- Create frame in Figma: "Login Screen"
- Get the Figma URL with node-id

### 2. Create wireframe in TraceRTM
```bash
rtm create wireframe "Login Screen Wireframe" \
  --figma-url "https://www.figma.com/file/abc123/App?node-id=1:42" \
  --components "Button,InputField,Card,Logo" \
  --screens "LoginScreen,SignupScreen" \
  --owner "@designer" \
  --status draft
```

### 3. Link to requirements
```bash
rtm link wireframe WF-001 --story STORY-001
rtm link wireframe WF-001 --story STORY-002
```

### 4. Review and approve
```bash
rtm update WF-001 --status review
# After team review
rtm update WF-001 --status approved
```

### 5. Developer implements design
```bash
# Create implementation
touch src/components/LoginForm.tsx

# Link implementation to wireframe
rtm link wireframe WF-001 --file src/components/LoginForm.tsx
```

### 6. Mark as implemented
```bash
rtm update WF-001 --status implemented
```

## Project Structure

```
.trace/
├── project.yaml              # Wireframe counter: WF-002
├── epics/
│   └── EPIC-001.md
├── stories/
│   ├── STORY-001.md
│   └── STORY-002.md
├── wireframes/               # ← New directory
│   ├── WF-001.md            # Login Screen Wireframe
│   └── WF-002.md            # Dashboard Wireframe
├── tests/
│   └── TEST-001.md
└── .meta/
    ├── links.yaml           # Includes wireframe_for links
    └── config.yaml
```

## Benefits

1. **Design-Code Traceability**: Direct links from requirements → design → code
2. **Figma Integration**: Auto-sync with Figma for up-to-date designs
3. **Component Tracking**: Know which components are designed and implemented
4. **Version Control**: Wireframes are git-versioned with the code
5. **Team Visibility**: Designers and developers share the same source of truth

## Future Enhancements

- **Auto-import**: Automatically create wireframes from Figma file structure
- **Design tokens**: Extract design tokens (colors, spacing) from Figma
- **Code generation**: Generate component scaffolding from wireframes
- **Visual diff**: Show design changes between versions
- **Component library sync**: Sync Figma components with code component library
