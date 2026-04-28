# TraceRTM - Architecture Document

**Author:** BMad
**Date:** 2025-11-20
**Version:** 1.0
**Status:** MVP Architecture

**Related Documents:**
- **PRD**: `docs/PRD.md` - 88 functional requirements, 23 NFRs
- **Epics & Stories**: `docs/epics.md` - Maps all FRs to 55 implementable stories
- **UX Design**: `docs/ux-design-specification.md` - CLI/TUI patterns for architecture components
- **Test Design**: `docs/test-design-system.md` - Validates architectural testability (9/10 score)
- **Test Framework**: `docs/test-framework-architecture.md` - pytest implementation for this architecture
- **Implementation Readiness**: `docs/implementation-readiness-report-2025-11-21.md` - 98% architecture completeness

---

## Executive Summary

TraceRTM is an agent-native, multi-view requirements traceability system built on a **PostgreSQL-backed, Python 3.12+ CLI architecture** optimized for 1-1000 concurrent AI agents managing multiple complex projects. The architecture prioritizes **sub-second query performance**, **optimistic concurrency control**, and **structured data access** to enable seamless human-agent collaboration at massive scale.

**Core Architectural Principles:**

1. **Agent-First Design**: Every component designed for programmatic access (Python API, JSON/YAML I/O, structured queries)
2. **Performance-Driven**: PostgreSQL with aggressive indexing, query optimization, and caching for <1s responses on 10K+ items
3. **Local-First**: Zero cloud dependencies, all data local, works offline
4. **Multi-View State Space**: 8 core views (Feature, Code, Wireframe, API, Test, Database, Roadmap, Progress) with bidirectional linking
5. **Concurrency-Safe**: Optimistic locking, conflict detection, transaction isolation for 1000+ concurrent agent operations
6. **CLI-Native**: Typer-based CLI with Rich output, shell completion, and composable commands

**Technology Stack:**

- **Language**: Python 3.12+ (type hints, match/case, async support)
- **Database**: PostgreSQL 16+ (JSONB, CTEs, window functions, full-text search)
- **ORM**: SQLAlchemy 2.0+ (async, type-safe, migration management via Alembic)
- **Validation**: Pydantic v2 (data validation, serialization, agent-friendly schemas)
- **CLI**: Typer (type-safe commands) + Rich (beautiful terminal output)
- **Testing**: pytest + pytest-asyncio + pytest-cov (80%+ coverage target)
- **Linting**: ruff (fast linter/formatter) + ty (type checking)

**Key Architectural Decisions:**

1. **PostgreSQL over Neo4j for MVP**: Relational integrity + JSONB flexibility sufficient for 8 views; defer graph DB to Phase 2
2. **Optimistic Locking over Pessimistic**: Better for agent concurrency (1000+ agents); conflicts rare with item-level granularity
3. **Synchronous CLI + Async Core**: CLI commands synchronous for simplicity; core engine async for concurrent agent operations
4. **View-as-Query Pattern**: Views are dynamic queries over unified item table, not separate tables
5. **Atomic Item Model**: Everything is an Item with type/view metadata; links are first-class entities
6. **Event Log for History**: Append-only event log for versioning; current state materialized for performance

---

## Project Initialization

### Prerequisites

**System Requirements:**
- macOS 12+ or Linux (Ubuntu 20.04+, Debian 11+)
- Python 3.12 or higher
- PostgreSQL 16 or higher
- 8GB RAM minimum (16GB recommended for large projects)
- 10GB disk space (scales with project size)

**Development Tools:**
- Git 2.30+
- pip 23.0+ or pipx
- PostgreSQL client tools (psql, pg_dump)
- Optional: Docker (for isolated PostgreSQL)

### Installation

```bash
# Via pip (recommended for developers)
pip install tracertm

# Via pipx (isolated environment)
pipx install tracertm

# From source (for contributors)
git clone https://github.com/bmad/tracertm
cd tracertm
pip install -e ".[dev]"  # Includes dev dependencies

# Verify installation
rtm --version
rtm --help
```

### Initial Setup

```bash
# Initialize PostgreSQL database
# Option 1: Local PostgreSQL
createdb tracertm

# Option 2: Docker PostgreSQL
docker run -d \
  --name tracertm-db \
  -e POSTGRES_PASSWORD=tracertm \
  -e POSTGRES_DB=tracertm \
  -p 5432:5432 \
  postgres:16-alpine

# Configure TraceRTM
rtm config init
# Creates ~/.tracertm/config.yaml with defaults

# Edit config to set database URL
# config.yaml:
# database_url: "postgresql://localhost/tracertm"
# default_project: null
# output_format: "table"  # table, json, yaml, markdown, csv

# Initialize first project
rtm project init my-first-project
# Creates project in database
# Sets up 8 core views
# Creates default configuration

# Verify setup
rtm project list
rtm view feature  # Should show empty feature view
```

### Project Structure

```
~/.tracertm/
├── config.yaml              # Global configuration
├── projects/                # Project-specific configs (optional)
│   ├── project-a.yaml
│   └── project-b.yaml
└── cache/                   # Query cache (optional)

# Database structure (PostgreSQL)
tracertm (database)
├── projects                 # Project metadata
├── items                    # All items (features, code, tests, etc.)
├── links                    # Cross-view relationships
├── events                   # Event log for history/versioning
├── agents                   # Agent registry and activity log
└── queries                  # Saved queries
```

---

## Decision Summary

| Category | Decision | Version | Affects FRs | Rationale |
| -------- | -------- | ------- | ----------- | --------- |
| **Database** | PostgreSQL 16+ | 16.x | All | Relational integrity + JSONB flexibility + proven at scale; defer Neo4j to Phase 2 |
| **ORM** | SQLAlchemy 2.0+ | 2.0.x | All data access | Type-safe, async support, excellent migration management via Alembic |
| **Validation** | Pydantic v2 | 2.x | All data models | Fast validation, serialization, agent-friendly schemas, type safety |
| **CLI Framework** | Typer | 0.12.x | FR23-FR35 | Type-safe commands, auto-documentation, excellent DX |
| **Terminal Output** | Rich | 13.x | FR31, FR34 | Beautiful tables, progress bars, syntax highlighting |
| **Concurrency** | Optimistic Locking | - | FR42-FR43, NFR-P5 | Better for 1000+ agents; conflicts rare with item-level granularity |
| **Async Strategy** | Async core + Sync CLI | - | FR36-FR45, NFR-P5 | CLI synchronous for simplicity; core async for agent concurrency |
| **View Pattern** | View-as-Query | - | FR1-FR5 | Dynamic queries over unified item table; flexible, performant |
| **Item Model** | Atomic Item + Links | - | FR6-FR22 | Everything is an Item; links are first-class; simple, extensible |


## FR Category to Architecture Mapping

