"""Merge heads for test cases and graph projections.

Revision ID: 010_merge_heads
Revises: 008_add_test_cases, 009_add_graphs_and_graph_nodes
Create Date: 2026-01-28
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '010_merge_heads'
down_revision: Union[str, Sequence[str], None] = ('008_add_test_cases', '009_add_graphs_and_graph_nodes')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
