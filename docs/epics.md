# TraceRTM - Epic Breakdown

**Author:** BMad
**Date:** 2025-11-20
**Project Level:** Enterprise
**Target Scale:** MVP (8 core views, 1-1000 concurrent agents)

---

## Overview

This document provides the complete epic and story breakdown for TraceRTM, decomposing the 88 functional requirements from the [PRD](./PRD.md) into implementable stories organized by user value delivery.

**Living Document Notice:** This is the initial version based on PRD + Architecture. Stories include technical implementation notes from the architecture document.

**Epic Structure Philosophy:**
- Each epic delivers **standalone user value**
- Epics are **NOT** organized by technical layers (database, API, CLI)
- Each story is completable by a single dev agent in one focused session
- Foundation/setup stories are grouped in Epic 1 (Project Foundation)

**Total Epics:** 8
**Total Stories:** ~45-50
**FR Coverage:** 88/88 FRs mapped to stories

---

## Functional Requirements Inventory

**FR Categories from PRD:**
1. Multi-View System (FR1-FR5) - 5 FRs
2. Item Management (FR6-FR15) - 10 FRs
3. Cross-View Linking (FR16-FR22) - 7 FRs
4. CLI Interface (FR23-FR35) - 13 FRs
5. Agent-Native API (FR36-FR45) - 10 FRs
6. Multi-Project Support (FR46-FR53) - 8 FRs
7. Versioning & History (FR54-FR59) - 6 FRs
8. Search & Filter (FR60-FR67) - 8 FRs
9. Progress Tracking (FR68-FR73) - 6 FRs
10. Data Import/Export (FR74-FR82) - 9 FRs
11. Configuration & Setup (FR83-FR88) - 6 FRs

**Total:** 88 Functional Requirements

---

## FR Coverage Map

| Epic | Epic Title | FRs Covered | Story Count |
|------|-----------|-------------|-------------|
| Epic 1 | Project Foundation & Setup | FR83-FR88 | 6 |
| Epic 2 | Core Item Management | FR6-FR15, FR1-FR5 | 8 |
| Epic 3 | Multi-View Navigation | FR1-FR5, FR23-FR35 | 7 |
| Epic 4 | Cross-View Linking & Relationships | FR16-FR22 | 6 |
| Epic 5 | Agent Coordination & Concurrency | FR36-FR45 | 8 |
| Epic 6 | Multi-Project Management | FR46-FR53 | 6 |
| Epic 7 | History, Search & Progress | FR54-FR73 | 9 |
| Epic 8 | Import/Export & Data Portability | FR74-FR82 | 5 |

**Total Stories:** 55

---

## Epic 1: Project Foundation & Setup

**Phase:** MVP
**Goal:** Enable users to initialize TraceRTM, configure database, and create their first project.

**User Value:** Users can install TraceRTM and start managing their first project within minutes.

**FRs Covered:** FR83-FR88 (Configuration & Setup)

**Prerequisites:** None (first epic)

---

### Story 1.1: Package Installation & Environment Setup

**Phase:** MVP
**As a** developer,
**I want** to install TraceRTM via pip and verify it's working,
**So that** I can start using the tool immediately.

**Acceptance Criteria:**

**Given** I have Python 3.12+ and PostgreSQL 16+ installed
**When** I run `pip install tracertm` and `rtm --version`
**Then** TraceRTM is installed and displays version information

**And** I can run `rtm --help` to see available commands
**And** Shell completion scripts are available for Bash/Zsh/Fish

**Prerequisites:** None

**Technical Notes:**
- Implement `setup.py` / `pyproject.toml` with entry point `rtm`
- Use Typer for CLI framework (per ADR-007)
- Include shell completion generation
- Package dependencies: SQLAlchemy 2.0+, Pydantic v2, Typer, Rich

**FRs Covered:** FR83 (initialize new project)

---

### Story 1.2: Database Connection & Migration System

**Phase:** MVP
**As a** developer,
**I want** TraceRTM to connect to my PostgreSQL database and create necessary tables,
**So that** I can store project data persistently.

**Acceptance Criteria:**

**Given** I have PostgreSQL 16+ running
**When** I run `rtm config init` and provide database URL
**Then** TraceRTM creates config file at `~/.config/tracertm/config.yaml`

**And** Database connection is validated
**And** Alembic migrations create all required tables (projects, items, links, events, agents)
**And** Indexes are created for performance (per architecture)

**Prerequisites:** Story 1.1

**Technical Notes:**
- Implement SQLAlchemy models: Project, Item, Link, Event, Agent
- Create Alembic migration for initial schema (see architecture.md database schema)
- Implement connection pooling (pool_size=20, max_overflow=10)
- Add health check: `rtm db status`

**FRs Covered:** FR84 (create project directory structure and database), FR85 (configure project settings)

---

### Story 1.3: Project Initialization Workflow

**Phase:** MVP  
**As a** developer,
**I want** to initialize my first project with a simple command,
**So that** I can start tracking items immediately.

**Acceptance Criteria:**

**Given** Database is configured and migrations are run
**When** I run `rtm project init my-first-project`
**Then** A new project is created in the database

**And** Project has default configuration (8 core views enabled)
**And** Project ID is returned and set as current project
**And** I can verify with `rtm project list`

**Prerequisites:** Story 1.2

**Technical Notes:**
- Implement `ProjectRepository.create()`
- Store project config in JSONB field
- Set current project in config file or environment variable
- Implement `rtm project switch <name>` for multi-project support
- Default config: 8 core views enabled, default_view=FEATURE, output_format=table

**FRs Covered:** FR83 (initialize new project), FR86 (set default view, output format)

---

### Story 1.4: Configuration Management

**Phase:** MVP  
**As a** developer,
**I want** to configure TraceRTM settings (default view, output format, preferences),
**So that** the tool behaves according to my preferences.

**Acceptance Criteria:**

**Given** I have initialized a project
**When** I run `rtm config set default_view FEATURE`
**Then** My default view is set to FEATURE

**And** I can set output format: `rtm config set output_format json`
**And** I can view current config: `rtm config show`
**And** Project-specific config overrides global config
**And** Config changes are persisted to `~/.config/tracertm/config.yaml`

**Prerequisites:** Story 1.3

**Technical Notes:**
- Implement config hierarchy: CLI flags > env vars > project config > global config
- Use Pydantic for config validation
- Support YAML config files
- Implement `ConfigManager` singleton pattern
- Config schema: default_view, output_format, database_url, current_project_id

**FRs Covered:** FR85-FR87 (configure project settings, default preferences, project-specific config)

---

### Story 1.5: Backup & Restore Capability

**Phase:** MVP  
**As a** developer,
**I want** to backup and restore my project configuration and data,
**So that** I can recover from failures or migrate to new environments.

**Acceptance Criteria:**

**Given** I have a project with data
**When** I run `rtm backup --output my-project-backup.json`
**Then** All project data is exported to JSON file

**And** I can restore with `rtm restore --input my-project-backup.json`
**And** Backup includes: projects, items, links, events, agents
**And** Restore validates data before applying
**And** Backup completes in <5s for 10K items

**Prerequisites:** Story 1.3

**Technical Notes:**
- Implement `ExportService.export_project()` (JSON/YAML)
- Implement `ImportService.import_project()` with validation
- Use Pydantic schemas for validation
- Support incremental backups (events only)
- Compress large backups with gzip

**FRs Covered:** FR88 (backup and restore project configuration)

---

### Story 1.6: Error Handling & User-Friendly Messages

**Phase:** MVP  
**As a** developer,
**I want** clear, actionable error messages when something goes wrong,
**So that** I can quickly fix issues without debugging.

**Acceptance Criteria:**

**Given** I run a command with invalid input
**When** An error occurs (e.g., database connection failed, invalid item ID)
**Then** I see a user-friendly error message (not a stack trace)

**And** Error message includes suggestions for fixing the issue
**And** Errors are logged to file for debugging
**And** Exit codes are meaningful (0=success, 1=error, 2=validation error)
**And** Stack traces only shown with `--debug` flag

**Prerequisites:** Story 1.1

**Technical Notes:**
- Implement exception hierarchy (TraceRTMError, ValidationError, NotFoundError, ConcurrencyError, DatabaseError)
- Use Rich for colored error output
- Implement error handling pattern in CLI commands
- Log errors to `~/.config/tracertm/logs/tracertm.log`
- Include suggestions in error messages (e.g., "Did you mean 'rtm project init'?")

**FRs Covered:** NFR-U3 (error messages), NFR-R3 (error handling)

---

## Epic 2: Core Item Management

**Phase:** MVP
**Goal:** Enable users to create, read, update, and delete items across all views with full CRUD operations.

**User Value:** Users can manage their project items (features, tasks, code files, tests, etc.) with a consistent interface.

**FRs Covered:** FR6-FR15 (Item Management), FR1-FR5 (Multi-View System)

**Prerequisites:** Epic 1 (Project Foundation)

---