| FR Category | Primary Components | Database Tables | Key Patterns |
| ----------- | ------------------ | --------------- | ------------ |
| **Multi-View System** (FR1-FR5) | ViewEngine, ViewRegistry | items (with view metadata) | View-as-Query pattern |
| **Item Management** (FR6-FR15) | ItemManager, ItemRepository | items, item_hierarchy | Repository pattern, Unit of Work |
| **Cross-View Linking** (FR16-FR22) | LinkManager, LinkRepository | links, link_types | Bidirectional graph traversal |
| **CLI Interface** (FR23-FR35) | CLI commands (Typer), OutputFormatter | - | Command pattern, Strategy pattern (output) |
| **Agent-Native API** (FR36-FR45) | AgentAPI, AgentLogger, ConcurrencyManager | agents, agent_activity | Optimistic locking, Event logging |
| **Multi-Project** (FR46-FR53) | ProjectManager, ProjectContext | projects, project_config | Context manager pattern |
| **Versioning** (FR54-FR59) | EventStore, TemporalQuery | events, snapshots | Event sourcing lite, CQRS |
| **Search & Filter** (FR60-FR67) | SearchEngine, QueryBuilder | items (with tsvector), saved_queries | PostgreSQL full-text search |
| **Progress Tracking** (FR68-FR73) | ProgressCalculator, MetricsCollector | items (with progress cache) | Materialized view pattern |
| **Import/Export** (FR74-FR82) | ImportExport, FormatAdapters | - | Adapter pattern, Strategy pattern |
| **Configuration** (FR83-FR88) | ConfigManager, ProjectInitializer | projects, config | Singleton pattern, Builder pattern |

---

## Technology Stack Details

### Core Technologies

**Python 3.12+**
- **Why**: Modern features (match/case, type hints, async), rich ecosystem, agent-friendly
- **Key Features Used**:
  - Type hints throughout for IDE support and ty validation
  - Async/await for concurrent agent operations
  - Match/case for clean command routing
  - Dataclasses and Pydantic for data models
- **Version Constraint**: `>=3.12,<4.0` (use latest 3.x features)

**PostgreSQL 16+**
- **Why**: Relational integrity, JSONB flexibility, proven at 10K+ items, excellent full-text search
- **Key Features Used**:
  - JSONB for flexible item metadata (different views have different fields)
  - CTEs (Common Table Expressions) for recursive hierarchy queries
  - Window functions for progress calculation
  - Full-text search (tsvector/tsquery) for FR60-FR67
  - Partial indexes for view-specific queries
  - Row-level locking for optimistic concurrency
- **Version Constraint**: `>=16.0` (use latest features)
- **Extensions**: `pg_trgm` (fuzzy matching), `btree_gin` (multi-column indexes)

**SQLAlchemy 2.0+**
- **Why**: Type-safe ORM, async support, excellent migration management
- **Key Features Used**:
  - Async engine and sessions for concurrent operations
  - Declarative models with type hints
  - Relationship loading strategies (lazy, eager, selectin)
  - Query optimization with `select()` API
  - Alembic integration for schema migrations
- **Version Constraint**: `>=2.0,<3.0`
- **Plugins**: `alembic` (migrations), `asyncpg` (async PostgreSQL driver)

**Pydantic v2**
- **Why**: Fast validation, serialization, agent-friendly schemas, type safety
- **Key Features Used**:
  - Data validation for all inputs (CLI, API, import)
  - JSON/YAML serialization for agent consumption
  - Type coercion and validation errors
  - Settings management (config.yaml parsing)
- **Version Constraint**: `>=2.0,<3.0`

**Typer**
- **Why**: Type-safe CLI framework, auto-documentation, excellent DX
- **Key Features Used**:
  - Type-annotated command functions
  - Automatic `--help` generation
  - Shell completion (Bash, Zsh, Fish)
  - Command groups and subcommands
  - Callback hooks for global options
- **Version Constraint**: `>=0.12,<1.0`

**Rich**
- **Why**: Beautiful terminal output, tables, progress bars, syntax highlighting
- **Key Features Used**:
  - Tables for item listings
  - Progress bars for bulk operations
  - Syntax highlighting for JSON/YAML output
  - Console markup for colored output
  - Live displays for real-time progress
- **Version Constraint**: `>=13.0,<14.0`

### Development & Testing Stack

**pytest + pytest-asyncio + pytest-cov**
- **Why**: Industry standard, async support, coverage reporting
- **Usage**:
  - Unit tests for all core logic
  - Integration tests for database operations
  - CLI tests using Typer's testing utilities
  - 80%+ coverage target (NFR-M1)
- **Version Constraints**: `pytest>=8.0`, `pytest-asyncio>=0.23`, `pytest-cov>=4.0`

**ruff + ty**
- **Why**: Ruff is 10-100x faster than pylint/flake8; ty for type safety
- **Usage**:
  - Ruff for linting and formatting (replaces black, isort, flake8)
  - Mypy for static type checking
  - Pre-commit hooks for automatic checks
- **Version Constraints**: `ruff>=0.1`, `ty>=0.0.2`

**Alembic**
- **Why**: Database migration management, version control for schema
- **Usage**:
  - Auto-generate migrations from SQLAlchemy models
  - Upgrade/downgrade database schema
  - Migration history tracking
- **Version Constraint**: `>=1.13,<2.0`

### Optional Dependencies (Phase 2+)

**Neo4j** (Phase 2 - Advanced graph queries)
- For PageRank, community detection, advanced relationship analysis
- `neo4j>=5.0` + `neomodel>=5.0`

**Redis** (Phase 2 - Caching)
- For query result caching, session management
- `redis>=5.0` + `hiredis>=2.0`

**TimescaleDB** (Phase 2 - Time-series metrics)
- For agent performance analytics, velocity tracking
- PostgreSQL extension, no additional Python deps

---

## Data Architecture

### Core Data Model

**Unified Item Model** (Atomic Item Pattern)

Every entity in TraceRTM is an **Item** with:
- **Core Fields**: `id`, `project_id`, `type`, `view`, `title`, `description`, `status`, `owner`, `created_at`, `updated_at`, `version`
- **Hierarchy**: `parent_id` (self-referential foreign key for Epic → Feature → Story → Task)
- **Metadata**: `metadata` (JSONB) for view-specific fields
- **Search**: `search_vector` (tsvector) for full-text search
- **Progress**: `progress` (float 0-1) cached from children

**Item Types by View:**
- **FEATURE**: epic, feature, story, task
- **CODE**: module, file, class, function
- **WIREFRAME**: screen, component, element
- **API**: service, endpoint, parameter
- **TEST**: suite, case, assertion
- **DATABASE**: schema, table, column
- **ROADMAP**: milestone, release, sprint
- **PROGRESS**: (computed view, no distinct types)

**Link Model** (First-Class Relationships)

Links connect items across views:
- **Core Fields**: `id`, `project_id`, `source_item_id`, `target_item_id`, `link_type`, `created_at`, `created_by`
- **Link Types**: `implements`, `tests`, `designs`, `depends_on`, `blocks`, `relates_to`
- **Bidirectional**: Queries can traverse both directions (source → target, target → source)

**Event Model** (Event Sourcing Lite)

All changes logged as events:
- **Core Fields**: `id`, `project_id`, `item_id`, `event_type`, `event_data` (JSONB), `timestamp`, `agent_id`
- **Event Types**: `item_created`, `item_updated`, `item_deleted`, `link_created`, `link_deleted`, `status_changed`
- **Purpose**: History (FR54-FR59), temporal queries, audit trail, rollback capability

### Database Schema

