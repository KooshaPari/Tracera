"""Add version_branches and related tables for temporal dimension.

Implements git-like versioning and branching for traceability items.
Enables time travel, branching, merging, and alternative tracking.

Revision ID: 043_add_version_branches
Revises: 042_add_derived_journeys
Create Date: 2026-01-30
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic
revision = "043_add_version_branches"
down_revision = "042_add_derived_journeys"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create version branches and related tables."""
    # =========================================================================
    # VERSION BRANCHES TABLE
    # =========================================================================
    op.create_table(
        "version_branches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Identity
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        # Branch type classification
        sa.Column(
            "branch_type",
            sa.String(50),
            nullable=False,
            server_default="'feature'",
        ),  # main, release, feature, experiment, hotfix, archive
        # Tree structure
        sa.Column(
            "parent_branch_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("version_branches.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "base_version_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,  # FK added after versions table created
        ),
        # State
        sa.Column(
            "status",
            sa.String(50),
            nullable=False,
            server_default="'active'",
        ),  # active, review, merged, abandoned, archived
        sa.Column("is_default", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("is_protected", sa.Boolean(), server_default="false", nullable=False),
        # Merge tracking
        sa.Column("merged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "merged_into",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("version_branches.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("merged_by", sa.String(255), nullable=True),
        # Statistics (denormalized for performance)
        sa.Column("version_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("item_count", sa.Integer(), server_default="0", nullable=False),
        # Metadata
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        sa.Column("created_by", sa.String(255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        # Constraints
        sa.UniqueConstraint("project_id", "slug", name="uq_version_branches_project_slug"),
    )

    # Indexes for version_branches
    op.create_index("ix_version_branches_project_id", "version_branches", ["project_id"])
    op.create_index("ix_version_branches_branch_type", "version_branches", ["branch_type"])
    op.create_index("ix_version_branches_status", "version_branches", ["status"])
    op.create_index("ix_version_branches_is_default", "version_branches", ["is_default"])
    op.create_index("ix_version_branches_parent_branch_id", "version_branches", ["parent_branch_id"])
    op.create_index(
        "ix_version_branches_project_default",
        "version_branches",
        ["project_id", "is_default"],
    )

    # =========================================================================
    # VERSIONS TABLE
    # =========================================================================
    op.create_table(
        "versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "branch_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("version_branches.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Sequence
        sa.Column("version_number", sa.Integer(), nullable=False),
        # Tree structure
        sa.Column(
            "parent_version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("versions.id", ondelete="SET NULL"),
            nullable=True,
        ),
        # Snapshot reference
        sa.Column("snapshot_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("changeset_id", postgresql.UUID(as_uuid=True), nullable=True),
        # Identity
        sa.Column("tag", sa.String(100), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        # Statistics
        sa.Column("item_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("change_count", sa.Integer(), server_default="0", nullable=False),
        # Quality gates
        sa.Column(
            "status",
            sa.String(50),
            nullable=False,
            server_default="'draft'",
        ),  # draft, pending_review, approved, rejected, superseded
        sa.Column("approved_by", sa.String(255), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        # Metadata
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        sa.Column("created_by", sa.String(255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        # Constraints
        sa.UniqueConstraint("branch_id", "version_number", name="uq_versions_branch_version_number"),
    )

    # Add FK from version_branches.base_version_id to versions.id
    op.create_foreign_key(
        "fk_version_branches_base_version",
        "version_branches",
        "versions",
        ["base_version_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Indexes for versions
    op.create_index("ix_versions_branch_id", "versions", ["branch_id"])
    op.create_index("ix_versions_project_id", "versions", ["project_id"])
    op.create_index("ix_versions_parent_version_id", "versions", ["parent_version_id"])
    op.create_index("ix_versions_status", "versions", ["status"])
    op.create_index("ix_versions_tag", "versions", ["tag"])
    op.create_index("ix_versions_created_at", "versions", ["created_at"])
    op.create_index(
        "ix_versions_branch_number",
        "versions",
        ["branch_id", "version_number"],
    )

    # =========================================================================
    # VERSION CHANGESETS TABLE
    # =========================================================================
    op.create_table(
        "version_changesets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("versions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "parent_version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("versions.id", ondelete="SET NULL"),
            nullable=True,
        ),
        # Changes (arrays of item IDs)
        sa.Column(
            "added_item_ids",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        sa.Column(
            "removed_item_ids",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        sa.Column(
            "modified_item_ids",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        # Statistics
        sa.Column("added_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("removed_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("modified_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_changes", sa.Integer(), server_default="0", nullable=False),
        # Detailed modifications (optional, for diff view)
        sa.Column(
            "modifications",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_index("ix_version_changesets_version_id", "version_changesets", ["version_id"])
    op.create_index(
        "ix_version_changesets_parent_version_id",
        "version_changesets",
        ["parent_version_id"],
    )

    # =========================================================================
    # ITEM VERSIONS TABLE (maps items to versions)
    # =========================================================================
    op.create_table(
        "item_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("items.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("versions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "branch_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("version_branches.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Item state snapshot (full item state at this version)
        sa.Column(
            "state",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        # Lifecycle
        sa.Column("lifecycle", sa.String(50), nullable=True),
        # Version tracking
        sa.Column(
            "introduced_in_version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("versions.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "last_modified_in_version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("versions.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        # Unique constraint: one item state per version
        sa.UniqueConstraint("item_id", "version_id", name="uq_item_versions_item_version"),
    )

    # Indexes for item_versions
    op.create_index("ix_item_versions_item_id", "item_versions", ["item_id"])
    op.create_index("ix_item_versions_version_id", "item_versions", ["version_id"])
    op.create_index("ix_item_versions_branch_id", "item_versions", ["branch_id"])
    op.create_index("ix_item_versions_project_id", "item_versions", ["project_id"])
    op.create_index("ix_item_versions_lifecycle", "item_versions", ["lifecycle"])
    op.create_index(
        "ix_item_versions_introduced_in",
        "item_versions",
        ["introduced_in_version_id"],
    )

    # =========================================================================
    # ITEM ALTERNATIVES TABLE
    # =========================================================================
    op.create_table(
        "item_alternatives",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # The items being compared
        sa.Column(
            "base_item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("items.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "alternative_item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("items.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Relationship type
        sa.Column(
            "relationship",
            sa.String(50),
            nullable=False,
        ),  # alternative_to, supersedes, experiment_of
        sa.Column("description", sa.Text(), nullable=True),
        # Selection tracking
        sa.Column("is_chosen", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("chosen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("chosen_by", sa.String(255), nullable=True),
        sa.Column("chosen_reason", sa.Text(), nullable=True),
        # Comparison metrics
        sa.Column(
            "metrics",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        # Unique constraint
        sa.UniqueConstraint(
            "base_item_id",
            "alternative_item_id",
            name="uq_item_alternatives_base_alternative",
        ),
    )

    # Indexes for item_alternatives
    op.create_index("ix_item_alternatives_project_id", "item_alternatives", ["project_id"])
    op.create_index("ix_item_alternatives_base_item_id", "item_alternatives", ["base_item_id"])
    op.create_index(
        "ix_item_alternatives_alternative_item_id",
        "item_alternatives",
        ["alternative_item_id"],
    )
    op.create_index("ix_item_alternatives_relationship", "item_alternatives", ["relationship"])
    op.create_index("ix_item_alternatives_is_chosen", "item_alternatives", ["is_chosen"])

    # =========================================================================
    # MERGE REQUESTS TABLE
    # =========================================================================
    op.create_table(
        "merge_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Branches
        sa.Column(
            "source_branch_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("version_branches.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "target_branch_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("version_branches.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Versions
        sa.Column(
            "source_version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("versions.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "base_version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("versions.id", ondelete="SET NULL"),
            nullable=True,
        ),
        # Status
        sa.Column(
            "status",
            sa.String(50),
            nullable=False,
            server_default="'open'",
        ),  # open, approved, merged, closed, conflict
        # Details
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "diff",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        # Conflicts
        sa.Column(
            "conflicts",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        # Review
        sa.Column(
            "reviewers",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        sa.Column(
            "approved_by",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        # Timestamps
        sa.Column("created_by", sa.String(255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("merged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("merged_by", sa.String(255), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # Indexes for merge_requests
    op.create_index("ix_merge_requests_project_id", "merge_requests", ["project_id"])
    op.create_index("ix_merge_requests_source_branch_id", "merge_requests", ["source_branch_id"])
    op.create_index("ix_merge_requests_target_branch_id", "merge_requests", ["target_branch_id"])
    op.create_index("ix_merge_requests_status", "merge_requests", ["status"])
    op.create_index("ix_merge_requests_created_at", "merge_requests", ["created_at"])


def downgrade() -> None:
    """Drop version branches and related tables."""
    # Drop merge_requests
    op.drop_index("ix_merge_requests_created_at", table_name="merge_requests")
    op.drop_index("ix_merge_requests_status", table_name="merge_requests")
    op.drop_index("ix_merge_requests_target_branch_id", table_name="merge_requests")
    op.drop_index("ix_merge_requests_source_branch_id", table_name="merge_requests")
    op.drop_index("ix_merge_requests_project_id", table_name="merge_requests")
    op.drop_table("merge_requests")

    # Drop item_alternatives
    op.drop_index("ix_item_alternatives_is_chosen", table_name="item_alternatives")
    op.drop_index("ix_item_alternatives_relationship", table_name="item_alternatives")
    op.drop_index("ix_item_alternatives_alternative_item_id", table_name="item_alternatives")
    op.drop_index("ix_item_alternatives_base_item_id", table_name="item_alternatives")
    op.drop_index("ix_item_alternatives_project_id", table_name="item_alternatives")
    op.drop_table("item_alternatives")

    # Drop item_versions
    op.drop_index("ix_item_versions_introduced_in", table_name="item_versions")
    op.drop_index("ix_item_versions_lifecycle", table_name="item_versions")
    op.drop_index("ix_item_versions_project_id", table_name="item_versions")
    op.drop_index("ix_item_versions_branch_id", table_name="item_versions")
    op.drop_index("ix_item_versions_version_id", table_name="item_versions")
    op.drop_index("ix_item_versions_item_id", table_name="item_versions")
    op.drop_table("item_versions")

    # Drop version_changesets
    op.drop_index("ix_version_changesets_parent_version_id", table_name="version_changesets")
    op.drop_index("ix_version_changesets_version_id", table_name="version_changesets")
    op.drop_table("version_changesets")

    # Drop FK before dropping versions
    op.drop_constraint("fk_version_branches_base_version", "version_branches", type_="foreignkey")

    # Drop versions
    op.drop_index("ix_versions_branch_number", table_name="versions")
    op.drop_index("ix_versions_created_at", table_name="versions")
    op.drop_index("ix_versions_tag", table_name="versions")
    op.drop_index("ix_versions_status", table_name="versions")
    op.drop_index("ix_versions_parent_version_id", table_name="versions")
    op.drop_index("ix_versions_project_id", table_name="versions")
    op.drop_index("ix_versions_branch_id", table_name="versions")
    op.drop_table("versions")

    # Drop version_branches
    op.drop_index("ix_version_branches_project_default", table_name="version_branches")
    op.drop_index("ix_version_branches_parent_branch_id", table_name="version_branches")
    op.drop_index("ix_version_branches_is_default", table_name="version_branches")
    op.drop_index("ix_version_branches_status", table_name="version_branches")
    op.drop_index("ix_version_branches_branch_type", table_name="version_branches")
    op.drop_index("ix_version_branches_project_id", table_name="version_branches")
    op.drop_table("version_branches")
