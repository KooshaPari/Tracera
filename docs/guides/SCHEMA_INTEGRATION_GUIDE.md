# Schema Integration Guide: Multi-Dimensional Traceability

## Overview

This guide explains how the new migrations integrate with the existing database schema to implement the multi-dimensional traceability model.

## Full Data Model Topology

### Layer 1: Canonical Concepts (Perspective-Agnostic)

```sql
canonical_concepts (031)
├── id (UUID PK)
├── project_id (FK → projects.id)
├── name (string)
├── slug (string)
├── description (text)
├── domain (string)
├── category (string)
├── tags (JSONB array)
├── embedding (float array) -- pgvector 1536 dimensions
├── confidence (float 0-1)
├── source ('manual' | 'inferred' | 'system')
└── [relationships]:
    ├── parent_concept_id (self-referential FK)
    ├── child_concept_ids (JSONB array)
    └── related_concept_ids (JSONB array)
```

**Purpose:** Abstract entities that exist independently of any perspective
**Example:** "User Authentication" concept exists across Product, Technical, Security views

### Layer 2: View Projections (Perspective-Specific)

```sql
items (existing core table)
├── id (UUID PK)
├── project_id (FK → projects.id)
├── type (string) -- e.g., 'feature', 'service', 'module'
├── title (string)
├── description (text)
├── status (enum)
└── [canonical linkage]:
    ├── canonical_id (FK → canonical_concepts.id) [NEW in plan]
    └── perspective (inferred from item type)

canonical_projections (032) -- Junction table
├── id (UUID PK)
├── canonical_id (FK → canonical_concepts.id)
├── item_id (FK → items.id)
├── perspective (string) -- which view this projection belongs to
├── role ('primary' | 'related' | 'derived')
├── confidence (float 0-1)
├── provenance ('manual' | 'auto')
└── status ('auto' | 'confirmed')
```

**Purpose:** Connect abstract concepts to concrete items in specific perspectives
**Example:**
- `canonical_concepts[auth-concept]` manifests as:
  - `items[login-feature]` in Product perspective (via canonical_projections)
  - `items[auth-service]` in Technical perspective (via canonical_projections)
  - `items[sec-auth-req]` in Security perspective (via canonical_projections)

### Layer 3: Cross-Perspective Linkage (NEW)

```sql
equivalence_links (038) -- Bridges between perspective-specific items
├── id (UUID PK)
├── project_id (FK → projects.id)
├── item_id_1 (FK → items.id)
├── item_id_2 (FK → items.id)
├── perspective_1 (string) -- view context of item_1
├── perspective_2 (string) -- view context of item_2
├── equivalence_type ('same_as' | 'represents' | 'manifests_as')
├── confidence (float 0-1)
├── provenance (
│   'manual' |
│   'naming' |        -- Pattern-based name matching
│   'semantic' |      -- Embedding similarity
│   'api_contract' |  -- Frontend → Backend API mapping
│   'annotation' |    -- @trace-implements comments
│   'canonical'       -- Both linked to same canonical
│ )
├── detection_signals (JSONB array of evidence)
├── status ('auto' | 'confirmed')
├── confirmed_by (UUID user_id, nullable)
└── confirmed_at (timestamp, nullable)
```

**Purpose:** Explicitly represent detected equivalences between items across perspectives
**Example:**
```json
equivalence_links {
  "item_id_1": "login-feature",
  "item_id_2": "auth-service",
  "perspective_1": "product",
  "perspective_2": "technical",
  "equivalence_type": "represents",
  "confidence": 0.95,
  "provenance": "api_contract",
  "detection_signals": [
    { "signal": "naming_match", "score": 0.7 },
    { "signal": "api_contract", "score": 0.95 },
    { "signal": "semantic_similarity", "score": 0.82 }
  ]
}
```

### Layer 4: Code & Documentation Integration

