# PostgreSQL 15 → 17 Migration Guide

**Date**: 2026-01-30
**Current**: PostgreSQL 15.15
**Target**: PostgreSQL 17 (latest)

---

## Why Migrate to PostgreSQL 17?

**Benefits**:
- ✅ **Better Performance** - Improved query planner, faster indexes
- ✅ **pgvector Support** - Native vector extension support (for semantic search)
- ✅ **JSON Improvements** - Better JSONB performance
- ✅ **Parallel Queries** - Enhanced parallelization
- ✅ **Security** - Latest security patches

**Your Current Issue**: pgvector installed for PostgreSQL 14, but you're using PostgreSQL 15, and now want to go to 17.

---

## Automated Migration (Recommended)

**One-command migration**:
```bash
./scripts/migrate_to_pg17.sh
```

**What it does**:
1. Installs PostgreSQL 17 via Homebrew
2. Installs pgvector for PostgreSQL 17
3. Backs up your current database
4. Stops PostgreSQL 15
5. Starts PostgreSQL 17
6. Creates user and database
7. Installs all extensions (uuid-ossp, pgcrypto, pg_trgm, vector)
8. Restores your data
9. Updates PATH in shell config

**Time**: ~5-10 minutes

---

## Manual Migration (Step-by-Step)

### Step 1: Install PostgreSQL 17

```bash
brew install postgresql@17
```

### Step 2: Install pgvector

```bash
brew install pgvector
```

### Step 3: Backup Current Database

```bash
# Create backup directory
mkdir -p /tmp/pg15_backup

# Backup database
pg_dump -U tracertm -d tracertm -F c -f /tmp/pg15_backup/tracertm.dump

# Backup users/roles
pg_dumpall -U tracertm --globals-only > /tmp/pg15_backup/globals.sql

echo "✅ Backup complete"
```

### Step 4: Stop PostgreSQL 15

```bash
brew services stop postgresql@15
```

### Step 5: Start PostgreSQL 17

```bash
brew services start postgresql@17

# Wait for it to start
sleep 3
```

### Step 6: Create User and Database

```bash
# Using your macOS username (has superuser access)
psql -d postgres << EOF
-- Create user
CREATE USER tracertm WITH PASSWORD 'tracertm' CREATEDB;

-- Create database
CREATE DATABASE tracertm OWNER tracertm;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE tracertm TO tracertm;
EOF
```

### Step 7: Install Extensions

```bash
psql -U tracertm -d tracertm << EOF
-- Install all required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Verify
SELECT extname, extversion FROM pg_extension ORDER BY extname;
EOF
```

### Step 8: Restore Database

```bash
pg_restore \
    -U tracertm \
    -d tracertm \
    --no-owner \
    --no-acl \
    /tmp/pg15_backup/tracertm.dump
```

### Step 9: Fix Permissions

```bash
psql -U tracertm -d tracertm << EOF
-- Set ownership
ALTER DATABASE tracertm OWNER TO tracertm;

-- Grant schema permissions
GRANT ALL PRIVILEGES ON SCHEMA public TO tracertm;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO tracertm;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO tracertm;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO tracertm;

-- Set default privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO tracertm;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO tracertm;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO tracertm;
EOF
```

### Step 10: Update PATH

```bash
# Add to your shell config (if not already done)
echo 'export PATH="/opt/homebrew/opt/postgresql@17/bin:$PATH"' >> ~/.zshrc

# Reload shell
source ~/.zshrc
```

### Step 11: Verify Migration

```bash
psql -U tracertm -d tracertm << EOF
-- Check version
SELECT version();

-- Check extensions
SELECT extname, extversion FROM pg_extension ORDER BY extname;

-- Check table count
SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';

-- Check data
SELECT COUNT(*) FROM items;
EOF
```

---

## Environment Variables to Update

**Check these files**:
- `.env`
- `.env.go-backend`
- `backend/.env`
- `docker-compose.yml` (if using Docker)

