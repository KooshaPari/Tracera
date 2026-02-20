# TraceRTM Database Migrations - Summary

Created: 2025-11-29

## Overview

Complete database migration and schema infrastructure for TraceRTM, including PostgreSQL setup, Alembic migrations, sample data seeding, and utility scripts.

## Files Created

### 1. Initial Migration (000_initial_schema.py)

**Location**: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/alembic/versions/000_initial_schema.py`

**Purpose**: Creates the foundational database schema

**Features**:
- Enables PostgreSQL extensions (vector, pg_trgm)
- Creates all core tables:
  - `projects`: Project definitions
  - `items`: Traceable items (requirements, features, code, tests, api)
  - `links`: Relationships between items
  - `agents`: AI agent registrations
  - `agent_events`: Agent activity logs
- Creates comprehensive indexes for performance
- Sets up full-text search indexes using pg_trgm
- Adds automatic timestamp update triggers
- Implements cascade deletes and referential integrity

**Schema Highlights**:
- All IDs use VARCHAR(255) for UUID strings
- JSONB columns for flexible metadata
- Timezone-aware timestamps
- Optimistic locking on items (version column)
- Soft delete support on items (deleted_at column)
- Composite indexes for common query patterns

### 2. Updated Migration Chain

**Location**: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/alembic/versions/001_add_change_tracking.py`

**Changes**: Updated to depend on migration 000 instead of being the first migration

This establishes the proper migration chain:
```
000 (initial_schema)
  -> 001 (add_change_tracking)
    -> 002 (add_materialized_views)
      -> 003 (add_refresh_functions)
        -> 004 (add_remaining_views)
          -> 005 (update_refresh_all_views)
            -> 006 (add_priority_owner_to_items)
```

### 3. Seed Data Script (seed.py)

**Location**: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/scripts/seed.py`

**Purpose**: Populate database with realistic sample data

**Creates**:
- 1 sample project ("Sample TraceRTM Project")
- 10 items across 5 views:
  - 2 requirements (functional and non-functional)
  - 2 features (login and registration)
  - 2 code files (login.py, oauth.py)
  - 2 test files (test_login.py, test_oauth.py)
  - 2 API endpoints (POST /api/auth/login, POST /api/auth/register)
- 8 traceability links showing relationships:
  - Feature -> Requirement (implements)
  - Code -> Feature (implements)
  - Test -> Code (tests)
  - API -> Code (exposes)
  - Code -> Code (depends_on)
- 3 AI agents:
  - Code Analyzer Agent
  - Traceability Agent
  - Quality Metrics Agent
- 4 agent events showing various activities

**Usage**:
```bash
python scripts/seed.py
```

**Features**:
- Idempotent (checks if sample project exists)
- Uses SQLAlchemy models for type safety
- Realistic metadata in JSONB fields
- Demonstrates full traceability chain

### 4. Database Utilities (db_utils.py)

**Location**: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/scripts/db_utils.py`

**Purpose**: Common database administration tasks

**Commands**:
```bash
# Check database connection
python scripts/db_utils.py check

# Create database
python scripts/db_utils.py create

# Drop database (with confirmation)
python scripts/db_utils.py drop

# Reset database (drop + create)
python scripts/db_utils.py reset

# Show database statistics
python scripts/db_utils.py stats

# Run VACUUM ANALYZE
python scripts/db_utils.py vacuum

# List installed extensions
python scripts/db_utils.py extensions
```

**Features**:
- Comprehensive error handling
- Confirmation prompts for destructive operations
- Detailed statistics output
- Automatic connection cleanup

### 5. Migration Test Script (test_migrations.py)

**Location**: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/scripts/test_migrations.py`

**Purpose**: Verify migrations create correct schema

**Checks**:
- All expected tables exist
- PostgreSQL extensions installed
- Indexes created correctly
- Foreign keys properly defined
- Triggers configured
- Data insertion works

**Usage**:
```bash
python scripts/test_migrations.py
```

### 6. Documentation

#### alembic/README.md

**Location**: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/alembic/README.md`

Comprehensive guide to:
- Migration files and their purposes
- Alembic commands
- Schema overview
- Best practices
- Troubleshooting

#### alembic/schema_reference.sql

**Location**: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/alembic/schema_reference.sql`

Complete SQL schema reference showing:
- Full CREATE TABLE statements
- All indexes
- Triggers and functions
- Useful example queries
- Comments explaining design decisions

#### DATABASE_SETUP.md

**Location**: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/DATABASE_SETUP.md`

Complete setup and operations guide covering:
- Prerequisites and installation
- Quick start guide
- Schema details
- Common operations
- Backup and restore
- Performance optimization
- Troubleshooting
- Production deployment
- Security configuration

## Database Schema

### Tables

#### projects
- Stores project definitions
- One project can contain many items and links

#### items
- Central table for all traceable artifacts
- Supports multiple views (requirements, features, code, tests, api)
- Flexible item_type within each view
- Hierarchical structure via parent_id
- Version control via version column
- Soft deletes via deleted_at

#### links
- Bidirectional relationships between items
- Typed links (implements, tests, depends_on, exposes)
- Metadata for confidence scores, etc.

