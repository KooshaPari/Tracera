#!/bin/bash
# Quick fix for graph rendering issue
# Creates graph tables and populates them from existing items/links

set -e

DB_URL="postgresql://tracertm:tracertm_password@localhost:5432/tracertm"

echo "🔧 TraceRTM Graph Quick Fix"
echo "=============================="
echo ""

echo "=== Step 1: Create graph tables if missing ==="
psql $DB_URL << 'SQL'
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

CREATE INDEX IF NOT EXISTS idx_graphs_project_type ON tracertm.graphs(project_id, graph_type);
CREATE UNIQUE INDEX IF NOT EXISTS idx_graphs_project_name ON tracertm.graphs(project_id, name);

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
ALTER TABLE tracertm.links ADD COLUMN IF NOT EXISTS graph_id VARCHAR(255);
CREATE INDEX IF NOT EXISTS idx_links_graph ON tracertm.links(graph_id);

SELECT 'Tables created successfully' as status;
SQL

echo ""
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
            'Auto-generated full traceability graph with all items and links',
            '{"auto_generated": true, "created_by": "quick_fix_script", "version": "1.0"}'::jsonb
        )
        ON CONFLICT (project_id, name) DO UPDATE
        SET updated_at = NOW(),
            description = EXCLUDED.description;

        -- Add all items as nodes
        INSERT INTO tracertm.graph_nodes (graph_id, item_id, project_id, is_primary)
        SELECT v_graph_id, id, project_id, TRUE
        FROM tracertm.items
        WHERE project_id = v_project.id AND deleted_at IS NULL
        ON CONFLICT (graph_id, item_id) DO NOTHING;

        GET DIAGNOSTICS v_items = ROW_COUNT;

        -- Associate links with graph
        UPDATE tracertm.links l
        SET graph_id = v_graph_id
        FROM tracertm.items i
        WHERE l.source_id = i.id
          AND i.project_id = v_project.id
          AND l.graph_id IS NULL;

        GET DIAGNOSTICS v_links = ROW_COUNT;

        RAISE NOTICE 'Project: % | Graph: % | Nodes: % | Links: %',
            v_project.name, v_graph_id, v_items, v_links;
    END LOOP;
END $$;
SQL

echo ""
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
echo ""
echo "Next steps:"
echo "  1. Refresh your browser (Cmd+R)"
echo "  2. Navigate to Traceability Graph view"
echo "  3. You should now see nodes and edges!"
echo ""