### Story 2.1: Item Creation with Type & View

**Phase:** MVP  
**As a** developer,
**I want** to create items with specific types and views,
**So that** I can organize my project across different perspectives.

**Acceptance Criteria:**

**Given** I have an initialized project
**When** I run `rtm create feature "User Authentication" --view FEATURE`
**Then** A new item is created with type=feature, view=FEATURE

**And** Item has auto-generated UUID
**And** Item has default status="todo", progress=0.0, version=1
**And** Item is returned in JSON format with `--format json`
**And** I can create items in all 8 core views (FEATURE, CODE, WIREFRAME, API, TEST, DATABASE, ROADMAP, PROGRESS)

**Prerequisites:** Story 1.3

**Technical Notes:**
- Implement `ItemRepository.create()` with optimistic locking (version=1)
- Use Pydantic `ItemCreate` schema for validation
- Support item types: epic, feature, story, task, bug, file, endpoint, test, table, milestone
- Implement CLI command: `rtm create <type> <title> [--view VIEW] [--description DESC]`
- Log creation event to event_log table

**FRs Covered:** FR6 (create items), FR1 (8 core views), FR7 (item types)

---

### Story 2.2: Item Retrieval & Display

**Phase:** MVP  
**As a** developer,
**I want** to view item details by ID or list items by view,
**So that** I can inspect my project state.

**Acceptance Criteria:**

**Given** I have created items
**When** I run `rtm show <item-id>`
**Then** Item details are displayed (title, description, status, metadata, links)

**And** I can list items by view: `rtm view FEATURE`
**And** I can filter by status: `rtm view FEATURE --status todo`
**And** I can format output as JSON, YAML, or table
**And** Query completes in <50ms for simple lookups

**Prerequisites:** Story 2.1

**Technical Notes:**
- Implement `ItemRepository.get_by_id()` with index on id
- Implement `ItemRepository.get_by_view()` with index on (project_id, view)
- Use Rich for table formatting
- Support output formats: json, yaml, table (default)
- Implement pagination for large result sets

**FRs Covered:** FR8 (view item details), FR2 (view items by view), FR23 (CLI commands)

---

### Story 2.3: Item Update with Optimistic Locking

**Phase:** MVP  
**As a** developer,
**I want** to update item properties with conflict detection,
**So that** concurrent updates don't overwrite each other.

**Acceptance Criteria:**

**Given** I have an item with version=1
**When** I run `rtm update <item-id> --status in_progress`
**Then** Item status is updated and version increments to 2

**And** If another agent updated the item first, I get a ConcurrencyError
**And** I can retry with `--force` to override
**And** Update event is logged with agent_id and timestamp
**And** I can update: title, description, status, owner, metadata

**Prerequisites:** Story 2.2

**Technical Notes:**
- Implement optimistic locking: check version before update
- Raise `ConcurrencyError` if version mismatch
- Implement retry logic with exponential backoff
- Log update event to event_log table
- Use Pydantic `ItemUpdate` schema for validation

**FRs Covered:** FR9 (edit item properties), FR36 (concurrent operations), FR54 (version tracking)

---

### Story 2.4: Item Deletion with Soft Delete

**Phase:** MVP  
**As a** developer,
**I want** to delete items with the option to recover them,
**So that** I can clean up my project without losing data permanently.

**Acceptance Criteria:**

**Given** I have an item
**When** I run `rtm delete <item-id>`
**Then** Item is soft-deleted (deleted_at timestamp set)

**And** Item no longer appears in default queries
**And** I can view deleted items: `rtm view FEATURE --include-deleted`
**And** I can permanently delete: `rtm delete <item-id> --permanent`
**And** Deletion event is logged

**Prerequisites:** Story 2.2

**Technical Notes:**
- Implement soft delete: set `deleted_at` timestamp
- Filter deleted items in default queries: `WHERE deleted_at IS NULL`
- Implement `--include-deleted` flag
- Implement permanent delete: `DELETE FROM items WHERE id = ?`
- Log deletion event to event_log table

**FRs Covered:** FR10 (delete items), FR54 (history tracking)

---

### Story 2.5: Item Metadata & Custom Fields

**Phase:** MVP  
**As a** developer,
**I want** to add custom metadata to items,
**So that** I can store domain-specific information.

**Acceptance Criteria:**

**Given** I have an item
**When** I run `rtm update <item-id> --metadata '{"priority": "high", "tags": ["auth", "security"]}'`
**Then** Item metadata is stored in JSONB field

**And** I can query by metadata: `rtm view FEATURE --filter 'metadata.priority=high'`
**And** Metadata is validated as valid JSON
**And** I can update specific metadata keys without replacing all metadata

**Prerequisites:** Story 2.3

**Technical Notes:**
- Use PostgreSQL JSONB for metadata field
- Implement JSONB indexing for common queries: `CREATE INDEX idx_items_metadata ON items USING GIN (metadata)`
- Support JSON path queries: `metadata @> '{"priority": "high"}'`
- Validate JSON structure with Pydantic

**FRs Covered:** FR11 (custom metadata), FR60 (filter by metadata)

---

### Story 2.6: Item Hierarchy (Parent-Child Relationships)

**Phase:** MVP  
**As a** developer,
**I want** to organize items hierarchically (epic → feature → story → task),
**So that** I can model complex project structures.

**Acceptance Criteria:**

**Given** I have created an epic
**When** I run `rtm create feature "OAuth Login" --parent <epic-id>`
**Then** Feature is created with parent_id set to epic

**And** I can query children: `rtm show <epic-id> --children`
**And** I can query ancestors: `rtm show <task-id> --ancestors`
**And** Progress rolls up from children to parents
**And** Deleting parent soft-deletes all children

**Prerequisites:** Story 2.1

**Technical Notes:**
- Add `parent_id` foreign key to items table
- Implement recursive CTE for ancestor/descendant queries
- Implement progress rollup: `UPDATE items SET progress = AVG(children.progress) WHERE id = parent_id`
- Cascade soft delete to children

**FRs Covered:** FR12 (hierarchical relationships), FR68 (progress rollup)

---

### Story 2.7: Item Status Workflow

**Phase:** MVP  
**As a** developer,
**I want** to transition items through status states (todo → in_progress → done),
**So that** I can track work progress.

**Acceptance Criteria:**

**Given** I have an item with status=todo
**When** I run `rtm update <item-id> --status in_progress`
**Then** Item status transitions to in_progress

**And** Valid statuses: todo, in_progress, blocked, done, archived
**And** Status transitions are logged in event_log
**And** I can query items by status: `rtm view FEATURE --status in_progress`
**And** Progress auto-updates: todo=0%, in_progress=50%, done=100%

**Prerequisites:** Story 2.3

**Technical Notes:**
- Define status enum: todo, in_progress, blocked, done, archived
- Implement status validation in Pydantic schema
- Auto-update progress based on status
- Log status change events
- Create index on (project_id, status) for fast queries

**FRs Covered:** FR13 (status tracking), FR68 (progress calculation)

---

### Story 2.8: Bulk Item Operations

**Phase:** MVP  
**As a** developer,
**I want** to perform bulk operations on multiple items,
**So that** I can efficiently manage large projects.

**Acceptance Criteria:**

**Given** I have multiple items
**When** I run `rtm bulk update --filter 'status=todo' --set status=in_progress`
**Then** I see a preview with:
  - Total count of matching items
  - Sample items (first 5) showing current and new values
  - Validation warnings (if any)
  - Estimated duration

**And** I can confirm or cancel the operation
**And** If confirmed, all matching items are updated
**And** I can skip preview with `--skip-preview` flag for automation

**And** I can bulk delete: `rtm bulk delete --filter 'view=TEST AND status=archived'` (with preview)
**And** I can bulk create from CSV: `rtm bulk create --input items.csv` (with validation preview)
**And** Operations are atomic (all succeed or all fail)
**And** Bulk operations complete in <5s for 1000 items
**And** Preview displays validation warnings for risky operations (>100 items, status conflicts)

**Prerequisites:** Story 2.3

**Technical Notes:**
- Implement `BulkOperationService` with preview and execution methods (see Architecture Pattern 6)
- Preview shows: total count, sample items (first 5), validation warnings, estimated duration
- Validation warnings for: large operations (>100 items), status conflicts, risky changes
- Implement batch operations with SQLAlchemy `bulk_update_mappings()`
- Use database transactions for atomicity
- Implement CSV import with Pydantic validation
- Optimize with batch size of 100 items per transaction
- Log bulk operation events
- Graceful handling of concurrency conflicts (log and continue)
- CLI uses Rich for preview display (table, warnings, confirmation prompt)
- Agent API supports programmatic preview and execution

**Architecture Reference:** Pattern 6 (Bulk Operation Preview Pattern)
**UX Reference:** BulkOperationPreview component, User Journey 3 (Bulk Manipulation)

**FRs Covered:** FR14 (bulk operations), FR74 (import from CSV)

---