#### agents
- AI agent registration
- Tracks agent status and activity
- Flexible metadata for capabilities

#### agent_events
- Audit log of agent actions
- Links to items when relevant
- Stores event details in JSONB

### Extensions

#### vector (pgvector)
- Enables semantic search
- Vector similarity queries
- Storage for embeddings

#### pg_trgm
- Trigram-based text search
- Fuzzy matching
- Fast LIKE queries with indexes

### Key Features

1. **Full-Text Search**
   - GIN indexes on items.title and items.description
   - Trigram matching for fuzzy search
   - Similarity scoring

2. **Performance Indexes**
   - Composite indexes on frequently queried columns
   - Foreign key indexes for efficient joins
   - Partial indexes for specific use cases

3. **Data Integrity**
   - Foreign key constraints with cascade deletes
   - Check constraints where appropriate
   - Automatic timestamp management

4. **Flexibility**
   - JSONB metadata columns for extensibility
   - Soft deletes preserve history
   - Optimistic locking prevents conflicts

## Quick Start

### 1. Setup Database

```bash
# Create database
createdb tracertm

# Or use utility
python scripts/db_utils.py create
```

### 2. Run Migrations

```bash
# Apply all migrations
alembic upgrade head

# Verify
alembic current
```

### 3. Seed Data (Optional)

```bash
# Add sample data
python scripts/seed.py
```

### 4. Verify

```bash
# Check connection
python scripts/db_utils.py check

# Show stats
python scripts/db_utils.py stats

# Test migrations
python scripts/test_migrations.py
```

## Migration Commands

```bash
# Current version
alembic current

# Migration history
alembic history --verbose

# Upgrade to latest
alembic upgrade head

# Upgrade to specific version
alembic upgrade <revision>

# Downgrade one version
alembic downgrade -1

# Create new migration
alembic revision --autogenerate -m "description"
```

## Environment Configuration

### Database URL

Default: `postgresql://localhost/tracertm`

Override with environment variable:
```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/tracertm"
```

### Alembic Configuration

Edit `alembic.ini`:
```ini
sqlalchemy.url = postgresql://localhost/tracertm
```

## File Paths Summary

### Migrations
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/alembic/versions/000_initial_schema.py` (9.1 KB)
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/alembic/versions/001_add_change_tracking.py` (updated)

### Scripts
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/scripts/seed.py` (14 KB, executable)
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/scripts/db_utils.py` (7.7 KB, executable)
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/scripts/test_migrations.py` (5.8 KB, executable)

### Documentation
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/alembic/README.md` (4.5 KB)
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/alembic/schema_reference.sql` (8.3 KB)
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/DATABASE_SETUP.md` (comprehensive guide)

## Testing

### Test Migrations

```bash
# Run migration tests
python scripts/test_migrations.py
```

### Manual Testing

```bash
# Create test database
createdb tracertm_test

# Run migrations
DATABASE_URL=postgresql://localhost/tracertm_test alembic upgrade head

# Seed data
DATABASE_URL=postgresql://localhost/tracertm_test python scripts/seed.py

# Verify
DATABASE_URL=postgresql://localhost/tracertm_test python scripts/db_utils.py stats

# Clean up
dropdb tracertm_test
```

## Production Checklist

- [ ] PostgreSQL 14+ installed
- [ ] pgvector extension available
- [ ] Database created
- [ ] Migrations applied (`alembic upgrade head`)
- [ ] Connection pooling configured
- [ ] Backup strategy in place
- [ ] Monitoring configured
- [ ] SSL enabled for connections
- [ ] Database user with minimal permissions
- [ ] Regular VACUUM ANALYZE scheduled

## Troubleshooting

### Common Issues

1. **Extension not found**
   ```bash
   # Install pgvector
   # Ubuntu: apt-get install postgresql-14-pgvector
   # macOS: brew install pgvector
   ```

2. **Connection refused**
   ```bash
   # Check PostgreSQL is running
   pg_isready

   # Check connection string
   python scripts/db_utils.py check
   ```

3. **Migration conflicts**
   ```bash
   # Check current state
   alembic current

   # Show heads
   alembic heads
   ```

## Next Steps

1. **Apply migrations**:
   ```bash
   alembic upgrade head
   ```

2. **Seed sample data**:
   ```bash
   python scripts/seed.py
   ```

3. **Verify setup**:
   ```bash
   python scripts/db_utils.py stats
   ```

4. **Explore schema**:
   - Review `alembic/schema_reference.sql`
   - Read `DATABASE_SETUP.md`
   - Run sample queries

## Support

For detailed information, see:
- `DATABASE_SETUP.md` - Complete setup guide
- `alembic/README.md` - Migration documentation
- `alembic/schema_reference.sql` - Schema reference

## Notes

- All scripts are executable and include proper error handling
- Documentation includes examples and best practices
- Schema supports both development (SQLite) and production (PostgreSQL)
- Full-text search ready out of the box
- Vector embeddings support ready (pgvector)
- Comprehensive indexing for performance
- Change tracking infrastructure included
- Agent coordination support built-in
