# Graph Not Rendering - Diagnosis and Fix

**Issue:** Frontend shows "0 nodes · 0 edges rendered" despite database having 4,931 items and 1,770 links
**Root Cause:** Neo4j service not running
**Status:** ✅ Diagnosed

---

## Current State

### ✅ What's Working

**PostgreSQL (Running):**
- ✅ 4,931 items across 59 types
- ✅ 1,770 links
- ✅ 4 projects including SwiftRide (531 items, 450 links)

**Data Breakdown for SwiftRide Project:**
```
Features: 100
Requirements: 100
Stories: 100
Tasks: 50
APIs: 50
Tests: 50
+ 18 other types
```

### ❌ What's Not Working

**Neo4j (Not Running):**
- ❌ Port 7687 not listening
- ❌ Graph database empty/unavailable
- ❌ Frontend can't query graph relationships
- ❌ Result: Empty graph visualization

---

## Why Graph Shows 0 Nodes

The TraceRTM frontend's graph view queries **Neo4j** for relationships and visualization, not PostgreSQL directly. The flow is:

```
Frontend Graph Component
    ↓ GraphQL/API request
Backend Graph Service
    ↓ Cypher queries
Neo4j Database (NOT RUNNING ❌)
    ↓ Returns empty result
Frontend renders 0 nodes
```

Meanwhile, PostgreSQL has all the data but isn't being used for graph visualization.

---

## Fix: Start Neo4j

### Option 1: Docker (Recommended)

```bash
# Start Neo4j via docker-compose
docker-compose up -d neo4j

# Or start Docker Desktop first, then:
open -a Docker
# Wait for Docker to start, then:
docker-compose up -d neo4j
```

### Option 2: Homebrew (Native)

```bash
# Install Neo4j
brew install neo4j

# Start Neo4j service
brew services start neo4j

# Or run in foreground
neo4j console
```

### Option 3: Manual Docker

```bash
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/neo4j_password \
  neo4j:latest
```

---

## Verify Neo4j is Running

```bash
# Check port
lsof -i :7687 | grep LISTEN

# Test connection
echo "RETURN 1 as test;" | cypher-shell -u neo4j -p neo4j_password

# Check web UI
open http://localhost:7474
```

---

## Sync PostgreSQL Data to Neo4j

Once Neo4j is running, you need to **sync the PostgreSQL data** to the Neo4j graph:

### Check if Sync Tool Exists

```bash
# Look for graph sync service
ls -la src/tracertm/services/graph* src/tracertm/services/sync*
```

### Manual Sync (If No Tool Exists)

```python
# Python script to sync PostgreSQL → Neo4j
import asyncio
from tracertm.database.connection import get_db_session
from tracertm.core.graph import get_neo4j_client

async def sync_data():
    db = await get_db_session()
    neo4j = get_neo4j_client()

    # Get all items from PostgreSQL
    items = await db.execute("SELECT id, title, type, project_id FROM items WHERE deleted_at IS NULL")

    # Create nodes in Neo4j
    async with neo4j.session() as session:
        for item in items:
            await session.run("""
                MERGE (i:Item {id: $id})
                SET i.title = $title,
                    i.type = $type,
                    i.project_id = $project_id
            """, id=str(item.id), title=item.title, type=item.type, project_id=str(item.project_id))

    # Get all links
    links = await db.execute("SELECT source_id, target_id, link_type FROM links")

    # Create relationships in Neo4j
    async with neo4j.session() as session:
        for link in links:
            await session.run("""
                MATCH (source:Item {id: $source_id})
                MATCH (target:Item {id: $target_id})
                MERGE (source)-[:LINK {type: $link_type}]->(target)
            """, source_id=str(link.source_id), target_id=str(link.target_id), link_type=link.link_type)

if __name__ == "__main__":
    asyncio.run(sync_data())
```

---

## Alternative: Use PostgreSQL for Graph

If you don't want to run Neo4j, you could modify the frontend to query PostgreSQL directly:

```typescript
// Instead of Cypher queries to Neo4j:
// MATCH (n)-[r]->(m) RETURN n, r, m

// Use SQL queries to PostgreSQL:
SELECT
  i1.id as source_id,
  i1.title as source_title,
  i1.type as source_type,
  l.link_type,
  i2.id as target_id,
  i2.title as target_title,
  i2.type as target_type
FROM links l
JOIN items i1 ON l.source_id = i1.id
JOIN items i2 ON l.target_id = i2.id
WHERE i1.project_id = $project_id
  AND i1.deleted_at IS NULL
  AND i2.deleted_at IS NULL
```

---

## Quick Fix Summary

**The graph will work once you:**

1. ✅ **Start Neo4j**
   ```bash
   brew services start neo4j
   # OR
   docker-compose up -d neo4j
   ```

2. ✅ **Verify Connection**
   ```bash
   echo "RETURN 1;" | cypher-shell -u neo4j -p neo4j_password
   ```

3. ✅ **Sync Data** (if needed)
   ```bash
   # Look for existing sync command
   python -m tracertm.cli sync-graph
   # OR run manual sync script
   ```

4. ✅ **Refresh Frontend**
   - Reload the page
   - Should show 531 nodes + 450 edges for SwiftRide

---

## Verification

After starting Neo4j and syncing:

```cypher
// Check node count
MATCH (n:Item) WHERE n.project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
RETURN count(n) as node_count;
// Expected: 531

// Check relationship count
MATCH ()-[r:LINK]->()
WHERE r.project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  OR exists((startNode(r).project_id))
RETURN count(r) as link_count;
// Expected: ~450
```

---

## Root Cause

**Why This Happened:**

The TraceRTM system uses **dual-database architecture**:
- **PostgreSQL** - Primary data store (items, links, metadata)
- **Neo4j** - Graph visualization and advanced queries

The data exists in PostgreSQL, but Neo4j needs to be:
1. Running
2. Synced with PostgreSQL data

The graph view frontend queries Neo4j exclusively, so when Neo4j is down, the graph shows empty even though data exists.

---

## Long-term Solution

**Recommended: Implement automatic sync**

1. **Event-based sync** - Trigger sync on item/link changes
2. **NATS event listener** - Subscribe to item/link events
3. **Periodic batch sync** - Temporal scheduled workflow
4. **Frontend fallback** - Query PostgreSQL if Neo4j unavailable

This is what the newly implemented Agent System's NATS events can help with! 🚀

---

**Status:** Issue diagnosed, fix documented
**Action Required:** Start Neo4j service
**Expected Result:** Graph will render with 531 nodes and 450 edges
