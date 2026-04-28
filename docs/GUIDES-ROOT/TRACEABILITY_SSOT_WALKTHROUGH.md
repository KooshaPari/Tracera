# Traceability & Single Source of Truth (SSOT) Features Walkthrough

## Overview

TraceRTM provides comprehensive traceability and Single Source of Truth (SSOT) capabilities through a multi-view architecture where items can exist in different views (FEATURE, CODE, TEST, API, etc.) but maintain a single authoritative record. This document walks through all traceability and SSOT features in the product model.

---

## 1. Multi-View System (Core SSOT Foundation)

### Concept
The **multi-view system** is the foundation of SSOT in TraceRTM. Each item has a `view` field that categorizes it, but all items share the same underlying data model and are stored in a single `items` table. This ensures:
- **Single Source of Truth**: One item = one record, regardless of view
- **Cross-View Traceability**: Items in different views can be linked
- **Unified Querying**: All items queryable from one place

### Supported Views
- `FEATURE`: Features, epics, and user stories
- `CODE`: Code files, classes, and functions
- `WIREFRAME`: UI screens, components, and buttons
- `API`: API endpoints and services
- `TEST`: Test suites and test cases
- `DATABASE`: Database tables, schemas, and queries
- `ROADMAP`: Future plans and milestones
- `PROGRESS`: Progress tracking and metrics

### Commands

#### View Management
```bash
# List all available views
rtm view list

# Switch to a specific view (sets current_view in config)
rtm view switch FEATURE

# Show current view
rtm view current

# Show statistics for all views
rtm view stats
```

#### Creating Items in Different Views
```bash
# Create a feature
rtm create epic "User Authentication" --view FEATURE

# Create a code item
rtm create file "auth.py" --view CODE --type file

# Create a test
rtm create test "test_auth.py" --view TEST --type test_case

# Create an API endpoint
rtm create endpoint "/api/auth/login" --view API --type endpoint
```

### How It Provides SSOT
- **Single Database Table**: All items stored in `items` table regardless of view
- **Unified ID System**: Each item has a unique UUID that works across all views
- **Consistent Schema**: Same fields (title, description, status, priority, owner, metadata) for all views
- **Cross-View Queries**: Can query items across views or filter by view
- **View-Agnostic Operations**: Create, update, delete, link work the same for all views

---

## 2. Linking System (Traceability)

### Concept
The **linking system** creates typed relationships between items, enabling traceability across views and within views. Links are bidirectional (though typed) and support various relationship types.

### Link Types
- `implements`: Feature → Code (e.g., "Login feature" implements "auth.py")
- `tests`: Test → Code/Feature (e.g., "test_auth.py" tests "auth.py")
- `designs`: Wireframe → Feature (e.g., "Login screen" designs "Login feature")
- `depends_on`: Item → Item (dependency relationship)
- `blocks`: Item → Item (blocking relationship)
- `related_to`: Item → Item (general relationship)
- `parent_of` / `child_of`: Hierarchical relationships
- `tested_by` / `implemented_by`: Reverse relationships
- `decomposes_to` / `decomposed_from`: Decomposition relationships (MVP)

### Commands

#### Create Links
```bash
# Link a feature to code that implements it
rtm link create FEATURE-001 CODE-001 --type implements

# Link a test to code it tests
rtm link create TEST-001 CODE-001 --type tests

# Link a wireframe to a feature it designs
rtm link create WIREFRAME-001 FEATURE-001 --type designs

# Link with metadata
rtm link create FEATURE-001 CODE-001 --type implements --metadata '{"priority": "high"}'
```

#### List All Links
```bash
# List all links in project
rtm link list

# List links filtered by type
rtm link list --type implements
```

#### Show Links for an Item
```bash
# Show all links for an item (incoming and outgoing)
rtm link show ITEM-001

# Show links filtered by target view
rtm link show ITEM-001 --view CODE
```

#### Delete Links
```bash
# Delete a specific link
rtm link delete LINK-001
```

