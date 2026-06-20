# ADR-0007: Database Architecture

**Status:** Accepted
**Date:** 2026-02-02
**Deciders:** Development Team
**Supersedes:** N/A

---

## Context

TraceRTM requires a database that supports:

1. **Relational data:** Requirements, test cases, projects (structured entities)
2. **Graph queries:** Traceability links, dependency traversal
3. **Full-text search:** Search requirements by content
4. **Vector embeddings:** AI-powered semantic search (planned)
5. **JSON storage:** Flexible metadata, API responses
6. **Async operations:** Non-blocking database queries (Python async)

Technology constraints:
- **Python backend:** SQLAlchemy 2.0 (async), Alembic (migrations)
- **Go backend:** pgx v5 (PostgreSQL driver)
- **Expected scale:** 10,000+ requirements, 100,000+ links, 1,000+ projects

Database requirements:
- **ACID transactions:** Data integrity for traceability links
- **Complex queries:** Recursive CTEs for graph traversal
- **Performance:** <100ms for simple queries, <1s for graph analysis
- **Schema flexibility:** Easy migrations during development

## Decision

We will use **PostgreSQL 16+** with the following extensions:
- **pg_trgm:** Full-text search (trigram similarity)
- **pgvector:** Vector embeddings for semantic search
- **uuid-ossp:** UUID generation
- **hstore:** Key-value pairs (if needed)

**ORM:** SQLAlchemy 2.0 (async) for Python, pgx v5 (raw SQL) for Go

## Rationale

### PostgreSQL Advantages

**From pyproject.toml:**
```toml
dependencies = [
    "sqlalchemy[asyncio]>=2.0.46",  # Async ORM
    "alembic>=1.18.3",               # Migrations
    "psycopg2-binary>=2.9.11",       # psycopg2 driver
    "asyncpg>=0.31.0",               # Async driver (fast)
    "aiosqlite>=0.22.1",             # SQLite for local dev
]
```

**From backend/go.mod:**
```go
require (
    github.com/jackc/pgx/v5 v5.8.0          // PostgreSQL driver
    github.com/lib/pq v1.11.1                // Legacy driver (migration)
    github.com/pgvector/pgvector-go v0.3.0  // Vector extension
    gorm.io/driver/postgres v1.6.0          // GORM (if needed)
)
```

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      PostgreSQL 16+                          │
├─────────────────────────────────────────────────────────────┤
│  Core Tables:                                                │
│    ├── projects                                              │
│    ├── items (requirements, features, test cases)           │
│    ├── links (traceability)                                 │
│    ├── test_cases                                           │
│    ├── scenarios (BDD)                                      │
│    └── adrs (architecture decisions)                        │
│                                                              │
│  Extensions:                                                 │
│    ├── pg_trgm (full-text search)                          │
│    ├── pgvector (embeddings)                               │
│    └── uuid-ossp (UUID generation)                         │
│                                                              │
│  Indexes:                                                    │
│    ├── GIN (JSON, full-text)                               │
│    ├── HNSW (vector similarity)                            │
│    └── B-tree (foreign keys, queries)                      │
└─────────────────────────────────────────────────────────────┘
                           │
           ┌───────────────┴────────────────┐
           │                                 │
    ┌──────▼───────┐                 ┌──────▼───────┐
    │  Python App  │                 │   Go Layer   │
    │  (SQLAlchemy)│                 │   (pgx)      │
    └──────────────┘                 └──────────────┘
```

### Schema Example

```sql
-- Items table (requirements, features, test cases)
CREATE TABLE items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    item_type VARCHAR(50) NOT NULL,  -- requirement, feature, test_case
    title VARCHAR(500) NOT NULL,
    description TEXT,
    metadata JSONB DEFAULT '{}',
    embedding vector(1536),  -- pgvector for semantic search
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Full-text search
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english', title || ' ' || COALESCE(description, ''))
    ) STORED
);

-- Indexes
CREATE INDEX idx_items_project ON items(project_id);
CREATE INDEX idx_items_type ON items(item_type);
CREATE INDEX idx_items_search ON items USING GIN(search_vector);
CREATE INDEX idx_items_embedding ON items USING hnsw(embedding vector_cosine_ops);

-- Links table (traceability)
CREATE TABLE links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_item_id UUID REFERENCES items(id) ON DELETE CASCADE,
    target_item_id UUID REFERENCES items(id) ON DELETE CASCADE,
    link_type VARCHAR(50) NOT NULL,  -- satisfies, tests, depends_on
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(source_item_id, target_item_id, link_type)
);

CREATE INDEX idx_links_source ON links(source_item_id);
CREATE INDEX idx_links_target ON links(target_item_id);
```

### SQLAlchemy 2.0 Models

```python
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

class Item(Base):
    __tablename__ = "items"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"))
    item_type: Mapped[str] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    metadata: Mapped[dict] = mapped_column(JSONB, default={})
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536))

    # Relationships
    project: Mapped["Project"] = relationship(back_populates="items")
    outgoing_links: Mapped[list["Link"]] = relationship(
        foreign_keys="Link.source_item_id", back_populates="source_item"
    )
    incoming_links: Mapped[list["Link"]] = relationship(
        foreign_keys="Link.target_item_id", back_populates="target_item"
    )
```

### Async Query Example

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def get_requirement_coverage(session: AsyncSession, requirement_id: str) -> float:
    # Get all test cases linked to requirement
    stmt = (
        select(TestCase)
        .join(Link, Link.target_item_id == TestCase.id)
        .where(Link.source_item_id == requirement_id)
        .where(Link.link_type == "tests")
    )
    result = await session.execute(stmt)
    test_cases = result.scalars().all()

    passed = sum(1 for tc in test_cases if tc.status == "passed")
    return passed / len(test_cases) if test_cases else 0.0
```