## Epic 3: Multi-View Navigation & CLI Interface

**Phase:** MVP  
**Goal:** Enable users to seamlessly switch between views and interact with TraceRTM via a powerful CLI.

**User Value:** Users can navigate their project from any perspective (Feature → Code → Test → API) with fast, intuitive commands.

**FRs Covered:** FR1-FR5 (Multi-View System), FR23-FR35 (CLI Interface)

**Prerequisites:** Epic 2 (Core Item Management)

---

### Story 3.1: View Switching & Navigation

**Phase:** MVP  
**As a** developer,
**I want** to switch between views instantly,
**So that** I can see my project from different perspectives.

**Acceptance Criteria:**

**Given** I have items in multiple views
**When** I run `rtm view FEATURE`
**Then** All items in FEATURE view are displayed

**And** I can switch to CODE view: `rtm view CODE`
**And** I can switch to TEST view: `rtm view TEST`
**And** View switch completes in <200ms
**And** All 8 core views are supported: FEATURE, CODE, WIREFRAME, API, TEST, DATABASE, ROADMAP, PROGRESS

**Prerequisites:** Story 2.2

**Technical Notes:**
- Implement `ViewService.get_items_by_view()`
- Use indexed query: `SELECT * FROM items WHERE project_id = ? AND view = ? AND deleted_at IS NULL`
- Cache view results for 5 seconds
- Implement view enum validation

**FRs Covered:** FR1 (8 core views), FR2 (view items by view), FR3 (switch views)

---

### Story 3.2: View Filtering & Sorting

**Phase:** MVP  
**As a** developer,
**I want** to filter and sort items within a view,
**So that** I can focus on relevant items.

**Acceptance Criteria:**

**Given** I am viewing items in FEATURE view
**When** I run `rtm view FEATURE --status todo --sort created_at`
**Then** Only todo items are displayed, sorted by creation date

**And** I can filter by multiple criteria: `--status todo --owner me`
**And** I can sort ascending/descending: `--sort -updated_at`
**And** I can limit results: `--limit 10`
**And** Filtered queries complete in <100ms

**Prerequisites:** Story 3.1

**Technical Notes:**
- Implement dynamic query builder for filters
- Support filter operators: =, !=, >, <, LIKE, IN
- Implement sorting with ORDER BY clause
- Add pagination with LIMIT/OFFSET
- Create composite indexes for common filter combinations

**FRs Covered:** FR60-FR67 (Search & Filter), FR24 (filter by criteria)

---

### Story 3.3: CLI Output Formatting

**Phase:** MVP  
**As a** developer,
**I want** to format CLI output as JSON, YAML, or table,
**So that** I can integrate TraceRTM with other tools or read output easily.

**Acceptance Criteria:**

**Given** I run any query command
**When** I add `--format json`
**Then** Output is formatted as valid JSON

**And** I can use `--format yaml` for YAML output
**And** I can use `--format table` for human-readable table (default)
**And** JSON/YAML output is parseable by standard tools (jq, yq)
**And** Table output uses Rich for colored, formatted display

**Prerequisites:** Story 2.2

**Technical Notes:**
- Implement `OutputFormatter` with strategies for json, yaml, table
- Use Pydantic `.model_dump_json()` for JSON serialization
- Use PyYAML for YAML serialization
- Use Rich Table for table formatting
- Support `--no-color` flag for CI environments

**FRs Covered:** FR25 (output formats), FR26 (JSON/YAML export)

---

### Story 3.4: Shell Completion & Autocomplete

**Phase:** MVP  
**As a** developer,
**I want** shell completion for commands and arguments,
**So that** I can work faster with less typing.

**Acceptance Criteria:**

**Given** I have installed TraceRTM
**When** I run `rtm --install-completion`
**Then** Shell completion is installed for my shell (Bash/Zsh/Fish)

**And** I can autocomplete commands: `rtm cr<TAB>` → `rtm create`
**And** I can autocomplete item IDs: `rtm show <TAB>` → shows recent item IDs
**And** I can autocomplete view names: `rtm view <TAB>` → shows all views
**And** Completion works for flags: `--for<TAB>` → `--format`

**Prerequisites:** Story 1.1

**Technical Notes:**
- Use Typer's built-in completion support
- Implement custom completers for item IDs (query recent items)
- Implement custom completers for view names (static list)
- Generate completion scripts for Bash, Zsh, Fish
- Install to standard locations: `~/.bash_completion.d/`, `~/.zsh/completion/`

**FRs Covered:** FR27 (shell completion), FR28 (autocomplete)

---

### Story 3.5: CLI Help & Documentation

**Phase:** MVP  
**As a** developer,
**I want** comprehensive help documentation in the CLI,
**So that** I can learn commands without leaving the terminal.

**Acceptance Criteria:**

**Given** I need help with a command
**When** I run `rtm --help`
**Then** I see a list of all available commands with descriptions

**And** I can get command-specific help: `rtm create --help`
**And** Help includes examples: `rtm create feature "Title" --view FEATURE`
**And** Help is formatted with Rich for readability
**And** I can access man pages: `man rtm`

**Prerequisites:** Story 1.1

**Technical Notes:**
- Use Typer's auto-generated help from docstrings
- Add rich_help_panel to group related commands
- Include examples in command docstrings
- Generate man pages from help text
- Use Rich markup for colored help output

**FRs Covered:** FR29 (help documentation), FR30 (command examples)

---

### Story 3.6: CLI Aliases & Shortcuts

**Phase:** MVP  
**As a** developer,
**I want** to create aliases for frequently used commands,
**So that** I can work more efficiently.

**Acceptance Criteria:**

**Given** I frequently run `rtm view FEATURE --status todo`
**When** I create an alias: `rtm alias add mytodo "view FEATURE --status todo"`
**Then** I can run `rtm mytodo` as a shortcut

**And** I can list aliases: `rtm alias list`
**And** I can remove aliases: `rtm alias remove mytodo`
**And** Aliases are stored in config file
**And** Aliases support parameters: `rtm alias add show-view "view $1"`

**Prerequisites:** Story 1.4

**Technical Notes:**
- Store aliases in config file: `~/.config/tracertm/aliases.yaml`
- Implement alias expansion before command parsing
- Support parameter substitution: $1, $2, etc.
- Validate alias names (no conflicts with built-in commands)
- Implement `AliasManager` class

**FRs Covered:** FR31 (command aliases), FR32 (shortcuts)

---

### Story 3.7: CLI Performance & Responsiveness

**Phase:** MVP  
**As a** developer,
**I want** CLI commands to execute quickly,
**So that** I can maintain flow state while working.

**Acceptance Criteria:**

**Given** I run any CLI command
**When** The command executes
**Then** Simple queries complete in <50ms

**And** Complex queries complete in <1s
**And** View switches complete in <200ms
**And** CLI startup time is <100ms
**And** Progress indicators show for long-running operations

**Prerequisites:** Story 2.2

**Technical Notes:**
- Optimize database queries with proper indexing
- Use connection pooling to avoid connection overhead
- Implement lazy loading for heavy imports
- Show progress bars with Rich for operations >1s
- Cache frequently accessed data (views, project config)

**FRs Covered:** NFR-P1 (query response time), NFR-P2 (view rendering), NFR-U1 (CLI responsiveness)

---


## Epic 4: Cross-View Linking & Relationships

**Phase:** MVP  
**Goal:** Enable users to create bidirectional links between items across views to model complex relationships.

**User Value:** Users can trace relationships (Feature → Code → Test → API) and understand project dependencies.

**FRs Covered:** FR16-FR22 (Cross-View Linking)

**Prerequisites:** Epic 2 (Core Item Management)

---

### Story 4.1: Link Creation & Types

**Phase:** MVP  
**As a** developer,
**I want** to create typed links between items,
**So that** I can model relationships like "implements", "tests", "depends_on".

**Acceptance Criteria:**

**Given** I have two items (feature and code file)
**When** I run `rtm link <feature-id> <code-id> --type implements`
**Then** A bidirectional link is created

**And** Link has type="implements"
**And** I can query links: `rtm show <feature-id> --links`
**And** Supported link types: implements, tests, depends_on, blocks, relates_to, documents
**And** Links are stored in links table with source_item_id, target_item_id, link_type

**Prerequisites:** Story 2.1

**Technical Notes:**
- Implement `LinkRepository.create()` with validation
- Create links table: (id, project_id, source_item_id, target_item_id, link_type, metadata, created_at)
- Implement bidirectional queries: source → target AND target → source
- Add foreign keys with CASCADE on item deletion
- Create indexes on (source_item_id), (target_item_id)

**FRs Covered:** FR16 (create links), FR17 (link types)

---

### Story 4.2: Link Traversal & Navigation

**Phase:** MVP  
**As a** developer,
**I want** to traverse links to navigate between related items,
**So that** I can explore project relationships.

**Acceptance Criteria:**

**Given** I have linked items
**When** I run `rtm show <item-id> --links`
**Then** All linked items are displayed with link types