### How It Provides Traceability
- **Cross-View Links**: Connect items across different views (e.g., FEATURE → CODE → TEST)
- **Bidirectional Navigation**: Can traverse links in both directions
- **Typed Relationships**: Link types provide semantic meaning
- **Metadata Support**: Links can carry additional context
- **Query Support**: Can query all links for an item, filter by type/view

---

## 3. Hierarchical Structure (Parent-Child Relationships)

### Concept
Items can have **parent-child relationships** through the `parent_id` field, creating hierarchical structures within and across views.

### Commands

#### Create Hierarchical Items
```bash
# Create a parent item
rtm create epic "User Management" --view FEATURE

# Create a child item (using parent_id)
rtm create story "User Login" --view FEATURE --parent-id EPIC-001

# Or update to set parent
rtm item update STORY-001 --parent-id EPIC-001
```

#### Drill-Down Navigation
```bash
# Drill down into an item's hierarchy (shows tree structure)
rtm drill ITEM-001

# Drill with custom depth
rtm drill ITEM-001 --depth 5

# Drill with view filter
rtm drill ITEM-001 --view FEATURE
```

### How It Provides Traceability
- **Hierarchical Navigation**: Understand item decomposition
- **Tree Visualization**: Visual representation of parent-child relationships
- **Cross-View Hierarchies**: Parent in one view, children in another
- **Depth Control**: Navigate to specific levels

---

## 4. Event Sourcing & History (SSOT Audit Trail)

### Concept
**Event sourcing** records all state changes as events, providing a complete audit trail and enabling history reconstruction. Every create, update, delete, and link operation generates an event.

### Event Model
- `event_type`: Type of event (item_created, item_updated, item_deleted, link_created, etc.)
- `entity_type`: Type of entity (item, link, project)
- `entity_id`: ID of the affected entity
- `agent_id`: Optional agent that made the change
- `data`: JSON payload with event details
- `created_at`: Timestamp of the event

### Commands

#### View History
```bash
# Show history for an item
rtm history ITEM-001

# Show history with limit
rtm history ITEM-001 --limit 50
```

#### View Version Information
```bash
# Show specific version of an item
rtm history version ITEM-001 --version 3
```

### How It Provides SSOT
- **Complete Audit Trail**: Every change is recorded
- **History Reconstruction**: Can see how an item evolved over time
- **Version Tracking**: Optimistic locking with version numbers
- **Agent Attribution**: Track who/what made changes
- **Temporal Queries**: Query events by time range

---

## 5. Versioning & Optimistic Locking

### Concept
**Optimistic locking** prevents concurrent modification conflicts. Each item has a `version` field that increments on every update. If two users try to update the same item simultaneously, the second update fails if the version has changed.

### How It Works
- Each item starts at `version: 1`
- On update, version increments: `version: 2, 3, 4...`
- Update operations check version matches before applying
- If version mismatch, raises `ConcurrencyError`

### Commands
```bash
# View current version (shown in item details)
rtm show ITEM-001

# View version history
rtm history ITEM-001
```

### How It Provides SSOT
- **Conflict Prevention**: Prevents lost updates
- **Version Tracking**: Know which version you're working with
- **Consistency**: Ensures updates are based on latest state
- **History Integration**: Versions correlate with event history

---

## 6. Traceability Matrix (Cross-View Analysis)

### Concept
The **traceability matrix** analyzes relationships between two views, showing coverage and gaps. For example, "Which features are implemented by which code files?" or "Which tests cover which features?"

### Service Implementation
Located in `src/tracertm/services/traceability_service.py`:

```python
async def generate_matrix(
    project_id: str,
    source_view: str,
    target_view: str,
) -> TraceabilityMatrix:
    """
    Generate traceability matrix between two views.
    
    Returns:
        - links: All links between source and target views
        - coverage_percentage: % of source items that have links
        - gaps: Source items without links to target view
    """
```

### Matrix Output
- **Links**: All relationships between source and target views
- **Coverage Percentage**: % of source items that have links to target view
- **Gaps**: Source items without any links to target view