```sql
code_entities (034)
├── id (UUID PK)
├── project_id (FK → projects.id)
├── symbol_name (string) -- e.g., "login()"
├── qualified_name (string) -- e.g., "auth.AuthService.login"
├── symbol_type ('function' | 'class' | 'method' | etc)
├── file_path (text)
├── language ('ts' | 'go' | 'python' | etc)
├── [linking]:
│   ├── linked_item_id (FK → items.id)
│   ├── canonical_id (FK → canonical_concepts.id)
│   └── imports/exports/calls (JSONB arrays)
└── embedding (float array)

doc_entities (033)
├── id (UUID PK)
├── project_id (FK → projects.id)
├── entity_type ('document' | 'section' | 'chunk')
├── source_path (text) -- README.md, docs/api.md, etc
├── [hierarchy]:
│   ├── parent_id (FK → doc_entities.id)
│   ├── path (JSONB array of ancestors)
│   └── heading_level (int 1-6)
├── [linking]:
│   ├── linked_item_ids (JSONB array → items.id)
│   └── code_refs (JSONB array of code symbols)
└── embedding (float array)
```

### Layer 5: Design System Integration

```sql
component_libraries (036)
├── id (UUID PK)
├── project_id (FK → projects.id)
├── name (string) -- "@tracertm/ui"
├── source ('storybook' | 'figma' | 'manual')
├── storybook_url (text)
├── figma_file_key (string)
└── sync_status (string)

library_components (036)
├── id (UUID PK)
├── library_id (FK → component_libraries.id)
├── project_id (FK → projects.id)
├── name (string) -- "Button"
├── category ('primitives' | 'compounds' | etc)
├── [linking]:
│   ├── code_entity_id (FK → code_entities.id)
│   └── storybook_id (string)
├── props (JSONB)
├── variants (JSONB)
└── status ('stable' | 'beta' | 'deprecated')

component_usage (039) -- NEW: Tracks instantiation
├── id (UUID PK)
├── component_id (FK → library_components.id)
├── page_item_id (FK → items.id)
├── file_path (text)
├── line_number (int)
├── [instance data]:
│   ├── props_used (JSONB)
│   ├── variant_used (string)
│   └── usage_context (string)
├── usage_count (int)
└── last_seen_at (timestamp)

design_token_refs (040) -- NEW: Token tracking
├── id (UUID PK)
├── component_id (FK → library_components.id, nullable)
├── item_id (FK → items.id, nullable)
├── token_type ('color' | 'typography' | 'spacing' | etc)
├── token_path (string) -- "colors.primary.500"
├── resolved_value (string) -- "#3b82f6"
├── figma_style_id (string)
└── sync_status (string)

figma_sync_state (041) -- NEW: Design-code sync
├── id (UUID PK)
├── item_id (FK → items.id, nullable)
├── component_id (FK → library_components.id, nullable)
├── file_key (string) -- Figma file
├── node_id (string) -- Figma node
├── [sync tracking]:
│   ├── sync_status ('synced' | 'outdated' | 'conflict')
│   ├── last_synced_at (timestamp)
│   ├── figma_modified_at (timestamp)
│   └── code_modified_at (timestamp)
├── has_conflict (boolean)
└── code_connect_enabled (boolean)
```

### Layer 6: Journey & Flow Analysis

```sql
derived_journeys (042) -- NEW: Flow detection
├── id (UUID PK)
├── project_id (FK → projects.id)
├── name (string)
├── slug (string)
├── journey_type ('user_flow' | 'data_flow' | 'call_chain' | 'process_flow')
├── [sequence]:
│   ├── item_ids (JSONB ordered array)
│   ├── link_ids (JSONB ordered array)
│   ├── item_count (int)
│   └── entry_item_id, exit_item_id (FK → items.id)
├── [detection]:
│   ├── detection_method ('graph_traversal' | 'ast_analysis' | etc)
│   ├── confidence (float 0-1)
│   └── detection_signals (JSONB)
├── [variants]:
│   ├── variants (JSONB array of alternative paths)
│   └── occurrence_count (int)
└── status ('auto' | 'confirmed')
```

## Query Patterns

### Pattern 1: Find All Perspectives of a Concept

```sql
-- All items that manifest the same canonical concept
SELECT
    c.name as concept,
    p.perspective,
    i.title as item_title
FROM canonical_concepts c
JOIN canonical_projections p ON c.id = p.canonical_id
JOIN items i ON p.item_id = i.id
WHERE c.project_id = $project_id
  AND c.slug = 'user-authentication'
ORDER BY p.perspective;
```