**And** I can filter by link type: `rtm show <item-id> --links --type implements`
**And** I can traverse links: `rtm show <item-id> --follow implements`
**And** I can query reverse links: `rtm show <code-id> --reverse-links`
**And** Link queries complete in <50ms

**Prerequisites:** Story 4.1

**Technical Notes:**
- Implement `LinkRepository.get_by_source()` and `get_by_target()`
- Implement link traversal with recursive CTE
- Support filtering by link_type
- Display linked items with Rich formatting
- Cache link queries for performance

**FRs Covered:** FR18 (traverse links), FR19 (bidirectional navigation)

---

### Story 4.3: Link Metadata & Annotations

**Phase:** MVP  
**As a** developer,
**I want** to add metadata to links,
**So that** I can store additional context about relationships.

**Acceptance Criteria:**

**Given** I have a link
**When** I run `rtm link update <link-id> --metadata '{"coverage": "80%", "notes": "Partial implementation"}'`
**Then** Link metadata is stored in JSONB field

**And** I can query links by metadata: `rtm links --filter 'metadata.coverage>50%'`
**And** Metadata is displayed when showing links
**And** I can update metadata without recreating link

**Prerequisites:** Story 4.1

**Technical Notes:**
- Add metadata JSONB field to links table
- Implement JSONB indexing: `CREATE INDEX idx_links_metadata ON links USING GIN (metadata)`
- Support JSON path queries
- Validate metadata with Pydantic

**FRs Covered:** FR20 (link metadata), FR60 (filter by metadata)

---

### Story 4.4: Link Deletion & Cleanup

**Phase:** MVP  
**As a** developer,
**I want** to delete links when relationships change,
**So that** my project graph stays accurate.

**Acceptance Criteria:**

**Given** I have a link
**When** I run `rtm link delete <link-id>`
**Then** Link is permanently deleted

**And** Deleting an item cascades to delete all its links
**And** I can delete all links of a type: `rtm link delete --type implements --source <item-id>`
**And** Deletion is logged in event_log
**And** I can bulk delete links: `rtm link delete --filter 'type=relates_to'`

**Prerequisites:** Story 4.1

**Technical Notes:**
- Implement `LinkRepository.delete()`
- Add CASCADE foreign keys on items table
- Log link deletion events
- Implement bulk delete with filters
- Use database transactions for atomicity

**FRs Covered:** FR21 (delete links), FR22 (cascade deletion)

---

### Story 4.5: Link Visualization (Text-Based)

**Phase:** MVP  
**As a** developer,
**I want** to visualize item relationships in the terminal,
**So that** I can understand project structure at a glance.

**Acceptance Criteria:**

**Given** I have linked items
**When** I run `rtm graph <item-id>`
**Then** A text-based graph is displayed showing relationships

**And** Graph shows item titles and link types
**And** Graph uses tree structure for hierarchical relationships
**And** I can limit depth: `rtm graph <item-id> --depth 2`
**And** I can filter by link type: `rtm graph <item-id> --type implements`

**Prerequisites:** Story 4.2

**Technical Notes:**
- Implement graph traversal with BFS/DFS
- Use Rich Tree for text-based visualization
- Limit depth to prevent infinite loops
- Support filtering by link_type
- Cache graph queries for performance

**FRs Covered:** FR19 (visualize relationships), FR18 (traverse links)

---

### Story 4.6: Dependency Detection & Cycle Prevention

**Phase:** MVP  
**As a** developer,
**I want** to detect circular dependencies,
**So that** I can avoid invalid project structures.

**Acceptance Criteria:**

**Given** I try to create a link that would create a cycle
**When** I run `rtm link <item-a> <item-b> --type depends_on`
**Then** If a cycle would be created, I get an error

**And** Error message shows the cycle path
**And** I can force creation with `--allow-cycles`
**And** I can detect cycles: `rtm graph --detect-cycles`
**And** Cycle detection completes in <1s for 10K items

**Prerequisites:** Story 4.2

**Technical Notes:**
- Implement cycle detection with DFS
- Check for cycles before creating depends_on links
- Use recursive CTE for cycle detection
- Cache dependency graph for performance
- Implement `--allow-cycles` flag for non-dependency links

**FRs Covered:** FR22 (dependency validation), NFR-R2 (data integrity)

---

## Epic 5: Agent Coordination & Concurrency

**Phase:** MVP  
**Goal:** Enable 1-1000 AI agents to work concurrently without conflicts using optimistic locking and agent tracking.

**User Value:** Users can orchestrate massive agent workforces to build projects at unprecedented scale and speed.

**FRs Covered:** FR36-FR45 (Agent-Native API)

**Prerequisites:** Epic 2 (Core Item Management)

---

### Story 5.1: Agent Registration & Authentication

**Phase:** MVP  
**As an** AI agent,
**I want** to register myself and authenticate,
**So that** my operations are tracked and attributed.

**Acceptance Criteria:**

**Given** I am an AI agent
**When** I call `AgentAPI.register(agent_id="agent-001", name="Code Generator", type="codegen")`
**Then** I am registered in the agents table

**And** My agent_id is returned
**And** I can authenticate with agent_id for subsequent operations
**And** My last_active timestamp is updated on each operation
**And** I can query my own activity: `AgentAPI.get_activity(agent_id="agent-001")`

**Prerequisites:** Story 1.2

**Technical Notes:**
- Create agents table: (id, name, type, config, created_at, last_active)
- Implement `AgentRepository.register()`
- Store agent_id in context for all operations
- Update last_active on each API call
- Implement agent activity logging

**FRs Covered:** FR36 (agent registration), FR37 (agent authentication)

---

### Story 5.2: Python API for Programmatic Access

**Phase:** MVP  
**As an** AI agent,
**I want** a Python API to interact with TraceRTM programmatically,
**So that** I can automate project management tasks.

**Acceptance Criteria:**

**Given** I am an AI agent
**When** I import `from tracertm import TraceRTMClient`
**Then** I can create a client: `client = TraceRTMClient(agent_id="agent-001")`

**And** I can create items: `client.items.create(type="feature", title="...")`
**And** I can query items: `client.items.get_by_view("FEATURE")`
**And** I can create links: `client.links.create(source_id, target_id, type="implements")`
**And** All operations use async/await for concurrency

**Prerequisites:** Story 5.1

**Technical Notes:**
- Implement `TraceRTMClient` class with async methods
- Implement resource classes: ItemsResource, LinksResource, ProjectsResource
- Use Pydantic for request/response validation
- Support both sync and async APIs (sync wraps async)
- Return Pydantic models from API calls

**FRs Covered:** FR38 (Python API), FR39 (programmatic access)

---

### Story 5.3: Concurrent Operations with Optimistic Locking

**Phase:** MVP  
**As an** AI agent,
**I want** to update items concurrently with conflict detection,
**So that** I don't overwrite other agents' changes.

**Acceptance Criteria:**

**Given** 10 agents try to update the same item
**When** Each agent calls `client.items.update(item_id, data, expected_version=1)`
**Then** First agent succeeds, others get ConcurrencyError

**And** Failed agents can retry with updated version
**And** Retry logic uses exponential backoff
**And** Conflict rate is <1% for different items
**And** All operations complete in <5s for 1000 concurrent agents

**Prerequisites:** Story 5.2

**Technical Notes:**
- Implement optimistic locking in `ItemRepository.update()`
- Raise `ConcurrencyError` on version mismatch
- Implement retry decorator with exponential backoff
- Log conflicts to agent_activity table
- Test with 1000 concurrent agents (integration test)

**Technical Risks:**
- ⚠️ **UNKNOWN: Optimal locking strategy for 1000 agents**
  - Risk: Optimistic locking may cause high conflict rate (>10%) at scale
  - Mitigation: Load test with 100, 500, 1000 agents to measure conflict rate
  - Fallback: Implement pessimistic locking or agent queuing for hot items
- ⚠️ **UNKNOWN: Database connection pool sizing**
  - Risk: 1000 concurrent connections may exhaust PostgreSQL connection limit
  - Mitigation: Test connection pooling with pgBouncer or SQLAlchemy pool
  - Fallback: Implement connection queuing or read replicas
- ⚠️ **UNKNOWN: Retry strategy effectiveness**
  - Risk: Exponential backoff may cause cascading delays under high contention
  - Mitigation: Test retry behavior under various conflict rates
  - Fallback: Implement adaptive retry with jitter or circuit breaker

**FRs Covered:** FR40 (concurrent operations), FR41 (optimistic locking), NFR-P5 (1000+ agents)

---

### Story 5.4: Agent Activity Logging & Monitoring

**Phase:** MVP  
**As a** developer,
**I want** to monitor agent activity and operations,
**So that** I can debug issues and track agent productivity.

**Acceptance Criteria:**

**Given** Agents are performing operations
**When** I run `rtm agents list`
**Then** I see all registered agents with last_active timestamps