### Use Cases
- **Requirements Coverage**: FEATURE → CODE (which features are implemented?)
- **Test Coverage**: TEST → CODE (which code is tested?)
- **Design Coverage**: WIREFRAME → FEATURE (which features are designed?)
- **API Coverage**: API → CODE (which endpoints are implemented?)

### How It Provides Traceability
- **Coverage Analysis**: Identify missing links
- **Gap Detection**: Find untraced items
- **Cross-View Mapping**: Visualize relationships between views
- **Completeness Metrics**: Measure traceability completeness

---

## 7. Impact Analysis

### Concept
**Impact analysis** determines what items are affected when an item changes, both directly (immediately linked) and indirectly (linked through other items).

### Service Implementation
Located in `src/tracertm/services/traceability_service.py`:

```python
async def analyze_impact(
    item_id: str,
    max_depth: int = 2,
) -> ImpactAnalysis:
    """
    Analyze impact of changing an item.
    
    Returns:
        - directly_affected: Items immediately linked
        - indirectly_affected: Items linked through other items (recursive)
        - total_impact_count: Total number of affected items
    """
```

### How It Works
1. **Direct Impact**: Find all items linked from the changed item
2. **Indirect Impact**: Recursively find items linked from directly affected items (up to `max_depth`)
3. **Aggregation**: Combine and deduplicate affected items

### Use Cases
- **Change Impact**: "If I change this feature, what code/tests are affected?"
- **Risk Assessment**: "How many items will be impacted by this change?"
- **Planning**: "What do I need to update if I change this?"

### How It Provides Traceability
- **Downstream Analysis**: Understand what depends on an item
- **Change Propagation**: See how changes ripple through the system
- **Risk Management**: Identify high-impact changes
- **Dependency Visualization**: Map dependency chains

---

## 8. Drill-Down Navigation

### Concept
**Drill-down** provides hierarchical navigation through parent-child relationships, showing a tree structure of items.

### Commands
```bash
# Drill down into an item (default depth: 3)
rtm drill ITEM-001

# Drill with custom depth
rtm drill ITEM-001 --depth 5

# Drill with view filter
rtm drill ITEM-001 --view FEATURE
```

### Output Format
```
Drill-down: User Management
Depth: 3, View: FEATURE

User Management (abc12345) - in_progress
├── User Login (def67890) - done
│   ├── Login Form (ghi11111) - done
│   └── Auth Service (jkl22222) - in_progress
└── User Registration (mno33333) - todo
```

### How It Provides Traceability
- **Hierarchical Visualization**: See item decomposition
- **Depth Control**: Navigate to specific levels
- **View Filtering**: Focus on specific views
- **Status Overview**: See status at each level

---

## 9. Search & Filtering (Cross-View Queries)

### Concept
**Search** allows querying items across all views or within specific views, enabling traceability through discovery.

### Commands
```bash
# Search across all views
rtm search "authentication"

# Search in specific view
rtm search "login" --view FEATURE

# Search with status filter
rtm search "user" --status in_progress

# Search with type filter
rtm search "api" --type endpoint
```

### How It Provides Traceability
- **Cross-View Discovery**: Find related items across views
- **Semantic Search**: Find items by content, not just ID
- **Filtered Queries**: Narrow down to specific views/types/statuses
- **Relationship Discovery**: Find items that might need linking

---

## 10. State Overview (Multi-View Dashboard)

### Concept
**State** provides a comprehensive overview of project state across all views, showing counts, statuses, and distributions.

### Commands
```bash
# Show overall project state
rtm state

# Show state for specific view
rtm state --view FEATURE

# Show state for specific status
rtm state --status in_progress
```

### Output Includes
- **View Statistics**: Item counts per view
- **Status Distribution**: Item counts per status
- **Type Distribution**: Item counts per type
- **Priority Distribution**: Item counts per priority

### How It Provides SSOT
- **Unified Dashboard**: Single view of entire project
- **Cross-View Metrics**: Compare states across views
- **Gap Identification**: See which views/statuses are underpopulated
- **Progress Tracking**: Monitor project health

---

## 11. Export & Import (SSOT Portability)