**Use Case:** Show all views of "User Authentication" concept

### Pattern 2: Find Equivalent Items Across Perspectives

```sql
-- Items connected via equivalence links
SELECT
    i1.title as product_item,
    i2.title as technical_item,
    el.confidence,
    el.provenance
FROM equivalence_links el
JOIN items i1 ON el.item_id_1 = i1.id
JOIN items i2 ON el.item_id_2 = i2.id
WHERE el.project_id = $project_id
  AND el.equivalence_type = 'represents'
  AND el.confidence > 0.8
ORDER BY el.confidence DESC;
```

**Use Case:** Find high-confidence equivalences for dashboard visualization

### Pattern 3: Track Component Usage Impact

```sql
-- Show all places a component is used
SELECT
    lc.name as component,
    i.title as page,
    cu.file_path,
    cu.line_number,
    cu.props_used,
    cu.usage_count
FROM library_components lc
JOIN component_usage cu ON lc.id = cu.component_id
LEFT JOIN items i ON cu.page_item_id = i.id
WHERE lc.library_id = $library_id
  AND lc.name = 'Button'
ORDER BY cu.usage_count DESC;
```

**Use Case:** Analyze component dependency graph before deprecation

### Pattern 4: Find Design-Code Sync Issues

```sql
-- Show components with sync conflicts
SELECT
    lc.name as component,
    fss.figma_modified_at,
    fss.code_modified_at,
    fss.conflict_details
FROM library_components lc
JOIN figma_sync_state fss ON lc.id = fss.component_id
WHERE fss.project_id = $project_id
  AND fss.has_conflict = true
ORDER BY fss.figma_modified_at DESC;
```

**Use Case:** Show design-code conflicts needing resolution

### Pattern 5: Trace User Journeys

```sql
-- Get a specific user journey with all items
SELECT
    dj.name as journey,
    dj.journey_type,
    dj.confidence,
    ARRAY_AGG(i.title ORDER BY dj.item_ids) as item_sequence
FROM derived_journeys dj
JOIN items i ON i.id = ANY(dj.item_ids::uuid[])
WHERE dj.project_id = $project_id
  AND dj.slug = 'login-flow'
GROUP BY dj.id
LIMIT 1;
```

**Use Case:** Visualize a complete user journey

## Data Flow Scenarios

### Scenario 1: Documenting a Feature

```
Product Manager creates item:
  "Login Feature" (item type: feature)
    ↓ [canonical projection]
    ↓
  Links to canonical_concepts: "User Authentication"
    ↓ [manifests in multiple perspectives]
    ↓
Technical Lead adds:
  "AuthService.login()" (code_entity)
    ↓ [code linking]
    ↓
  Linked to canonical same concept
    ↓ [equivalence detection]
    ↓
System detects equivalence:
  equivalence_link created with
  confidence=0.95, provenance='api_contract'
    ↓ [confirmation]
    ↓
Team reviews & confirms
  status changed to 'confirmed'
```

### Scenario 2: Design System Sync

```
Designer creates component in Figma:
  "Button" (Figma node: xyz123)
    ↓
System creates:
  figma_sync_state record with
  sync_status='unlinked'
    ↓
Developer implements:
  Button component in @tracertm/ui
    ↓
System creates:
  library_components record
    ↓
Developer manually links:
  figma_sync_state.component_id = library_components.id
  sync_status='synced'
    ↓
Component used in pages:
  component_usage records created
    ↓
Tokens referenced:
  design_token_refs created for each token used
```

### Scenario 3: Journey Detection

```
System analyzes item graph:
  "Login Page" → "Auth Form" → "AuthService" → "Database"
    ↓ [graph traversal]
    ↓
Creates derived_journey:
  journey_type='user_flow'
  item_ids=[page, form, service, db]
  confidence=0.85
  detection_method='graph_traversal'
    ↓
Finds variant paths:
  "Login Page" → "Social Auth" → "OAuth Service"
  variants=[...]
    ↓
Team approves journey:
  status='confirmed'
  approved_by=user_id
    ↓
Journey used for:
  - E2E test generation
  - Documentation
  - Impact analysis
```

