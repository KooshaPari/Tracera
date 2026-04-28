# Graph Rendering Fix - Complete Solution

**Issue:** Frontend shows 0 nodes despite 4,931 items in database
**Root Cause:** Graph tables not created yet (migrations not fully applied)
**Status:** Solution documented

---

## Current State Analysis

### ✅ What Exists

**PostgreSQL Data:**
- ✅ 4,931 items across 59 types
- ✅ 1,770 links
- ✅ 4 projects (including SwiftRide: 531 items, 450 links)
- ✅ Database version: 053 (current)

**Infrastructure:**
- ✅ PostgreSQL running (port 5432)
- ⚠️ Neo4j running but not responding yet (port 7687)
- ✅ Migrations exist (009_add_graphs_and_graph_nodes.py)

### ❌ What's Missing

**Graph Tables:**
- ❌ `graphs` table - Not found
- ❌ `graph_nodes` table - Not found
- ❌ Graph-link associations

**Result:** Frontend queries graph tables → gets empty → shows 0 nodes

---

## Solution 1: Check Migration Status

The migration files exist but the tables weren't created. This could mean:

1. **Migration 009 was skipped** - Database jumped from 008 to later version
2. **Migration failed silently** - Tables creation errored but version updated
3. **Wrong schema** - Tables exist in different schema

### Verify Migration

```bash
# Check all tables in all schemas
psql postgresql://tracertm:tracertm_password@localhost:5432/tracertm -c "
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_name LIKE '%graph%'
  AND table_schema IN ('public', 'tracertm');"

# Check if migration ran
psql postgresql://tracertm:tracertm_password@localhost:5432/tracertm -c "
SELECT * FROM alembic_version;"

# List all migrations applied
ls -la alembic/versions/*.py | wc -l
```

### Manual Table Creation (If Migration Skipped)

```sql
-- Run this in psql if tables don't exist
CREATE TABLE IF NOT EXISTS tracertm.graphs (
    id VARCHAR(255) PRIMARY KEY,
    project_id UUID REFERENCES tracertm.projects(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    graph_type VARCHAR(100) NOT NULL,
    description TEXT,
    root_item_id UUID REFERENCES tracertm.items(id) ON DELETE SET NULL,
    graph_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_graphs_project_type ON tracertm.graphs(project_id, graph_type);
CREATE UNIQUE INDEX idx_graphs_project_name ON tracertm.graphs(project_id, name);

CREATE TABLE IF NOT EXISTS tracertm.graph_nodes (
    graph_id VARCHAR(255) REFERENCES tracertm.graphs(id) ON DELETE CASCADE,
    item_id UUID REFERENCES tracertm.items(id) ON DELETE CASCADE,
    project_id UUID REFERENCES tracertm.projects(id) ON DELETE CASCADE,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (graph_id, item_id)
);

CREATE INDEX idx_graph_nodes_graph ON tracertm.graph_nodes(graph_id);
CREATE INDEX idx_graph_nodes_item ON tracertm.graph_nodes(item_id);
CREATE INDEX idx_graph_nodes_project_graph ON tracertm.graph_nodes(project_id, graph_id);

-- Add graph_id to links if not exists
ALTER TABLE tracertm.links
ADD COLUMN IF NOT EXISTS graph_id VARCHAR(255) REFERENCES tracertm.graphs(id) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS idx_links_graph ON tracertm.links(graph_id);
```

---

## Solution 2: Existing Sync Tool Analysis

Found sync-related files:
- `src/tracertm/cli/commands/sync.py` - Local storage sync (not graph sync)
- `src/tracertm/services/sync_service.py` - Stub service
- `src/tracertm/services/integration_sync_processor.py` - Integration sync

**None of these sync PostgreSQL items → graph tables.**

We need to create a graph population service.

---

## Solution 3: Create Graph Population Script

### Graph Population Service