**And** I can view agent activity: `rtm agents activity <agent-id>`
**And** Activity log shows: operation type, item_id, timestamp, success/failure
**And** I can filter by time range: `rtm agents activity <agent-id> --since 1h`
**And** I can export activity to JSON for analysis

**Prerequisites:** Story 5.1

**Technical Notes:**
- Create agent_activity table: (id, agent_id, operation, item_id, timestamp, success, error_message)
- Log all agent operations (create, update, delete, link)
- Implement `AgentRepository.get_activity()`
- Support time range filtering
- Implement JSON export for activity logs

**FRs Covered:** FR42 (agent activity logging), FR43 (agent monitoring)

---

### Story 5.5: Batch Operations for Agent Efficiency

**Phase:** MVP  
**As an** AI agent,
**I want** to perform batch operations,
**So that** I can work more efficiently.

**Acceptance Criteria:**

**Given** I need to create 100 items
**When** I call `client.items.batch_create([item1, item2, ..., item100])`
**Then** All items are created in a single transaction

**And** Batch operations are atomic (all succeed or all fail)
**And** I can batch update: `client.items.batch_update([...])`
**And** I can batch delete: `client.items.batch_delete([id1, id2, ...])`
**And** Batch operations complete in <1s for 100 items

**Prerequisites:** Story 5.2

**Technical Notes:**
- Implement `batch_create()`, `batch_update()`, `batch_delete()` methods
- Use SQLAlchemy `bulk_insert_mappings()` for performance
- Wrap in database transaction for atomicity
- Validate all items before executing batch
- Log batch operations to agent_activity

**FRs Covered:** FR44 (batch operations), FR14 (bulk operations)

---

### Story 5.6: Agent Coordination & Task Assignment

**Phase:** MVP  
**As a** developer,
**I want** to assign tasks to specific agents,
**So that** I can coordinate agent workflows.

**Acceptance Criteria:**

**Given** I have multiple agents
**When** I run `rtm assign <item-id> --agent agent-001`
**Then** Item owner is set to agent-001

**And** Agent can query assigned tasks: `client.items.get_assigned(agent_id="agent-001")`
**And** I can reassign tasks: `rtm assign <item-id> --agent agent-002`
**And** Assignment history is logged
**And** I can view agent workload: `rtm agents workload`

**Prerequisites:** Story 5.1

**Technical Notes:**
- Add owner field to items table (agent_id or user_id)
- Implement `ItemRepository.get_by_owner()`
- Log assignment changes to event_log
- Implement workload calculation: COUNT(items WHERE owner = agent_id AND status != 'done')
- Create index on (owner, status)

**FRs Covered:** FR45 (task assignment), FR13 (owner tracking)

---

### Story 5.7: Agent Error Handling & Recovery

**Phase:** MVP  
**As an** AI agent,
**I want** clear error messages and recovery guidance,
**So that** I can handle failures gracefully.

**Acceptance Criteria:**

**Given** I perform an operation that fails
**When** An error occurs (e.g., validation error, not found, concurrency conflict)
**Then** I receive a structured error response

**And** Error includes: error_code, message, details, suggested_action
**And** I can retry with corrected input
**And** Transient errors (DB connection) are retried automatically
**And** Permanent errors (validation) are not retried

**Prerequisites:** Story 5.2

**Technical Notes:**
- Implement structured error responses with Pydantic
- Define error codes: VALIDATION_ERROR, NOT_FOUND, CONCURRENCY_ERROR, DB_ERROR
- Implement retry logic for transient errors
- Log all errors to agent_activity table
- Return suggested_action in error response

**FRs Covered:** NFR-R3 (error handling), NFR-U3 (error messages)

---

### Story 5.8: Agent Performance Metrics

**Phase:** MVP  
**As a** developer,
**I want** to track agent performance metrics,
**So that** I can optimize agent workflows.

**Acceptance Criteria:**

**Given** Agents have performed operations
**When** I run `rtm agents metrics`
**Then** I see metrics for all agents

**And** Metrics include: operations/hour, success rate, avg response time, conflict rate
**And** I can view metrics for specific agent: `rtm agents metrics <agent-id>`
**And** I can export metrics to JSON for analysis
**And** Metrics are calculated in <1s for 10K operations

**Prerequisites:** Story 5.4

**Technical Notes:**
- Calculate metrics from agent_activity table
- Implement aggregation queries with window functions
- Cache metrics for 5 minutes
- Support time range filtering
- Implement JSON export for metrics

**FRs Covered:** FR43 (agent monitoring), NFR-P1 (performance tracking)


## Epic 6: Multi-Project Management

**Phase:** MVP  
**Goal:** Enable users to manage multiple projects simultaneously with fast project switching.

**User Value:** Users can juggle 10+ projects without context switching overhead.

**FRs Covered:** FR46-FR53 (Multi-Project Support)

**Prerequisites:** Epic 1 (Project Foundation)

---

### Story 6.1: Project Creation & Listing

**Phase:** MVP  
**As a** developer,
**I want** to create and list multiple projects,
**So that** I can organize different initiatives separately.

**Acceptance Criteria:**

**Given** I have TraceRTM installed
**When** I run `rtm project create my-second-project`
**Then** A new project is created

**And** I can list all projects: `rtm project list`
**And** Project list shows: name, created_at, item_count, last_updated
**And** I can filter projects: `rtm project list --active`
**And** Project creation completes in <500ms

**Prerequisites:** Story 1.3

**Technical Notes:**
- Implement `ProjectRepository.create()` and `list()`
- Add active/archived status to projects table
- Calculate item_count with COUNT query
- Display with Rich table formatting
- Create index on (created_at)

**FRs Covered:** FR46 (create projects), FR47 (list projects)

---

### Story 6.2: Project Switching & Context

**Phase:** MVP  
**As a** developer,
**I want** to switch between projects instantly,
**So that** I can work on multiple projects without delay.

**Acceptance Criteria:**

**Given** I have multiple projects
**When** I run `rtm project switch my-second-project`
**Then** Current project is switched

**And** All subsequent commands operate on new project
**And** Current project is stored in config file
**And** I can view current project: `rtm project current`
**And** Project switch completes in <500ms

**Prerequisites:** Story 6.1

**Technical Notes:**
- Store current_project_id in config file
- Implement `ProjectRepository.set_current()`
- Update config file atomically
- Cache current project in memory
- Validate project exists before switching

**FRs Covered:** FR48 (switch projects), FR49 (current project context), NFR-P3 (project switch <500ms)

---

### Story 6.3: Cross-Project Queries

**Phase:** MVP  
**As a** developer,
**I want** to query items across all projects,
**So that** I can get a global view of my work.

**Acceptance Criteria:**

**Given** I have items in multiple projects
**When** I run `rtm view FEATURE --all-projects`
**Then** Items from all projects are displayed

**And** Results show project name for each item
**And** I can filter by project: `rtm view FEATURE --project my-project`
**And** I can search across projects: `rtm search "authentication" --all-projects`
**And** Cross-project queries complete in <1s

**Prerequisites:** Story 6.2

**Technical Notes:**
- Implement `--all-projects` flag for view commands
- Add project_name to query results
- Implement cross-project search with full-text search
- Use UNION queries for cross-project aggregation
- Create indexes on (project_id, view)

**FRs Covered:** FR50 (cross-project queries), FR51 (global search)

---

### Story 6.4: Project Archiving & Deletion

**Phase:** MVP  
**As a** developer,
**I want** to archive or delete completed projects,
**So that** I can keep my project list clean.

**Acceptance Criteria:**

**Given** I have a completed project
**When** I run `rtm project archive my-old-project`
**Then** Project is archived (not shown in default list)

**And** I can view archived projects: `rtm project list --archived`
**And** I can unarchive: `rtm project unarchive my-old-project`
**And** I can permanently delete: `rtm project delete my-old-project --permanent`
**And** Deletion requires confirmation

**Prerequisites:** Story 6.1

**Technical Notes:**
- Add archived_at timestamp to projects table
- Filter archived projects in default queries
- Implement soft delete for projects
- Cascade delete to items, links, events
- Require confirmation for permanent delete

**FRs Covered:** FR52 (archive projects), FR53 (delete projects)

---

### Story 6.5: Project Templates & Cloning

**Phase:** MVP  
**As a** developer,
**I want** to create projects from templates,
**So that** I can quickly set up new projects with standard structure.

**Acceptance Criteria:**

**Given** I have a project with standard structure
**When** I run `rtm project clone my-template --name new-project`
**Then** A new project is created with same structure

**And** Items and links are copied (not events/history)
**And** I can create templates: `rtm project template create my-template`
**And** I can list templates: `rtm project template list`
**And** Cloning completes in <5s for 1000 items

**Prerequisites:** Story 6.1

**Technical Notes:**
- Implement `ProjectRepository.clone()`
- Copy items and links with new UUIDs
- Don't copy events (fresh history)
- Implement template storage (special project type)
- Use batch operations for performance