```sql
-- Projects table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    config JSONB,  -- Project-specific configuration
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Items table (unified model for all views)
CREATE TABLE items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,  -- epic, feature, story, task, file, class, etc.
    view VARCHAR(50) NOT NULL,  -- FEATURE, CODE, WIREFRAME, API, TEST, DATABASE, ROADMAP, PROGRESS
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'todo',  -- todo, in_progress, blocked, complete, cancelled
    owner VARCHAR(255),  -- User or agent ID
    parent_id UUID REFERENCES items(id) ON DELETE CASCADE,  -- Hierarchy
    metadata JSONB,  -- View-specific fields
    progress FLOAT DEFAULT 0.0,  -- Cached progress (0.0-1.0)
    search_vector tsvector,  -- Full-text search
    version INTEGER DEFAULT 1,  -- Optimistic locking
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255),  -- User or agent ID
    updated_by VARCHAR(255)
);

-- Indexes for performance
CREATE INDEX idx_items_project_view ON items(project_id, view);
CREATE INDEX idx_items_project_type ON items(project_id, type);
CREATE INDEX idx_items_project_status ON items(project_id, status);
CREATE INDEX idx_items_parent ON items(parent_id);
CREATE INDEX idx_items_search ON items USING GIN(search_vector);
CREATE INDEX idx_items_metadata ON items USING GIN(metadata);

-- Links table (cross-view relationships)
CREATE TABLE links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    source_item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    target_item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    link_type VARCHAR(50) NOT NULL,  -- implements, tests, designs, depends_on, blocks
    metadata JSONB,  -- Optional link metadata
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255),
    UNIQUE(source_item_id, target_item_id, link_type)  -- Prevent duplicate links
);

CREATE INDEX idx_links_source ON links(source_item_id);
CREATE INDEX idx_links_target ON links(target_item_id);
CREATE INDEX idx_links_type ON links(link_type);

-- Events table (event sourcing for history)
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    item_id UUID REFERENCES items(id) ON DELETE SET NULL,  -- NULL for project-level events
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB NOT NULL,  -- Full event payload
    timestamp TIMESTAMP DEFAULT NOW(),
    agent_id VARCHAR(255)  -- User or agent ID
);

CREATE INDEX idx_events_project ON events(project_id, timestamp DESC);
CREATE INDEX idx_events_item ON events(item_id, timestamp DESC);
CREATE INDEX idx_events_agent ON events(agent_id, timestamp DESC);

-- Agents table (agent registry)
CREATE TABLE agents (
    id VARCHAR(255) PRIMARY KEY,  -- Agent identifier
    name VARCHAR(255),
    type VARCHAR(50),  -- implementation, testing, documentation, etc.
    config JSONB,  -- Agent-specific configuration
    created_at TIMESTAMP DEFAULT NOW(),
    last_active TIMESTAMP
);

-- Agent activity log
CREATE TABLE agent_activity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id VARCHAR(255) NOT NULL REFERENCES agents(id),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL,  -- query, create, update, delete
    item_id UUID REFERENCES items(id) ON DELETE SET NULL,
    details JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_agent_activity_agent ON agent_activity(agent_id, timestamp DESC);
CREATE INDEX idx_agent_activity_project ON agent_activity(project_id, timestamp DESC);

-- Saved queries table
CREATE TABLE saved_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    query_filter JSONB NOT NULL,  -- Structured query filter
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255)
);
```

### Query Patterns for Performance

**View Queries** (FR1-FR5)
```sql
-- Get all items in FEATURE view for a project
SELECT * FROM items
WHERE project_id = $1 AND view = 'FEATURE'
ORDER BY created_at DESC;

-- Get hierarchy (Epic → Feature → Story → Task)
WITH RECURSIVE item_tree AS (
    SELECT *, 0 as level
    FROM items
    WHERE project_id = $1 AND view = 'FEATURE' AND parent_id IS NULL
    UNION ALL
    SELECT i.*, t.level + 1
    FROM items i
    JOIN item_tree t ON i.parent_id = t.id
)
SELECT * FROM item_tree ORDER BY level, created_at;
```

**Progress Calculation** (FR68-FR73)
```sql
-- Calculate progress for parent item from children
WITH child_progress AS (
    SELECT parent_id, AVG(progress) as avg_progress
    FROM items
    WHERE parent_id IS NOT NULL
    GROUP BY parent_id
)
UPDATE items i
SET progress = cp.avg_progress
FROM child_progress cp
WHERE i.id = cp.parent_id;
```

**Cross-View Linking** (FR16-FR22)
```sql
-- Get all code files that implement a feature
SELECT i.*
FROM items i
JOIN links l ON i.id = l.target_item_id
WHERE l.source_item_id = $1  -- feature ID
  AND l.link_type = 'implements'
  AND i.view = 'CODE';

-- Bidirectional: Get feature implemented by a code file
SELECT i.*
FROM items i
JOIN links l ON i.id = l.source_item_id
WHERE l.target_item_id = $1  -- code file ID
  AND l.link_type = 'implements'
  AND i.view = 'FEATURE';
```

**Full-Text Search** (FR60-FR67)
```sql
-- Search across all items in a project
SELECT *
FROM items
WHERE project_id = $1
  AND search_vector @@ to_tsquery('english', $2)
ORDER BY ts_rank(search_vector, to_tsquery('english', $2)) DESC;

-- Update search vector (trigger on insert/update)
CREATE OR REPLACE FUNCTION update_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := to_tsvector('english',
        COALESCE(NEW.title, '') || ' ' ||
        COALESCE(NEW.description, '') || ' ' ||
        COALESCE(NEW.metadata::text, '')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER items_search_vector_update
BEFORE INSERT OR UPDATE ON items
FOR EACH ROW EXECUTE FUNCTION update_search_vector();
```

---


## Implementation Patterns

These patterns ensure consistent implementation across all AI agents working on TraceRTM.

### 1. Repository Pattern (Data Access)

**Purpose**: Centralize data access logic, provide clean API for agents

**Pattern**:
```python
# tracertm/repositories/item_repository.py
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from tracertm.models import Item
from tracertm.schemas import ItemCreate, ItemUpdate

class ItemRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, project_id: UUID, data: ItemCreate) -> Item:
        """Create new item with optimistic locking."""
        item = Item(project_id=project_id, **data.model_dump(), version=1)
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def get_by_id(self, item_id: UUID) -> Optional[Item]:
        """Get item by ID."""
        result = await self.session.execute(
            select(Item).where(Item.id == item_id)
        )
        return result.scalar_one_or_none()

    async def update(self, item_id: UUID, data: ItemUpdate, expected_version: int) -> Item:
        """Update item with optimistic locking."""
        item = await self.get_by_id(item_id)
        if not item:
            raise ValueError(f"Item {item_id} not found")
        if item.version != expected_version:
            raise ConcurrencyError(f"Item {item_id} was modified by another agent")

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(item, key, value)
        item.version += 1

        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def get_by_view(self, project_id: UUID, view: str) -> List[Item]:
        """Get all items in a view."""
        result = await self.session.execute(
            select(Item)
            .where(Item.project_id == project_id, Item.view == view)
            .order_by(Item.created_at.desc())
        )
        return list(result.scalars().all())
```

**Agent Usage**:
```python
# Agent code
from tracertm import ItemRepository, ItemCreate

async with get_session() as session:
    repo = ItemRepository(session)
    item = await repo.create(
        project_id=project.id,
        data=ItemCreate(
            type="feature",
            view="FEATURE",
            title="User Authentication",
            description="Implement OAuth 2.0",
            status="todo"
        )
    )
```

### 2. Service Layer Pattern (Business Logic)

