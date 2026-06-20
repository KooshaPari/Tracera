"""Add processes and process_executions tables if not exist (schema sync).

Databases migrated via a branch that did not include 007_add_problems_and_processes
may not have the processes table. This revision is idempotent: it creates the tables
only when they do not exist.

Revision ID: 050_add_processes_if_not_exists
Revises: 049_add_problems_if_not_exists
Create Date: 2026-01-31

"""

from collections.abc import Sequence

from alembic import op

revision: str = "050_add_processes_if_not_exists"
down_revision: str | None = "049_add_problems_if_not_exists"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade."""
    # Create processes table if not exist (match 007_add_problems_and_processes schema)
    op.execute("""
        CREATE TABLE IF NOT EXISTS processes (
            id VARCHAR(255) PRIMARY KEY,
            process_number VARCHAR(50) UNIQUE NOT NULL,
            project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            name VARCHAR(500) NOT NULL,
            description TEXT,
            purpose TEXT,
            status VARCHAR(50) NOT NULL DEFAULT 'draft',
            category VARCHAR(100),
            tags VARCHAR[],
            version_number INTEGER NOT NULL DEFAULT 1,
            is_active_version BOOLEAN NOT NULL DEFAULT true,
            parent_version_id VARCHAR(255) REFERENCES processes(id) ON DELETE SET NULL,
            version_notes TEXT,
            stages JSONB,
            swimlanes JSONB,
            bpmn_xml TEXT,
            bpmn_diagram_url VARCHAR(500),
            inputs JSONB,
            outputs JSONB,
            triggers JSONB,
            exit_criteria VARCHAR[],
            owner VARCHAR(255),
            responsible_team VARCHAR(255),
            expected_duration_hours INTEGER,
            sla_hours INTEGER,
            activated_at TIMESTAMPTZ,
            activated_by VARCHAR(255),
            deprecated_at TIMESTAMPTZ,
            deprecated_by VARCHAR(255),
            deprecation_reason TEXT,
            related_process_ids VARCHAR[],
            process_metadata JSONB NOT NULL DEFAULT '{}',
            version INTEGER NOT NULL DEFAULT 1,
            deleted_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    for stmt in [
        "CREATE INDEX IF NOT EXISTS idx_processes_process_number ON processes (process_number)",
        "CREATE INDEX IF NOT EXISTS idx_processes_project_id ON processes (project_id)",
        "CREATE INDEX IF NOT EXISTS idx_processes_status ON processes (status)",
        "CREATE INDEX IF NOT EXISTS idx_processes_project_status ON processes (project_id, status)",
        "CREATE INDEX IF NOT EXISTS idx_processes_project_category ON processes (project_id, category)",
        "CREATE INDEX IF NOT EXISTS idx_processes_is_active ON processes (is_active_version)",
        "CREATE INDEX IF NOT EXISTS idx_processes_owner ON processes (owner)",
        "CREATE INDEX IF NOT EXISTS idx_processes_category ON processes (category)",
        "CREATE INDEX IF NOT EXISTS idx_processes_deleted_at ON processes (deleted_at)",
    ]:
        op.execute(stmt)

    # Create process_executions table if not exist
    op.execute("""
        CREATE TABLE IF NOT EXISTS process_executions (
            id VARCHAR(255) PRIMARY KEY,
            process_id VARCHAR(255) NOT NULL REFERENCES processes(id) ON DELETE CASCADE,
            execution_number VARCHAR(50) UNIQUE NOT NULL,
            status VARCHAR(50) NOT NULL DEFAULT 'pending',
            current_stage_id VARCHAR(255),
            completed_stages VARCHAR[],
            started_at TIMESTAMPTZ,
            completed_at TIMESTAMPTZ,
            initiated_by VARCHAR(255),
            completed_by VARCHAR(255),
            trigger_item_id UUID,
            context_data JSONB NOT NULL DEFAULT '{}',
            result_summary TEXT,
            output_item_ids VARCHAR[],
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    for stmt in [
        "CREATE INDEX IF NOT EXISTS idx_process_executions_process_id ON process_executions (process_id)",
        "CREATE INDEX IF NOT EXISTS idx_process_executions_status ON process_executions (status)",
        "CREATE INDEX IF NOT EXISTS idx_process_executions_execution_number ON process_executions (execution_number)",
    ]:
        op.execute(stmt)


def downgrade() -> None:
    """Downgrade."""
