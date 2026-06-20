"""Add item specification tables for enhanced smart-contract-like items.

This migration creates 6 specification tables for different item types:
- requirement_specs: Rich requirement specifications with EARS, constraints, quality metrics
- test_specs: Test specifications with execution history, flakiness, coverage
- epic_specs: Epic specifications with portfolio alignment, capacity tracking
- user_story_specs: User story specifications with acceptance criteria, velocity
- task_specs: Task specifications with time tracking, dependencies
- defect_specs: Defect specifications with RCA, reproduction, verification

Revision ID: 028_add_item_specifications
Revises: 027_add_step_definitions
Create Date: 2026-01-29 15:00:00.000000
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

# revision identifiers, used by Alembic.
revision = "028_add_item_specifications"
down_revision = "027_add_step_definitions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add item specification tables."""
    # === requirement_specs ===
    op.create_table(
        "requirement_specs",
        sa.Column("id", sa.String(255), primary_key=True),
        sa.Column(
            "item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("items.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        # EARS Classification
        sa.Column("requirement_type", sa.String(50), nullable=False, server_default="ubiquitous"),
        sa.Column("ears_trigger", sa.Text, nullable=True),
        sa.Column("ears_precondition", sa.Text, nullable=True),
        sa.Column("ears_postcondition", sa.Text, nullable=True),
        # Constraint Classification
        sa.Column("constraint_type", sa.String(50), nullable=False, server_default="hard"),
        sa.Column("constraint_target", sa.Float, nullable=True),
        sa.Column("constraint_tolerance", sa.Float, nullable=True),
        sa.Column("constraint_unit", sa.String(50), nullable=True),
        # Verification
        sa.Column("verification_status", sa.String(50), nullable=False, server_default="unverified"),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verified_by", sa.String(255), nullable=True),
        sa.Column("verification_evidence", JSONB, nullable=False, server_default="{}"),
        # Formal Specification
        sa.Column("formal_spec", sa.Text, nullable=True),
        sa.Column("invariants", JSONB, nullable=False, server_default="[]"),
        sa.Column("preconditions", JSONB, nullable=False, server_default="[]"),
        sa.Column("postconditions", JSONB, nullable=False, server_default="[]"),
        # Quality Metrics
        sa.Column("quality_scores", JSONB, nullable=False, server_default="{}"),
        sa.Column("ambiguity_score", sa.Float, nullable=True),
        sa.Column("completeness_score", sa.Float, nullable=True),
        sa.Column("testability_score", sa.Float, nullable=True),
        sa.Column("overall_quality_score", sa.Float, nullable=True),
        sa.Column("quality_issues", JSONB, nullable=False, server_default="[]"),
        # Change Tracking
        sa.Column("volatility_index", sa.Float, nullable=True),
        sa.Column("change_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_changed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("change_history", JSONB, nullable=False, server_default="[]"),
        # Impact Analysis
        sa.Column("change_propagation_index", sa.Float, nullable=True),
        sa.Column("downstream_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("upstream_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("impact_assessment", JSONB, nullable=False, server_default="{}"),
        # Risk & Priority
        sa.Column("risk_level", sa.String(50), nullable=False, server_default="medium"),
        sa.Column("risk_factors", JSONB, nullable=False, server_default="[]"),
        sa.Column("wsjf_score", sa.Float, nullable=True),
        sa.Column("business_value", sa.Integer, nullable=True),
        sa.Column("time_criticality", sa.Integer, nullable=True),
        sa.Column("risk_reduction", sa.Integer, nullable=True),
        # Semantic Analysis
        sa.Column("embeddings_hash", sa.String(64), nullable=True),
        sa.Column("similar_items", JSONB, nullable=False, server_default="[]"),
        sa.Column("auto_tags", JSONB, nullable=False, server_default="[]"),
        sa.Column("complexity_estimate", sa.String(20), nullable=True),
        # Traceability
        sa.Column("source_reference", sa.Text, nullable=True),
        sa.Column("rationale", sa.Text, nullable=True),
        sa.Column("stakeholders", JSONB, nullable=False, server_default="[]"),
        # Metadata
        sa.Column("spec_metadata", JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_index("idx_req_spec_item", "requirement_specs", ["item_id"])
    op.create_index("idx_req_spec_type", "requirement_specs", ["requirement_type"])
    op.create_index("idx_req_spec_risk", "requirement_specs", ["risk_level"])
    op.create_index("idx_req_spec_verification", "requirement_specs", ["verification_status"])

    # === test_specs ===
    op.create_table(
        "test_specs",
        sa.Column("id", sa.String(255), primary_key=True),
        sa.Column(
            "item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("items.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        # Test Classification
        sa.Column("test_type", sa.String(50), nullable=False, server_default="unit"),
        sa.Column("test_level", sa.String(50), nullable=False, server_default="component"),
        sa.Column("test_category", sa.String(100), nullable=True),
        # Execution History & Metrics
        sa.Column("execution_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("passed_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("failed_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("skipped_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_executed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_execution_status", sa.String(50), nullable=True),
        sa.Column("execution_history", JSONB, nullable=False, server_default="[]"),
        # Performance & Flakiness
        sa.Column("avg_execution_time_ms", sa.Float, nullable=True),
        sa.Column("max_execution_time_ms", sa.Float, nullable=True),
        sa.Column("min_execution_time_ms", sa.Float, nullable=True),
        sa.Column("flakiness_index", sa.Float, nullable=True),
        sa.Column("flakiness_history", JSONB, nullable=False, server_default="[]"),
        sa.Column("is_flaky", sa.Boolean, nullable=False, server_default="false"),
        # Coverage
        sa.Column("coverage_percent", sa.Float, nullable=True),
        sa.Column("lines_covered", sa.Integer, nullable=True),
        sa.Column("lines_total", sa.Integer, nullable=True),
        sa.Column("branches_covered", sa.Integer, nullable=True),
        sa.Column("branches_total", sa.Integer, nullable=True),
        sa.Column("coverage_trend", JSONB, nullable=False, server_default="[]"),
        # Test Artifacts
        sa.Column("test_code", sa.Text, nullable=True),
        sa.Column("test_data", JSONB, nullable=False, server_default="{}"),
        sa.Column("fixtures", JSONB, nullable=False, server_default="[]"),
        sa.Column("setup_code", sa.Text, nullable=True),
        sa.Column("teardown_code", sa.Text, nullable=True),
        # Assertions & Expectations
        sa.Column("assertions", JSONB, nullable=False, server_default="[]"),
        sa.Column("expected_behavior", sa.Text, nullable=True),
        sa.Column("edge_cases", JSONB, nullable=False, server_default="[]"),
        # Dependencies & Related Tests
        sa.Column("depends_on_tests", JSONB, nullable=False, server_default="[]"),
        sa.Column("dependent_tests", JSONB, nullable=False, server_default="[]"),
        sa.Column("related_tests", JSONB, nullable=False, server_default="[]"),
        # Defect Tracking
        sa.Column("related_defects", JSONB, nullable=False, server_default="[]"),
        sa.Column("failure_patterns", JSONB, nullable=False, server_default="[]"),
        # Quality & Risk
        sa.Column("quality_score", sa.Float, nullable=True),
        sa.Column("risk_level", sa.String(50), nullable=False, server_default="medium"),
        sa.Column("maintenance_burden", sa.String(50), nullable=True),
        # Metadata
        sa.Column("spec_metadata", JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_index("idx_test_spec_item", "test_specs", ["item_id"])
    op.create_index("idx_test_spec_type", "test_specs", ["test_type"])
    op.create_index("idx_test_spec_level", "test_specs", ["test_level"])
    op.create_index("idx_test_spec_flaky", "test_specs", ["is_flaky"])
    op.create_index("idx_test_spec_last_executed", "test_specs", ["last_executed_at"])

    # === epic_specs ===
    op.create_table(
        "epic_specs",
        sa.Column("id", sa.String(255), primary_key=True),
        sa.Column(
            "item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("items.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        # Epic Classification
        sa.Column("epic_type", sa.String(50), nullable=False, server_default="feature"),
        sa.Column("strategic_alignment", sa.String(100), nullable=True),
        sa.Column("portfolio_status", sa.String(50), nullable=False, server_default="proposed"),
        # Vision & Goals
        sa.Column("vision_statement", sa.Text, nullable=True),
        sa.Column("success_criteria", JSONB, nullable=False, server_default="[]"),
        sa.Column("business_outcomes", JSONB, nullable=False, server_default="[]"),
        sa.Column("user_outcomes", JSONB, nullable=False, server_default="[]"),
        # Capacity & Planning
        sa.Column("estimated_effort_points", sa.Float, nullable=True),
        sa.Column("actual_effort_points", sa.Float, nullable=True),
        sa.Column("capacity_allocated", sa.Float, nullable=True),
        sa.Column("capacity_remaining", sa.Float, nullable=True),
        sa.Column("planned_start_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("planned_end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_start_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_end_date", sa.DateTime(timezone=True), nullable=True),
        # Dependencies & Roadmap
        sa.Column("dependent_epics", JSONB, nullable=False, server_default="[]"),
        sa.Column("blocking_epics", JSONB, nullable=False, server_default="[]"),
        sa.Column("roadmap_phase", sa.String(50), nullable=True),
        sa.Column("release_target", sa.String(50), nullable=True),
        # Stakeholders
        sa.Column("stakeholders", JSONB, nullable=False, server_default="[]"),
        sa.Column("epic_owner", sa.String(255), nullable=True),
        sa.Column("sponsor", sa.String(255), nullable=True),
        # Progress Tracking
        sa.Column("progress_percent", sa.Float, nullable=False, server_default="0"),
        sa.Column("health_status", sa.String(50), nullable=False, server_default="healthy"),
        sa.Column("risk_assessment", JSONB, nullable=False, server_default="{}"),
        sa.Column("issues_log", JSONB, nullable=False, server_default="[]"),
        # Stories & Work Items
        sa.Column("user_stories_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("completed_stories_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("child_items", JSONB, nullable=False, server_default="[]"),
        # Metrics
        sa.Column("quality_score", sa.Float, nullable=True),
        sa.Column("velocity_trend", JSONB, nullable=False, server_default="[]"),
        # Metadata
        sa.Column("spec_metadata", JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_index("idx_epic_spec_item", "epic_specs", ["item_id"])
    op.create_index("idx_epic_spec_type", "epic_specs", ["epic_type"])
    op.create_index("idx_epic_spec_portfolio_status", "epic_specs", ["portfolio_status"])
    op.create_index("idx_epic_spec_health", "epic_specs", ["health_status"])

    # === user_story_specs ===
    op.create_table(
        "user_story_specs",
        sa.Column("id", sa.String(255), primary_key=True),
        sa.Column(
            "item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("items.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        # User Story Classification
        sa.Column("story_type", sa.String(50), nullable=False, server_default="feature"),
        sa.Column("priority", sa.String(50), nullable=False, server_default="medium"),
        sa.Column("value_stream", sa.String(100), nullable=True),
        # User & Actor
        sa.Column("user_persona", sa.String(255), nullable=True),
        sa.Column("actor_role", sa.String(100), nullable=True),
        sa.Column("as_a", sa.Text, nullable=True),
        sa.Column("i_want", sa.Text, nullable=True),
        sa.Column("so_that", sa.Text, nullable=True),
        # Acceptance Criteria
        sa.Column("acceptance_criteria", JSONB, nullable=False, server_default="[]"),
        sa.Column("definition_of_done", JSONB, nullable=False, server_default="[]"),
        sa.Column("out_of_scope", sa.Text, nullable=True),
        # Scenarios & Examples
        sa.Column("scenarios", JSONB, nullable=False, server_default="[]"),
        sa.Column("gherkin_feature", sa.Text, nullable=True),
        sa.Column("example_workflows", JSONB, nullable=False, server_default="[]"),
        # Estimation & Velocity
        sa.Column("story_points", sa.Float, nullable=True),
        sa.Column("complexity_level", sa.String(50), nullable=True),
        sa.Column("effort_breakdown", JSONB, nullable=False, server_default="{}"),
        sa.Column("estimated_days", sa.Float, nullable=True),
        sa.Column("actual_days", sa.Float, nullable=True),
        sa.Column("velocity_contribution", sa.Float, nullable=True),
        # Implementation Details
        sa.Column("implementation_notes", sa.Text, nullable=True),
        sa.Column("technical_approach", sa.Text, nullable=True),
        sa.Column("affected_systems", JSONB, nullable=False, server_default="[]"),
        sa.Column("affected_services", JSONB, nullable=False, server_default="[]"),
        # Dependencies
        sa.Column("depends_on_stories", JSONB, nullable=False, server_default="[]"),
        sa.Column("blocking_stories", JSONB, nullable=False, server_default="[]"),
        sa.Column("epic_id", sa.String(255), nullable=True),
        # Testing & Quality
        sa.Column("test_coverage_percent", sa.Float, nullable=True),
        sa.Column("required_test_scenarios", JSONB, nullable=False, server_default="[]"),
        sa.Column("quality_gates", JSONB, nullable=False, server_default="[]"),
        # Progress Tracking
        sa.Column("status", sa.String(50), nullable=False, server_default="backlog"),
        sa.Column("completion_percent", sa.Float, nullable=False, server_default="0"),
        sa.Column("assignee", sa.String(255), nullable=True),
        # Metrics
        sa.Column("quality_score", sa.Float, nullable=True),
        # Metadata
        sa.Column("spec_metadata", JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_index("idx_story_spec_item", "user_story_specs", ["item_id"])
    op.create_index("idx_story_spec_type", "user_story_specs", ["story_type"])
    op.create_index("idx_story_spec_priority", "user_story_specs", ["priority"])
    op.create_index("idx_story_spec_status", "user_story_specs", ["status"])

    # === task_specs ===
    op.create_table(
        "task_specs",
        sa.Column("id", sa.String(255), primary_key=True),
        sa.Column(
            "item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("items.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        # Task Classification
        sa.Column("task_type", sa.String(50), nullable=False, server_default="implementation"),
        sa.Column("priority", sa.String(50), nullable=False, server_default="medium"),
        sa.Column("task_category", sa.String(100), nullable=True),
        # Time Tracking
        sa.Column("estimated_hours", sa.Float, nullable=True),
        sa.Column("actual_hours", sa.Float, nullable=True),
        sa.Column("remaining_hours", sa.Float, nullable=True),
        sa.Column("effort_tracking", JSONB, nullable=False, server_default="[]"),
        sa.Column("time_logs", JSONB, nullable=False, server_default="[]"),
        # Scheduling
        sa.Column("planned_start_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("planned_end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_start_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        # Dependencies
        sa.Column("depends_on_tasks", JSONB, nullable=False, server_default="[]"),
        sa.Column("blocking_tasks", JSONB, nullable=False, server_default="[]"),
        sa.Column("parallel_tasks", JSONB, nullable=False, server_default="[]"),
        sa.Column("related_tasks", JSONB, nullable=False, server_default="[]"),
        # Dependencies Graph (for critical path analysis)
        sa.Column("critical_path_position", sa.Integer, nullable=True),
        sa.Column("slack_time_hours", sa.Float, nullable=True),
        sa.Column("is_critical", sa.Boolean, nullable=False, server_default="false"),
        # Assignment & Ownership
        sa.Column("assignee", sa.String(255), nullable=True),
        sa.Column("owner", sa.String(255), nullable=True),
        sa.Column("reviewers", JSONB, nullable=False, server_default="[]"),
        # Implementation Details
        sa.Column("implementation_notes", sa.Text, nullable=True),
        sa.Column("acceptance_criteria", JSONB, nullable=False, server_default="[]"),
        sa.Column("deliverables", JSONB, nullable=False, server_default="[]"),
        # Progress & Status
        sa.Column("status", sa.String(50), nullable=False, server_default="todo"),
        sa.Column("completion_percent", sa.Float, nullable=False, server_default="0"),
        sa.Column("status_history", JSONB, nullable=False, server_default="[]"),
        # Blockers & Issues
        sa.Column("blockers", JSONB, nullable=False, server_default="[]"),
        sa.Column("risks", JSONB, nullable=False, server_default="[]"),
        sa.Column("issues_encountered", JSONB, nullable=False, server_default="[]"),
        # Quality
        sa.Column("quality_score", sa.Float, nullable=True),
        sa.Column("code_review_status", sa.String(50), nullable=True),
        # Parent References
        sa.Column("parent_task_id", sa.String(255), nullable=True),
        sa.Column("epic_id", sa.String(255), nullable=True),
        # Metadata
        sa.Column("spec_metadata", JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_index("idx_task_spec_item", "task_specs", ["item_id"])
    op.create_index("idx_task_spec_type", "task_specs", ["task_type"])
    op.create_index("idx_task_spec_priority", "task_specs", ["priority"])
    op.create_index("idx_task_spec_status", "task_specs", ["status"])
    op.create_index("idx_task_spec_assignee", "task_specs", ["assignee"])
    op.create_index("idx_task_spec_critical", "task_specs", ["is_critical"])

    # === defect_specs ===
    op.create_table(
        "defect_specs",
        sa.Column("id", sa.String(255), primary_key=True),
        sa.Column(
            "item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("items.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        # Defect Classification
        sa.Column("defect_type", sa.String(50), nullable=False, server_default="bug"),
        sa.Column("severity", sa.String(50), nullable=False, server_default="medium"),
        sa.Column("priority", sa.String(50), nullable=False, server_default="medium"),
        sa.Column("defect_category", sa.String(100), nullable=True),
        # Reproduction
        sa.Column("reproduction_steps", JSONB, nullable=False, server_default="[]"),
        sa.Column("reproduction_environment", JSONB, nullable=False, server_default="{}"),
        sa.Column("reproducibility_rate", sa.Float, nullable=True),
        sa.Column("is_reproducible", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("reproduction_frequency", sa.String(50), nullable=True),
        # Root Cause Analysis
        sa.Column("root_cause", sa.Text, nullable=True),
        sa.Column("rca_status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("rca_performed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rca_performed_by", sa.String(255), nullable=True),
        sa.Column("contributing_factors", JSONB, nullable=False, server_default="[]"),
        sa.Column("rca_evidence", JSONB, nullable=False, server_default="[]"),
        # Affected Components
        sa.Column("affected_component", sa.String(255), nullable=True),
        sa.Column("affected_systems", JSONB, nullable=False, server_default="[]"),
        sa.Column("affected_services", JSONB, nullable=False, server_default="[]"),
        sa.Column("affected_users", JSONB, nullable=False, server_default="[]"),
        # Impact Assessment
        sa.Column("business_impact", sa.Text, nullable=True),
        sa.Column("user_impact_count", sa.Integer, nullable=True),
        sa.Column("data_integrity_risk", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("security_risk", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("performance_impact", sa.String(50), nullable=True),
        # Verification & Testing
        sa.Column("verification_status", sa.String(50), nullable=False, server_default="unverified"),
        sa.Column("verification_method", sa.String(100), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verified_by", sa.String(255), nullable=True),
        sa.Column("test_case_id", sa.String(255), nullable=True),
        sa.Column("verification_evidence", JSONB, nullable=False, server_default="[]"),
        # Fix & Resolution
        sa.Column("proposed_solution", sa.Text, nullable=True),
        sa.Column("solution_approach", sa.String(100), nullable=True),
        sa.Column("fix_effort_hours", sa.Float, nullable=True),
        sa.Column("fix_complexity", sa.String(50), nullable=True),
        sa.Column("fix_status", sa.String(50), nullable=False, server_default="open"),
        sa.Column("fixed_in_version", sa.String(50), nullable=True),
        sa.Column("fix_commit", sa.String(255), nullable=True),
        sa.Column("fix_verified_at", sa.DateTime(timezone=True), nullable=True),
        # Regression Analysis
        sa.Column("regression_risk", sa.String(50), nullable=False, server_default="low"),
        sa.Column("regression_areas", JSONB, nullable=False, server_default="[]"),
        sa.Column("regression_tests_added", JSONB, nullable=False, server_default="[]"),
        # Workarounds
        sa.Column("has_workaround", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("workaround_description", sa.Text, nullable=True),
        # Lifecycle Tracking
        sa.Column("status", sa.String(50), nullable=False, server_default="open"),
        sa.Column("discovered_date", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("discovered_by", sa.String(255), nullable=True),
        sa.Column("assigned_to", sa.String(255), nullable=True),
        sa.Column("closed_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_reason", sa.String(100), nullable=True),
        sa.Column("status_history", JSONB, nullable=False, server_default="[]"),
        # Related Items
        sa.Column("related_defects", JSONB, nullable=False, server_default="[]"),
        sa.Column("duplicate_of", sa.String(255), nullable=True),
        sa.Column("related_issues", JSONB, nullable=False, server_default="[]"),
        # Metadata
        sa.Column("spec_metadata", JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_index("idx_defect_spec_item", "defect_specs", ["item_id"])
    op.create_index("idx_defect_spec_type", "defect_specs", ["defect_type"])
    op.create_index("idx_defect_spec_severity", "defect_specs", ["severity"])
    op.create_index("idx_defect_spec_priority", "defect_specs", ["priority"])
    op.create_index("idx_defect_spec_status", "defect_specs", ["status"])
    op.create_index("idx_defect_spec_rca_status", "defect_specs", ["rca_status"])


def downgrade() -> None:
    """Remove item specification tables."""
    op.drop_index("idx_defect_spec_rca_status", table_name="defect_specs")
    op.drop_index("idx_defect_spec_status", table_name="defect_specs")
    op.drop_index("idx_defect_spec_priority", table_name="defect_specs")
    op.drop_index("idx_defect_spec_severity", table_name="defect_specs")
    op.drop_index("idx_defect_spec_type", table_name="defect_specs")
    op.drop_index("idx_defect_spec_item", table_name="defect_specs")
    op.drop_table("defect_specs")

    op.drop_index("idx_task_spec_critical", table_name="task_specs")
    op.drop_index("idx_task_spec_assignee", table_name="task_specs")
    op.drop_index("idx_task_spec_status", table_name="task_specs")
    op.drop_index("idx_task_spec_priority", table_name="task_specs")
    op.drop_index("idx_task_spec_type", table_name="task_specs")
    op.drop_index("idx_task_spec_item", table_name="task_specs")
    op.drop_table("task_specs")

    op.drop_index("idx_story_spec_status", table_name="user_story_specs")
    op.drop_index("idx_story_spec_priority", table_name="user_story_specs")
    op.drop_index("idx_story_spec_type", table_name="user_story_specs")
    op.drop_index("idx_story_spec_item", table_name="user_story_specs")
    op.drop_table("user_story_specs")

    op.drop_index("idx_epic_spec_health", table_name="epic_specs")
    op.drop_index("idx_epic_spec_portfolio_status", table_name="epic_specs")
    op.drop_index("idx_epic_spec_type", table_name="epic_specs")
    op.drop_index("idx_epic_spec_item", table_name="epic_specs")
    op.drop_table("epic_specs")

    op.drop_index("idx_test_spec_last_executed", table_name="test_specs")
    op.drop_index("idx_test_spec_flaky", table_name="test_specs")
    op.drop_index("idx_test_spec_level", table_name="test_specs")
    op.drop_index("idx_test_spec_type", table_name="test_specs")
    op.drop_index("idx_test_spec_item", table_name="test_specs")
    op.drop_table("test_specs")

    op.drop_index("idx_req_spec_verification", table_name="requirement_specs")
    op.drop_index("idx_req_spec_risk", table_name="requirement_specs")
    op.drop_index("idx_req_spec_type", table_name="requirement_specs")
    op.drop_index("idx_req_spec_item", table_name="requirement_specs")
    op.drop_table("requirement_specs")