**Update database connection strings**:
```bash
# Old (PostgreSQL 15)
DATABASE_URL=postgresql://tracertm:tracertm@localhost:5432/tracertm

# New (PostgreSQL 17 - usually same port)
DATABASE_URL=postgresql://tracertm:tracertm@localhost:5432/tracertm
```

Usually the port stays the same (5432), but verify:
```bash
psql -U tracertm -d tracertm -c "SHOW port;"
```

---

## Verification Checklist

After migration, verify:

- [ ] PostgreSQL 17 running: `brew services list | grep postgresql@17`
- [ ] Can connect: `psql -U tracertm -d tracertm`
- [ ] Extensions installed: `\dx` in psql
- [ ] Tables exist: `\dt` in psql
- [ ] Data intact: `SELECT COUNT(*) FROM items;`
- [ ] Backend starts: `cd backend && go run main.go`
- [ ] Migrations run: Check for "All infrastructure services initialized"
- [ ] No errors in logs

---

## Rollback Plan

If something goes wrong:

### Quick Rollback

```bash
# Stop PostgreSQL 17
brew services stop postgresql@17

# Start PostgreSQL 15
brew services start postgresql@15

# Verify
psql -U tracertm -d tracertm -c "SELECT version();"
```

Your original database is unchanged in PostgreSQL 15.

### Full Rollback with Backup

```bash
# Stop PostgreSQL 17
brew services stop postgresql@17

# Start PostgreSQL 15
brew services start postgresql@15

# If data was corrupted, restore from backup
psql -U tracertm -d postgres -c "DROP DATABASE IF EXISTS tracertm;"
psql -U tracertm -d postgres -c "CREATE DATABASE tracertm OWNER tracertm;"

pg_restore \
    -U tracertm \
    -d tracertm \
    --no-owner \
    --no-acl \
    /tmp/pg15_backup/tracertm.dump
```

---

## Post-Migration

### Remove PostgreSQL 15 (Optional)

After confirming everything works:

```bash
# Stop service
brew services stop postgresql@15

# Uninstall
brew uninstall postgresql@15

# Remove old data directory (careful!)
# rm -rf /opt/homebrew/var/postgresql@15
```

**Warning**: Only do this after verifying the migration is successful and you have backups!

### Update Backend Configuration

**File**: `.env.go-backend`

Verify database URL is correct:
```bash
DATABASE_URL=postgresql://tracertm:tracertm@localhost:5432/tracertm
```

---

## Troubleshooting

### "psql: command not found" after migration

```bash
# Reload shell
source ~/.zshrc

# Or manually set PATH
export PATH="/opt/homebrew/opt/postgresql@17/bin:$PATH"
```

### "connection refused"

```bash
# Check if PostgreSQL 17 is running
brew services list | grep postgresql@17

# If not, start it
brew services start postgresql@17
```

### "role tracertm does not exist"

```bash
# Recreate user in PostgreSQL 17
psql -d postgres -c "CREATE USER tracertm WITH PASSWORD 'tracertm' CREATEDB;"
```

### Migration fails

```bash
# Check backup exists
ls -lh /tmp/pg15_backup*/tracertm.dump

# Verify PostgreSQL 17 is running
psql -d postgres -c "SELECT version();"

# Re-run restoration manually (see Step 8-9 above)
```

---

## Expected Results

### Before Migration
```
PostgreSQL 15.15 (Homebrew)
Extensions: uuid-ossp, pgcrypto, pg_trgm
Missing: vector (pgvector)
```

### After Migration
```
PostgreSQL 17.x (Homebrew)
Extensions: uuid-ossp, pgcrypto, pg_trgm, vector ✅
All data intact ✅
Backend starts without errors ✅
```

---

## Running the Migration

**Ready to migrate?**

```bash
# Option 1: Automated (recommended)
./scripts/migrate_to_pg17.sh

# Option 2: Manual
# Follow steps 1-11 above
```

**Estimated time**: 5-10 minutes

---

**Important**: The migration script creates a timestamped backup before making any changes. You can safely rollback if needed.
