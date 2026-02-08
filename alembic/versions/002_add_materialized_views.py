"""Add materialized views for SSOT layers.

Revision ID: 002
Revises: 001
Create Date: 2025-11-21

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: str | None = "001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create materialized views for 8 attached layers."""
    # Layer 1: Traceability Matrix View
    op.execute("""
        CREATE MATERIALIZED VIEW traceability_matrix AS
        SELECT
            l.id as link_id,
            l.project_id,
            i1.id as source_id,
            i1.title as source_title,
            i1.view as source_view,
            i1.item_type as source_type,
            i2.id as target_id,
            i2.title as target_title,
            i2.view as target_view,
            i2.item_type as target_type,
            l.link_type,
            l.created_at,
            l.link_metadata as metadata
        FROM links l
        JOIN items i1 ON l.source_item_id = i1.id
        JOIN items i2 ON l.target_item_id = i2.id
        WHERE i1.deleted_at IS NULL AND i2.deleted_at IS NULL;
    """)

    # Create unique index for concurrent refresh
    op.execute("""
        CREATE UNIQUE INDEX idx_traceability_unique ON traceability_matrix(link_id);
    """)

    # Create indexes for performance
    op.execute("CREATE INDEX idx_traceability_project ON traceability_matrix(project_id);")
    op.execute("CREATE INDEX idx_traceability_source ON traceability_matrix(source_id);")
    op.execute("CREATE INDEX idx_traceability_target ON traceability_matrix(target_id);")
    op.execute("CREATE INDEX idx_traceability_type ON traceability_matrix(link_type);")
    op.execute("CREATE INDEX idx_traceability_source_type ON traceability_matrix(source_id, link_type);")
    op.execute("CREATE INDEX idx_traceability_target_type ON traceability_matrix(target_id, link_type);")

    # Layer 2: Impact Analysis View
    op.execute("""
        CREATE MATERIALIZED VIEW impact_analysis AS
        WITH RECURSIVE impact_chain AS (
            -- Base case: direct relationships
            SELECT
                l.source_item_id as root_id,
                l.target_item_id as affected_id,
                l.link_type,
                1 as depth,
                ARRAY[l.source_item_id, l.target_item_id] as path,
                l.project_id
            FROM links l
            WHERE l.link_type IN ('depends_on', 'blocks', 'implements', 'tests')

            UNION ALL

            -- Recursive case: transitive relationships
            SELECT
                ic.root_id,
                l.target_item_id,
                l.link_type,
                ic.depth + 1,
                ic.path || l.target_item_id,
                l.project_id
            FROM impact_chain ic
            JOIN links l ON ic.affected_id = l.source_item_id
            WHERE ic.depth < 10  -- Limit recursion depth
            AND NOT l.target_item_id = ANY(ic.path)  -- Avoid cycles
            AND l.link_type IN ('depends_on', 'blocks', 'implements', 'tests')
        )
        SELECT
            root_id,
            affected_id,
            link_type,
            depth,
            path,
            project_id
        FROM impact_chain;
    """)

    # Create unique index for concurrent refresh
    op.execute("""
        CREATE UNIQUE INDEX idx_impact_unique ON impact_analysis(root_id, affected_id, depth);
    """)

    # Create indexes
    op.execute("CREATE INDEX idx_impact_root ON impact_analysis(root_id);")
    op.execute("CREATE INDEX idx_impact_affected ON impact_analysis(affected_id);")
    op.execute("CREATE INDEX idx_impact_depth ON impact_analysis(depth);")
    op.execute("CREATE INDEX idx_impact_project ON impact_analysis(project_id);")

    # Layer 3: Coverage Analysis View
    op.execute("""
        CREATE MATERIALIZED VIEW coverage_analysis AS
        SELECT
            i.id as item_id,
            i.project_id,
            i.title,
            i.view,
            i.item_type,
            i.status,
            COUNT(DISTINCT CASE WHEN l.link_type = 'tested_by' THEN l.target_item_id END) as test_count,
            COUNT(DISTINCT CASE WHEN l.link_type = 'implemented_by' THEN l.target_item_id END) as code_count,
            CASE
                WHEN COUNT(DISTINCT CASE WHEN l.link_type = 'tested_by' THEN l.target_item_id END) > 0 THEN TRUE
                ELSE FALSE
            END as has_tests,
            CASE
                WHEN COUNT(DISTINCT CASE WHEN l.link_type = 'implemented_by' THEN l.target_item_id END) > 0 THEN TRUE
                ELSE FALSE
            END as has_code,
            CASE
                WHEN COUNT(DISTINCT CASE WHEN l.link_type = 'tested_by' THEN l.target_item_id END) > 0
                 AND COUNT(DISTINCT CASE WHEN l.link_type = 'implemented_by' THEN l.target_item_id END) > 0
                THEN 'Covered'
                WHEN COUNT(DISTINCT CASE WHEN l.link_type = 'tested_by' THEN l.target_item_id END) > 0
                 OR COUNT(DISTINCT CASE WHEN l.link_type = 'implemented_by' THEN l.target_item_id END) > 0
                THEN 'Partial'
                ELSE 'Not Covered'
            END as coverage_status
        FROM items i
        LEFT JOIN links l ON i.id = l.source_item_id
        WHERE i.deleted_at IS NULL
        GROUP BY i.id, i.project_id, i.title, i.view, i.item_type, i.status;
    """)

    # Create unique index for concurrent refresh
    op.execute("""
        CREATE UNIQUE INDEX idx_coverage_unique ON coverage_analysis(item_id);
    """)

    # Create indexes
    op.execute("CREATE INDEX idx_coverage_item ON coverage_analysis(item_id);")
    op.execute("CREATE INDEX idx_coverage_project ON coverage_analysis(project_id);")
    op.execute("CREATE INDEX idx_coverage_status ON coverage_analysis(coverage_status);")
    op.execute("CREATE INDEX idx_coverage_view ON coverage_analysis(view);")


def downgrade() -> None:
    """Drop materialized views."""
    # Drop materialized views
    op.execute("DROP MATERIALIZED VIEW IF EXISTS coverage_analysis;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS impact_analysis;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS traceability_matrix;")
