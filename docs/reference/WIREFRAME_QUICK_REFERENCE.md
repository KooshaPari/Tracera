# Wireframe Quick Reference

Quick reference for working with wireframes in TraceRTM.

## Create Wireframe File

### Manual Creation

Create `.trace/wireframes/WF-XXX.md`:

```yaml
---
id: "uuid"
external_id: "WF-001"
type: wireframe
status: draft                # draft, review, approved, implemented
priority: high
owner: "@designer"
created: 2024-01-15T10:30:00Z
updated: 2024-01-15T10:30:00Z
version: 1

# Figma integration
figma_url: "https://www.figma.com/file/abc123/Project?node-id=1:42"
figma_file_key: "abc123"
figma_node_id: "1:42"

# Design metadata
components:
  - Button
  - InputField
screens:
  - LoginScreen
implements:
  - STORY-001

tags:
  - ui
  - authentication
---

# Wireframe Title

## Description
Description of the wireframe...

## Figma Preview
![Preview](figma://abc123/1:42)
[View in Figma](https://www.figma.com/file/abc123/Project?node-id=1:42)

## Components Used
- Button (primary variant)
- InputField (email type)

## Screens
- LoginScreen

## Notes
Design notes...
```

### Using Python API

```python
from pathlib import Path
from datetime import datetime
from tracertm.storage.markdown_parser import ItemData, write_item_markdown

# Create wireframe
wireframe = ItemData(
    id="550e8400-e29b-41d4-a716-446655440001",
    external_id="WF-001",
    item_type="wireframe",
    status="draft",
    priority="high",
    owner="@designer",
    created=datetime.now(),
    updated=datetime.now(),

    # Figma fields
    figma_url="https://www.figma.com/file/abc123/Project?node-id=1:42",
    figma_file_key="abc123",
    figma_node_id="1:42",

    # Design metadata
    components=["Button", "InputField"],
    screens=["LoginScreen", "SignupScreen"],
    implements=["STORY-001", "STORY-002"],

    # Content
    title="Login Screen Wireframe",
    description="Wireframe for user authentication flow",
    tags=["authentication", "ui"],
)

# Write to file
write_item_markdown(wireframe, Path(".trace/wireframes/WF-001.md"))
```

## Parse Wireframe File

```python
from pathlib import Path
from tracertm.storage.markdown_parser import parse_item_markdown

# Read wireframe
wireframe = parse_item_markdown(Path(".trace/wireframes/WF-001.md"))

# Access fields
print(wireframe.title)           # "Login Screen Wireframe"
print(wireframe.figma_file_key)  # "abc123"
print(wireframe.components)      # ["Button", "InputField"]
print(wireframe.implements)      # ["STORY-001", "STORY-002"]
```

## Parse Figma URLs

```python
from tracertm.utils.figma import parse_figma_url, build_figma_url

# Parse URL
url = "https://www.figma.com/file/abc123/MyProject?node-id=1:42"
meta = parse_figma_url(url)

print(meta.file_key)      # "abc123"
print(meta.node_id)       # "1:42"
print(meta.file_name)     # "MyProject"
print(meta.api_file_url)  # "https://api.figma.com/v1/files/abc123"

# Build URL
url = build_figma_url(
    file_key="abc123",
    file_name="MyProject",
    node_id="1:42"
)
# Returns: "https://www.figma.com/file/abc123/MyProject?node-id=1:42"
```

## Validate Figma Metadata

```python
from tracertm.utils.figma import validate_figma_metadata

metadata = {
    "figma_url": "https://www.figma.com/file/abc123/Project?node-id=1:42",
    "figma_file_key": "abc123",
    "figma_node_id": "1:42",
}

errors = validate_figma_metadata(metadata)
if errors:
    for error in errors:
        print(f"Validation error: {error}")
else:
    print("All metadata is valid!")
```

## Link Types

### wireframe_for
Wireframe implements a story/epic:

```yaml
# .trace/.meta/links.yaml
- id: "link-uuid"
  source: WF-001
  target: STORY-001
  type: wireframe_for
  created: 2024-01-15T10:30:00Z
```

### designed_by
Component is designed by a wireframe:

```yaml
- id: "link-uuid"
  source: Button
  target: WF-001
  type: designed_by
  created: 2024-01-15T10:30:00Z
```

### implemented_in
Wireframe is implemented in code:

