"""Add specification system tables.

Creates tables for ADRs, Contracts, BDD Features, Scenarios, and Requirement Quality.

Revision ID: 020_specifications
Revises: 019_add_execution_system
Create Date: 2026-01-30 00:00:00.000000
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.sqlite import JSON

from alembic import op

# revision identifiers, used by Alembic.
revision = "020_specifications"
down_revision = "019_add_execution_system"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade."""
    # ADRs
    op.create_table(
        "adrs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("adr_number", sa.String(50), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("context", sa.Text(), nullable=False),
        sa.Column("decision", sa.Text(), nullable=False),
        sa.Column("consequences", sa.Text(), nullable=False),
        sa.Column("decision_drivers", JSON(), nullable=True),
        sa.Column("considered_options", JSON(), nullable=True),
        sa.Column("related_requirements", JSON(), nullable=True),
        sa.Column("related_adrs", JSON(), nullable=True),
        sa.Column("supersedes", sa.String(50), nullable=True),
        sa.Column("superseded_by", sa.String(50), nullable=True),
        sa.Column("compliance_score", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("last_verified_at", sa.String(50), nullable=True),
        sa.Column("stakeholders", JSON(), nullable=True),
        sa.Column("tags", JSON(), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("metadata", JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("idx_adrs_project", "adrs", ["project_id"])
    op.create_index("idx_adrs_status", "adrs", ["status"])
    op.create_index("idx_adrs_date", "adrs", ["date"])

    # Contracts
    op.create_table(
        "contracts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("items.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("contract_number", sa.String(50), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("contract_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="draft"),
        sa.Column("preconditions", JSON(), nullable=True),
        sa.Column("postconditions", JSON(), nullable=True),
        sa.Column("invariants", JSON(), nullable=True),
        sa.Column("states", JSON(), nullable=True),
        sa.Column("transitions", JSON(), nullable=True),
        sa.Column("executable_spec", sa.Text(), nullable=True),
        sa.Column("spec_language", sa.String(50), nullable=True),
        sa.Column("last_verified_at", sa.String(50), nullable=True),
        sa.Column("verification_result", JSON(), nullable=True),
        sa.Column("tags", JSON(), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("metadata", JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("idx_contracts_project", "contracts", ["project_id"])
    op.create_index("idx_contracts_item", "contracts", ["item_id"])

    # Features
    op.create_table(
        "features",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("feature_number", sa.String(50), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("as_a", sa.String(255), nullable=True),
        sa.Column("i_want", sa.String(255), nullable=True),
        sa.Column("so_that", sa.String(500), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="draft"),
        sa.Column("file_path", sa.String(500), nullable=True),
        sa.Column("tags", JSON(), nullable=True),
        sa.Column("related_requirements", JSON(), nullable=True),
        sa.Column("related_adrs", JSON(), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("metadata", JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("idx_features_project", "features", ["project_id"])

    # Scenarios
    op.create_table(
        "scenarios",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("feature_id", sa.String(36), sa.ForeignKey("features.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scenario_number", sa.String(50), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("gherkin_text", sa.Text(), nullable=False),
        sa.Column("background", JSON(), nullable=True),
        sa.Column("given_steps", JSON(), nullable=True),
        sa.Column("when_steps", JSON(), nullable=True),
        sa.Column("then_steps", JSON(), nullable=True),
        sa.Column("is_outline", sa.Boolean(), server_default="0", nullable=False),
        sa.Column("examples", JSON(), nullable=True),
        sa.Column("tags", JSON(), nullable=True),
        sa.Column("requirement_ids", JSON(), nullable=True),
        sa.Column("test_case_ids", JSON(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="draft"),
        sa.Column("pass_rate", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("metadata", JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("idx_scenarios_feature", "scenarios", ["feature_id"])
    op.create_index("idx_scenarios_status", "scenarios", ["status"])

    # Requirement Quality
    op.create_table(
        "requirement_quality",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("items.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("smells", JSON(), nullable=True),
        sa.Column("ambiguity_score", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("completeness_score", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("suggestions", JSON(), nullable=True),
        sa.Column("last_analyzed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("idx_requirement_quality_item", "requirement_quality", ["item_id"])


def downgrade() -> None:
    """Downgrade."""
    op.drop_index("idx_requirement_quality_item", table_name="requirement_quality")
    op.drop_table("requirement_quality")

    op.drop_index("idx_scenarios_status", table_name="scenarios")
    op.drop_index("idx_scenarios_feature", table_name="scenarios")
    op.drop_table("scenarios")

    op.drop_index("idx_features_project", table_name="features")
    op.drop_table("features")

    op.drop_index("idx_contracts_item", table_name="contracts")
    op.drop_index("idx_contracts_project", table_name="contracts")
    op.drop_table("contracts")

    op.drop_index("idx_adrs_date", table_name="adrs")
    op.drop_index("idx_adrs_status", table_name="adrs")
    op.drop_index("idx_adrs_project", table_name="adrs")
    op.drop_table("adrs")
