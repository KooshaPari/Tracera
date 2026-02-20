"""Merge heads for test coverage and graph integrity.

Revision ID: 012_merge_heads2
Revises: 010_add_test_coverage, 011_graph_integrity
Create Date: 2026-01-28
"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "012_merge_heads2"
down_revision: str | Sequence[str] | None = ("010_add_test_coverage", "011_graph_integrity")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade."""


def downgrade() -> None:
    """Downgrade."""
