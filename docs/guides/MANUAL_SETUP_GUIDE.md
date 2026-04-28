# Manual Setup Guide - TraceRTM Infrastructure

**Status:** All infrastructure configured, manual steps required to finalize

---

## 1️⃣ SUPABASE DATABASE SETUP

### Step 1: Apply Schema
1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Select project "TraceRTM" (Reference ID: uftgquyagdvshekivcat)
3. Go to **SQL Editor**
4. Click **New Query**
5. Copy content from `backend/schema.sql`
6. Paste into editor
7. Click **Run**

### Step 2: Verify Extensions
In SQL Editor, run:
```sql
SELECT * FROM pg_extension WHERE extname IN ('uuid-ossp', 'pg_trgm', 'vector');
```

Should show 3 rows. If not, run:
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "vector";
```

### Step 3: Verify Tables
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

Should show: profiles, projects, items, links, agents, subscriptions

---

## 2️⃣ NEO4J SETUP

### Step 1: Connect to Neo4j
1. Go to [Neo4j Aura Console](https://console.neo4j.io)
2. Select instance "Instance01"
3. Click **Open**
4. Use credentials from `.env`:
   - Username: `neo4j`
   - Password: `vn3SzzBOn0nOiVnZNW224NYUYPt66NF37tTDP6yAh5w`

### Step 2: Create Constraints
Run in Neo4j Browser:
```cypher
CREATE CONSTRAINT item_id_unique IF NOT EXISTS FOR (i:Item) REQUIRE i.id IS UNIQUE;
CREATE CONSTRAINT project_id_unique IF NOT EXISTS FOR (p:Project) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT agent_id_unique IF NOT EXISTS FOR (a:Agent) REQUIRE a.id IS UNIQUE;
```

### Step 3: Create Indexes
```cypher
CREATE INDEX item_project_idx IF NOT EXISTS FOR (i:Item) ON (i.project_id);
CREATE INDEX item_type_idx IF NOT EXISTS FOR (i:Item) ON (i.type);
CREATE INDEX project_name_idx IF NOT EXISTS FOR (p:Project) ON (p.name);
CREATE INDEX agent_project_idx IF NOT EXISTS FOR (a:Agent) ON (a.project_id);
```

---

## 3️⃣ VERIFY BACKEND

### Build Backend
```bash
cd backend
go build -o tracertm-backend
```

### Run Backend
```bash
cd backend
./tracertm-backend
```

Expected output:
```
✅ PostgreSQL connected
✅ Redis connected
✅ NATS connected
✅ Neo4j connected
✅ Hatchet connected
✅ Server running on :8080
```

---

## 4️⃣ SEED INITIAL DATA

### Create Initial Project
```bash
curl -X POST http://localhost:8080/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bifrost",
    "description": "Initial test project"
  }'
```

### Create Initial Agent
```bash
curl -X POST http://localhost:8080/api/v1/agents \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "<project_id>",
    "name": "Agent-1",
    "capabilities": ["read", "write"]
  }'
```

---

## ✅ VERIFICATION CHECKLIST

- [ ] Supabase schema applied
- [ ] Neo4j constraints created
- [ ] Neo4j indexes created
- [ ] Backend builds successfully
- [ ] Backend starts without errors
- [ ] All services report healthy
- [ ] Initial project created
- [ ] Initial agent created
- [ ] API endpoints responding

---

## 🚀 READY FOR PRODUCTION

Once all steps complete, system is ready for:
- Development testing
- Integration testing
- Production deployment

