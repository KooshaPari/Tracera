# TraceRTM - Canonical Setup Approach

## Overview

All setup operations are now integrated into the canonical Go codebase. No standalone scripts or temporary files are used.

---

## Setup Command Location

**File**: `backend/cmd/setup/main.go`

This is a proper Go command that:
- ✅ Integrates with the canonical codebase
- ✅ Uses proper dependency management (go.mod)
- ✅ Follows Go best practices
- ✅ Can be built and distributed as a binary
- ✅ Handles errors gracefully

---

## How to Use

### Option 1: Using Make (Recommended)

```bash
cd backend
make setup-db
```

### Option 2: Direct Go Command

```bash
cd backend
go run cmd/setup/main.go
```

### Option 3: Build Binary First

```bash
cd backend
go build -o tracertm-setup cmd/setup/main.go
./tracertm-setup
```

---

## What It Does

### PostgreSQL Setup
1. Connects to Supabase using `DB_DIRECT_URL`
2. Creates extensions:
   - `uuid-ossp` - UUID generation
   - `pg_trgm` - Full-text search
   - `vector` - Vector embeddings
3. Applies schema from `schema.sql`
4. Verifies table creation

### Neo4j Setup
1. Connects to Neo4j Aura using credentials
2. Creates unique constraints:
   - `item_id_unique` - Item uniqueness
   - `project_id_unique` - Project uniqueness
   - `agent_id_unique` - Agent uniqueness
3. Creates performance indexes:
   - `project_id_idx` - Project filtering
   - `type_idx` - Type filtering
   - `name_idx` - Name filtering
4. Verifies constraint/index creation

---

## Environment Variables Required

```bash
# PostgreSQL
DB_DIRECT_URL=postgresql://...

# Neo4j
NEO4J_URI=neo4j+s://...
NEO4J_USERNAME=...
NEO4J_PASSWORD=...
```

---

## Makefile Integration

The `backend/Makefile` includes these commands:

```makefile
make setup-db      # Setup databases only
make build         # Build backend binary
make run           # Run backend
make setup         # Full setup: databases + build
```

---

## Build Status

✅ Compiles successfully
✅ Uses proper Go imports
✅ Integrates with go.mod
✅ No external dependencies beyond what's already in the project

---

## Why This Approach?

1. **Canonical**: Part of the official codebase, not temporary scripts
2. **Maintainable**: Easy to update and version control
3. **Distributable**: Can be built as a standalone binary
4. **Testable**: Can be tested like any other Go code
5. **Integrated**: Works with existing build system (Makefile)
6. **Professional**: Follows Go best practices

---

## Next Steps

1. Run setup: `cd backend && make setup-db`
2. Build backend: `make build`
3. Run backend: `make run`
4. Deploy: Use Docker or Kubernetes manifests

---

**Status**: ✅ COMPLETE
**Location**: `backend/cmd/setup/main.go`
**Integration**: Makefile + go.mod

