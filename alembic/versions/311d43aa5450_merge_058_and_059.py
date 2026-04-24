"""Merge 058 and 059.

Revision ID: 311d43aa5450
Revises: 058_add_api_keys, 059_fix_schema_validation
Create Date: 2026-02-07 12:58:36.384415

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "311d43aa5450"
down_revision: str | None = ("058_add_api_keys", "059_fix_schema_validation")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade."""


def downgrade() -> None:
    """Downgrade."""
