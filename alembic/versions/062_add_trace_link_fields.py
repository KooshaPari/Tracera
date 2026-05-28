"""Add confidence and rationale columns to the links table.

These two fields are the SOTA-research P0 first-class fields on a trace
link: ``confidence`` (miner posterior in [0, 1], defaulting to 1.0 for
human-curated links) and ``rationale`` (short natural-language
justification). They live as proper columns rather than inside
``link_metadata`` so they can be indexed and filtered cheaply by the
RAG / explainability layer.

Revision ID: 062_add_trace_link_fields
Revises: 061_add_agent_tasks
Create Date: 2026-05-28
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "062_add_trace_link_fields"
down_revision = "061_add_agent_tasks"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add confidence + rationale columns to links and a confidence index."""
    op.execute("""
        ALTER TABLE links
        ADD COLUMN IF NOT EXISTS confidence DOUBLE PRECISION
            NOT NULL DEFAULT 1.0
    """)
    op.execute("""
        ALTER TABLE links
        ADD CONSTRAINT links_confidence_range
        CHECK (confidence >= 0.0 AND confidence <= 1.0)
    """)
    op.execute("""
        ALTER TABLE links
        ADD COLUMN IF NOT EXISTS rationale TEXT
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_links_confidence
        ON links(confidence)
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_links_project_type_confidence
        ON links(project_id, link_type, confidence DESC)
    """)


def downgrade() -> None:
    """Drop the confidence / rationale columns and their indexes."""
    op.execute("DROP INDEX IF EXISTS idx_links_project_type_confidence")
    op.execute("DROP INDEX IF EXISTS idx_links_confidence")
    op.execute("ALTER TABLE links DROP COLUMN IF EXISTS rationale")
    op.execute("ALTER TABLE links DROP CONSTRAINT IF EXISTS links_confidence_range")
    op.execute("ALTER TABLE links DROP COLUMN IF EXISTS confidence")
