"""Add UUID format constraints.

Revision ID: 006_add_uuid_constraints
Revises: 005
Create Date: 2026-01-30 16:30:00.000000

"""

import contextlib

import sqlalchemy as sa

from alembic import context, op

# revision identifiers, used by Alembic.
revision = "006_add_uuid_constraints"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add CHECK constraints for UUID format validation on all primary key columns."""
    # List of tables with UUID primary keys
    tables = [
        "items",
        "links",
        "projects",
        "agents",
        "specifications",
        "contracts",
        "test_runs",
        "test_cases",
        "requirements",
        "features",
        "scenarios",
        "users",
        "teams",
        "organizations",
    ]

    # Add UUID format constraint to each table
    for table in tables:
        connection = op.get_bind()
        constraint_name = f"{table}_id_uuid_check"
        if connection is None or context.is_offline_mode():
            op.execute(
                f"""
                ALTER TABLE {table}
                ADD CONSTRAINT {constraint_name}
                CHECK (id::TEXT ~ '^[0-9a-f]{{8}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{12}}$')
                """,
            )
            continue

        inspector = sa.inspect(connection)
        if table in inspector.get_table_names():
            with contextlib.suppress(Exception):
                op.execute(
                    f"""
                    ALTER TABLE {table}
                    ADD CONSTRAINT {constraint_name}
                    CHECK (id::TEXT ~ '^[0-9a-f]{{8}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{12}}$')
                    """,
                )


def downgrade() -> None:
    """Remove UUID format constraints."""
    tables = [
        "items",
        "links",
        "projects",
        "agents",
        "specifications",
        "contracts",
        "test_runs",
        "test_cases",
        "requirements",
        "features",
        "scenarios",
        "users",
        "teams",
        "organizations",
    ]

    for table in tables:
        constraint_name = f"{table}_id_uuid_check"
        with contextlib.suppress(Exception):
            op.execute(f"ALTER TABLE {table} DROP CONSTRAINT IF EXISTS {constraint_name}")
