"""Add problems and problem_activities tables if not exist (schema sync).

Databases migrated via a branch that did not include 007_add_problems_and_processes
may not have the problems table. This revision is idempotent: it creates the tables
only when they do not exist.

Revision ID: 049_add_problems_if_not_exists
Revises: 048_add_items_version
Create Date: 2026-01-31

"""

from collections.abc import Sequence

from alembic import op

revision: str = "049_add_problems_if_not_exists"
down_revision: str | None = "048_add_items_version"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade."""
    # Create problems table if not exist (match 007_add_problems_and_processes schema)
    op.execute("""
        CREATE TABLE IF NOT EXISTS problems (
            id VARCHAR(255) PRIMARY KEY,
            problem_number VARCHAR(50) UNIQUE NOT NULL,
            project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            title VARCHAR(500) NOT NULL,
            description TEXT,
            status VARCHAR(50) NOT NULL DEFAULT 'open',
            resolution_type VARCHAR(50),
            category VARCHAR(100),
            sub_category VARCHAR(100),
            tags VARCHAR[],
            impact_level VARCHAR(20) NOT NULL DEFAULT 'medium',
            urgency VARCHAR(20) NOT NULL DEFAULT 'medium',
            priority VARCHAR(20) NOT NULL DEFAULT 'medium',
            affected_systems VARCHAR[],
            affected_users_estimated INTEGER,
            business_impact_description TEXT,
            rca_performed BOOLEAN NOT NULL DEFAULT false,
            rca_method VARCHAR(50),
            rca_notes TEXT,
            rca_data JSONB,
            root_cause_identified BOOLEAN NOT NULL DEFAULT false,
            root_cause_description TEXT,
            root_cause_category VARCHAR(50),
            root_cause_confidence VARCHAR(20),
            rca_completed_at TIMESTAMPTZ,
            rca_completed_by VARCHAR(255),
            workaround_available BOOLEAN NOT NULL DEFAULT false,
            workaround_description TEXT,
            workaround_effectiveness VARCHAR(50),
            permanent_fix_available BOOLEAN NOT NULL DEFAULT false,
            permanent_fix_description TEXT,
            permanent_fix_implemented_at TIMESTAMPTZ,
            permanent_fix_change_id VARCHAR(255),
            known_error_id VARCHAR(255),
            knowledge_article_id VARCHAR(255),
            assigned_to VARCHAR(255),
            assigned_team VARCHAR(255),
            owner VARCHAR(255),
            closed_by VARCHAR(255),
            closed_at TIMESTAMPTZ,
            closure_notes TEXT,
            target_resolution_date TIMESTAMPTZ,
            problem_metadata JSONB NOT NULL DEFAULT '{}',
            version INTEGER NOT NULL DEFAULT 1,
            deleted_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    # Indexes for problems (IF NOT EXISTS)
    for _idx, stmt in [
        (
            "idx_problems_problem_number",
            "CREATE INDEX IF NOT EXISTS idx_problems_problem_number ON problems (problem_number)",
        ),
        ("idx_problems_project_id", "CREATE INDEX IF NOT EXISTS idx_problems_project_id ON problems (project_id)"),
        ("idx_problems_status", "CREATE INDEX IF NOT EXISTS idx_problems_status ON problems (status)"),
        (
            "idx_problems_project_status",
            "CREATE INDEX IF NOT EXISTS idx_problems_project_status ON problems (project_id, status)",
        ),
        (
            "idx_problems_project_priority",
            "CREATE INDEX IF NOT EXISTS idx_problems_project_priority ON problems (project_id, priority)",
        ),
        (
            "idx_problems_project_impact",
            "CREATE INDEX IF NOT EXISTS idx_problems_project_impact ON problems (project_id, impact_level)",
        ),
        ("idx_problems_assigned_to", "CREATE INDEX IF NOT EXISTS idx_problems_assigned_to ON problems (assigned_to)"),
        ("idx_problems_category", "CREATE INDEX IF NOT EXISTS idx_problems_category ON problems (category)"),
        (
            "idx_problems_known_error_id",
            "CREATE INDEX IF NOT EXISTS idx_problems_known_error_id ON problems (known_error_id)",
        ),
        ("idx_problems_deleted_at", "CREATE INDEX IF NOT EXISTS idx_problems_deleted_at ON problems (deleted_at)"),
    ]:
        op.execute(stmt)

    # Create problem_activities table if not exist
    op.execute("""
        CREATE TABLE IF NOT EXISTS problem_activities (
            id VARCHAR(255) PRIMARY KEY,
            problem_id VARCHAR(255) NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
            activity_type VARCHAR(50) NOT NULL,
            from_value VARCHAR(255),
            to_value VARCHAR(255),
            description TEXT,
            performed_by VARCHAR(255),
            activity_metadata JSONB NOT NULL DEFAULT '{}',
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_problem_activities_problem_id ON problem_activities (problem_id)")


def downgrade() -> None:
    """Downgrade."""
    # Only drop if this migration created them; leave tables if they existed from 007
    # We cannot safely know, so we do not drop in downgrade (no-op or optional manual drop)