```yaml
- id: "link-uuid"
  source: WF-001
  target: src/components/LoginForm.tsx
  type: implemented_in
  created: 2024-01-15T10:30:00Z
```

## Status Workflow

```
draft → review → approved → implemented
```

## Figma URL Formats

Supported URL formats:

```
# Standard format
https://www.figma.com/file/{file_key}/{file_name}?node-id={node_id}

# Design format (newer)
https://www.figma.com/design/{file_key}/{file_name}?node-id={node_id}

# Without https://
figma.com/file/{file_key}/{file_name}

# Without node-id
https://www.figma.com/file/{file_key}/{file_name}
```

Example:
```
https://www.figma.com/file/abc123xyz/MyProject?node-id=1:42
                         ^^^^^^^^^ file_key    ^^^^ node_id
```

## Figma Protocol

Embed Figma previews in markdown:

```markdown
![Preview](figma://abc123/1:42)
```

Convert to standard URLs:

```python
from tracertm.utils.figma import convert_figma_protocol_to_url

text = "![Preview](figma://abc123/1:42)"
converted = convert_figma_protocol_to_url(text)
# Returns: "![Preview](https://www.figma.com/file/abc123?node-id=1:42)"
```

## Project Configuration

Add to `.trace/project.yaml`:

```yaml
# Counters
counters:
  wireframe: 0  # Next: WF-001

# Figma integration (optional)
figma:
  team_id: "your-team-id"
  access_token_env: "FIGMA_ACCESS_TOKEN"
  auto_sync: false
  watch_files:
    - "abc123"  # File keys to watch
```

## Common Patterns

### Design Handoff
```python
# 1. Designer creates wireframe
wireframe = ItemData(
    external_id="WF-001",
    item_type="wireframe",
    status="review",
    figma_url="...",
    implements=["STORY-001"],
    # ... other fields
)

# 2. Team reviews, designer updates to approved
wireframe.status = "approved"
wireframe.version += 1

# 3. Developer implements, links code
# (Add link: WF-001 → src/components/LoginForm.tsx)

# 4. Mark as implemented
wireframe.status = "implemented"
```

### Component Tracking
```python
# Track all wireframes using a component
from tracertm.storage.markdown_parser import list_items, parse_item_markdown

wireframes = list_items(Path(".trace"), "my-project", "wireframe")
for path in wireframes:
    item = parse_item_markdown(path)
    if "Button" in item.components:
        print(f"{item.external_id}: {item.title}")
```

### Figma Sync (Future)
```python
# Pseudo-code for future Figma API integration
from tracertm.integrations.figma import FigmaClient

client = FigmaClient(token=os.getenv("FIGMA_ACCESS_TOKEN"))

# Fetch latest from Figma
figma_data = client.get_file(wireframe.figma_file_key)
node_data = client.get_node(wireframe.figma_file_key, wireframe.figma_node_id)

# Update wireframe metadata
wireframe.components = extract_components(node_data)
wireframe.updated = datetime.now()
```

## Testing

```python
# Test wireframe parsing
from tracertm.storage.markdown_parser import parse_item_markdown, write_item_markdown

# Write
wireframe = ItemData(
    id="test-uuid",
    external_id="WF-TEST",
    item_type="wireframe",
    status="draft",
    figma_url="https://figma.com/file/abc/test?node-id=1:1",
    figma_file_key="abc",
    figma_node_id="1:1",
)
write_item_markdown(wireframe, Path("test.md"))

# Read
parsed = parse_item_markdown(Path("test.md"))
assert parsed.figma_file_key == "abc"
assert parsed.figma_node_id == "1:1"
```

## Directory Structure

```
.trace/
├── project.yaml              # Add wireframe counter
├── wireframes/               # Wireframe storage
│   ├── WF-001.md
│   ├── WF-002.md
│   └── WF-003.md
└── .meta/
    └── links.yaml           # wireframe_for, designed_by, implemented_in
```

## Quick Commands (Future CLI)

```bash
# Create wireframe
rtm create wireframe "Login Screen" \
  --figma-url "https://figma.com/file/abc/Project?node-id=1:42" \
  --components "Button,InputField" \
  --status draft

# Link to story
rtm link wireframe WF-001 --story STORY-001

# Update status
rtm update WF-001 --status approved

# List wireframes
rtm list --type wireframe --status approved

# Sync with Figma
rtm figma sync WF-001
```