**Purpose**: Encapsulate business logic, coordinate multiple repositories

**Pattern**:
```python
# tracertm/services/item_service.py
from tracertm.repositories import ItemRepository, LinkRepository, EventRepository
from tracertm.schemas import ItemCreate, LinkCreate

class ItemService:
    def __init__(self, session: AsyncSession):
        self.items = ItemRepository(session)
        self.links = LinkRepository(session)
        self.events = EventRepository(session)

    async def create_item_with_links(
        self,
        project_id: UUID,
        item_data: ItemCreate,
        link_to: List[UUID],
        link_type: str,
        agent_id: str
    ) -> Item:
        """Create item and establish links in one transaction."""
        # Create item
        item = await self.items.create(project_id, item_data)

        # Create links
        for target_id in link_to:
            await self.links.create(
                project_id=project_id,
                data=LinkCreate(
                    source_item_id=item.id,
                    target_item_id=target_id,
                    link_type=link_type
                )
            )

        # Log event
        await self.events.log(
            project_id=project_id,
            item_id=item.id,
            event_type="item_created",
            event_data={"item": item.model_dump(), "links": link_to},
            agent_id=agent_id
        )

        return item
```

### 3. CLI Command Pattern

**Purpose**: Consistent CLI command structure for all agents

**Pattern**:
```python
# tracertm/cli/commands/item.py
import typer
from rich.console import Console
from rich.table import Table
from tracertm.core import get_current_project, get_session
from tracertm.services import ItemService
from tracertm.schemas import ItemCreate

app = typer.Typer()
console = Console()

@app.command()
def create(
    type: str = typer.Argument(..., help="Item type (epic, feature, story, task)"),
    title: str = typer.Argument(..., help="Item title"),
    description: str = typer.Option("", help="Item description"),
    status: str = typer.Option("todo", help="Initial status"),
    view: str = typer.Option("FEATURE", help="View (FEATURE, CODE, etc.)"),
    format: str = typer.Option("table", help="Output format (table, json, yaml)")
):
    """Create a new item."""
    project = get_current_project()

    async with get_session() as session:
        service = ItemService(session)
        item = await service.create_item_with_links(
            project_id=project.id,
            item_data=ItemCreate(
                type=type,
                view=view,
                title=title,
                description=description,
                status=status
            ),
            link_to=[],
            link_type="",
            agent_id="cli-user"
        )

    # Output formatting
    if format == "json":
        console.print_json(item.model_dump_json())
    elif format == "yaml":
        import yaml
        console.print(yaml.dump(item.model_dump()))
    else:  # table
        table = Table(title="Created Item")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("ID", str(item.id))
        table.add_row("Type", item.type)
        table.add_row("Title", item.title)
        table.add_row("Status", item.status)
        console.print(table)
```

### 4. Optimistic Locking Pattern (Concurrency)

**Purpose**: Prevent conflicts when 1000+ agents update same items

**Pattern**:
```python
# tracertm/core/concurrency.py
from sqlalchemy.exc import IntegrityError

class ConcurrencyError(Exception):
    """Raised when optimistic lock fails."""
    pass

async def update_with_retry(
    repo: ItemRepository,
    item_id: UUID,
    update_fn: callable,
    max_retries: int = 3
) -> Item:
    """Update item with automatic retry on conflict."""
    for attempt in range(max_retries):
        try:
            # Get current item
            item = await repo.get_by_id(item_id)
            if not item:
                raise ValueError(f"Item {item_id} not found")

            # Apply update function
            updated_data = update_fn(item)

            # Update with version check
            return await repo.update(
                item_id=item_id,
                data=updated_data,
                expected_version=item.version
            )
        except ConcurrencyError:
            if attempt == max_retries - 1:
                raise
            # Retry with exponential backoff
            await asyncio.sleep(0.1 * (2 ** attempt))

    raise ConcurrencyError(f"Failed to update {item_id} after {max_retries} retries")
```

**Agent Usage**:
```python
# Agent updates item status
await update_with_retry(
    repo=item_repo,
    item_id=feature_id,
    update_fn=lambda item: ItemUpdate(status="in_progress")
)
```

### 5. Event Sourcing Lite Pattern (History)

**Purpose**: Track all changes for FR54-FR59 (history, temporal queries, rollback)

**Pattern**:
```python
# tracertm/services/event_service.py
from datetime import datetime
from typing import List, Optional

class EventService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def log_event(
        self,
        project_id: UUID,
        item_id: Optional[UUID],
        event_type: str,
        event_data: dict,
        agent_id: str
    ):
        """Log an event."""
        event = Event(
            project_id=project_id,
            item_id=item_id,
            event_type=event_type,
            event_data=event_data,
            timestamp=datetime.utcnow(),
            agent_id=agent_id
        )
        self.session.add(event)
        await self.session.commit()

    async def get_item_history(self, item_id: UUID) -> List[Event]:
        """Get all events for an item."""
        result = await self.session.execute(
            select(Event)
            .where(Event.item_id == item_id)
            .order_by(Event.timestamp.desc())
        )
        return list(result.scalars().all())

    async def get_item_at_time(self, item_id: UUID, at_time: datetime) -> Optional[dict]:
        """Reconstruct item state at a specific time."""
        # Get all events up to that time
        result = await self.session.execute(
            select(Event)
            .where(Event.item_id == item_id, Event.timestamp <= at_time)
            .order_by(Event.timestamp.asc())
        )
        events = list(result.scalars().all())

        if not events:
            return None

        # Replay events to reconstruct state
        state = {}
        for event in events:
            if event.event_type == "item_created":
                state = event.event_data["item"]
            elif event.event_type == "item_updated":
                state.update(event.event_data["changes"])
            elif event.event_type == "item_deleted":
                return None  # Item was deleted at this point

        return state
```

### 6. Bulk Operation Preview Pattern (User Safety)

**Purpose**: Provide preview and confirmation for bulk operations (FR6-FR15, Story 2.8)

**Pattern**:
```python
# tracertm/services/bulk_service.py
from typing import List, Dict, Any
from dataclasses import dataclass
from tracertm.repositories import ItemRepository
from tracertm.schemas import ItemUpdate

@dataclass
class BulkPreview:
    """Preview of bulk operation before execution."""
    total_count: int
    sample_items: List[Dict[str, Any]]  # First 5 items
    validation_warnings: List[str]
    estimated_duration_ms: int

    def is_safe(self) -> bool:
        """Check if operation is safe to execute."""
        return len(self.validation_warnings) == 0

class BulkOperationService:
    def __init__(self, session: AsyncSession):
        self.items = ItemRepository(session)

    async def preview_bulk_update(
        self,
        project_id: UUID,
        filter_criteria: Dict[str, Any],
        update_data: ItemUpdate
    ) -> BulkPreview:
        """Preview bulk update before execution."""
        # Query matching items
        matching_items = await self.items.query(project_id, filter_criteria)

        # Validation warnings
        warnings = []
        if len(matching_items) > 100:
            warnings.append(f"Large operation: {len(matching_items)} items will be updated")
        if update_data.status == "complete" and any(item.status == "blocked" for item in matching_items):
            warnings.append("Some blocked items will be marked complete")

        # Sample items (first 5)
        sample = [
            {
                "id": str(item.id),
                "title": item.title,
                "current_status": item.status,
                "new_status": update_data.status or item.status
            }
            for item in matching_items[:5]
        ]

        # Estimate duration (10ms per item)
        estimated_duration = len(matching_items) * 10

        return BulkPreview(
            total_count=len(matching_items),
            sample_items=sample,
            validation_warnings=warnings,
            estimated_duration_ms=estimated_duration
        )

    async def execute_bulk_update(
        self,
        project_id: UUID,
        filter_criteria: Dict[str, Any],
        update_data: ItemUpdate,
        agent_id: str,
        skip_preview: bool = False
    ) -> List[Item]:
        """Execute bulk update with optional preview."""
        if not skip_preview:
            preview = await self.preview_bulk_update(project_id, filter_criteria, update_data)
            if not preview.is_safe():
                raise ValueError(f"Bulk operation has warnings: {preview.validation_warnings}")

        # Execute bulk update
        matching_items = await self.items.query(project_id, filter_criteria)
        updated_items = []

        for item in matching_items:
            try:
                updated = await self.items.update(
                    item_id=item.id,
                    data=update_data,
                    expected_version=item.version
                )
                updated_items.append(updated)
            except ConcurrencyError:
                # Log conflict, continue with other items
                logger.warning(f"Conflict updating item {item.id}, skipping")

        return updated_items
```

