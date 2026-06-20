# TraceRTM Database Setup Guide

Complete guide for setting up and managing the TraceRTM PostgreSQL database.

## Prerequisites

- PostgreSQL 14+ installed
- Python 3.11+ with pip
- pgvector extension available
- pg_trgm extension (usually included with PostgreSQL)

### Install PostgreSQL Extensions

```bash
# On Ubuntu/Debian
sudo apt-get install postgresql-contrib postgresql-14-pgvector

# On macOS with Homebrew
brew install postgresql@14 pgvector

# Verify PostgreSQL is running
pg_isready
```

## Quick Start

### 1. Create Database

```bash
# Method 1: Using createdb command
createdb tracertm

# Method 2: Using the utility script
python scripts/db_utils.py create
```

### 2. Run Migrations

```bash
# Upgrade to latest schema
alembic upgrade head

# Verify migration status
alembic current
```

### 3. Seed Sample Data (Optional)

```bash
# Add sample data for testing/demo
python scripts/seed.py
```

### 4. Verify Setup

```bash
# Check connection
python scripts/db_utils.py check

# Show database stats
python scripts/db_utils.py stats
```

## Database Configuration

### Connection String

Default: `postgresql://localhost/tracertm`

Set custom connection via environment variable:

```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/tracertm"
```

### Alembic Configuration

Edit `alembic.ini` to change the default connection:

```ini
sqlalchemy.url = postgresql://user:password@localhost:5432/tracertm
```

## Schema Overview

### Core Tables

#### projects
Stores project definitions.

Key columns:
- `id`: UUID primary key
- `name`: Unique project name
- `description`: Project description
- `project_metadata`: JSONB for flexible metadata

#### items
Stores all traceable items (requirements, features, code, tests, etc.).

Key columns:
- `id`: UUID primary key
- `project_id`: Foreign key to projects
- `title`: Item title
- `description`: Detailed description
- `view`: Which view (requirements, features, code, tests, api)
- `item_type`: Type within view
- `status`: Current status (todo, in_progress, complete)
- `priority`: Priority level (low, medium, high)
- `owner`: Assigned owner
- `parent_id`: For hierarchical items
- `version`: For optimistic locking
- `deleted_at`: For soft deletes

#### links
Stores relationships between items.

Key columns:
- `id`: UUID primary key
- `project_id`: Foreign key to projects
- `source_item_id`: Source item
- `target_item_id`: Target item
- `link_type`: Type of relationship (implements, tests, depends_on)
- `link_metadata`: JSONB for additional link data

#### agents
Stores AI agent registrations.

Key columns:
- `id`: UUID primary key
- `project_id`: Foreign key to projects
- `name`: Agent name
- `agent_type`: Type of agent
- `status`: Current status
- `agent_metadata`: JSONB for agent configuration

#### agent_events
Stores agent activity logs.

Key columns:
- `id`: UUID primary key
- `project_id`: Foreign key to projects
- `agent_id`: Foreign key to agents
- `event_type`: Type of event
- `item_id`: Optional related item
- `event_data`: JSONB for event details

### PostgreSQL Extensions

#### vector
Enables semantic search and embedding storage.

```sql
CREATE EXTENSION vector;
```

Use for:
- Storing embeddings in vector columns
- Similarity search using cosine distance
- Semantic matching of requirements/code

#### pg_trgm
Enables trigram-based text search.

```sql
CREATE EXTENSION pg_trgm;
```

Use for:
- Fuzzy text search
- Similarity matching
- Fast LIKE queries

### Indexes

#### Full-Text Search
- `idx_items_title_trgm`: GIN index on items.title
- `idx_items_description_trgm`: GIN index on items.description

Usage:
```sql
-- Fuzzy search
SELECT * FROM items WHERE title % 'search term';

-- With similarity score
SELECT *, similarity(title, 'search term') AS score
FROM items
WHERE title % 'search term'
ORDER BY score DESC;
```

#### Performance Indexes
- Composite indexes on frequently queried columns
- Foreign key indexes for join optimization
- Partial indexes for specific queries

## Common Operations

### Database Utilities

```bash
# Check database connection
python scripts/db_utils.py check

# Show database statistics
python scripts/db_utils.py stats

# List installed extensions
python scripts/db_utils.py extensions

# Optimize database
python scripts/db_utils.py vacuum
```

### Migration Management

```bash
# Show current migration version
alembic current

# Show migration history
alembic history --verbose

# Upgrade to specific version
alembic upgrade <revision>

# Downgrade one version
alembic downgrade -1

# Downgrade to base (drops all tables)
alembic downgrade base

# Create new migration
alembic revision --autogenerate -m "description"
```

### Backup and Restore

