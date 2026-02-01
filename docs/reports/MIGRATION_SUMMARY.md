# Multi-Dimensional Traceability Database Migrations

## Overview

This document summarizes the database migrations created to implement the multi-dimensional traceability model as defined in the eventual-toasting-eich plan.

## Migration Chain

All migrations build on top of the existing schema and form a sequential chain:

```
036_add_component_libraries
    ↓
037_add_blockchain_ml_tables (existing blockchain/ML tables)
    ↓
038_add_equivalence_links (NEW - cross-perspective equivalences)
    ↓
039_add_component_usage (NEW - component usage tracking)
    ↓
040_add_design_token_refs (NEW - design token tracking)
    ↓
041_add_figma_sync_state (NEW - Figma integration)
    ↓
042_add_derived_journeys (NEW - journey detection)
```

## New Migrations

### 1. Migration 038: equivalence_links

**Purpose:** Store detected and manually-created equivalences between items across different perspectives.

**Table:** `equivalence_links`

**Key Columns:**
- `id` - UUID primary key
- `project_id` - Project reference
- `item_id_1, item_id_2` - Links two items
- `perspective_1, perspective_2` - Perspective context of each item
- `equivalence_type` - Type of equivalence: `same_as`, `represents`, `manifests_as`
- `confidence` - Float 0-1 indicating how confident the equivalence is
- `provenance` - Source of equivalence: `manual`, `naming`, `semantic`, `api_contract`, `annotation`, `canonical`
- `detection_signals` - JSONB array of signals that led to detection (for debugging)
- `status` - `auto` or `confirmed`
- `confirmed_by, confirmed_at` - User confirmation tracking

**Indexes:**
- Single-column: project, items, perspectives, type, provenance, status, confidence
- Composite: `(item_id_1, confidence)`, `(item_id_2, confidence)` for efficient queries

**Use Cases:**
- Find all equivalences for a given item
- Discover cross-perspective links by confidence threshold
- Track manual approvals of auto-detected equivalences
- Analyze detection patterns across the system

### 2. Migration 039: component_usage

**Purpose:** Track where library components are used throughout the application.

**Table:** `component_usage`

**Key Columns:**
- `id` - UUID primary key
- `project_id` - Project reference
- `component_id` - Reference to `library_components`
- `page_item_id` - Item ID of the page using the component
- `file_path` - Source file path
- `line_number, column_number` - Location in file
- `usage_context` - Context where used (e.g., `form-field`, `navigation`)
- `parent_component_id` - If nested in another component
- `props_used` - JSONB object of props passed
- `variant_used` - Which variant of the component
- `code_entity_id` - Linked code entity
- `usage_count` - Frequency tracking
- `last_seen_at` - For staleness detection

**Indexes:**
- Single-column: project, component, page, file_path, usage_context, code_entity
- Composite: `(component_id, last_seen_at)` for frequency queries

**Use Cases:**
- Find all usages of a component
- Component usage analytics and metrics
- Deprecation impact analysis
- Code-component traceability

### 3. Migration 040: design_token_refs

**Purpose:** Link components and items to design system tokens (colors, typography, spacing, etc.).

**Table:** `design_token_refs`

**Key Columns:**
- `id` - UUID primary key
- `project_id` - Project reference
- `component_id` - Component using the token (nullable)
- `item_id` - Item using the token (nullable)
- `token_type` - Type: `color`, `typography`, `spacing`, `shadow`, `border`, `motion`
- `token_path` - Hierarchical path (e.g., `colors.primary.500`)
- `token_name` - Display name
- `resolved_value` - Actual value (e.g., `#3b82f6`, `16px`)
- `resolved_value_type` - Value unit: `hex`, `rgb`, `px`, `rem`, etc.
- `figma_style_id` - Link to Figma style
- `usage_property` - CSS property name (e.g., `backgroundColor`)
- `sync_status` - Sync state with Figma
- `last_synced_at` - Last sync timestamp

**Indexes:**
- Single-column: project, component, item, token_type, token_path, figma_style_id
- Composite: `(project_id, token_type)`, `(component_id, token_type)`

**Use Cases:**
- Find all components using a specific token
- Token change impact analysis
- Design system compliance checking
- Figma ↔ code synchronization

### 4. Migration 041: figma_sync_state

**Purpose:** Track synchronization status between Figma designs and code/UI items.

**Table:** `figma_sync_state`

**Key Columns:**
- `id` - UUID primary key
- `project_id` - Project reference
- `item_id` - UI item (nullable)
- `component_id` - Component (nullable)
- `file_key` - Figma file identifier
- `page_name` - Page in Figma
- `node_id` - Specific Figma node
- `node_name, node_type` - Figma node metadata
- `figma_url` - Direct link to node
- `sync_status` - `synced`, `outdated`, `unlinked`, `conflict`
- `sync_direction` - `auto`, `manual`, `bidirectional`
- `last_synced_at` - Last sync timestamp
- `figma_modified_at, code_modified_at` - Change tracking
- `has_conflict` - Boolean flag for conflicts
- `conflict_details` - Conflict description
- `code_connect_enabled` - Figma Code Connect support
- `code_connect_url` - Code snippet URL

**Indexes:**
- Single-column: project, item, component, file_key, node_id, sync_status, has_conflict
- Composite: `(project_id, sync_status)`, `(file_key, page_name)`

**Unique Constraints:**
- `(project_id, file_key, node_id, item_id)` - One sync per item
- `(project_id, file_key, node_id, component_id)` - One sync per component

**Use Cases:**
- Display design-code sync status
- Detect outdated designs/code
- Find conflicts needing resolution
- Figma → Code Connect integration

### 5. Migration 042: derived_journeys