**CLI Usage** (Story 2.8):
```python
# tracertm/cli/commands/bulk.py
import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm
from tracertm.services import BulkOperationService

app = typer.Typer()
console = Console()

@app.command()
async def update(
    filter_status: str = typer.Option(None, help="Filter by status"),
    filter_view: str = typer.Option(None, help="Filter by view"),
    new_status: str = typer.Option(None, help="New status to set"),
    skip_preview: bool = typer.Option(False, help="Skip preview confirmation")
):
    """Bulk update items with preview."""
    project = get_current_project()

    # Build filter criteria
    filter_criteria = {}
    if filter_status:
        filter_criteria["status"] = filter_status
    if filter_view:
        filter_criteria["view"] = filter_view

    # Build update data
    update_data = ItemUpdate(status=new_status) if new_status else ItemUpdate()

    async with get_session() as session:
        bulk_service = BulkOperationService(session)

        # Show preview
        if not skip_preview:
            preview = await bulk_service.preview_bulk_update(
                project_id=project.id,
                filter_criteria=filter_criteria,
                update_data=update_data
            )

            # Display preview
            console.print(f"\n[bold cyan]Bulk Update Preview[/bold cyan]")
            console.print(f"Total items to update: [bold]{preview.total_count}[/bold]")
            console.print(f"Estimated duration: [bold]{preview.estimated_duration_ms}ms[/bold]\n")

            # Show sample items
            if preview.sample_items:
                table = Table(title="Sample Items (first 5)")
                table.add_column("ID", style="dim")
                table.add_column("Title", style="cyan")
                table.add_column("Current Status", style="yellow")
                table.add_column("New Status", style="green")

                for item in preview.sample_items:
                    table.add_row(
                        item["id"][:8],
                        item["title"],
                        item["current_status"],
                        item["new_status"]
                    )
                console.print(table)

            # Show warnings
            if preview.validation_warnings:
                console.print("\n[bold yellow]⚠️  Warnings:[/bold yellow]")
                for warning in preview.validation_warnings:
                    console.print(f"  • {warning}")

            # Confirm
            if not Confirm.ask("\nProceed with bulk update?"):
                console.print("[yellow]Bulk update cancelled[/yellow]")
                return

        # Execute bulk update
        updated_items = await bulk_service.execute_bulk_update(
            project_id=project.id,
            filter_criteria=filter_criteria,
            update_data=update_data,
            agent_id="cli-user",
            skip_preview=skip_preview
        )

        console.print(f"\n[bold green]✓[/bold green] Updated {len(updated_items)} items")
```

**Agent Usage** (Python API):
```python
# Agent performs bulk update with preview
from tracertm import BulkOperationService, ItemUpdate

async with get_session() as session:
    bulk_service = BulkOperationService(session)

    # Preview first
    preview = await bulk_service.preview_bulk_update(
        project_id=project_id,
        filter_criteria={"status": "todo", "view": "FEATURE"},
        update_data=ItemUpdate(status="in_progress")
    )

    if preview.is_safe() and preview.total_count < 50:
        # Execute if safe and reasonable size
        updated = await bulk_service.execute_bulk_update(
            project_id=project_id,
            filter_criteria={"status": "todo", "view": "FEATURE"},
            update_data=ItemUpdate(status="in_progress"),
            agent_id="agent-123",
            skip_preview=True  # Already previewed
        )
        print(f"Updated {len(updated)} items")
    else:
        print(f"Bulk operation not safe: {preview.validation_warnings}")
```

**Key Features**:
- ✅ Preview shows total count, sample items (first 5), validation warnings
- ✅ Confirmation required before execution (CLI)
- ✅ Validation warnings for large operations (>100 items) or risky changes
- ✅ Estimated duration based on item count
- ✅ Graceful handling of concurrency conflicts (log and continue)
- ✅ Agent API supports programmatic preview and execution

**References**:
- **Story 2.8**: Bulk operations with preview and confirmation
- **UX Design**: BulkOperationPreview component specification
- **User Journey 3**: Bulk Manipulation (select, preview, execute, verify)

---

## Consistency Rules

### Naming Conventions