```bash
# Backup database
pg_dump tracertm > tracertm_backup_$(date +%Y%m%d).sql

# Backup with compression
pg_dump tracertm | gzip > tracertm_backup_$(date +%Y%m%d).sql.gz

# Restore from backup
psql tracertm < tracertm_backup.sql

# Restore from compressed backup
gunzip -c tracertm_backup.sql.gz | psql tracertm
```

### Reset Database (Development)

```bash
# Complete reset (drops and recreates)
python scripts/db_utils.py reset

# Then run migrations
alembic upgrade head

# Optionally seed data
python scripts/seed.py
```

## Useful SQL Queries

### Count Items by View
```sql
SELECT view, COUNT(*) as count
FROM items
WHERE deleted_at IS NULL
GROUP BY view
ORDER BY count DESC;
```

### Find Items by Status
```sql
SELECT view, item_type, title, status
FROM items
WHERE project_id = 'project-id'
AND status = 'in_progress'
AND deleted_at IS NULL;
```

### Traceability Matrix
```sql
SELECT
    i1.view as target_view,
    i1.title as target_item,
    l.link_type,
    i2.view as source_view,
    i2.title as source_item
FROM links l
JOIN items i1 ON l.target_item_id = i1.id
JOIN items i2 ON l.source_item_id = i2.id
WHERE l.project_id = 'project-id'
ORDER BY i1.view, i1.title;
```

### Recent Agent Activity
```sql
SELECT
    a.name as agent,
    ae.event_type,
    i.title as related_item,
    ae.created_at
FROM agent_events ae
JOIN agents a ON ae.agent_id = a.id
LEFT JOIN items i ON ae.item_id = i.id
WHERE ae.project_id = 'project-id'
ORDER BY ae.created_at DESC
LIMIT 20;
```

### Coverage Analysis
```sql
-- Requirements without implementation
SELECT r.title
FROM items r
WHERE r.view = 'requirements'
AND r.project_id = 'project-id'
AND NOT EXISTS (
    SELECT 1 FROM links l
    WHERE l.target_item_id = r.id
    AND l.link_type = 'implements'
)
AND r.deleted_at IS NULL;
```

## Performance Optimization

### Analyze Tables
```bash
# Analyze all tables
python scripts/db_utils.py vacuum

# Or manually
psql tracertm -c "VACUUM ANALYZE;"
```

### Monitor Query Performance
```sql
-- Enable query timing
\timing

-- Explain query plan
EXPLAIN ANALYZE
SELECT * FROM items WHERE project_id = 'id';

-- Show slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### Index Maintenance
```sql
-- List unused indexes
SELECT schemaname, tablename, indexname
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- Rebuild indexes
REINDEX TABLE items;
```

## Troubleshooting

### Connection Issues

```bash
# Check if PostgreSQL is running
pg_isready

# Check connection settings
psql tracertm -c "SELECT version();"

# Check user permissions
psql tracertm -c "SELECT current_user, current_database();"
```

### Migration Issues

```bash
# If migration fails, check current state
alembic current

# View pending migrations
alembic heads

# If stuck, manually fix in database then stamp
alembic stamp head
```

### Extension Issues

```sql
-- Check if extensions are installed
SELECT * FROM pg_extension;

-- Install missing extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

### Disk Space

```sql
-- Check database size
SELECT pg_size_pretty(pg_database_size('tracertm'));

-- Check table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Production Deployment

### Recommended Settings

```sql
-- Connection pooling (adjust based on load)
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 16MB

-- Performance
random_page_cost = 1.1  -- For SSDs
effective_io_concurrency = 200

-- Logging
log_min_duration_statement = 1000  -- Log queries > 1s
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
```

### Backup Strategy

```bash
# Daily backups with rotation
0 2 * * * pg_dump tracertm | gzip > /backup/tracertm_$(date +\%Y\%m\%d).sql.gz
0 3 * * * find /backup -name "tracertm_*.sql.gz" -mtime +7 -delete
```

### Monitoring

```sql
-- Active connections
SELECT count(*) FROM pg_stat_activity WHERE datname = 'tracertm';

-- Lock monitoring
SELECT * FROM pg_locks WHERE NOT granted;

-- Table statistics
SELECT * FROM pg_stat_user_tables WHERE schemaname = 'public';
```

## Security

### User Management

```sql
-- Create read-only user
CREATE USER tracertm_readonly WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE tracertm TO tracertm_readonly;
GRANT USAGE ON SCHEMA public TO tracertm_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO tracertm_readonly;

-- Create application user with limited permissions
CREATE USER tracertm_app WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE tracertm TO tracertm_app;
GRANT USAGE ON SCHEMA public TO tracertm_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO tracertm_app;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO tracertm_app;
```

### SSL Connection

```bash
# Connect with SSL
export DATABASE_URL="postgresql://user:pass@localhost/tracertm?sslmode=require"
```

## Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