**Purpose:** Store automatically-detected and manually-created user journeys, data flows, and call chains.

**Table:** `derived_journeys`

**Key Columns:**
- `id` - UUID primary key
- `project_id` - Project reference
- `name, slug` - Journey identity
- `description` - Human-readable description
- `journey_type` - Type: `user_flow`, `data_flow`, `call_chain`, `process_flow`
- `perspectives` - JSONB array of perspectives involved
- `item_ids` - JSONB ordered array of items in sequence
- `item_count` - Count of items
- `link_ids` - JSONB array of links between items
- `entry_item_id, exit_item_id` - Start and end points
- `detection_method` - How found: `graph_traversal`, `ast_analysis`, `annotation`, `manual`
- `confidence` - 0-1 confidence score
- `score` - Custom ranking score
- `occurrence_count` - How many times detected
- `last_occurred_at` - Timestamp of last occurrence
- `variants` - JSONB array of alternative paths
- `status` - `auto` or `confirmed`
- `approved_by, approved_at` - User approval tracking

**Indexes:**
- Single-column: project, journey_type, entry_item, exit_item, detection_method, confidence, status
- GIN arrays: `item_ids`, `perspectives` for array searches
- Composite: `(project_id, journey_type)`, `(project_id, status)`

**Use Cases:**
- Visualize user journeys through the product
- Trace data flows across system
- Understand call chains in code
- Identify critical paths
- Journey-based testing and documentation

## Related Existing Migrations

### 031-036: Foundation Tables (Created Previously)

These migrations establish the core multi-dimensional traceability model:

- **031:** `canonical_concepts` - Abstract entities across perspectives
- **032:** `canonical_projections` - Many-to-many mappings to items
- **033:** `doc_entities` - Documentation hierarchy
- **034:** `code_entities` - Code symbol indexing
- **035:** `perspective_configs` - Project-specific perspective customization
- **036:** `component_libraries`, `library_components` - Design system tracking

### 037: Blockchain & ML Tables (Existing)

Adds blockchain-style versioning and ML embedding support:
- `version_blocks` - Immutable change history
- `version_chains` - Blockchain linking
- `baselines` - Merkle tree snapshots
- `baseline_items` - Items in baselines
- `merkle_proofs` - Cached proofs
- `spec_embeddings` - Semantic similarity vectors

## Data Flow Integration

```
┌─────────────────────────────────────────────────────────────────┐
│                    CANONICAL LAYER (031-032)                    │
│  Abstract concepts that manifest in multiple perspectives        │
└──────────────────────────┬──────────────────────────────────────┘
                           │ manifests_as
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
    CODE (034)        PRODUCT (items)    DESIGN (036)
    - Functions       - Features         - Components
    - Classes         - Requirements     - Tokens
    - Files           - User Stories     - Pages
        │                  │                  │
        └──────────────────┼──────────────────┘
          equivalence_links (038)
          ↓
        CROSS-PERSPECTIVE MAPPING
        - Same concepts identified
        - Confidence scored
        - Manually confirmed
        │
        ├─→ component_usage (039)
        │   Where components appear
        │   What props/variants used
        │
        ├─→ design_token_refs (040)
        │   Which tokens used
        │   Sync status with Figma
        │
        ├─→ figma_sync_state (041)
        │   Design-code alignment
        │   Conflict detection
        │
        └─→ derived_journeys (042)
            User flows
            Data flows
            Call chains
```

## Migration Execution Order

To apply all migrations:

```bash
# Apply all pending migrations
alembic upgrade head

# Or apply specific migration
alembic upgrade 042_add_derived_journeys
```

To rollback:

```bash
# Rollback one step
alembic downgrade -1

# Rollback to specific migration
alembic downgrade 037_add_blockchain_ml_tables
```

## Schema Statistics

| Table | Columns | Indexes | Purpose |
|-------|---------|---------|---------|
| equivalence_links | 13 | 11 | Cross-perspective equivalences |
| component_usage | 14 | 8 | Component usage tracking |
| design_token_refs | 15 | 9 | Design token references |
| figma_sync_state | 18 | 10 | Figma integration sync |
| derived_journeys | 18 | 10 | Journey detection results |

**Total New Tables:** 5
**Total New Columns:** 78
**Total New Indexes:** 48

## Performance Considerations

### Equivalence Links
- Bidirectional queries supported via separate indexes on both item columns
- Confidence filtering enabled for top-matches queries
- Composite indexes optimize cross-perspective queries

### Component Usage
- Efficient component discovery via GIN-compatible compound index
- Last-seen tracking enables staleness detection
- File-path indexing for code-location correlation

### Design Tokens
- Token-type filtering common in UI builders
- Project + type composite index for fast filtering
- Figma style ID enables bidirectional sync

### Figma Sync State
- File+page index optimizes dashboard queries
- Status filtering for conflict/outdated detection
- Project+status composite for sync workflows

### Derived Journeys
- GIN array indexes enable multi-perspective queries
- Entry/exit indexes support flow visualization
- Detection method filtering for algorithm comparison

## Next Steps

1. **Apply Migrations:** Run `alembic upgrade head` to create tables
2. **Add RLS Policies:** Implement row-level security for each table
3. **Seed Data:** Populate from existing items and code entities
4. **Build APIs:** Create tRPC endpoints for querying/updating
5. **Implement Detection:** Build equivalence/journey detection algorithms
6. **Create UIs:** Build components for visualization and management

## References

- **Plan:** `/Users/kooshapari/.claude/plans/eventual-toasting-eich.md`
- **Alembic Docs:** https://alembic.sqlalchemy.org/
- **PostgreSQL Types:** https://www.postgresql.org/docs/current/datatype.html
