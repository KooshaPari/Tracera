# Infrastructure Quick Fix Guide

## TL;DR - What Was Fixed

### 1. Neo4j Index Syntax Error ✅
**File:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend/internal/graph/neo4j_client.go`

**Changed:**
```diff
- "CREATE INDEX idx_project_id IF NOT EXISTS FOR (n) ON n.project_id",
+ "CREATE INDEX idx_project_id IF NOT EXISTS FOR (n:Node) ON (n.project_id)",
```

**Why:** Neo4j requires node labels in index creation. Missing `:Node` label caused syntax error.

### 2. PostgreSQL Permissions ✅
**Commands executed:**
```sql
GRANT ALL PRIVILEGES ON DATABASE tracertm TO tracertm;
GRANT ALL PRIVILEGES ON SCHEMA public TO tracertm;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO tracertm;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO tracertm;
```

**Why:** The `tracertm` user needed full permissions on database and schema.

---

## Test the Fixes

```bash
# Test backend startup
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend
go run main.go

# Expected output (no errors):
# ✅ Neo4j initialized
# ✅ All infrastructure services initialized successfully!
```

---

## If You Still See Errors

### Neo4j Index Errors
```bash
# Check Neo4j is running
brew services list | grep neo4j

# Start if needed
brew services start neo4j
```

### PostgreSQL Migration Errors
```bash
# Test database connection
psql -U tracertm -d tracertm -c "SELECT version();"

# If connection fails, check DATABASE_URL in .env.go-backend:
# DATABASE_URL=postgres://tracertm:tracertm_password@localhost:5432/tracertm
```

---

## Files Changed

1. **`backend/internal/graph/neo4j_client.go`** - Fixed Neo4j index syntax
2. **PostgreSQL permissions** - Granted via SQL commands (no file changes)

---

## Next Steps

The infrastructure should now initialize without errors. If you see any other issues, check:

1. Neo4j is running: `brew services list | grep neo4j`
2. PostgreSQL is running: `brew services list | grep postgresql`
3. Environment variables are correct in `.env.go-backend`
