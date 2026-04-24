"""Add test_suites and test_runs tables if not exist (schema sync).

Databases migrated via a branch that did not include 009_add_test_suites_runs
may not have test_runs. This revision is idempotent: it creates the tables
only when they do not exist.

Revision ID: 053_add_test_suites_runs_if_not_exists
Revises: 052_add_agent_sessions
Create Date: 2026-01-31

"""

from collections.abc import Sequence

from alembic import op

revision: str = "053_add_test_suites_runs_if_not_exists"
down_revision: str | None = "052_add_agent_sessions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade."""
    conn = op.get_bind()
    if conn.dialect.name != "postgresql":
        return

    # Create enum types if not exist
    for enum_name, values in [
        ("test_suite_status", ("draft", "active", "deprecated", "archived")),
        ("test_run_status", ("pending", "running", "passed", "failed", "blocked", "cancelled")),
        ("test_run_type", ("manual", "automated", "ci_cd", "scheduled")),
    ]:
        vals = ", ".join(f"'{v}'" for v in values)
        op.execute(
            f"""
            DO $$ BEGIN
                CREATE TYPE {enum_name} AS ENUM ({vals});
            EXCEPTION
                WHEN duplicate_object THEN NULL;
            END $$;
            """,
        )

    # Create test_suites if not exist
    op.execute("""
        CREATE TABLE IF NOT EXISTS test_suites (
            id VARCHAR(36) PRIMARY KEY,
            suite_number VARCHAR(50) NOT NULL UNIQUE,
            project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            name VARCHAR(500) NOT NULL,
            description TEXT,
            objective TEXT,
            status test_suite_status NOT NULL DEFAULT 'draft',
            parent_id VARCHAR(36) REFERENCES test_suites(id) ON DELETE SET NULL,
            order_index INTEGER NOT NULL DEFAULT 0,
            category VARCHAR(100),
            tags JSONB,
            is_parallel_execution BOOLEAN NOT NULL DEFAULT false,
            estimated_duration_minutes INTEGER,
            required_environment VARCHAR(255),
            environment_variables JSONB,
            setup_instructions TEXT,
            teardown_instructions TEXT,
            owner VARCHAR(255),
            responsible_team VARCHAR(255),
            total_test_cases INTEGER NOT NULL DEFAULT 0,
            automated_count INTEGER NOT NULL DEFAULT 0,
            last_run_at TIMESTAMPTZ,
            last_run_result VARCHAR(50),
            pass_rate FLOAT,
            metadata JSONB,
            version INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_test_suites_project_id ON test_suites (project_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_test_suites_status ON test_suites (status)")

    # Create test_runs if not exist (run_metadata to match current model)
    op.execute("""
        CREATE TABLE IF NOT EXISTS test_runs (
            id VARCHAR(36) PRIMARY KEY,
            run_number VARCHAR(50) NOT NULL UNIQUE,
            project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            suite_id VARCHAR(36) REFERENCES test_suites(id) ON DELETE SET NULL,
            name VARCHAR(500) NOT NULL,
            description TEXT,
            status test_run_status NOT NULL DEFAULT 'pending',
            run_type test_run_type NOT NULL DEFAULT 'manual',
            environment VARCHAR(255),
            build_number VARCHAR(255),
            build_url VARCHAR(1000),
            branch VARCHAR(255),
            commit_sha VARCHAR(64),
            scheduled_at TIMESTAMPTZ,
            started_at TIMESTAMPTZ,
            completed_at TIMESTAMPTZ,
            duration_seconds INTEGER,
            initiated_by VARCHAR(255),
            executed_by VARCHAR(255),
            total_tests INTEGER NOT NULL DEFAULT 0,
            passed_count INTEGER NOT NULL DEFAULT 0,
            failed_count INTEGER NOT NULL DEFAULT 0,
            skipped_count INTEGER NOT NULL DEFAULT 0,
            blocked_count INTEGER NOT NULL DEFAULT 0,
            error_count INTEGER NOT NULL DEFAULT 0,
            pass_rate FLOAT,
            notes TEXT,
            failure_summary TEXT,
            tags JSONB,
            external_run_id VARCHAR(255),
            webhook_id VARCHAR(36),
            run_metadata JSONB,
            version INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_test_runs_project_id ON test_runs (project_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_test_runs_suite_id ON test_runs (suite_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_test_runs_status ON test_runs (status)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_test_runs_run_type ON test_runs (run_type)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_test_runs_started_at ON test_runs (started_at)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_test_runs_completed_at ON test_runs (completed_at)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_test_runs_environment ON test_runs (environment)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_test_runs_initiated_by ON test_runs (initiated_by)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_test_runs_external_run_id ON test_runs (external_run_id)")


def downgrade() -> None:
    """Downgrade."""
