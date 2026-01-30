"""Merge heads for test coverage and graph integrity.

Revision ID: 012_merge_heads2
Revises: 010_add_test_coverage, 011_graph_integrity
Create Date: 2026-01-28
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '012_merge_heads2'
down_revision: Union[str, Sequence[str], None] = ('010_add_test_coverage', '011_graph_integrity')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
