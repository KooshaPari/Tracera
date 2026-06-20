"""merge_heads_2026_01_31.

Revision ID: d0fa574bb4f6
Revises: 006_add_uuid_constraints, 009_add_test_suites_runs, 047_add_workflow_schedules
Create Date: 2026-01-31 02:49:59.781495

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "d0fa574bb4f6"
down_revision: str | tuple[str, ...] | None = ("006_add_uuid_constraints", "047_add_workflow_schedules")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade."""


def downgrade() -> None:
    """Downgrade."""