**FRs Covered:** FR46 (project templates), FR74 (import/export)

---

### Story 6.6: Project Statistics & Dashboard

**Phase:** MVP  
**As a** developer,
**I want** to view project statistics,
**So that** I can track progress across all projects.

**Acceptance Criteria:**

**Given** I have multiple projects
**When** I run `rtm dashboard`
**Then** I see statistics for all projects

**And** Statistics include: total items, items by status, items by view, progress %
**And** I can view project-specific dashboard: `rtm dashboard --project my-project`
**And** Dashboard updates in real-time
**And** Dashboard renders in <1s

**Prerequisites:** Story 6.1

**Technical Notes:**
- Implement aggregation queries for statistics
- Use window functions for progress calculation
- Cache dashboard data for 30 seconds
- Display with Rich panels and progress bars
- Support JSON export for external dashboards

**FRs Covered:** FR51 (project dashboard), FR68-FR73 (progress tracking)

---

## Epic 7: History, Search & Progress Tracking

**Phase:** MVP  
**Goal:** Enable users to track item history, search across projects, and monitor progress in real-time.

**User Value:** Users can understand "what changed when", find anything instantly, and track project velocity.

**FRs Covered:** FR54-FR73 (Versioning, Search, Progress)

**Prerequisites:** Epic 2 (Core Item Management)

---

### Story 7.1: Event Sourcing & History Tracking

**Phase:** MVP  
**As a** developer,
**I want** to view complete history of item changes,
**So that** I can understand how my project evolved.

**Acceptance Criteria:**

**Given** I have updated an item multiple times
**When** I run `rtm history <item-id>`
**Then** I see all changes with timestamps and agents

**And** History shows: created, updated, deleted events
**And** Each event shows: timestamp, agent_id, operation, old_value, new_value
**And** I can filter by date range: `rtm history <item-id> --since 2024-01-01`
**And** History queries complete in <100ms

**Prerequisites:** Story 2.3

**Technical Notes:**
- Log all operations to event_log table
- Store event_data as JSONB with old/new values
- Implement `EventRepository.get_by_item()`
- Support time range filtering
- Create index on (item_id, timestamp)

**FRs Covered:** FR54 (version tracking), FR55 (change history), FR56 (event log)

---

### Story 7.2: Temporal Queries & Time Travel

**Phase:** MVP  
**As a** developer,
**I want** to query item state at a specific point in time,
**So that** I can see how my project looked in the past.

**Acceptance Criteria:**

**Given** I have item history
**When** I run `rtm show <item-id> --at 2024-01-01T12:00:00`
**Then** I see item state as it was at that timestamp

**And** I can query view state: `rtm view FEATURE --at 2024-01-01`
**And** I can compare states: `rtm diff <item-id> --from 2024-01-01 --to 2024-01-15`
**And** Temporal queries complete in <500ms
**And** Event replay is deterministic

**Prerequisites:** Story 7.1

**Technical Notes:**
- Implement event replay from event_log
- Use recursive CTE to reconstruct state
- Cache temporal queries for performance
- Implement diff algorithm for state comparison
- Validate event replay correctness (property-based testing)

**Technical Risks:**
- ⚠️ **UNKNOWN: Event replay performance with large histories**
  - Risk: Replaying 10K+ events to reconstruct state may exceed 500ms target
  - Mitigation: Test with large event logs, measure replay time
  - Fallback: Implement periodic snapshots (daily state snapshots) to reduce replay distance
- ⚠️ **UNKNOWN: Event replay determinism**
  - Risk: Non-deterministic event replay could produce incorrect historical state
  - Mitigation: Property-based testing to verify replay produces same state
  - Fallback: Add event sequence numbers and checksums for validation
- ⚠️ **UNKNOWN: Storage growth rate**
  - Risk: Event log may grow to 100GB+ over time, causing storage issues
  - Mitigation: Monitor event log size, implement archival strategy
  - Fallback: Compress old events, implement event log rotation

**FRs Covered:** FR57 (temporal queries), FR58 (time travel), FR59 (state reconstruction)

---

### Story 7.3: Full-Text Search

**Phase:** MVP  
**As a** developer,
**I want** to search items by title, description, and metadata,
**So that** I can find anything instantly.

**Acceptance Criteria:**

**Given** I have items with text content
**When** I run `rtm search "authentication"`
**Then** All items matching "authentication" are displayed

**And** Search includes: title, description, metadata
**And** I can filter by view: `rtm search "auth" --view FEATURE`
**And** I can filter by type: `rtm search "auth" --type feature`
**And** Search completes in <100ms for 10K items

**Prerequisites:** Story 2.2

**Technical Notes:**
- Use PostgreSQL full-text search with tsvector
- Create GIN index on tsvector column
- Implement search ranking with ts_rank
- Support phrase search and wildcards
- Create materialized view for search performance

**FRs Covered:** FR60 (full-text search), FR61 (search ranking), FR62 (search filters)

---

### Story 7.4: Advanced Filtering & Queries

**Phase:** MVP  
**As a** developer,
**I want** to filter items with complex criteria,
**So that** I can find exactly what I need.

**Acceptance Criteria:**

**Given** I have items with various properties
**When** I run `rtm view FEATURE --filter 'status=todo AND owner=me AND metadata.priority=high'`
**Then** Only matching items are displayed

**And** I can use operators: =, !=, >, <, >=, <=, LIKE, IN
**And** I can combine with AND, OR, NOT
**And** I can filter by metadata: `metadata.tags CONTAINS "security"`
**And** Complex queries complete in <200ms

**Prerequisites:** Story 2.5

**Technical Notes:**
- Implement query parser for filter expressions
- Support JSONB operators for metadata queries
- Use prepared statements for security
- Create composite indexes for common filters
- Validate filter syntax before execution

**FRs Covered:** FR63 (advanced filtering), FR64 (query operators), FR65 (metadata queries)

---

### Story 7.5: Saved Queries & Views

**Phase:** MVP  
**As a** developer,
**I want** to save frequently used queries,
**So that** I can reuse them without retyping.

**Acceptance Criteria:**

**Given** I have a complex query
**When** I run `rtm query save my-todos "view FEATURE --filter 'status=todo AND owner=me'"`
**Then** Query is saved with name "my-todos"

**And** I can execute saved query: `rtm query run my-todos`
**And** I can list saved queries: `rtm query list`
**And** I can delete saved queries: `rtm query delete my-todos`
**And** Saved queries support parameters: `rtm query run my-view --param status=in_progress`

**Prerequisites:** Story 7.4

**Technical Notes:**
- Store saved queries in config file or database
- Implement parameter substitution
- Validate query syntax before saving
- Support query templates with placeholders
- Implement `QueryManager` class

**FRs Covered:** FR66 (saved queries), FR67 (query templates)

---

### Story 7.6: Progress Calculation & Rollup

**Phase:** MVP  
**As a** developer,
**I want** automatic progress calculation based on item status,
**So that** I can track project completion.

**Acceptance Criteria:**

**Given** I have hierarchical items (epic → features → stories)
**When** I mark a story as done
**Then** Parent feature progress updates automatically

**And** Progress rolls up to epic level
**And** Progress is calculated as: (done_items / total_items) * 100
**And** I can view progress: `rtm show <epic-id> --progress`
**And** Progress updates complete in <50ms

**Prerequisites:** Story 2.6

**Technical Notes:**
- Implement progress rollup with recursive CTE
- Update parent progress on child status change
- Use database triggers for automatic updates
- Cache progress calculations
- Implement `ProgressService.calculate()`

**Technical Risks:**
- ⚠️ **UNKNOWN: Trigger performance with deep hierarchies**
  - Risk: Database triggers may cause cascading updates through 10+ levels, causing slow writes
  - Mitigation: Test with deep hierarchies (10+ levels), measure update latency
  - Fallback: Implement async progress calculation or batch updates
- ⚠️ **UNKNOWN: Cache invalidation strategy**
  - Risk: Stale progress data if cache not invalidated correctly
  - Mitigation: Implement cache invalidation on item status changes
  - Fallback: Short TTL (5 seconds) or disable caching for progress

**FRs Covered:** FR68 (progress calculation), FR69 (progress rollup), FR70 (hierarchical progress)

---

### Story 7.7: Velocity Tracking & Forecasting

**Phase:** MVP  
**As a** developer,
**I want** to track completion velocity,
**So that** I can forecast project completion.

**Acceptance Criteria:**

**Given** I have completed items over time
**When** I run `rtm velocity`
**Then** I see items completed per day/week

**And** Velocity shows: items/day, items/week, trend
**And** I can forecast completion: `rtm forecast <epic-id>`
**And** Forecast shows: estimated completion date based on velocity
**And** I can view velocity chart in terminal

**Prerequisites:** Story 7.1

**Technical Notes:**
- Calculate velocity from event_log (status changes to done)
- Use window functions for time-based aggregation
- Implement linear regression for forecasting
- Display velocity chart with Rich
- Support different time windows (day, week, month)