**Python Code**:
- **Modules**: `snake_case` (e.g., `item_repository.py`, `event_service.py`)
- **Classes**: `PascalCase` (e.g., `ItemRepository`, `EventService`)
- **Functions/Methods**: `snake_case` (e.g., `create_item`, `get_by_id`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`, `DEFAULT_STATUS`)
- **Private**: Prefix with `_` (e.g., `_internal_helper`)

**Database**:
- **Tables**: `snake_case` plural (e.g., `items`, `links`, `events`)
- **Columns**: `snake_case` (e.g., `project_id`, `created_at`)
- **Indexes**: `idx_{table}_{columns}` (e.g., `idx_items_project_view`)
- **Foreign Keys**: `fk_{table}_{ref_table}` (e.g., `fk_items_projects`)

**CLI Commands**:
- **Commands**: `kebab-case` (e.g., `rtm project switch`, `rtm view feature`)
- **Flags**: `--kebab-case` (e.g., `--output-format`, `--filter-status`)
- **Short flags**: Single letter (e.g., `-f` for `--format`, `-o` for `--output`)

**Item Types**:
- **FEATURE view**: `epic`, `feature`, `story`, `task`
- **CODE view**: `module`, `file`, `class`, `function`
- **WIREFRAME view**: `screen`, `component`, `element`
- **API view**: `service`, `endpoint`, `parameter`
- **TEST view**: `suite`, `case`, `assertion`
- **DATABASE view**: `schema`, `table`, `column`
- **ROADMAP view**: `milestone`, `release`, `sprint`

**Status Values**:
- Standard: `todo`, `in_progress`, `blocked`, `complete`, `cancelled`
- Custom statuses allowed in metadata JSONB

### Code Organization

**Project Structure**:
```
tracertm/
├── __init__.py
├── __main__.py              # Entry point: python -m tracertm
├── cli/                     # CLI commands
│   ├── __init__.py
│   ├── main.py             # Main CLI app
│   ├── commands/
│   │   ├── project.py      # Project commands
│   │   ├── item.py         # Item CRUD commands
│   │   ├── view.py         # View navigation
│   │   ├── link.py         # Link management
│   │   ├── query.py        # Query/filter commands
│   │   └── export.py       # Export commands
│   └── output/
│       ├── formatters.py   # Output formatting (table, json, yaml)
│       └── renderers.py    # Rich rendering utilities
├── core/                    # Core business logic
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   ├── database.py         # Database connection/session
│   ├── concurrency.py      # Optimistic locking, retries
│   └── context.py          # Project context management
├── models/                  # SQLAlchemy models
│   ├── __init__.py
│   ├── project.py
│   ├── item.py
│   ├── link.py
│   ├── event.py
│   └── agent.py
├── schemas/                 # Pydantic schemas
│   ├── __init__.py
│   ├── item.py             # ItemCreate, ItemUpdate, ItemResponse
│   ├── link.py
│   ├── event.py
│   └── query.py            # Query filter schemas
├── repositories/            # Data access layer
│   ├── __init__.py
│   ├── item_repository.py
│   ├── link_repository.py
│   ├── event_repository.py
│   └── agent_repository.py
├── services/                # Business logic layer
│   ├── __init__.py
│   ├── item_service.py
│   ├── link_service.py
│   ├── view_service.py
│   ├── progress_service.py
│   ├── search_service.py
│   └── export_service.py
├── api/                     # Python API for agents
│   ├── __init__.py
│   ├── client.py           # High-level API client
│   └── async_client.py     # Async API client
└── utils/                   # Utilities
    ├── __init__.py
    ├── logging.py
    ├── validation.py
    └── helpers.py

tests/
├── unit/                    # Unit tests
│   ├── test_repositories/
│   ├── test_services/
│   └── test_utils/
├── integration/             # Integration tests
│   ├── test_database/
│   ├── test_cli/
│   └── test_api/
└── fixtures/                # Test fixtures
    ├── conftest.py
    └── sample_data.py

alembic/                     # Database migrations
├── versions/
└── env.py

docs/                        # Documentation
├── README.md
├── CLI-REFERENCE.md
├── API-REFERENCE.md
├── ARCHITECTURE.md
└── AGENT-GUIDE.md
```

### Error Handling

**Principle**: Clear, actionable errors for both humans and agents

**Error Hierarchy**:
```python
# tracertm/exceptions.py
class TraceRTMError(Exception):
    """Base exception for all TraceRTM errors."""
    pass

class ValidationError(TraceRTMError):
    """Data validation failed."""
    pass

class NotFoundError(TraceRTMError):
    """Resource not found."""
    pass

class ConcurrencyError(TraceRTMError):
    """Optimistic lock conflict."""
    pass

class ConfigurationError(TraceRTMError):
    """Configuration invalid or missing."""
    pass

class DatabaseError(TraceRTMError):
    """Database operation failed."""
    pass
```

**Error Handling Pattern**:
```python
# CLI commands handle errors gracefully
@app.command()
def show(item_id: str):
    try:
        item = item_service.get_by_id(UUID(item_id))
        if not item:
            raise NotFoundError(f"Item {item_id} not found")
        console.print(format_item(item))
    except ValidationError as e:
        console.print(f"[red]Validation Error:[/red] {e}")
        console.print("[yellow]Hint:[/yellow] Check item ID format (must be UUID)")
        raise typer.Exit(code=1)
    except NotFoundError as e:
        console.print(f"[red]Not Found:[/red] {e}")
        console.print(f"[yellow]Hint:[/yellow] Use `rtm query` to find items")
        raise typer.Exit(code=1)
    except ConcurrencyError as e:
        console.print(f"[red]Conflict:[/red] {e}")
        console.print("[yellow]Hint:[/yellow] Item was modified by another agent. Retry your operation.")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Unexpected Error:[/red] {e}")
        console.print("[yellow]Please report this issue with the full error message.[/yellow]")
        raise typer.Exit(code=1)
```

### Logging Strategy

**Levels**:
- **DEBUG**: Detailed diagnostic info (SQL queries, function calls)
- **INFO**: General informational messages (item created, project switched)
- **WARNING**: Unexpected but handled situations (optimistic lock retry, deprecated usage)
- **ERROR**: Error conditions (database connection failed, validation error)
- **CRITICAL**: System-level failures (database unavailable, corruption detected)

**Configuration**:
```python
# tracertm/core/logging.py
import logging
from rich.logging import RichHandler

def setup_logging(level: str = "INFO"):
    """Configure logging with Rich handler."""
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )

    # Separate loggers for different components
    logger = logging.getLogger("tracertm")
    db_logger = logging.getLogger("tracertm.database")
    agent_logger = logging.getLogger("tracertm.agents")

    return logger
```

**Usage**:
```python
# In services/repositories
logger = logging.getLogger("tracertm")

async def create_item(self, data: ItemCreate) -> Item:
    logger.info(f"Creating item: {data.title}")
    try:
        item = await self.repo.create(data)
        logger.info(f"Created item {item.id}")
        return item
    except Exception as e:
        logger.error(f"Failed to create item: {e}")
        raise
```

**Agent Activity Logging**:
```python
# All agent operations logged to database
async def log_agent_activity(
    agent_id: str,
    project_id: UUID,
    action: str,
    item_id: Optional[UUID],
    details: dict
):
    """Log agent activity to database."""
    activity = AgentActivity(
        agent_id=agent_id,
        project_id=project_id,
        action=action,
        item_id=item_id,
        details=details,
        timestamp=datetime.utcnow()
    )
    session.add(activity)
    await session.commit()
```

---

## Security Architecture

### Local Data Storage (NFR-S1)

- All data stored locally in PostgreSQL
- No cloud transmission unless explicitly configured
- Database files in user-controlled location
- No telemetry or analytics collection

### Database Security (NFR-S2)

**Connection Security**:
```python
# config.yaml
database_url: "postgresql://user:password@localhost/tracertm?sslmode=require"
```

**Password Management**:
- Never store passwords in plain text
- Use environment variables: `DATABASE_URL` env var
- Support `.env` files (not committed to git)
- Keyring integration for password storage (optional)

**Access Control**:
- PostgreSQL role-based access control
- Separate roles for read-only vs read-write
- Agent-specific database users (optional)

### Agent Authentication (NFR-S3)

**Agent Registry**:
```python
# Agents must register before operating
async def register_agent(agent_id: str, name: str, type: str, config: dict):
    """Register a new agent."""
    agent = Agent(
        id=agent_id,
        name=name,
        type=type,
        config=config,
        created_at=datetime.utcnow()
    )
    session.add(agent)
    await session.commit()
```

**API Key Authentication** (Optional):
```python
# For remote agent access (Phase 2)
async def authenticate_agent(agent_id: str, api_key: str) -> bool:
    """Verify agent API key."""
    agent = await agent_repo.get_by_id(agent_id)
    if not agent:
        return False
    return agent.api_key_hash == hash_api_key(api_key)
```

### Data Integrity (NFR-S4)

**ACID Transactions**:
- All database operations in transactions
- Rollback on error
- Foreign key constraints enforced
- Check constraints for data validity

**Validation**:
```python
# Pydantic schemas validate all inputs
class ItemCreate(BaseModel):
    type: str = Field(..., pattern="^[a-z_]+$")
    view: str = Field(..., pattern="^[A-Z_]+$")
    title: str = Field(..., min_length=1, max_length=500)
    status: str = Field(default="todo", pattern="^(todo|in_progress|blocked|complete|cancelled)$")