### Concept
**Export/Import** allows maintaining SSOT across systems by exporting complete project data (items, links, metadata) and importing it elsewhere.

### Export Formats
- **JSON**: Complete project structure with all relationships
- **CSV**: Tabular format for spreadsheet analysis
- **Markdown**: Human-readable documentation format

### Commands

#### Export
```bash
# Export to JSON (default)
rtm export --output project.json

# Export to CSV
rtm export --format csv --output project.csv

# Export to Markdown
rtm export --format markdown --output project.md
```

#### Export Contents
- **Project Metadata**: Name, description, timestamps
- **All Items**: Complete item data including view, type, status, priority, owner, metadata
- **All Links**: Source, target, type, metadata
- **Relationships**: Preserves all traceability links

### How It Provides SSOT
- **Data Portability**: Move SSOT to other systems
- **Backup & Restore**: Maintain SSOT across backups
- **Integration**: Import into other tools while preserving relationships
- **Documentation**: Generate human-readable traceability docs

---

## 12. Ingestion (SSOT from External Sources)

### Concept
**Stateless ingestion** imports items and links from external sources (Markdown, MDX, YAML, OpenAPI, BMad) while maintaining SSOT by creating items in the unified database.

### Supported Formats
- **Markdown/MDX**: Parse frontmatter and content
- **YAML**: Structured data import
- **OpenAPI**: API specification import
- **BMad**: Business Model and Design format with traceability links

### Commands
```bash
# Ingest Markdown file
rtm ingest markdown requirements.md

# Ingest YAML file
rtm ingest yaml features.yaml

# Ingest OpenAPI spec
rtm ingest openapi api-spec.yaml

# Ingest BMad format (with traceability)
rtm ingest bmad design.bmad
```

### How It Provides SSOT
- **Unified Import**: External sources → TraceRTM database
- **Link Preservation**: Maintains relationships from source formats
- **View Assignment**: Automatically assigns items to appropriate views
- **Metadata Preservation**: Keeps source metadata in `item_metadata`

---

## 13. Project Isolation (SSOT Scope)

### Concept
**Projects** provide isolation boundaries, ensuring each project maintains its own SSOT. Items, links, and events are scoped to projects.

### Commands
```bash
# Create a project
rtm project create "My Project"

# List projects
rtm project list

# Switch to a project
rtm project switch "My Project"

# Show current project
rtm project current
```

### How It Provides SSOT
- **Scope Isolation**: Each project is a separate SSOT
- **Multi-Project Support**: Work with multiple projects without conflicts
- **Project-Scoped Queries**: All operations respect project boundaries
- **Independent State**: Each project has its own items, links, events

---

## 14. Metadata & Extensibility

### Concept
**Metadata fields** (`item_metadata`, `link_metadata`, `project_metadata`) allow extending the data model without schema changes, maintaining SSOT while supporting custom attributes.

### Metadata Usage
- **Item Metadata**: Custom fields per item (e.g., tags, custom attributes)
- **Link Metadata**: Additional context for links (e.g., priority, notes)
- **Project Metadata**: Project-level configuration and custom data

### Commands
```bash
# Create item with metadata
rtm create epic "Feature" --metadata '{"tags": ["auth", "security"], "jira_id": "PROJ-123"}'

# Update item metadata
rtm item update ITEM-001 --metadata '{"priority": "high"}'

# Create link with metadata
rtm link create ITEM-001 ITEM-002 --type implements --metadata '{"verified": true}'
```

### How It Provides SSOT
- **Extensibility**: Add custom fields without breaking SSOT
- **Integration Data**: Store external system IDs (Jira, GitHub, etc.)
- **Rich Context**: Additional information without schema changes
- **Backward Compatibility**: Existing items work with new metadata

---

## 15. Soft Deletes (SSOT Preservation)

### Concept
**Soft deletes** mark items as deleted (`deleted_at` timestamp) without removing them from the database, preserving SSOT and history.

### How It Works
- Items are never physically deleted
- `deleted_at` field marks deletion time
- Queries filter out soft-deleted items by default
- History and links are preserved