## Migration Dependencies Graph

```
projects (core)
    ↓
items (core)
    ↓
┌─────────────────────────────────────────┐
│  Foundation: 031-037                     │
│  - canonical_concepts (031)              │
│  - canonical_projections (032)           │
│  - doc_entities (033)                    │
│  - code_entities (034)                   │
│  - perspective_configs (035)             │
│  - component_libraries (036)             │
│  - blockchain_ml_tables (037)            │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  Cross-Perspective: 038                  │
│  - equivalence_links (038)               │
│    ├─ FK: items.id (both)                │
│    └─ Depends on: items in place         │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  Usage Tracking: 039                     │
│  - component_usage (039)                 │
│    ├─ FK: library_components.id (036)    │
│    ├─ FK: items.id                       │
│    ├─ FK: code_entities.id (034)         │
│    └─ Depends on: 038                    │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  Design System: 040                      │
│  - design_token_refs (040)               │
│    ├─ FK: library_components.id (036)    │
│    ├─ FK: items.id                       │
│    └─ Depends on: 039                    │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  Figma Integration: 041                  │
│  - figma_sync_state (041)                │
│    ├─ FK: items.id                       │
│    ├─ FK: library_components.id (036)    │
│    └─ Depends on: 040                    │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  Journey Analysis: 042                   │
│  - derived_journeys (042)                │
│    ├─ FK: items.id (entry/exit)          │
│    ├─ item_ids JSONB array               │
│    └─ Depends on: 041                    │
└─────────────────────────────────────────┘
```

## Indexing Strategy

### Equivalence Links Indexes
- **Primary:** `(item_id_1, item_id_2)` - find specific relationship
- **Lookup:** `(item_id_1, confidence)`, `(item_id_2, confidence)` - top matches
- **Filter:** `(perspective_1)`, `(perspective_2)` - filter by view
- **Analysis:** `(equivalence_type)`, `(provenance)`, `(status)` - understand relationships

### Component Usage Indexes
- **Discovery:** `(component_id, last_seen_at)` - find all usages
- **Location:** `(file_path)` - code search
- **Context:** `(usage_context)` - behavioral analysis
- **Hierarchy:** `(parent_component_id)` - component composition

### Design Tokens Indexes
- **System:** `(project_id, token_type)` - find tokens by type
- **Component:** `(component_id, token_type)` - component design surface
- **Sync:** `(figma_style_id)` - bidirectional Figma sync
- **Tracking:** `(sync_status)` - identify out-of-sync tokens

### Figma Sync State Indexes
- **File:** `(file_key, page_name)` - organization by Figma structure
- **Status:** `(project_id, sync_status)` - find conflicts/outdated
- **Conflict:** `(has_conflict)` - conflict resolution workflow
- **Recent:** `(last_synced_at)` - stale design detection

### Derived Journeys Indexes
- **Type:** `(project_id, journey_type)` - list journeys by type
- **Status:** `(project_id, status)` - approval workflow
- **Arrays:** GIN index on `(item_ids)`, `(perspectives)` - search items in journeys
- **Flow:** `(entry_item_id)`, `(exit_item_id)` - entry/exit analysis

## Next Implementation Steps

1. **Approve & Apply Migrations**
   - Review and run: `alembic upgrade 042_add_derived_journeys`
   - Verify all tables created

2. **Implement RLS Policies**
   - Row-level security for all new tables
   - Ensure users only see project-scoped data

3. **Build Detection Algorithms**
   - Equivalence detection: naming, semantic, API contract, annotation
   - Journey detection: graph traversal, AST analysis
   - Component usage: code parsing and linking

4. **Create tRPC APIs**
   - Query endpoints for each table
   - Mutation endpoints for confirmation/approval
   - Aggregation endpoints for analytics

5. **Build UI Components**
   - Equivalence visualization
   - Journey explorer
   - Component usage matrix
   - Figma sync dashboard
   - Design token browser

6. **Seed Initial Data**
   - Parse existing code for code_entities
   - Analyze existing documentation
   - Extract existing components
   - Run initial equivalence detection

See MIGRATION_SUMMARY.md for detailed table specifications and MIGRATION_CHECKLIST.md for deployment verification steps.
