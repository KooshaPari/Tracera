"""Fix schema validation issues.

Revision ID: 059_fix_schema_validation
Revises: 058_add_api_keys_table
Create Date: 2026-02-01 21:20:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "059_fix_schema_validation"
down_revision = "057_create_materialized_views"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Fix schema validation issues identified in tests."""
    # 1. Add missing updated_at column to links table
    op.execute("""
        ALTER TABLE links
        ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW();
    """)

    # 2. Set NOT NULL constraints on project_id columns
    # First, ensure no NULL values exist
    op.execute("""
        UPDATE items SET project_id = (SELECT id FROM projects LIMIT 1)
        WHERE project_id IS NULL;
    """)

    op.execute("""
        UPDATE agents SET project_id = (SELECT id FROM projects LIMIT 1)
        WHERE project_id IS NULL;
    """)

    # Then add NOT NULL constraints
    op.execute("""
        ALTER TABLE items
        ALTER COLUMN project_id SET NOT NULL;
    """)

    op.execute("""
        ALTER TABLE agents
        ALTER COLUMN project_id SET NOT NULL;
    """)

    # 3. Add missing deleted_at column and index on projects
    op.execute("""
        ALTER TABLE projects
        ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE;
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_projects_deleted_at
        ON projects(deleted_at);
    """)

    # 4. Create views table if it doesn't exist, or add missing columns
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'views') THEN
                CREATE TABLE views (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                    name VARCHAR(255) NOT NULL,
                    type VARCHAR(100) NOT NULL,
                    config VARCHAR(255),
                    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
                );
            ELSE
                -- Add missing columns to existing views table
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'views' AND column_name = 'type') THEN
                    ALTER TABLE views ADD COLUMN type VARCHAR(100) NOT NULL DEFAULT 'graph';
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'views' AND column_name = 'config') THEN
                    ALTER TABLE views ADD COLUMN config VARCHAR(255);
                END IF;
            END IF;
        END $$;
    """)

    # Add indexes for views table
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_views_project_id ON views(project_id);
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_views_type ON views(type);
    """)

    # Add RLS policy for views table
    op.execute("""
        ALTER TABLE views ENABLE ROW LEVEL SECURITY;
    """)

    op.execute("""
        DROP POLICY IF EXISTS views_isolation_policy ON views;
        CREATE POLICY views_isolation_policy ON views
        USING (
            project_id IN (
                SELECT id FROM projects
                WHERE account_id IN (
                    SELECT account_id FROM account_users
                    WHERE user_id = current_setting('app.current_user_id', true)
                )
            )
        );
    """)


def downgrade() -> None:
    """Revert schema validation fixes."""
    # Remove views table
    op.execute("DROP TABLE IF EXISTS views CASCADE;")

    # Remove index on projects.deleted_at
    op.execute("DROP INDEX IF EXISTS idx_projects_deleted_at;")

    # Remove NOT NULL constraints
    op.execute("ALTER TABLE items ALTER COLUMN project_id DROP NOT NULL;")
    op.execute("ALTER TABLE agents ALTER COLUMN project_id DROP NOT NULL;")

    # Remove updated_at from links
    op.execute("ALTER TABLE links DROP COLUMN IF EXISTS updated_at;")
