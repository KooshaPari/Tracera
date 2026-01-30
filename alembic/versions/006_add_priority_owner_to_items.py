"""Add priority and owner fields to items table

Revision ID: 006_add_priority_owner
Revises: 005_update_refresh_all_views
Create Date: 2025-01-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '006_add_priority_owner'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add priority column with default 'medium'
    op.add_column('items', sa.Column('priority', sa.String(50), nullable=False, server_default='medium'))
    
    # Add owner column (nullable)
    op.add_column('items', sa.Column('owner', sa.String(255), nullable=True))
    
    # Create index on priority for filtering
    op.create_index('idx_items_priority', 'items', ['priority'])
    
    # Create index on owner for filtering
    op.create_index('idx_items_owner', 'items', ['owner'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_items_owner', table_name='items')
    op.drop_index('idx_items_priority', table_name='items')
    
    # Drop columns
    op.drop_column('items', 'owner')
    op.drop_column('items', 'priority')