```python
# src/tracertm/services/graph_population_service.py
"""Service to populate graph tables from existing items and links."""

import logging
import uuid
from typing import Any, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.item import Item
from tracertm.models.link import Link

logger = logging.getLogger(__name__)


class GraphPopulationService:
    """Populates graph tables from existing items and links."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_default_graph_for_project(
        self,
        project_id: str,
        graph_name: str = "Default Traceability Graph",
        graph_type: str = "FULL",
    ) -> str:
        """Create a default graph containing all items and links for a project."""

        # Import here to avoid circular imports
        from tracertm.models.graph import Graph
        from tracertm.models.graph_node import GraphNode

        # Create graph record
        graph_id = f"graph_{uuid.uuid4()}"
        graph = Graph(
            id=graph_id,
            project_id=uuid.UUID(project_id),
            name=graph_name,
            graph_type=graph_type,
            description=f"Auto-generated graph containing all items and links",
            graph_metadata={"auto_generated": True, "version": "1.0"},
        )
        self.db.add(graph)
        await self.db.flush()

        # Get all non-deleted items for this project
        result = await self.db.execute(
            select(Item)
            .where(
                and_(
                    Item.project_id == uuid.UUID(project_id),
                    Item.deleted_at.is_(None)
                )
            )
        )
        items = result.scalars().all()

        logger.info(f"Found {len(items)} items for project {project_id}")

        # Add all items as graph nodes
        node_count = 0
        for item in items:
            node = GraphNode(
                graph_id=graph_id,
                item_id=item.id,
                project_id=uuid.UUID(project_id),
                is_primary=True,
            )
            self.db.add(node)
            node_count += 1

            if node_count % 100 == 0:
                await self.db.flush()
                logger.info(f"Added {node_count} graph nodes...")

        await self.db.flush()
        logger.info(f"Added {node_count} total graph nodes")

        # Update links to reference this graph
        result = await self.db.execute(
            select(Link)
            .where(
                Link.source_id.in_([item.id for item in items])
            )
        )
        links = result.scalars().all()

        link_count = 0
        for link in links:
            link.graph_id = graph_id
            link_count += 1

            if link_count % 100 == 0:
                await self.db.flush()
                logger.info(f"Updated {link_count} links...")

        await self.db.flush()
        logger.info(f"Updated {link_count} total links")

        await self.db.commit()

        return graph_id

    async def populate_all_projects(self) -> dict[str, str]:
        """Create default graphs for all projects."""
        from tracertm.models.project import Project

        result = await self.db.execute(select(Project))
        projects = result.scalars().all()

        graphs = {}
        for project in projects:
            try:
                logger.info(f"Creating graph for project: {project.name}")
                graph_id = await self.create_default_graph_for_project(
                    str(project.id),
                    graph_name=f"{project.name} - Traceability Graph",
                )
                graphs[str(project.id)] = graph_id
                logger.info(f"✅ Created graph {graph_id} for {project.name}")
            except Exception as e:
                logger.error(f"❌ Failed to create graph for {project.name}: {e}")

        return graphs
```

### CLI Command

```python
# src/tracertm/cli/commands/graph.py
"""Graph management CLI commands."""

import asyncio
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from tracertm.database.connection import get_async_session
from tracertm.services.graph_population_service import GraphPopulationService

app = typer.Typer(help="Graph management commands")
console = Console()


@app.command("populate")
def populate_graphs(
    project_id: str = typer.Option(None, "--project", help="Specific project ID"),
):
    """Populate graph tables from existing items and links."""

    async def _populate():
        async with get_async_session() as db:
            service = GraphPopulationService(db)

            if project_id:
                console.print(f"[cyan]Populating graph for project {project_id}...[/cyan]")
                graph_id = await service.create_default_graph_for_project(project_id)
                console.print(f"[green]✅ Created graph: {graph_id}[/green]")
            else:
                console.print("[cyan]Populating graphs for all projects...[/cyan]")
                graphs = await service.populate_all_projects()
                console.print(f"[green]✅ Created {len(graphs)} graphs[/green]")
                for pid, gid in graphs.items():
                    console.print(f"  Project {pid}: {gid}")

    asyncio.run(_populate())


@app.command("list")
def list_graphs():
    """List all graphs in the database."""

    async def _list():
        async with get_async_session() as db:
            from sqlalchemy import select
            from tracertm.models.graph import Graph

            result = await db.execute(
                select(Graph)
                .order_by(Graph.created_at.desc())
            )
            graphs = result.scalars().all()

            if not graphs:
                console.print("[yellow]No graphs found[/yellow]")
                return

            console.print(f"\n[cyan]Found {len(graphs)} graphs:[/cyan]\n")
            for g in graphs:
                # Count nodes
                from tracertm.models.graph_node import GraphNode
                result = await db.execute(
                    select(GraphNode).where(GraphNode.graph_id == g.id)
                )
                node_count = len(result.scalars().all())

                console.print(f"  [green]{g.name}[/green]")
                console.print(f"    ID: {g.id}")
                console.print(f"    Type: {g.graph_type}")
                console.print(f"    Nodes: {node_count}")
                console.print(f"    Project: {g.project_id}\n")

    asyncio.run(_list())


if __name__ == "__main__":
    app()
```

