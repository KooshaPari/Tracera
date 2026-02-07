"""Merge 058 and 059

Revision ID: 311d43aa5450
Revises: 058_add_api_keys, 059_fix_schema_validation
Create Date: 2026-02-07 12:58:36.384415

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '311d43aa5450'
down_revision: Union[str, None] = ('058_add_api_keys', '059_fix_schema_validation')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

