"""Merge heads for test cases and graph projections.

Revision ID: 010_merge_heads
Revises: 008_add_test_cases, 009_add_graphs_and_graph_nodes
Create Date: 2026-01-28
"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "010_merge_heads"
down_revision: str | Sequence[str] | None = ("009_add_test_suites_runs", "009_add_graphs_and_graph_nodes")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade."""


def downgrade() -> None:
    """Downgrade."""