---

## Solution 3: Neo4j Sync Service (Future)

For Neo4j integration once it's running:

```python
# src/tracertm/services/neo4j_sync_service.py
"""Sync PostgreSQL data to Neo4j graph database."""

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class Neo4jSyncService:
    """Synchronize PostgreSQL data to Neo4j graph."""

    def __init__(self, db_session: AsyncSession, neo4j_client: Any):
        self.db = db_session
        self.neo4j = neo4j_client

    async def sync_project(self, project_id: str) -> dict[str, int]:
        """Sync all items and links for a project to Neo4j."""
        from tracertm.models.item import Item
        from tracertm.models.link import Link

        # Get items
        result = await self.db.execute(
            select(Item).where(
                Item.project_id == project_id,
                Item.deleted_at.is_(None)
            )
        )
        items = result.scalars().all()

        # Create nodes in Neo4j
        async with self.neo4j.session() as session:
            for item in items:
                await session.run("""
                    MERGE (i:Item {id: $id})
                    SET i.title = $title,
                        i.type = $type,
                        i.project_id = $project_id,
                        i.status = $status
                """,
                id=str(item.id),
                title=item.title,
                type=item.type,
                project_id=str(project_id),
                status=item.status
                )

        # Get links
        item_ids = [item.id for item in items]
        result = await self.db.execute(
            select(Link).where(Link.source_id.in_(item_ids))
        )
        links = result.scalars().all()

        # Create relationships
        async with self.neo4j.session() as session:
            for link in links:
                await session.run("""
                    MATCH (source:Item {id: $source_id})
                    MATCH (target:Item {id: $target_id})
                    MERGE (source)-[r:LINK {id: $link_id}]->(target)
                    SET r.type = $link_type
                """,
                source_id=str(link.source_id),
                target_id=str(link.target_id),
                link_id=str(link.id),
                link_type=link.link_type
                )

        return {
            "items_synced": len(items),
            "links_synced": len(links)
        }
```

---

## Immediate Fix: Create Graph Tables

### Step 1: Check Current Schema

```bash
psql postgresql://tracertm:tracertm_password@localhost:5432/tracertm -c "
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'tracertm'
  AND table_name LIKE '%graph%'
ORDER BY table_name;"
```

### Step 2: Manually Create Tables (If Missing)

```bash
psql postgresql://tracertm:tracertm_password@localhost:5432/tracertm << 'EOF'
-- Create graphs table
CREATE TABLE IF NOT EXISTS tracertm.graphs (
    id VARCHAR(255) PRIMARY KEY,
    project_id UUID REFERENCES tracertm.projects(id) ON DELETE CASCADE NOT NULL,
    name VARCHAR(200) NOT NULL,
    graph_type VARCHAR(100) NOT NULL,
    description TEXT,
    root_item_id UUID REFERENCES tracertm.items(id) ON DELETE SET NULL,
    graph_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_graphs_project_type
ON tracertm.graphs(project_id, graph_type);

CREATE UNIQUE INDEX IF NOT EXISTS idx_graphs_project_name
ON tracertm.graphs(project_id, name);

-- Create graph_nodes table
CREATE TABLE IF NOT EXISTS tracertm.graph_nodes (
    graph_id VARCHAR(255) REFERENCES tracertm.graphs(id) ON DELETE CASCADE,
    item_id UUID REFERENCES tracertm.items(id) ON DELETE CASCADE,
    project_id UUID REFERENCES tracertm.projects(id) ON DELETE CASCADE NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    PRIMARY KEY (graph_id, item_id)
);

CREATE INDEX IF NOT EXISTS idx_graph_nodes_graph ON tracertm.graph_nodes(graph_id);
CREATE INDEX IF NOT EXISTS idx_graph_nodes_item ON tracertm.graph_nodes(item_id);
CREATE INDEX IF NOT EXISTS idx_graph_nodes_project_graph ON tracertm.graph_nodes(project_id, graph_id);

-- Add graph_id to links
ALTER TABLE tracertm.links
ADD COLUMN IF NOT EXISTS graph_id VARCHAR(255) REFERENCES tracertm.graphs(id) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS idx_links_graph ON tracertm.links(graph_id);

-- Verify tables created
\dt tracertm.graph*
EOF
```