### Commands
```bash
# Delete an item (soft delete)
rtm item delete ITEM-001

# List items (excludes soft-deleted by default)
rtm list

# History still shows deleted items
rtm history ITEM-001
```

### How It Provides SSOT
- **Data Preservation**: Never lose traceability data
- **Audit Trail**: Deletion is recorded in history
- **Recovery**: Can restore deleted items if needed
- **Link Preservation**: Links to deleted items remain valid

---

## Summary: How Traceability & SSOT Work Together

### Traceability Features
1. **Linking System**: Typed relationships between items
2. **Hierarchical Structure**: Parent-child relationships
3. **Traceability Matrix**: Cross-view coverage analysis
4. **Impact Analysis**: Change propagation analysis
5. **Drill-Down**: Hierarchical navigation
6. **Search**: Cross-view discovery
7. **History**: Event-based audit trail

### SSOT Features
1. **Multi-View System**: Single database, multiple views
2. **Unified Schema**: Same fields for all items
3. **Project Isolation**: Scoped SSOT per project
4. **Versioning**: Optimistic locking and version tracking
5. **Event Sourcing**: Complete audit trail
6. **Export/Import**: SSOT portability
7. **Ingestion**: External source → SSOT
8. **Soft Deletes**: Data preservation
9. **Metadata**: Extensibility without breaking SSOT

### Integration
- **Items in different views** are linked through the **linking system**
- **History and versioning** provide **SSOT audit trail**
- **Traceability matrix** analyzes **cross-view relationships**
- **Impact analysis** uses **links** to determine **change propagation**
- **Export/Import** maintains **SSOT** across systems
- **Ingestion** brings external data into **SSOT**

---

## Example: End-to-End Traceability Flow

### Scenario: Feature → Code → Test Traceability

1. **Create Feature** (FEATURE view):
   ```bash
   rtm create epic "User Authentication" --view FEATURE
   # Creates: FEATURE-001
   ```

2. **Create Code** (CODE view):
   ```bash
   rtm create file "auth.py" --view CODE --type file
   # Creates: CODE-001
   ```

3. **Create Test** (TEST view):
   ```bash
   rtm create test "test_auth.py" --view TEST --type test_case
   # Creates: TEST-001
   ```

4. **Link Feature → Code**:
   ```bash
   rtm link create FEATURE-001 CODE-001 --type implements
   ```

5. **Link Test → Code**:
   ```bash
   rtm link create TEST-001 CODE-001 --type tests
   ```

6. **View Traceability**:
   ```bash
   # See all links for feature
   rtm link show FEATURE-001
   # Shows: FEATURE-001 → [implements] → CODE-001
   
   # See all links for code
   rtm link show CODE-001
   # Shows: 
   #   FEATURE-001 → [implements] → CODE-001 (incoming)
   #   CODE-001 → [tests] → TEST-001 (outgoing)
   
   # Generate traceability matrix
   # FEATURE → CODE: 100% coverage (FEATURE-001 linked to CODE-001)
   # CODE → TEST: 100% coverage (CODE-001 linked to TEST-001)
   ```

7. **Impact Analysis**:
   ```bash
   # If FEATURE-001 changes, what's affected?
   # Direct: CODE-001 (implements link)
   # Indirect: TEST-001 (tests CODE-001)
   ```

8. **History**:
   ```bash
   rtm history FEATURE-001
   # Shows: created, updated, linked events
   ```

9. **Export**:
   ```bash
   rtm export --output traceability.json
   # Exports: All items, links, preserving traceability
   ```

---

## Conclusion

TraceRTM's traceability and SSOT features work together to provide:
- **Single Source of Truth**: One database, unified schema, multi-view support
- **Complete Traceability**: Links, hierarchies, matrices, impact analysis
- **Audit Trail**: Event sourcing, versioning, history
- **Portability**: Export/import, ingestion
- **Extensibility**: Metadata, soft deletes, project isolation

All features are accessible through the CLI and work together to maintain traceability while preserving SSOT principles.
