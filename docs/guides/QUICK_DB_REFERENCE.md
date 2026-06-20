# TraceRTM Database Quick Reference

## Quick Start

```bash
# 1. Create database
createdb tracertm

# 2. Run migrations
alembic upgrade head

# 3. Seed sample data (optional)
python scripts/seed.py

# 4. Verify
python scripts/db_utils.py stats
```

## Common Commands

### Database Operations
```bash
# Check connection
python scripts/db_utils.py check

# Show statistics
python scripts/db_utils.py stats

# List extensions
python scripts/db_utils.py extensions

# Optimize database
python scripts/db_utils.py vacuum

# Reset database (development only)
python scripts/db_utils.py reset
```

### Migrations
```bash
# Show current version
alembic current

# Show history
alembic history

# Upgrade to latest
alembic upgrade head

# Downgrade one version
alembic downgrade -1

# Create new migration
alembic revision --autogenerate -m "description"

# Test migrations
python scripts/test_migrations.py
```

### Data Management
```bash
# Seed sample data
python scripts/seed.py

# Backup database
pg_dump tracertm > backup.sql

# Restore database
psql tracertm < backup.sql
```

## Schema Quick Reference

### Tables
- `projects` - Project definitions
- `items` - All traceable items (requirements, features, code, tests, api)
- `links` - Relationships between items
- `agents` - AI agent registrations
- `agent_events` - Agent activity logs
- `change_log` - Change tracking for materialized views

### Key Columns

#### items
- `view` - requirements, features, code, tests, api
- `item_type` - Type within the view
- `status` - todo, in_progress, complete
- `priority` - low, medium, high
- `owner` - Assigned owner
- `parent_id` - Hierarchical structure
- `deleted_at` - Soft delete timestamp

#### links
- `link_type` - implements, tests, depends_on, exposes
- `source_item_id` - Source item
- `target_item_id` - Target item

## Useful SQL Queries

### Count items by view
```sql
SELECT view, COUNT(*) FROM items
WHERE deleted_at IS NULL
GROUP BY view;
```

### Find unlinked requirements
```sql
SELECT title FROM items
WHERE view = 'requirements'
AND id NOT IN (SELECT target_item_id FROM links)
AND deleted_at IS NULL;
```

### Traceability matrix
```sql
SELECT
    i1.title as requirement,
    l.link_type,
    i2.title as implementation
FROM links l
JOIN items i1 ON l.target_item_id = i1.id
JOIN items i2 ON l.source_item_id = i2.id
WHERE i1.view = 'requirements';
```

### Recent agent activity
```sql
SELECT a.name, ae.event_type, ae.created_at
FROM agent_events ae
JOIN agents a ON ae.agent_id = a.id
ORDER BY ae.created_at DESC
LIMIT 10;
```

## Environment Variables

```bash
# Database connection
export DATABASE_URL="postgresql://user:pass@localhost/tracertm"
```

## Extensions

### pgvector
Enables semantic search and vector similarity.

### pg_trgm
Enables fuzzy text search with trigram matching.

```sql
-- Fuzzy search example
SELECT * FROM items
WHERE title % 'authentication'
ORDER BY similarity(title, 'authentication') DESC;
```

## File Locations

### Migrations
- `/alembic/versions/000_initial_schema.py` - Initial schema
- `/alembic/versions/001_*.py` - Subsequent migrations

### Scripts
- `/scripts/seed.py` - Sample data seeding
- `/scripts/db_utils.py` - Database utilities
- `/scripts/test_migrations.py` - Migration testing

### Documentation
- `/DATABASE_SETUP.md` - Complete setup guide
- `/DATABASE_MIGRATION_SUMMARY.md` - Migration summary
- `/alembic/README.md` - Migration documentation
- `/alembic/schema_reference.sql` - SQL schema reference

## Troubleshooting

### Connection Issues
```bash
# Check PostgreSQL is running
pg_isready

# Test connection
python scripts/db_utils.py check
```

### Migration Issues
```bash
# Check current state
alembic current

# Show migration heads
alembic heads

# If stuck, manually verify and stamp
alembic stamp head
```

### Extension Issues
```sql
-- Check installed extensions
SELECT * FROM pg_extension;

-- Install missing extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

## Production Checklist

- [ ] PostgreSQL 14+ installed
- [ ] pgvector extension installed
- [ ] Database created
- [ ] Migrations applied
- [ ] Backup strategy configured
- [ ] Connection pooling set up
- [ ] SSL enabled
- [ ] Monitoring configured

## Quick Links

- [Complete Setup Guide](DATABASE_SETUP.md)
- [Migration Summary](DATABASE_MIGRATION_SUMMARY.md)
- [Alembic Documentation](alembic/README.md)
- [Schema Reference](alembic/schema_reference.sql)