### Step 3: Populate Graphs

```bash
# Create graph population script
cat > /tmp/populate_graphs.sql << 'EOF'
-- Populate graph for SwiftRide project
DO $$
DECLARE
    v_project_id UUID := 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e';
    v_graph_id VARCHAR := 'graph_swiftride_default';
    v_item_record RECORD;
    v_link_record RECORD;
    v_node_count INT := 0;
    v_link_count INT := 0;
BEGIN
    -- Create default graph
    INSERT INTO tracertm.graphs (id, project_id, name, graph_type, description, graph_metadata)
    VALUES (
        v_graph_id,
        v_project_id,
        'SwiftRide - Traceability Graph',
        'FULL',
        'Default graph with all items and links',
        '{"auto_generated": true, "version": "1.0"}'::jsonb
    )
    ON CONFLICT (project_id, name) DO NOTHING;

    -- Add all items as nodes
    FOR v_item_record IN
        SELECT id FROM tracertm.items
        WHERE project_id = v_project_id
          AND deleted_at IS NULL
    LOOP
        INSERT INTO tracertm.graph_nodes (graph_id, item_id, project_id, is_primary)
        VALUES (v_graph_id, v_item_record.id, v_project_id, TRUE)
        ON CONFLICT (graph_id, item_id) DO NOTHING;

        v_node_count := v_node_count + 1;
    END LOOP;

    -- Associate links with graph
    FOR v_link_record IN
        SELECT l.id FROM tracertm.links l
        JOIN tracertm.items i ON l.source_id = i.id
        WHERE i.project_id = v_project_id
    LOOP
        UPDATE tracertm.links
        SET graph_id = v_graph_id
        WHERE id = v_link_record.id;

        v_link_count := v_link_count + 1;
    END LOOP;

    RAISE NOTICE 'Graph created: %', v_graph_id;
    RAISE NOTICE 'Nodes added: %', v_node_count;
    RAISE NOTICE 'Links updated: %', v_link_count;
END $$;
EOF

# Run the script
psql postgresql://tracertm:tracertm_password@localhost:5432/tracertm -f /tmp/populate_graphs.sql
```

---

## Quick Fix: All-in-One Script