### Graph Traversal (Recursive CTE)

```sql
-- Find all dependencies of a requirement (transitive closure)
WITH RECURSIVE dependencies AS (
    -- Base case: direct dependencies
    SELECT target_item_id AS item_id, 1 AS depth
    FROM links
    WHERE source_item_id = $1 AND link_type = 'depends_on'

    UNION

    -- Recursive case: dependencies of dependencies
    SELECT l.target_item_id, d.depth + 1
    FROM links l
    INNER JOIN dependencies d ON l.source_item_id = d.item_id
    WHERE l.link_type = 'depends_on' AND d.depth < 10  -- Prevent infinite loops
)
SELECT DISTINCT i.*
FROM items i
INNER JOIN dependencies d ON i.id = d.item_id
ORDER BY d.depth;
```

## Alternatives Rejected

### Alternative 1: MongoDB (Document Database)

- **Description:** Store requirements/tests as JSON documents
- **Pros:** Schema flexibility, easy to denormalize, JSON-native
- **Cons:** No foreign keys, complex graph queries, weaker ACID guarantees
- **Why Rejected:** Traceability requires relational integrity. PostgreSQL JSONB provides schema flexibility without sacrificing relations.

### Alternative 2: Neo4j (Graph Database)

- **Description:** Native graph database for traceability links
- **Pros:** Graph queries (Cypher), optimal for traversals
- **Cons:** Separate database (dual-database complexity), limited relational features, expensive at scale
- **Why Rejected:** PostgreSQL recursive CTEs handle graph queries. Neo4j adds operational complexity without sufficient benefit.

### Alternative 3: MySQL

- **Description:** Alternative relational database
- **Pros:** Widely used, good performance
- **Cons:** No JSONB (only JSON), weaker full-text search, no pgvector equivalent
- **Why Rejected:** PostgreSQL has superior JSON support, full-text search, and vector extensions.

### Alternative 4: SQLite

- **Description:** Embedded database (file-based)
- **Pros:** Zero setup, easy local dev, single file
- **Cons:** No concurrent writes, no pgvector, limited scalability
- **Why Rejected:** TraceRTM needs multi-user concurrency. SQLite used for local dev only (aiosqlite), PostgreSQL for production.

## Consequences

### Positive

- **Mature ecosystem:** PostgreSQL 30+ years, battle-tested
- **Rich extensions:** pg_trgm (search), pgvector (AI), PostGIS (geospatial, if needed)
- **ACID compliance:** Reliable transactions for traceability links
- **Async support:** asyncpg (Python), pgx (Go) are fast
- **JSON + relational:** Best of both worlds (structured + flexible)
- **Recursive CTEs:** Native graph traversal without external graph DB

### Negative

- **Operational overhead:** Requires database server (not embedded like SQLite)
- **Migration complexity:** Alembic migrations for schema changes
- **Vector extension:** pgvector requires manual installation (not default PostgreSQL)
- **Query optimization:** Complex queries need EXPLAIN ANALYZE tuning

### Neutral

- **Backup strategy:** pg_dump for backups, point-in-time recovery
- **Replication:** Streaming replication for read replicas (if needed)
- **Connection pooling:** PgBouncer or Neon pooling (deployment-specific)

## Implementation

### Affected Components

- `src/tracertm/models/` - SQLAlchemy models
- `src/tracertm/database/` - Database connection, session management
- `alembic/versions/` - Migration scripts
- `backend/internal/repository/` - Go database layer
- `scripts/db-utils.py` - Database utilities (backup, restore)

### Migration Strategy

**Phase 1: Schema Setup (Week 1)**
```bash
# Create database
createdb tracertm

# Install extensions
psql tracertm -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
psql tracertm -c "CREATE EXTENSION IF NOT EXISTS vector;"
psql tracertm -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"

# Run migrations
alembic upgrade head
```

**Phase 2: Data Migration (Week 2)**
- Export existing data (if any) from old schema
- Transform to new schema
- Import via Alembic data migrations

**Phase 3: Optimization (Week 3)**
- Analyze query patterns
- Add indexes based on slow queries
- Configure autovacuum, shared_buffers

### Rollout Plan

- **Phase 1:** Local development (SQLite for dev, PostgreSQL for tests)
- **Phase 2:** Staging deployment (Neon PostgreSQL)
- **Phase 3:** Production deployment (Fly.io PostgreSQL or Neon)

### Success Criteria

- [ ] All tables created via Alembic migrations
- [ ] Full-text search <100ms for 10,000 requirements
- [ ] Graph traversal (5 levels deep) <1s
- [ ] Vector similarity search <500ms
- [ ] Zero data loss during migrations
- [ ] Automated backups (daily)

## References

- [PostgreSQL Documentation](https://www.postgresql.org/docs/16/)
- [SQLAlchemy 2.0 Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [pgvector](https://github.com/pgvector/pgvector)
- [Alembic](https://alembic.sqlalchemy.org/)
- [ADR-0006: Deployment Architecture](ADR-0006-deployment-architecture.md)

---

**Notes:**
- **Current schema:** ~30 tables (projects, items, links, test_cases, scenarios, adrs, etc.)
- **Indexes:** ~60 indexes (B-tree for FK, GIN for JSON/FTS, HNSW for vectors)
- **Extensions required:** pg_trgm, pgvector, uuid-ossp
- **Migration status:** Alembic migrations in `alembic/versions/`
