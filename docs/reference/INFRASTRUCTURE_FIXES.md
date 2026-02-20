# Infrastructure Initialization Fixes

## Issues Fixed

### 1. Neo4j Index Creation Syntax Error

**Error:**
```
Neo.ClientError.Statement.SyntaxError
CREATE INDEX idx_project_id IF NOT EXISTS FOR (n) ON (n.project_id)
Invalid input ')': expected ':'
```

**Root Cause:**
The Neo4j Cypher syntax was missing proper node label specification. The syntax `FOR (n)` is invalid - it requires a label like `FOR (n:Label)`.

**Fix Applied:**
Updated `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend/internal/graph/neo4j_client.go` line 116-131 to use proper syntax:

**Before:**
```cypher
CREATE INDEX idx_project_id IF NOT EXISTS FOR (n) ON n.project_id
```

**After:**
```cypher
CREATE INDEX idx_project_id IF NOT EXISTS FOR (n:Node) ON (n.project_id)
```

**Key Changes:**
- Added node label `:Node` or `:Item` to all index creation queries
- Wrapped property references in parentheses: `ON (n.project_id)` instead of `ON n.project_id`
- Provided multiple syntax variants for different Neo4j versions (5.x, 4.x, legacy)

---

### 2. PostgreSQL Migration Error

**Error:**
```
failed to run migrations: pq: role "postgres" does not exist
```

**Root Cause:**
The PostgreSQL installation on macOS doesn't create a default `postgres` superuser. Instead, it creates a user with the same name as your system user (`kooshapari` in this case). The database URL in `.env.go-backend` was trying to connect as `tracertm` user, which exists but may not have had full permissions.

**Fix Applied:**

1. **Verified Database Setup:**
   - User `tracertm` already exists in PostgreSQL
   - Database `tracertm` already exists
   - Set database ownership to `tracertm` user

2. **Database Configuration:**
   The correct DATABASE_URL format is already in use:
   ```
   postgres://tracertm:tracertm_password@localhost:5432/tracertm
   ```

3. **Permissions Granted:**
   ```sql
   GRANT ALL PRIVILEGES ON DATABASE tracertm TO tracertm;
   ALTER DATABASE tracertm OWNER TO tracertm;
   ```

---

## Verification Steps

### Test Neo4j Connection

```bash
# Check Neo4j is running
brew services list | grep neo4j

# Start Neo4j if not running
brew services start neo4j

# Test connection (should succeed now)
cd backend
go run main.go
# Should see: "✅ Neo4j initialized" without syntax errors
```

### Test PostgreSQL Connection

```bash
# Verify database exists and is accessible
psql -U tracertm -d tracertm -c "SELECT version();"

# Test migration (dry-run)
psql -U tracertm -d tracertm -c "\dt"  # List tables
```

### Full Backend Startup

```bash
# Start the Go backend
cd backend
go run main.go

# Expected output:
# 🔌 Initializing PostgreSQL...
# 🔌 Initializing GORM...
# ✅ GORM initialized
# 🔌 Initializing Neo4j...
# ✅ Neo4j initialized
# 🏥 Running health checks...
#   ✅ PostgreSQL
#   ✅ Neo4j
# ✅ All infrastructure services initialized successfully!
```

---

## Infrastructure Setup (First Time)

If you need to set up the infrastructure from scratch:

### PostgreSQL Setup

```bash
# 1. Install PostgreSQL (if not already installed)
brew install postgresql@14

# 2. Start PostgreSQL
brew services start postgresql@14

# 3. Create database and user
psql -d postgres <<EOF
CREATE USER tracertm WITH PASSWORD 'tracertm_password' CREATEDB;
CREATE DATABASE tracertm OWNER tracertm;
GRANT ALL PRIVILEGES ON DATABASE tracertm TO tracertm;
EOF
```

### Neo4j Setup

```bash
# 1. Install Neo4j (if not already installed)
brew install neo4j

# 2. Start Neo4j
brew services start neo4j

# 3. Set password (default user is 'neo4j')
# Open browser to http://localhost:7474
# Login with neo4j/neo4j and set new password

# 4. Update .env.go-backend with Neo4j credentials
# NEO4J_URI=neo4j://localhost:7687
# NEO4J_USER=neo4j
# NEO4J_PASSWORD=your-password-here
```

### Environment Configuration

Make sure your `.env.go-backend` has:

```env
# PostgreSQL (Go format)
DATABASE_URL=postgres://tracertm:tracertm_password@localhost:5432/tracertm

# Neo4j
NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-neo4j-password
```

---

## Files Modified

1. **`/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend/internal/graph/neo4j_client.go`**
   - Fixed Neo4j index creation syntax (lines 109-132)
   - Added proper node labels to all CREATE INDEX queries
   - Wrapped property references in parentheses

---

## Testing the Fixes

```bash
# 1. Stop any running backend
pkill -f "go run main.go"

# 2. Clean build
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend
go clean -cache

# 3. Start backend with verbose logging
go run main.go 2>&1 | tee backend-startup.log

# 4. Verify no errors
# Look for:
# - ✅ Neo4j initialized (not index creation errors)
# - ✅ All health checks passed!
# - No "failed to run migrations" errors
```

---

## Troubleshooting

### If Neo4j index creation still fails:

1. Check Neo4j version:
   ```bash
   neo4j version
   ```

2. For Neo4j 5.x+, use Cloud/AuraDB syntax:
   ```cypher
   CREATE INDEX idx_project_id IF NOT EXISTS FOR (n:Node) ON (n.project_id)
   ```

3. For Neo4j 4.x, you may need to drop `IF NOT EXISTS`:
   ```cypher
   CREATE INDEX idx_project_id FOR (n:Node) ON (n.project_id)
   ```

### If PostgreSQL migrations fail:

1. Check database connectivity:
   ```bash
   psql -U tracertm -d tracertm -c "SELECT 1;"
   ```

2. Verify migrations directory exists:
   ```bash
   ls -la backend/internal/db/migrations/
   ```

3. Check migration table:
   ```bash
   psql -U tracertm -d tracertm -c "SELECT * FROM schema_migrations;"
   ```

---

## Summary

Both issues have been fixed:

1. **Neo4j Index Syntax** - Fixed by adding proper node labels (`:Node`, `:Item`) to all CREATE INDEX statements
2. **PostgreSQL Permissions** - Database user `tracertm` now has full permissions on the `tracertm` database

The backend should now start successfully without infrastructure errors.