```bash
#!/bin/bash
# quick_fix_graph.sh

set -e

DB_URL="postgresql://tracertm:tracertm_password@localhost:5432/tracertm"

echo "=== Step 1: Create graph tables if missing ==="
psql $DB_URL << 'SQL'
CREATE TABLE IF NOT EXISTS tracertm.graphs (
    id VARCHAR(255) PRIMARY KEY,
    project_id UUID REFERENCES tracertm.projects(id) ON DELETE CASCADE NOT NULL,
    name VARCHAR(200) NOT NULL,
    graph_type VARCHAR(100) NOT NULL,
    description TEXT,
    root_item_id UUID REFERENCES tracertm.items(id) ON DELETE SET NULL,
    graph_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_graphs_project_type ON tracertm.graphs(project_id, graph_type);
CREATE UNIQUE INDEX IF NOT EXISTS idx_graphs_project_name ON tracertm.graphs(project_id, name);

CREATE TABLE IF NOT EXISTS tracertm.graph_nodes (
    graph_id VARCHAR(255) REFERENCES tracertm.graphs(id) ON DELETE CASCADE,
    item_id UUID REFERENCES tracertm.items(id) ON DELETE CASCADE,
    project_id UUID REFERENCES tracertm.projects(id) ON DELETE CASCADE NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    PRIMARY KEY (graph_id, item_id)
);
CREATE INDEX IF NOT EXISTS idx_graph_nodes_graph ON tracertm.graph_nodes(graph_id);
CREATE INDEX IF NOT EXISTS idx_graph_nodes_item ON tracertm.graph_nodes(item_id);

ALTER TABLE tracertm.links ADD COLUMN IF NOT EXISTS graph_id VARCHAR(255);
CREATE INDEX IF NOT EXISTS idx_links_graph ON tracertm.links(graph_id);
SQL

echo "=== Step 2: Populate graphs for all projects ==="
psql $DB_URL << 'SQL'
DO $$
DECLARE
    v_project RECORD;
    v_graph_id VARCHAR;
    v_items INT;
    v_links INT;
BEGIN
    FOR v_project IN SELECT id, name FROM tracertm.projects LOOP
        v_graph_id := 'graph_' || replace(v_project.id::text, '-', '');

        -- Create graph
        INSERT INTO tracertm.graphs (id, project_id, name, graph_type, description, graph_metadata)
        VALUES (
            v_graph_id,
            v_project.id,
            v_project.name || ' - Traceability Graph',
            'FULL',
            'Auto-generated full traceability graph',
            '{"auto_generated": true}'::jsonb
        )
        ON CONFLICT (project_id, name) DO UPDATE SET updated_at = NOW();

        -- Add nodes
        INSERT INTO tracertm.graph_nodes (graph_id, item_id, project_id, is_primary)
        SELECT v_graph_id, id, project_id, TRUE
        FROM tracertm.items
        WHERE project_id = v_project.id AND deleted_at IS NULL
        ON CONFLICT (graph_id, item_id) DO NOTHING;

        GET DIAGNOSTICS v_items = ROW_COUNT;

        -- Update links
        UPDATE tracertm.links l
        SET graph_id = v_graph_id
        FROM tracertm.items i
        WHERE l.source_id = i.id AND i.project_id = v_project.id;

        GET DIAGNOSTICS v_links = ROW_COUNT;

        RAISE NOTICE 'Project: % | Graph: % | Nodes: % | Links: %',
            v_project.name, v_graph_id, v_items, v_links;
    END LOOP;
END $$;
SQL

echo "=== Step 3: Verify graphs created ==="
psql $DB_URL -c "
SELECT
    g.name,
    g.graph_type,
    (SELECT COUNT(*) FROM tracertm.graph_nodes WHERE graph_id = g.id) as nodes,
    (SELECT COUNT(*) FROM tracertm.links WHERE graph_id = g.id) as links
FROM tracertm.graphs g
ORDER BY nodes DESC;"

echo ""
echo "✅ Graph population complete!"
echo "Refresh your frontend to see the graph."
```

---

## Execution Plan

### Run the Quick Fix

```bash
# Make script executable
chmod +x quick_fix_graph.sh

# Run it
./quick_fix_graph.sh
```

**Expected Output:**
```
=== Step 1: Create graph tables if missing ===
CREATE TABLE
CREATE INDEX
...

=== Step 2: Populate graphs for all projects ===
NOTICE:  Project: SwiftRide - Ride-sharing Platform | Graph: graph_cd6d847c0f2e4cccbf1ac96b08c97d4e | Nodes: 531 | Links: 450
...

=== Step 3: Verify graphs created ===
                     name                      | graph_type | nodes | links
----------------------------------------------+------------+-------+-------
 SwiftRide - Ride-sharing Platform - Traceability Graph | FULL | 531   | 450

✅ Graph population complete!
```

### Verify in Frontend

1. Refresh the browser (Cmd+R)
2. Navigate to Traceability Graph view
3. Should now show: **531 nodes · 450 edges rendered**

---

## Summary of 3 Solutions

1. ✅ **Neo4j Started** - Via Homebrew (still warming up)
2. ✅ **Sync Tool Found** - Existing sync is for local storage, not graphs
3. ✅ **Graph Population Script Created** - SQL script to populate graph tables from items/links

---

## Next Steps

1. **Run the quick fix script** to create and populate graph tables
2. **Refresh frontend** to see the graph
3. **Once Neo4j is ready** (check with `curl http://localhost:7474`), run Neo4j sync for advanced queries

**File Location:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/GRAPH_FIX_SOLUTION.md`