```

### Backup & Recovery (NFR-S5)

**Automatic Backups**:
```bash
# Daily backup cron job
0 2 * * * pg_dump tracertm > ~/backups/tracertm-$(date +\%Y\%m\%d).sql
```

**Manual Backup**:
```bash
# Export entire project
rtm export --project my-project --format json > my-project-backup.json

# Restore from backup
rtm import --project my-project --file my-project-backup.json
```

**Point-in-Time Recovery**:
- PostgreSQL WAL archiving (optional)
- Event log replay for item-level recovery
- Temporal queries to view historical state

---

## Performance Considerations

### Query Optimization (NFR-P1, NFR-P2)

**Indexing Strategy**:
- Composite indexes for common queries: `(project_id, view)`, `(project_id, status)`
- GIN indexes for JSONB metadata and full-text search
- Partial indexes for view-specific queries
- Index-only scans where possible

**Query Patterns**:
```python
# Use selectinload for relationships to avoid N+1 queries
items = await session.execute(
    select(Item)
    .options(selectinload(Item.links))
    .where(Item.project_id == project_id)
)

# Use CTEs for recursive queries (hierarchy)
# Use window functions for progress calculation
# Use EXPLAIN ANALYZE to optimize slow queries
```

**Caching** (Phase 2):
- Redis cache for frequently-accessed items
- Cache invalidation on updates
- TTL-based expiration

### Concurrent Agent Operations (NFR-P5)

**Optimistic Locking**:
- Version field on items table
- Check version before update
- Retry with exponential backoff on conflict

**Connection Pooling**:
```python
# SQLAlchemy async engine with connection pool
engine = create_async_engine(
    database_url,
    pool_size=20,  # Max 20 concurrent connections
    max_overflow=10,  # Allow 10 additional connections under load
    pool_pre_ping=True  # Verify connections before use
)
```

**Batch Operations**:
```python
# Bulk insert for agent batch operations
async def bulk_create_items(items: List[ItemCreate]) -> List[Item]:
    """Create multiple items in one transaction."""
    db_items = [Item(**item.model_dump()) for item in items]
    session.add_all(db_items)
    await session.commit()
    return db_items
```

### Scalability (NFR-SC1, NFR-SC4)

**Database Growth**:
- Partitioning for events table (by timestamp)
- Archiving old events to separate table
- VACUUM and ANALYZE scheduled maintenance

**Large Result Sets**:
```python
# Pagination for large queries
async def get_items_paginated(
    project_id: UUID,
    page: int = 1,
    page_size: int = 100
) -> List[Item]:
    """Get items with pagination."""
    offset = (page - 1) * page_size
    result = await session.execute(
        select(Item)
        .where(Item.project_id == project_id)
        .limit(page_size)
        .offset(offset)
    )
    return list(result.scalars().all())
```

---

## Deployment Architecture

### Local Installation (MVP)

**Package Distribution**:
```bash
# PyPI package
pip install tracertm

# Installs:
# - Python package to site-packages
# - CLI entry point: rtm
# - Shell completion scripts
```

**Database Setup**:
```bash
# User creates PostgreSQL database
createdb tracertm

# TraceRTM runs migrations on first use
rtm config init  # Creates config, runs migrations
```

### Development Environment

**Prerequisites**:
```bash
# Install Python 3.12+
brew install python@3.12  # macOS
apt install python3.12    # Ubuntu

# Install PostgreSQL 16+
brew install postgresql@16  # macOS
apt install postgresql-16   # Ubuntu

# Start PostgreSQL
brew services start postgresql@16  # macOS
sudo systemctl start postgresql    # Ubuntu
```

**Setup Commands**:
```bash
# Clone repository
git clone https://github.com/bmad/tracertm
cd tracertm

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -e ".[dev]"  # Editable install with dev dependencies

# Setup database
createdb tracertm_dev
export DATABASE_URL="postgresql://localhost/tracertm_dev"

# Run migrations
alembic upgrade head

# Run tests
pytest

# Run linting
ruff check .
ty check src/ --error-on-warning

# Run CLI
python -m tracertm --help
```

### Docker Deployment (Optional)

```dockerfile
# Dockerfile
FROM python:3.12-slim

# Install PostgreSQL client
RUN apt-get update && apt-get install -y postgresql-client

# Install TraceRTM
COPY . /app
WORKDIR /app
RUN pip install .

