# Database Setup Instructions

## Supabase PostgreSQL Setup

### Step 1: Access Supabase Dashboard

1. Go to https://app.supabase.com
2. Select project "TraceRTM" (Reference ID: uftgquyagdvshekivcat)
3. Navigate to SQL Editor

### Step 2: Create Extensions

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "vector";
```

### Step 3: Run Migration

1. Open `backend/db/migrations/20250130000000_init.sql`
2. Copy entire content
3. Paste into Supabase SQL Editor
4. Click "Run"

**Tables created**:
- profiles
- projects
- items
- links
- agents
- subscriptions
- events
- snapshots

### Step 4: Verify

```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';
```

Should show 8 tables.

## Neo4j Aura Setup

### Step 1: Access Neo4j Browser

1. Go to https://console.neo4j.io
2. Select "TraceRTM" instance
3. Click "Open"
4. Login with credentials from .env

### Step 2: Create Constraints

```cypher
CREATE CONSTRAINT item_id_unique IF NOT EXISTS
FOR (i:Item) REQUIRE i.item_id IS UNIQUE;

CREATE CONSTRAINT project_id_unique IF NOT EXISTS
FOR (p:Project) REQUIRE p.project_id IS UNIQUE;

CREATE CONSTRAINT agent_id_unique IF NOT EXISTS
FOR (a:Agent) REQUIRE a.agent_id IS UNIQUE;
```

### Step 3: Create Indexes

```cypher
CREATE INDEX project_id_idx IF NOT EXISTS
FOR (n) ON (n.project_id);

CREATE INDEX type_idx IF NOT EXISTS
FOR (n) ON (n.type);

CREATE INDEX name_idx IF NOT EXISTS
FOR (n) ON (n.name);
```

### Step 4: Verify

```cypher
SHOW CONSTRAINTS;
SHOW INDEXES;
```

## Verification

### Test PostgreSQL Connection

```bash
cd backend
psql $DB_DIRECT_URL -c "SELECT COUNT(*) FROM projects;"
```

### Test Neo4j Connection

```bash
cd backend
./tracertm-backend
# Check logs for Neo4j connection success
```

### Test All Services

```bash
curl http://localhost:8080/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "postgres": "connected",
    "redis": "connected",
    "nats": "connected",
    "neo4j": "connected"
  }
}
```

## Troubleshooting

**PostgreSQL connection fails**:
- Check DB_DIRECT_URL in .env
- Verify IP whitelist in Supabase

**Neo4j connection fails**:
- Check NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
- Verify credentials in .env

**Extensions not found**:
- Supabase free tier may not support all extensions
- Use alternative: pgvector via Supabase managed extension

**Estimated time**: 15-20 minutes

