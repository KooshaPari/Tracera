"""Add milestones, sprints, and progress tracking tables.

Implements project progress dimension with milestones, sprints,
burndown/velocity tracking, and progress snapshots.

Revision ID: 044_add_milestones
Revises: 043_add_version_branches
Create Date: 2026-01-30
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic
revision = "044_add_milestones"
down_revision = "043_add_version_branches"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create milestones, sprints, and progress tracking tables."""
    # =========================================================================
    # MILESTONES TABLE
    # =========================================================================
    op.create_table(
        "milestones",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Hierarchy
        sa.Column(
            "parent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("milestones.id", ondelete="SET NULL"),
            nullable=True,
        ),
        # Identity
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("objective", sa.Text(), nullable=True),
        # Timing
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("target_date", sa.Date(), nullable=False),
        sa.Column("actual_date", sa.Date(), nullable=True),
        # Status
        sa.Column(
            "status",
            sa.String(50),
            nullable=False,
            server_default="'not_started'",
        ),  # not_started, in_progress, at_risk, blocked, completed, cancelled
        sa.Column(
            "health",
            sa.String(20),
            nullable=False,
            server_default="'unknown'",
        ),  # green, yellow, red, unknown
        # Progress metrics (denormalized)
        sa.Column("total_items", sa.Integer(), server_default="0", nullable=False),
        sa.Column("completed_items", sa.Integer(), server_default="0", nullable=False),
        sa.Column("in_progress_items", sa.Integer(), server_default="0", nullable=False),
        sa.Column("blocked_items", sa.Integer(), server_default="0", nullable=False),
        sa.Column("progress_percentage", sa.Float(), server_default="0", nullable=False),
        # Risk assessment
        sa.Column("risk_score", sa.Float(), server_default="0", nullable=False),
        sa.Column(
            "risk_factors",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        # Dependencies
        sa.Column(
            "depends_on_milestones",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        sa.Column(
            "blocked_by_milestones",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        # Team
        sa.Column("owner", sa.String(255), nullable=True),
        sa.Column(
            "assignees",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        # Metadata
        sa.Column(
            "tags",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
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
        sa.UniqueConstraint("project_id", "slug", name="uq_milestones_project_slug"),
    )

    # Indexes for milestones
    op.create_index("ix_milestones_project_id", "milestones", ["project_id"])
    op.create_index("ix_milestones_parent_id", "milestones", ["parent_id"])
    op.create_index("ix_milestones_status", "milestones", ["status"])
    op.create_index("ix_milestones_health", "milestones", ["health"])
    op.create_index("ix_milestones_target_date", "milestones", ["target_date"])
    op.create_index("ix_milestones_owner", "milestones", ["owner"])
    op.create_index(
        "ix_milestones_project_status",
        "milestones",
        ["project_id", "status"],
    )
    op.create_index(
        "ix_milestones_project_target",
        "milestones",
        ["project_id", "target_date"],
    )

    # =========================================================================
    # MILESTONE ITEMS TABLE (junction table)
    # =========================================================================
    op.create_table(
        "milestone_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "milestone_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("milestones.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("items.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "added_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("added_by", sa.String(255), nullable=True),
        # Constraints
        sa.UniqueConstraint("milestone_id", "item_id", name="uq_milestone_items_milestone_item"),
    )

    op.create_index("ix_milestone_items_milestone_id", "milestone_items", ["milestone_id"])
    op.create_index("ix_milestone_items_item_id", "milestone_items", ["item_id"])

    # =========================================================================
    # SPRINTS TABLE
    # =========================================================================
    op.create_table(
        "sprints",
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
        sa.Column("goal", sa.Text(), nullable=True),
        # Time box
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("duration_days", sa.Integer(), nullable=False),
        # Status
        sa.Column(
            "status",
            sa.String(50),
            nullable=False,
            server_default="'planning'",
        ),  # planning, active, completed, cancelled
        sa.Column(
            "health",
            sa.String(20),
            nullable=False,
            server_default="'unknown'",
        ),
        # Capacity
        sa.Column("planned_capacity", sa.Float(), nullable=True),
        sa.Column("actual_capacity", sa.Float(), nullable=True),
        # Progress (points/story points)
        sa.Column("planned_points", sa.Float(), server_default="0", nullable=False),
        sa.Column("completed_points", sa.Float(), server_default="0", nullable=False),
        sa.Column("remaining_points", sa.Float(), server_default="0", nullable=False),
        sa.Column("added_points", sa.Float(), server_default="0", nullable=False),
        sa.Column("removed_points", sa.Float(), server_default="0", nullable=False),
        # Velocity
        sa.Column("velocity", sa.Float(), nullable=True),
        sa.Column("estimated_completion", sa.Date(), nullable=True),
        # Item counts
        sa.Column("item_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("completed_item_count", sa.Integer(), server_default="0", nullable=False),
        # Burndown data (daily snapshots)
        sa.Column(
            "burndown_data",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        # Carryover
        sa.Column(
            "carryover_item_ids",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        # Team
        sa.Column(
            "team_members",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        # Metadata
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
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
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        # Constraints
        sa.UniqueConstraint("project_id", "slug", name="uq_sprints_project_slug"),
    )

    # Indexes for sprints
    op.create_index("ix_sprints_project_id", "sprints", ["project_id"])
    op.create_index("ix_sprints_status", "sprints", ["status"])
    op.create_index("ix_sprints_start_date", "sprints", ["start_date"])
    op.create_index("ix_sprints_end_date", "sprints", ["end_date"])
    op.create_index(
        "ix_sprints_project_status",
        "sprints",
        ["project_id", "status"],
    )
    op.create_index(
        "ix_sprints_project_dates",
        "sprints",
        ["project_id", "start_date", "end_date"],
    )

    # =========================================================================
    # SPRINT ITEMS TABLE (junction table)
    # =========================================================================
    op.create_table(
        "sprint_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "sprint_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sprints.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("items.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Point estimate
        sa.Column("points", sa.Float(), nullable=True),
        # Status tracking
        sa.Column("is_completed", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_carryover", sa.Boolean(), server_default="false", nullable=False),
        # When added to sprint
        sa.Column(
            "added_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("added_by", sa.String(255), nullable=True),
        # Constraints
        sa.UniqueConstraint("sprint_id", "item_id", name="uq_sprint_items_sprint_item"),
    )

    op.create_index("ix_sprint_items_sprint_id", "sprint_items", ["sprint_id"])
    op.create_index("ix_sprint_items_item_id", "sprint_items", ["item_id"])
    op.create_index("ix_sprint_items_is_completed", "sprint_items", ["is_completed"])

    # =========================================================================
    # PROGRESS SNAPSHOTS TABLE
    # =========================================================================
    op.create_table(
        "progress_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Snapshot date
        sa.Column("snapshot_date", sa.Date(), nullable=False),
        # Aggregate metrics (full project state)
        sa.Column(
            "metrics",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        # Milestone snapshots
        sa.Column(
            "milestone_snapshots",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        # Sprint snapshot (if active sprint)
        sa.Column(
            "sprint_snapshot",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        # One snapshot per project per day
        sa.UniqueConstraint("project_id", "snapshot_date", name="uq_progress_snapshots_project_date"),
    )

    op.create_index("ix_progress_snapshots_project_id", "progress_snapshots", ["project_id"])
    op.create_index("ix_progress_snapshots_snapshot_date", "progress_snapshots", ["snapshot_date"])
    op.create_index(
        "ix_progress_snapshots_project_date",
        "progress_snapshots",
        ["project_id", "snapshot_date"],
    )

    # =========================================================================
    # VELOCITY HISTORY TABLE
    # =========================================================================
    op.create_table(
        "velocity_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Period
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("period_label", sa.String(100), nullable=False),  # "Sprint 23", "Week 12"
        # Points
        sa.Column("planned_points", sa.Float(), server_default="0", nullable=False),
        sa.Column("completed_points", sa.Float(), server_default="0", nullable=False),
        sa.Column("velocity", sa.Float(), nullable=False),
        # Context
        sa.Column(
            "sprint_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sprints.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_index("ix_velocity_history_project_id", "velocity_history", ["project_id"])
    op.create_index("ix_velocity_history_period_start", "velocity_history", ["period_start"])
    op.create_index(
        "ix_velocity_history_project_period",
        "velocity_history",
        ["project_id", "period_start"],
    )

    # =========================================================================
    # DASHBOARD LAYOUTS TABLE
    # =========================================================================
    op.create_table(
        "dashboard_layouts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Identity
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("is_default", sa.Boolean(), server_default="false", nullable=False),
        # Layout config
        sa.Column(
            "widgets",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        sa.Column("columns", sa.Integer(), server_default="12", nullable=False),
        sa.Column("row_height", sa.Integer(), server_default="100", nullable=False),
        # Metadata
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
    )

    op.create_index("ix_dashboard_layouts_project_id", "dashboard_layouts", ["project_id"])
    op.create_index("ix_dashboard_layouts_is_default", "dashboard_layouts", ["is_default"])


def downgrade() -> None:
    """Drop milestones and related tables."""
    # Drop dashboard_layouts
    op.drop_index("ix_dashboard_layouts_is_default", table_name="dashboard_layouts")
    op.drop_index("ix_dashboard_layouts_project_id", table_name="dashboard_layouts")
    op.drop_table("dashboard_layouts")

    # Drop velocity_history
    op.drop_index("ix_velocity_history_project_period", table_name="velocity_history")
    op.drop_index("ix_velocity_history_period_start", table_name="velocity_history")
    op.drop_index("ix_velocity_history_project_id", table_name="velocity_history")
    op.drop_table("velocity_history")

    # Drop progress_snapshots
    op.drop_index("ix_progress_snapshots_project_date", table_name="progress_snapshots")
    op.drop_index("ix_progress_snapshots_snapshot_date", table_name="progress_snapshots")
    op.drop_index("ix_progress_snapshots_project_id", table_name="progress_snapshots")
    op.drop_table("progress_snapshots")

    # Drop sprint_items
    op.drop_index("ix_sprint_items_is_completed", table_name="sprint_items")
    op.drop_index("ix_sprint_items_item_id", table_name="sprint_items")
    op.drop_index("ix_sprint_items_sprint_id", table_name="sprint_items")
    op.drop_table("sprint_items")

    # Drop sprints
    op.drop_index("ix_sprints_project_dates", table_name="sprints")
    op.drop_index("ix_sprints_project_status", table_name="sprints")
    op.drop_index("ix_sprints_end_date", table_name="sprints")
    op.drop_index("ix_sprints_start_date", table_name="sprints")
    op.drop_index("ix_sprints_status", table_name="sprints")
    op.drop_index("ix_sprints_project_id", table_name="sprints")
    op.drop_table("sprints")

    # Drop milestone_items
    op.drop_index("ix_milestone_items_item_id", table_name="milestone_items")
    op.drop_index("ix_milestone_items_milestone_id", table_name="milestone_items")
    op.drop_table("milestone_items")

    # Drop milestones
    op.drop_index("ix_milestones_project_target", table_name="milestones")
    op.drop_index("ix_milestones_project_status", table_name="milestones")
    op.drop_index("ix_milestones_owner", table_name="milestones")
    op.drop_index("ix_milestones_target_date", table_name="milestones")
    op.drop_index("ix_milestones_health", table_name="milestones")
    op.drop_index("ix_milestones_status", table_name="milestones")
    op.drop_index("ix_milestones_parent_id", table_name="milestones")
    op.drop_index("ix_milestones_project_id", table_name="milestones")
    op.drop_table("milestones")
