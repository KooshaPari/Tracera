-- Migration: Add Spatial Viewport Support for Infinite Graph Exploration
-- Purpose: Add position_x, position_y columns with B-tree indexes for O(log n) spatial queries

-- =============================================================================
-- PART 1: Add Position Columns to Items Table
-- =============================================================================

-- Add position_x and position_y columns if they don't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'items' AND column_name = 'position_x'
    ) THEN
        ALTER TABLE items ADD COLUMN position_x DOUBLE PRECISION DEFAULT 0;
        RAISE NOTICE 'Added position_x column to items table';
    ELSE
        RAISE NOTICE 'position_x column already exists, skipping';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'items' AND column_name = 'position_y'
    ) THEN
        ALTER TABLE items ADD COLUMN position_y DOUBLE PRECISION DEFAULT 0;
        RAISE NOTICE 'Added position_y column to items table';
    ELSE
        RAISE NOTICE 'position_y column already exists, skipping';
    END IF;
END $$;

-- =============================================================================
-- PART 2: Create Spatial Indexes for Viewport Queries
-- =============================================================================

-- B-tree index on position_x for range queries (min_x <= x <= max_x)
CREATE INDEX IF NOT EXISTS idx_items_position_x
ON items (position_x)
WHERE deleted_at IS NULL;

-- B-tree index on position_y for range queries (min_y <= y <= max_y)
CREATE INDEX IF NOT EXISTS idx_items_position_y
ON items (position_y)
WHERE deleted_at IS NULL;

-- Composite B-tree index for 2D range queries (viewport bounds)
-- PostgreSQL can use this for both X and Y range filtering
CREATE INDEX IF NOT EXISTS idx_items_position_xy
ON items (position_x, position_y)
WHERE deleted_at IS NULL;

-- Composite index with project_id for project-scoped viewport queries
CREATE INDEX IF NOT EXISTS idx_items_project_position
ON items (project_id, position_x, position_y)
WHERE deleted_at IS NULL;

-- =============================================================================
-- PART 3: Add Comments for Documentation
-- =============================================================================

COMMENT ON COLUMN items.position_x IS
'X coordinate for graph layout. Used for spatial viewport queries in infinite canvas.';

COMMENT ON COLUMN items.position_y IS
'Y coordinate for graph layout. Used for spatial viewport queries in infinite canvas.';

COMMENT ON INDEX idx_items_position_x IS
'B-tree index for X-axis range queries in viewport bounds.';

COMMENT ON INDEX idx_items_position_y IS
'B-tree index for Y-axis range queries in viewport bounds.';

COMMENT ON INDEX idx_items_position_xy IS
'Composite B-tree index for 2D spatial range queries (viewport bounds).';

COMMENT ON INDEX idx_items_project_position IS
'Composite index for project-scoped spatial queries. Enables O(log n) viewport queries.';

-- =============================================================================
-- PART 4: Create Helper Function for Viewport Query
-- =============================================================================

CREATE OR REPLACE FUNCTION get_viewport_bounds(p_project_id TEXT)
RETURNS TABLE (
    min_x DOUBLE PRECISION,
    max_x DOUBLE PRECISION,
    min_y DOUBLE PRECISION,
    max_y DOUBLE PRECISION,
    total_nodes BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        MIN(position_x) AS min_x,
        MAX(position_x) AS max_x,
        MIN(position_y) AS min_y,
        MAX(position_y) AS max_y,
        COUNT(*) AS total_nodes
    FROM items
    WHERE project_id = p_project_id
      AND deleted_at IS NULL
      AND position_x IS NOT NULL
      AND position_y IS NOT NULL;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_viewport_bounds IS
'Returns the bounding box and total node count for a project. Useful for initial viewport setup.';

-- =============================================================================
-- PART 5: Create Statistics for Query Planner
-- =============================================================================

-- Update statistics to include position columns
DROP STATISTICS IF EXISTS items_spatial_stats;
CREATE STATISTICS items_spatial_stats (dependencies)
ON project_id, position_x, position_y, deleted_at
FROM items;

-- Analyze table to update statistics
ANALYZE items;

-- =============================================================================
-- VERIFICATION
-- =============================================================================

-- Verify columns were added
SELECT
    column_name,
    data_type,
    column_default,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'items'
  AND column_name IN ('position_x', 'position_y')
ORDER BY ordinal_position;

-- Verify indexes were created
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'items'
  AND indexname LIKE '%position%'
ORDER BY indexname;

-- Show position data distribution (if any data exists)
SELECT
    COUNT(*) AS total_items,
    COUNT(*) FILTER (WHERE position_x IS NOT NULL) AS items_with_x,
    COUNT(*) FILTER (WHERE position_y IS NOT NULL) AS items_with_y,
    COUNT(*) FILTER (WHERE position_x IS NOT NULL AND position_y IS NOT NULL) AS items_with_positions
FROM items
WHERE deleted_at IS NULL;