**FRs Covered:** FR71 (velocity tracking), FR72 (forecasting), FR73 (trend analysis)

---

### Story 7.8: Real-Time Progress Monitoring

**Phase:** MVP  
**As a** developer,
**I want** real-time progress updates,
**So that** I can monitor agent activity live.

**Acceptance Criteria:**

**Given** Agents are working on items
**When** I run `rtm watch`
**Then** I see real-time updates as items change

**And** Updates show: item title, status change, agent_id, timestamp
**And** I can filter updates: `rtm watch --view FEATURE`
**And** I can watch specific item: `rtm watch <item-id>`
**And** Updates appear within 1 second of change

**Prerequisites:** Story 7.1

**Technical Notes:**
- Implement polling mechanism (check event_log every 1s)
- Use Rich Live display for real-time updates
- Support filtering by view, type, agent
- Implement graceful shutdown (Ctrl+C)
- Consider PostgreSQL LISTEN/NOTIFY for future

**FRs Covered:** FR73 (real-time monitoring), FR42 (agent activity)

---

## Epic 8: Import/Export & Data Portability

**Phase:** MVP  
**Goal:** Enable users to import/export data in multiple formats for backup, migration, and integration.

**User Value:** Users can backup projects, migrate between environments, and integrate with external tools.

**FRs Covered:** FR74-FR82 (Data Import/Export)

**Prerequisites:** Epic 2 (Core Item Management)

---

### Story 8.1: JSON Export

**Phase:** MVP  
**As a** developer,
**I want** to export project data to JSON,
**So that** I can backup or migrate my projects.

**Acceptance Criteria:**

**Given** I have a project with data
**When** I run `rtm export --format json --output my-project.json`
**Then** All project data is exported to JSON file

**And** Export includes: projects, items, links, events, agents
**And** JSON is valid and parseable
**And** I can export specific views: `rtm export --view FEATURE --format json`
**And** Export completes in <5s for 10K items

**Prerequisites:** Story 2.2

**Technical Notes:**
- Implement `ExportService.export_json()`
- Use Pydantic `.model_dump_json()` for serialization
- Support incremental export (only changed items)
- Compress large exports with gzip
- Validate JSON structure before writing

**FRs Covered:** FR74 (export to JSON), FR75 (export formats)

---

### Story 8.2: YAML Export

**Phase:** MVP  
**As a** developer,
**I want** to export project data to YAML,
**So that** I can edit it manually or use it in CI/CD.

**Acceptance Criteria:**

**Given** I have a project with data
**When** I run `rtm export --format yaml --output my-project.yaml`
**Then** All project data is exported to YAML file

**And** YAML is human-readable and editable
**And** I can export specific items: `rtm export <item-id> --format yaml`
**And** YAML includes comments for clarity
**And** Export completes in <5s for 10K items

**Prerequisites:** Story 2.2

**Technical Notes:**
- Implement `ExportService.export_yaml()`
- Use PyYAML for serialization
- Add comments for structure clarity
- Support multi-document YAML (one per item)
- Validate YAML structure before writing

**FRs Covered:** FR76 (export to YAML), FR75 (export formats)

---

### Story 8.3: CSV Export

**Phase:** MVP  
**As a** developer,
**I want** to export items to CSV,
**So that** I can analyze data in spreadsheets.

**Acceptance Criteria:**

**Given** I have items
**When** I run `rtm export --format csv --output items.csv`
**Then** Items are exported to CSV file

**And** CSV includes: id, type, view, title, status, owner, created_at, updated_at
**And** I can customize columns: `rtm export --format csv --columns id,title,status`
**And** CSV is compatible with Excel and Google Sheets
**And** Export completes in <5s for 10K items

**Prerequisites:** Story 2.2

**Technical Notes:**
- Implement `ExportService.export_csv()`
- Use Python csv module
- Support custom column selection
- Flatten nested data (metadata as JSON string)
- Handle special characters and escaping

**FRs Covered:** FR77 (export to CSV), FR75 (export formats)

---

### Story 8.4: JSON Import

**Phase:** MVP  
**As a** developer,
**I want** to import project data from JSON,
**So that** I can restore backups or migrate projects.

**Acceptance Criteria:**

**Given** I have a JSON export file
**When** I run `rtm import --format json --input my-project.json`
**Then** All data is imported into current project

**And** Import validates data before applying
**And** I can import into new project: `rtm import --input backup.json --project new-project`
**And** Import handles conflicts (skip, overwrite, merge)
**And** Import completes in <10s for 10K items

**Prerequisites:** Story 8.1

**Technical Notes:**
- Implement `ImportService.import_json()`
- Validate with Pydantic schemas
- Use database transactions for atomicity
- Implement conflict resolution strategies
- Log import operations to event_log

**FRs Covered:** FR78 (import from JSON), FR79 (import validation)

---

### Story 8.5: CSV Import

**Phase:** MVP  
**As a** developer,
**I want** to import items from CSV,
**So that** I can bulk-create items from spreadsheets.

**Acceptance Criteria:**

**Given** I have a CSV file with items
**When** I run `rtm import --format csv --input items.csv`
**Then** Items are created from CSV rows

**And** CSV must have headers: type, view, title, description, status
**And** Import validates each row before creating
**And** Invalid rows are skipped with error report
**And** Import completes in <10s for 1000 items

**Prerequisites:** Story 2.1

**Technical Notes:**
- Implement `ImportService.import_csv()`
- Validate CSV headers and data types
- Use batch operations for performance
- Generate error report for invalid rows
- Support dry-run mode: `--dry-run`

**FRs Covered:** FR80 (import from CSV), FR79 (import validation)

---

### Story 8.6: Incremental Sync & Merge

**Phase:** MVP  
**As a** developer,
**I want** to sync changes between projects,
**So that** I can keep multiple environments in sync.

**Acceptance Criteria:**

**Given** I have two projects (local and remote)
**When** I run `rtm sync --from remote-backup.json`
**Then** Only changed items are imported

**And** Sync detects conflicts (same item modified in both)
**And** I can choose conflict resolution: skip, overwrite, merge
**And** Sync is bidirectional: `rtm sync --bidirectional`
**And** Sync completes in <5s for 1000 changed items

**Prerequisites:** Story 8.4

**Technical Notes:**
- Implement `SyncService.sync()`
- Compare versions to detect changes
- Implement 3-way merge for conflicts
- Use event_log for change detection
- Support dry-run mode

**FRs Covered:** FR81 (incremental sync), FR82 (conflict resolution)

---




## FR Coverage Matrix