# Entry point
ENTRYPOINT ["rtm"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: tracertm
      POSTGRES_PASSWORD: tracertm
    volumes:
      - tracertm-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  tracertm:
    build: .
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql://postgres:tracertm@db/tracertm
    volumes:
      - ~/.tracertm:/root/.tracertm

volumes:
  tracertm-data:
```

---


## Architecture Decision Records (ADRs)

### ADR-001: PostgreSQL over Neo4j for MVP

**Status**: Accepted
**Date**: 2025-11-20
**Context**: Need to choose primary database for multi-view traceability system with cross-view linking.

**Decision**: Use PostgreSQL 16+ for MVP; defer Neo4j to Phase 2.

**Rationale**:
- **Sufficient for 8 views**: PostgreSQL handles 10,000+ items with sub-second queries
- **JSONB flexibility**: View-specific metadata without schema rigidity
- **Proven at scale**: Well-understood performance characteristics
- **Simpler operations**: Single database vs PostgreSQL + Neo4j
- **Cost**: Free, no licensing concerns
- **Phase 2 path**: Can add Neo4j later for advanced graph queries (PageRank, community detection)

**Consequences**:
- ✅ Faster MVP development
- ✅ Simpler deployment and operations
- ✅ Lower resource requirements
- ❌ Graph traversal queries less elegant (use CTEs instead)
- ❌ Advanced graph algorithms deferred to Phase 2

---

### ADR-002: Optimistic Locking over Pessimistic Locking

**Status**: Accepted
**Date**: 2025-11-20
**Context**: Need concurrency control for 1-1000 agents updating items simultaneously.

**Decision**: Use optimistic locking with version field and retry logic.

**Rationale**:
- **Better for high concurrency**: 1000+ agents don't block each other
- **Conflicts rare**: Item-level granularity means agents usually work on different items
- **Retry is acceptable**: Exponential backoff handles occasional conflicts
- **Simpler code**: No lock management, timeouts, or deadlock detection
- **Agent-friendly**: Agents can retry automatically without human intervention

**Consequences**:
- ✅ Higher throughput for concurrent agents
- ✅ No deadlocks
- ✅ Simpler implementation
- ❌ Retry logic required in all update operations
- ❌ Potential for starvation if one item is heavily contended (mitigated by exponential backoff)

---

### ADR-003: Async Core + Sync CLI

**Status**: Accepted
**Date**: 2025-11-20
**Context**: Need to support both CLI (human users) and Python API (agents).

**Decision**: Async core engine with synchronous CLI wrapper.

**Rationale**:
- **CLI simplicity**: Synchronous commands easier for humans to understand
- **Agent performance**: Async API enables concurrent operations
- **Best of both**: Sync CLI calls async core via `asyncio.run()`
- **Future-proof**: Async core ready for Phase 2 features (real-time updates, websockets)

**Consequences**:
- ✅ Simple CLI for humans
- ✅ High-performance API for agents
- ✅ Ready for future async features
- ❌ Slight complexity in CLI layer (async/sync bridge)
- ❌ All core code must be async-aware

---

### ADR-004: View-as-Query Pattern

**Status**: Accepted
**Date**: 2025-11-20
**Context**: Need to implement 8 views (expanding to 32) over same item data.

**Decision**: Views are dynamic queries over unified `items` table, not separate tables.

**Rationale**:
- **Flexibility**: Add new views without schema changes
- **Consistency**: Single source of truth for all items
- **Performance**: Indexed queries fast enough (<1s for 10K+ items)
- **Simplicity**: One table to manage, not 32 tables
- **Cross-view linking**: Natural with single table

**Consequences**:
- ✅ Easy to add new views
- ✅ Consistent data model
- ✅ Simple cross-view queries
- ❌ View-specific fields in JSONB (less type-safe than columns)
- ❌ Must maintain view definitions in code

---

### ADR-005: Event Sourcing Lite (Not Full Event Sourcing)

**Status**: Accepted
**Date**: 2025-11-20
**Context**: Need history, temporal queries, and rollback (FR54-FR59).

**Decision**: Append-only event log + materialized current state (not full event sourcing).

**Rationale**:
- **Performance**: Current state queries are fast (no event replay)
- **History**: Event log provides complete audit trail
- **Temporal queries**: Replay events to reconstruct past state
- **Simpler**: Don't need CQRS, event store, projections
- **Good enough**: MVP doesn't need full event sourcing complexity

**Consequences**:
- ✅ Fast current state queries
- ✅ Complete history available
- ✅ Simpler implementation
- ❌ Temporal queries slower (must replay events)
- ❌ Can't use event sourcing patterns (CQRS, projections)

---

### ADR-006: PostgreSQL Full-Text Search (Not Elasticsearch)

**Status**: Accepted
**Date**: 2025-11-20
**Context**: Need full-text search across items (FR60-FR67).

**Decision**: Use PostgreSQL `tsvector`/`tsquery` for full-text search.

**Rationale**:
- **Built-in**: No external dependencies
- **Fast enough**: Sub-second search on 10,000+ items
- **Simple**: Single database, no sync issues
- **Good enough**: MVP doesn't need advanced search features
- **Phase 2 path**: Can add Elasticsearch later if needed

**Consequences**:
- ✅ No external dependencies
- ✅ Simple deployment
- ✅ Fast enough for MVP
- ❌ Less powerful than Elasticsearch (no fuzzy matching, no facets)
- ❌ Search features limited to PostgreSQL capabilities

---

### ADR-007: Typer + Rich for CLI (Not Click or Argparse)

**Status**: Accepted
**Date**: 2025-11-20
**Context**: Need CLI framework for developer tool.

**Decision**: Use Typer for CLI framework + Rich for output.

**Rationale**:
- **Type-safe**: Typer uses type hints for validation
- **Auto-documentation**: `--help` generated from type hints
- **Modern**: Better DX than Click or argparse
- **Rich integration**: Beautiful tables, progress bars, syntax highlighting
- **Shell completion**: Built-in support for Bash/Zsh/Fish

**Consequences**:
- ✅ Excellent developer experience
- ✅ Type-safe commands
- ✅ Beautiful output
- ❌ Newer library (less mature than Click)
- ❌ Typer dependency (but small and stable)

---

### ADR-008: Ruff over Pylint/Flake8/Black

**Status**: Accepted
**Date**: 2025-11-20
**Context**: Need linting and formatting for code quality.

**Decision**: Use Ruff for linting and formatting (replaces pylint, flake8, black, isort).

**Rationale**:
- **Speed**: 10-100x faster than pylint/flake8
- **All-in-one**: Linting + formatting in one tool
- **Compatible**: Implements same rules as flake8, black, isort
- **Modern**: Written in Rust, actively maintained
- **Good defaults**: Sensible rules out of the box

**Consequences**:
- ✅ Fast linting (seconds vs minutes)
- ✅ Single tool instead of 4
- ✅ Better developer experience
- ❌ Newer tool (less mature than pylint)
- ❌ Some advanced pylint rules not available

---

### ADR-009: Local-First (No Cloud for MVP)

**Status**: Accepted
**Date**: 2025-11-20
**Context**: Need to decide on deployment model.

**Decision**: Local-first for MVP; defer cloud sync to Phase 2.

**Rationale**:
- **Privacy**: Developer data stays local
- **Simplicity**: No cloud infrastructure to manage
- **Performance**: No network latency
- **Offline**: Works without internet
- **Cost**: Free, no cloud hosting costs
- **Phase 2 path**: Can add optional cloud sync later

**Consequences**:
- ✅ Simple deployment
- ✅ Privacy-preserving
- ✅ Fast (no network)
- ✅ Works offline
- ❌ No multi-device sync (Phase 2)
- ❌ No collaboration features (Phase 2)

---

### ADR-010: Python 3.12+ (Not 3.10 or 3.11)

**Status**: Accepted
**Date**: 2025-11-20
**Context**: Need to choose minimum Python version.

**Decision**: Require Python 3.12 or higher.

**Rationale**:
- **Modern features**: Match/case, improved type hints, better async
- **Performance**: 3.12 is faster than 3.10/3.11
- **Future-proof**: 3.12 supported until 2028
- **Developer tool**: Target audience has latest Python
- **Simplicity**: Don't need to support older versions

**Consequences**:
- ✅ Use latest Python features
- ✅ Better performance
- ✅ Simpler codebase (no compatibility shims)
- ❌ Excludes users on Python 3.10/3.11 (acceptable for developer tool)
- ❌ May need to update dependencies for 3.12 compatibility

---

## Summary

This architecture document defines the technical foundation for TraceRTM: an agent-native, multi-view requirements traceability system optimized for 1-1000 concurrent AI agents managing multiple complex projects.

**Key Architectural Decisions:**
1. **PostgreSQL** for data persistence (defer Neo4j to Phase 2)
2. **Optimistic locking** for agent concurrency (1000+ agents)
3. **Async core + Sync CLI** for best of both worlds
4. **View-as-Query** pattern for 8 views (expanding to 32)
5. **Event Sourcing Lite** for history and temporal queries
6. **PostgreSQL full-text search** (defer Elasticsearch to Phase 2)
7. **Typer + Rich** for beautiful CLI
8. **Ruff** for fast linting and formatting
9. **Local-first** deployment (defer cloud to Phase 2)
10. **Python 3.12+** for modern features and performance

**Implementation Patterns:**
- Repository pattern for data access
- Service layer for business logic
- CLI command pattern for consistency
- Optimistic locking with retry for concurrency
- Event sourcing lite for history

**Performance Targets:**
- <50ms simple queries
- <1s complex queries (10,000+ items)
- <500ms project switching
- 1000+ concurrent agent operations

**Next Steps:**
1. **Test Design**: Define testing strategy (unit, integration, CLI tests)
2. **Epic Breakdown**: Break down PRD into implementable epics and stories
3. **Implementation**: Build MVP with 8 core views

---

_This architecture was created through analysis of the PRD (88 FRs + NFRs) and 250,000+ words of research. It provides the technical foundation for AI agents to implement TraceRTM consistently and correctly._

_**Document Status**: Ready for Test Design and Epic Breakdown phases._