| FR ID | Requirement | Epic | Story | Status |
|-------|-------------|------|-------|--------|
| FR1 | 8 core views | Epic 2 | 2.1 | ✅ |
| FR2 | View items by view | Epic 3 | 3.1 | ✅ |
| FR3 | Switch views | Epic 3 | 3.1 | ✅ |
| FR4 | View metadata | Epic 2 | 2.5 | ✅ |
| FR5 | View filtering | Epic 3 | 3.2 | ✅ |
| FR6 | Create items | Epic 2 | 2.1 | ✅ |
| FR7 | Item types | Epic 2 | 2.1 | ✅ |
| FR8 | View item details | Epic 2 | 2.2 | ✅ |
| FR9 | Edit item properties | Epic 2 | 2.3 | ✅ |
| FR10 | Delete items | Epic 2 | 2.4 | ✅ |
| FR11 | Custom metadata | Epic 2 | 2.5 | ✅ |
| FR12 | Hierarchical relationships | Epic 2 | 2.6 | ✅ |
| FR13 | Status tracking | Epic 2 | 2.7 | ✅ |
| FR14 | Bulk operations | Epic 2 | 2.8 | ✅ |
| FR15 | Item validation | Epic 2 | 2.1 | ✅ |
| FR16 | Create links | Epic 4 | 4.1 | ✅ |
| FR17 | Link types | Epic 4 | 4.1 | ✅ |
| FR18 | Traverse links | Epic 4 | 4.2 | ✅ |
| FR19 | Bidirectional navigation | Epic 4 | 4.2, 4.5 | ✅ |
| FR20 | Link metadata | Epic 4 | 4.3 | ✅ |
| FR21 | Delete links | Epic 4 | 4.4 | ✅ |
| FR22 | Dependency validation | Epic 4 | 4.6 | ✅ |
| FR23 | CLI commands | Epic 3 | 3.1-3.7 | ✅ |
| FR24 | Filter by criteria | Epic 3 | 3.2 | ✅ |
| FR25 | Output formats | Epic 3 | 3.3 | ✅ |
| FR26 | JSON/YAML export | Epic 3 | 3.3 | ✅ |
| FR27 | Shell completion | Epic 3 | 3.4 | ✅ |
| FR28 | Autocomplete | Epic 3 | 3.4 | ✅ |
| FR29 | Help documentation | Epic 3 | 3.5 | ✅ |
| FR30 | Command examples | Epic 3 | 3.5 | ✅ |
| FR31 | Command aliases | Epic 3 | 3.6 | ✅ |
| FR32 | Shortcuts | Epic 3 | 3.6 | ✅ |
| FR33 | CLI responsiveness | Epic 3 | 3.7 | ✅ |
| FR34 | Progress indicators | Epic 3 | 3.7 | ✅ |
| FR35 | Error messages | Epic 1 | 1.6 | ✅ |
| FR36 | Agent registration | Epic 5 | 5.1 | ✅ |
| FR37 | Agent authentication | Epic 5 | 5.1 | ✅ |
| FR38 | Python API | Epic 5 | 5.2 | ✅ |
| FR39 | Programmatic access | Epic 5 | 5.2 | ✅ |
| FR40 | Concurrent operations | Epic 5 | 5.3 | ✅ |
| FR41 | Optimistic locking | Epic 5 | 5.3 | ✅ |
| FR42 | Agent activity logging | Epic 5 | 5.4 | ✅ |
| FR43 | Agent monitoring | Epic 5 | 5.4, 5.8 | ✅ |
| FR44 | Batch operations | Epic 5 | 5.5 | ✅ |
| FR45 | Task assignment | Epic 5 | 5.6 | ✅ |
| FR46 | Create projects | Epic 6 | 6.1, 6.5 | ✅ |
| FR47 | List projects | Epic 6 | 6.1 | ✅ |
| FR48 | Switch projects | Epic 6 | 6.2 | ✅ |
| FR49 | Current project context | Epic 6 | 6.2 | ✅ |
| FR50 | Cross-project queries | Epic 6 | 6.3 | ✅ |
| FR51 | Global search | Epic 6 | 6.3, 6.6 | ✅ |
| FR52 | Archive projects | Epic 6 | 6.4 | ✅ |
| FR53 | Delete projects | Epic 6 | 6.4 | ✅ |
| FR54 | Version tracking | Epic 7 | 7.1 | ✅ |
| FR55 | Change history | Epic 7 | 7.1 | ✅ |
| FR56 | Event log | Epic 7 | 7.1 | ✅ |
| FR57 | Temporal queries | Epic 7 | 7.2 | ✅ |
| FR58 | Time travel | Epic 7 | 7.2 | ✅ |
| FR59 | State reconstruction | Epic 7 | 7.2 | ✅ |
| FR60 | Full-text search | Epic 7 | 7.3 | ✅ |
| FR61 | Search ranking | Epic 7 | 7.3 | ✅ |
| FR62 | Search filters | Epic 7 | 7.3 | ✅ |
| FR63 | Advanced filtering | Epic 7 | 7.4 | ✅ |
| FR64 | Query operators | Epic 7 | 7.4 | ✅ |
| FR65 | Metadata queries | Epic 7 | 7.4 | ✅ |
| FR66 | Saved queries | Epic 7 | 7.5 | ✅ |
| FR67 | Query templates | Epic 7 | 7.5 | ✅ |
| FR68 | Progress calculation | Epic 7 | 7.6 | ✅ |
| FR69 | Progress rollup | Epic 7 | 7.6 | ✅ |
| FR70 | Hierarchical progress | Epic 7 | 7.6 | ✅ |
| FR71 | Velocity tracking | Epic 7 | 7.7 | ✅ |
| FR72 | Forecasting | Epic 7 | 7.7 | ✅ |
| FR73 | Trend analysis | Epic 7 | 7.7, 7.8 | ✅ |
| FR74 | Export to JSON | Epic 8 | 8.1 | ✅ |
| FR75 | Export formats | Epic 8 | 8.1, 8.2, 8.3 | ✅ |
| FR76 | Export to YAML | Epic 8 | 8.2 | ✅ |
| FR77 | Export to CSV | Epic 8 | 8.3 | ✅ |
| FR78 | Import from JSON | Epic 8 | 8.4 | ✅ |
| FR79 | Import validation | Epic 8 | 8.4, 8.5 | ✅ |
| FR80 | Import from CSV | Epic 8 | 8.5 | ✅ |
| FR81 | Incremental sync | Epic 8 | 8.6 | ✅ |
| FR82 | Conflict resolution | Epic 8 | 8.6 | ✅ |
| FR83 | Initialize project | Epic 1 | 1.1, 1.3 | ✅ |
| FR84 | Create database | Epic 1 | 1.2 | ✅ |
| FR85 | Configure settings | Epic 1 | 1.4 | ✅ |
| FR86 | Default preferences | Epic 1 | 1.4 | ✅ |
| FR87 | Project-specific config | Epic 1 | 1.4 | ✅ |
| FR88 | Backup & restore | Epic 1 | 1.5 | ✅ |

**Total FRs:** 88
**FRs Covered:** 88 (100%)

---

## Summary

**Epic Breakdown Complete:** ✅

**Total Epics:** 8
**Total Stories:** 55
**FR Coverage:** 88/88 (100%)

### Epic Summary

| Epic | Title | Stories | FRs | User Value |
|------|-------|---------|-----|------------|
| Epic 1 | Project Foundation & Setup | 6 | FR83-88 | Install, configure, and initialize TraceRTM |
| Epic 2 | Core Item Management | 8 | FR6-15, FR1-5 | Create, read, update, delete items across views |
| Epic 3 | Multi-View Navigation & CLI | 7 | FR1-5, FR23-35 | Navigate views with powerful CLI interface |
| Epic 4 | Cross-View Linking | 6 | FR16-22 | Link items across views, trace relationships |
| Epic 5 | Agent Coordination | 8 | FR36-45 | Enable 1-1000 concurrent AI agents |
| Epic 6 | Multi-Project Management | 6 | FR46-53 | Manage 10+ projects simultaneously |
| Epic 7 | History, Search & Progress | 9 | FR54-73 | Track history, search, monitor progress |
| Epic 8 | Import/Export & Data Portability | 5 | FR74-82 | Backup, migrate, integrate with external tools |

### Implementation Sequence

**Recommended Order:**
1. **Epic 1** (Foundation) - Required for all other epics
2. **Epic 2** (Core Items) - Core functionality
3. **Epic 3** (CLI) - User interface
4. **Epic 4** (Linking) - Relationships
5. **Epic 5** (Agents) - Concurrency & API
6. **Epic 6** (Multi-Project) - Scale to multiple projects
7. **Epic 7** (History/Search) - Advanced features
8. **Epic 8** (Import/Export) - Data portability

**Parallel Tracks Possible:**
- Epic 3 (CLI) can be developed alongside Epic 2 (Core Items)
- Epic 5 (Agents) can be developed alongside Epic 4 (Linking)
- Epic 7 (History/Search) can be developed alongside Epic 6 (Multi-Project)

### Story Sizing

**Small Stories (1-2 hours):** 15 stories
- Configuration, simple CRUD, basic CLI commands

**Medium Stories (2-4 hours):** 30 stories
- Complex queries, linking, agent coordination

**Large Stories (4-8 hours):** 10 stories
- Event sourcing, temporal queries, sync/merge

**Average Story Size:** ~3 hours (with AI assistance)

### Technical Debt & Future Enhancements

**Phase 2 Enhancements (Post-MVP):**
- Neo4j integration for graph queries (ADR-001)
- Redis caching for performance (architecture.md)
- TimescaleDB for time-series data (architecture.md)
- WebSocket support for real-time updates (Story 7.8)
- GraphQL API for flexible queries
- Web UI for visualization
- Mobile app for on-the-go access

**Known Technical Debt:**
- Event sourcing replay performance (optimize with snapshots)
- Full-text search ranking (improve with custom scoring)
- Cycle detection performance (cache dependency graph)

### Quality Gates

**Before Starting Implementation:**
- ✅ PRD complete (88 FRs)
- ✅ Architecture complete (10 ADRs)
- ✅ Test strategy complete (testability review)
- ✅ Epic breakdown complete (55 stories)
- ⏭️ Test framework setup (pytest, fixtures, factories)

**Per-Story Quality Gates:**
- Unit tests written (90%+ coverage for business logic)
- Integration tests written (80%+ coverage for database operations)
- E2E tests written (100% of critical workflows)
- Code reviewed (by AI or human)
- Documentation updated (docstrings, README)

**Per-Epic Quality Gates:**
- All stories complete
- All FRs covered
- All tests passing
- Performance benchmarks met
- User acceptance criteria validated

---

_This epic breakdown provides a complete roadmap for implementing TraceRTM. Each story is sized for a single dev agent to complete in one focused session. All 88 FRs are mapped to specific stories with clear acceptance criteria and technical implementation notes._

_**Next Steps:** Begin implementation with Epic 1 (Project Foundation & Setup), setting up the database, CLI framework, and configuration management. Use the test framework architecture (docs/test-framework-architecture.md) to write tests alongside implementation._

_**For Implementation:** Use the architecture document (docs/architecture.md) for technical decisions, the test design document (docs/test-design-system.md) for testing strategy, and this epic breakdown for story-by-story implementation guidance._
