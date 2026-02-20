"""Enhance item specs with blockchain/NFT-like fields.

Adds content addressing, audit trail, EARS classification, ISO 29148 quality,
META-style flakiness, IBM ODC, CVSS, and WSJF/RICE prioritization fields.

Revision ID: 030_enhance_item_specs_blockchain
Revises: 029_add_notifications
Create Date: 2026-01-29
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic
revision = "030_enhance_item_specs_blockchain"
down_revision = "029_add_notifications"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add blockchain/NFT-like fields to all spec tables."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # =========================================================================
    # REQUIREMENT_SPECS - Content Addressing & Audit Trail
    # =========================================================================
    req_columns = [c["name"] for c in inspector.get_columns("requirement_specs")]

    if "content_hash" not in req_columns:
        op.add_column("requirement_specs", sa.Column("content_hash", sa.String(64), nullable=True))
    if "content_cid" not in req_columns:
        op.add_column("requirement_specs", sa.Column("content_cid", sa.String(100), nullable=True))
    if "merkle_root" not in req_columns:
        op.add_column("requirement_specs", sa.Column("merkle_root", sa.String(64), nullable=True))
    if "version_chain_head" not in req_columns:
        op.add_column("requirement_specs", sa.Column("version_chain_head", sa.String(64), nullable=True))
    if "created_by_hash" not in req_columns:
        op.add_column("requirement_specs", sa.Column("created_by_hash", sa.String(64), nullable=True))
    if "previous_version_hash" not in req_columns:
        op.add_column("requirement_specs", sa.Column("previous_version_hash", sa.String(64), nullable=True))
    if "digital_signature" not in req_columns:
        op.add_column("requirement_specs", sa.Column("digital_signature", sa.String(512), nullable=True))

    # EARS Classification
    if "ears_pattern_type" not in req_columns:
        op.add_column("requirement_specs", sa.Column("ears_pattern_type", sa.String(50), nullable=True))
    if "ears_trigger" not in req_columns:
        op.add_column("requirement_specs", sa.Column("ears_trigger", sa.Text(), nullable=True))
    if "ears_precondition" not in req_columns:
        op.add_column("requirement_specs", sa.Column("ears_precondition", sa.Text(), nullable=True))
    if "ears_postcondition" not in req_columns:
        op.add_column("requirement_specs", sa.Column("ears_postcondition", sa.Text(), nullable=True))
    if "ears_system_name" not in req_columns:
        op.add_column("requirement_specs", sa.Column("ears_system_name", sa.String(255), nullable=True))
    if "ears_confidence" not in req_columns:
        op.add_column("requirement_specs", sa.Column("ears_confidence", sa.Float(), nullable=True))
    if "ears_formal_structure" not in req_columns:
        op.add_column("requirement_specs", sa.Column("ears_formal_structure", sa.Text(), nullable=True))

    # ISO 29148 Quality Dimensions
    if "quality_dimensions" not in req_columns:
        op.add_column(
            "requirement_specs",
            sa.Column(
                "quality_dimensions",
                postgresql.JSONB(astext_type=sa.Text()),
                server_default="{}",
                nullable=False,
            ),
        )
    if "quality_grade" not in req_columns:
        op.add_column("requirement_specs", sa.Column("quality_grade", sa.String(5), nullable=True))

    # Formal Verification
    if "formal_constraints" not in req_columns:
        op.add_column(
            "requirement_specs",
            sa.Column(
                "formal_constraints",
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=True,
            ),
        )
    if "invariants" not in req_columns:
        op.add_column(
            "requirement_specs",
            sa.Column(
                "invariants",
                postgresql.JSONB(astext_type=sa.Text()),
                server_default="[]",
                nullable=False,
            ),
        )

    # RICE Prioritization
    if "rice_score" not in req_columns:
        op.add_column("requirement_specs", sa.Column("rice_score", sa.Float(), nullable=True))
    if "rice_reach" not in req_columns:
        op.add_column("requirement_specs", sa.Column("rice_reach", sa.Integer(), nullable=True))
    if "rice_impact" not in req_columns:
        op.add_column("requirement_specs", sa.Column("rice_impact", sa.Integer(), nullable=True))
    if "rice_confidence" not in req_columns:
        op.add_column("requirement_specs", sa.Column("rice_confidence", sa.Float(), nullable=True))
    if "rice_effort" not in req_columns:
        op.add_column("requirement_specs", sa.Column("rice_effort", sa.Integer(), nullable=True))
    if "moscow_priority" not in req_columns:
        op.add_column("requirement_specs", sa.Column("moscow_priority", sa.String(20), nullable=True))

    # Create indexes for content addressing
    if "ix_requirement_specs_content_hash" not in [i["name"] for i in inspector.get_indexes("requirement_specs")]:
        op.create_index("ix_requirement_specs_content_hash", "requirement_specs", ["content_hash"])
    if "ix_requirement_specs_content_cid" not in [i["name"] for i in inspector.get_indexes("requirement_specs")]:
        op.create_index("ix_requirement_specs_content_cid", "requirement_specs", ["content_cid"])

    # =========================================================================
    # TEST_SPECS - Content Addressing, Flakiness, Oracle, Coverage
    # =========================================================================
    test_columns = [c["name"] for c in inspector.get_columns("test_specs")]

    if "content_hash" not in test_columns:
        op.add_column("test_specs", sa.Column("content_hash", sa.String(64), nullable=True))
    if "content_cid" not in test_columns:
        op.add_column("test_specs", sa.Column("content_cid", sa.String(100), nullable=True))
    if "merkle_root" not in test_columns:
        op.add_column("test_specs", sa.Column("merkle_root", sa.String(64), nullable=True))
    if "version_chain_head" not in test_columns:
        op.add_column("test_specs", sa.Column("version_chain_head", sa.String(64), nullable=True))
    if "created_by_hash" not in test_columns:
        op.add_column("test_specs", sa.Column("created_by_hash", sa.String(64), nullable=True))
    if "previous_version_hash" not in test_columns:
        op.add_column("test_specs", sa.Column("previous_version_hash", sa.String(64), nullable=True))
    if "digital_signature" not in test_columns:
        op.add_column("test_specs", sa.Column("digital_signature", sa.String(512), nullable=True))

    # META-style Flakiness Detection
    if "flakiness_probability" not in test_columns:
        op.add_column("test_specs", sa.Column("flakiness_probability", sa.Float(), nullable=True))
    if "flakiness_entropy" not in test_columns:
        op.add_column("test_specs", sa.Column("flakiness_entropy", sa.Float(), nullable=True))
    if "flakiness_pattern" not in test_columns:
        op.add_column("test_specs", sa.Column("flakiness_pattern", sa.String(50), nullable=True))
    if "quarantine_recommended" not in test_columns:
        op.add_column(
            "test_specs",
            sa.Column(
                "quarantine_recommended",
                sa.Boolean(),
                server_default="false",
                nullable=False,
            ),
        )
    if "flakiness_contributing_factors" not in test_columns:
        op.add_column(
            "test_specs",
            sa.Column(
                "flakiness_contributing_factors",
                postgresql.JSONB(astext_type=sa.Text()),
                server_default="[]",
                nullable=False,
            ),
        )

    # Test Oracle Patterns
    if "oracle_type" not in test_columns:
        op.add_column("test_specs", sa.Column("oracle_type", sa.String(50), nullable=True))
    if "metamorphic_relations" not in test_columns:
        op.add_column(
            "test_specs",
            sa.Column(
                "metamorphic_relations",
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=True,
            ),
        )

    # Coverage Classification
    if "coverage_type" not in test_columns:
        op.add_column("test_specs", sa.Column("coverage_type", sa.String(50), nullable=True))
    if "safety_level" not in test_columns:
        op.add_column("test_specs", sa.Column("safety_level", sa.String(10), nullable=True))
    if "branch_coverage" not in test_columns:
        op.add_column("test_specs", sa.Column("branch_coverage", sa.Float(), nullable=True))
    if "mcdc_coverage" not in test_columns:
        op.add_column("test_specs", sa.Column("mcdc_coverage", sa.Float(), nullable=True))
    if "mutation_score" not in test_columns:
        op.add_column("test_specs", sa.Column("mutation_score", sa.Float(), nullable=True))

    # Create indexes
    test_indexes = [i["name"] for i in inspector.get_indexes("test_specs")]
    if "ix_test_specs_content_hash" not in test_indexes:
        op.create_index("ix_test_specs_content_hash", "test_specs", ["content_hash"])
    if "ix_test_specs_content_cid" not in test_indexes:
        op.create_index("ix_test_specs_content_cid", "test_specs", ["content_cid"])
    if "ix_test_specs_flakiness_probability" not in test_indexes:
        op.create_index("ix_test_specs_flakiness_probability", "test_specs", ["flakiness_probability"])

    # =========================================================================
    # DEFECT_SPECS - Content Addressing, ODC, CVSS, Root Cause
    # =========================================================================
    defect_columns = [c["name"] for c in inspector.get_columns("defect_specs")]

    if "content_hash" not in defect_columns:
        op.add_column("defect_specs", sa.Column("content_hash", sa.String(64), nullable=True))
    if "content_cid" not in defect_columns:
        op.add_column("defect_specs", sa.Column("content_cid", sa.String(100), nullable=True))
    if "merkle_root" not in defect_columns:
        op.add_column("defect_specs", sa.Column("merkle_root", sa.String(64), nullable=True))
    if "version_chain_head" not in defect_columns:
        op.add_column("defect_specs", sa.Column("version_chain_head", sa.String(64), nullable=True))
    if "created_by_hash" not in defect_columns:
        op.add_column("defect_specs", sa.Column("created_by_hash", sa.String(64), nullable=True))
    if "previous_version_hash" not in defect_columns:
        op.add_column("defect_specs", sa.Column("previous_version_hash", sa.String(64), nullable=True))
    if "digital_signature" not in defect_columns:
        op.add_column("defect_specs", sa.Column("digital_signature", sa.String(512), nullable=True))
    if "change_count" not in defect_columns:
        op.add_column("defect_specs", sa.Column("change_count", sa.Integer(), server_default="0", nullable=False))

    # IBM Orthogonal Defect Classification
    if "odc_defect_type" not in defect_columns:
        op.add_column("defect_specs", sa.Column("odc_defect_type", sa.String(50), nullable=True))
    if "odc_trigger" not in defect_columns:
        op.add_column("defect_specs", sa.Column("odc_trigger", sa.String(50), nullable=True))
    if "odc_impact" not in defect_columns:
        op.add_column("defect_specs", sa.Column("odc_impact", sa.String(50), nullable=True))
    if "odc_confidence" not in defect_columns:
        op.add_column("defect_specs", sa.Column("odc_confidence", sa.Float(), nullable=True))

    # CVSS Security Scoring
    if "cvss_base_score" not in defect_columns:
        op.add_column("defect_specs", sa.Column("cvss_base_score", sa.Float(), nullable=True))
    if "cvss_vector" not in defect_columns:
        op.add_column("defect_specs", sa.Column("cvss_vector", sa.String(255), nullable=True))
    if "cvss_severity" not in defect_columns:
        op.add_column("defect_specs", sa.Column("cvss_severity", sa.String(20), nullable=True))
    if "cvss_breakdown" not in defect_columns:
        op.add_column(
            "defect_specs",
            sa.Column(
                "cvss_breakdown",
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=True,
            ),
        )

    # Root Cause Analysis
    if "root_cause_category" not in defect_columns:
        op.add_column("defect_specs", sa.Column("root_cause_category", sa.String(100), nullable=True))
    if "injection_phase" not in defect_columns:
        op.add_column("defect_specs", sa.Column("injection_phase", sa.String(50), nullable=True))
    if "detection_phase" not in defect_columns:
        op.add_column("defect_specs", sa.Column("detection_phase", sa.String(50), nullable=True))

    # Create indexes
    defect_indexes = [i["name"] for i in inspector.get_indexes("defect_specs")]
    if "ix_defect_specs_content_hash" not in defect_indexes:
        op.create_index("ix_defect_specs_content_hash", "defect_specs", ["content_hash"])
    if "ix_defect_specs_content_cid" not in defect_indexes:
        op.create_index("ix_defect_specs_content_cid", "defect_specs", ["content_cid"])
    if "ix_defect_specs_odc_defect_type" not in defect_indexes:
        op.create_index("ix_defect_specs_odc_defect_type", "defect_specs", ["odc_defect_type"])
    if "ix_defect_specs_cvss_severity" not in defect_indexes:
        op.create_index("ix_defect_specs_cvss_severity", "defect_specs", ["cvss_severity"])

    # =========================================================================
    # EPIC_SPECS - Content Addressing & Prioritization
    # =========================================================================
    epic_columns = [c["name"] for c in inspector.get_columns("epic_specs")]

    if "content_hash" not in epic_columns:
        op.add_column("epic_specs", sa.Column("content_hash", sa.String(64), nullable=True))
    if "content_cid" not in epic_columns:
        op.add_column("epic_specs", sa.Column("content_cid", sa.String(100), nullable=True))
    if "merkle_root" not in epic_columns:
        op.add_column("epic_specs", sa.Column("merkle_root", sa.String(64), nullable=True))
    if "version_chain_head" not in epic_columns:
        op.add_column("epic_specs", sa.Column("version_chain_head", sa.String(64), nullable=True))
    if "created_by_hash" not in epic_columns:
        op.add_column("epic_specs", sa.Column("created_by_hash", sa.String(64), nullable=True))
    if "previous_version_hash" not in epic_columns:
        op.add_column("epic_specs", sa.Column("previous_version_hash", sa.String(64), nullable=True))
    if "digital_signature" not in epic_columns:
        op.add_column("epic_specs", sa.Column("digital_signature", sa.String(512), nullable=True))
    if "change_count" not in epic_columns:
        op.add_column("epic_specs", sa.Column("change_count", sa.Integer(), server_default="0", nullable=False))

    # WSJF Prioritization
    if "wsjf_score" not in epic_columns:
        op.add_column("epic_specs", sa.Column("wsjf_score", sa.Float(), nullable=True))
    if "business_value" not in epic_columns:
        op.add_column("epic_specs", sa.Column("business_value", sa.Integer(), nullable=True))
    if "time_criticality" not in epic_columns:
        op.add_column("epic_specs", sa.Column("time_criticality", sa.Integer(), nullable=True))
    if "risk_reduction" not in epic_columns:
        op.add_column("epic_specs", sa.Column("risk_reduction", sa.Integer(), nullable=True))
    if "job_size" not in epic_columns:
        op.add_column("epic_specs", sa.Column("job_size", sa.Integer(), nullable=True))

    # RICE Prioritization
    if "rice_score" not in epic_columns:
        op.add_column("epic_specs", sa.Column("rice_score", sa.Float(), nullable=True))
    if "rice_reach" not in epic_columns:
        op.add_column("epic_specs", sa.Column("rice_reach", sa.Integer(), nullable=True))
    if "rice_impact" not in epic_columns:
        op.add_column("epic_specs", sa.Column("rice_impact", sa.Integer(), nullable=True))
    if "rice_confidence" not in epic_columns:
        op.add_column("epic_specs", sa.Column("rice_confidence", sa.Float(), nullable=True))
    if "rice_effort" not in epic_columns:
        op.add_column("epic_specs", sa.Column("rice_effort", sa.Integer(), nullable=True))
    if "moscow_priority" not in epic_columns:
        op.add_column("epic_specs", sa.Column("moscow_priority", sa.String(20), nullable=True))

    # Create indexes
    epic_indexes = [i["name"] for i in inspector.get_indexes("epic_specs")]
    if "ix_epic_specs_content_hash" not in epic_indexes:
        op.create_index("ix_epic_specs_content_hash", "epic_specs", ["content_hash"])
    if "ix_epic_specs_content_cid" not in epic_indexes:
        op.create_index("ix_epic_specs_content_cid", "epic_specs", ["content_cid"])
    if "ix_epic_specs_wsjf_score" not in epic_indexes:
        op.create_index("ix_epic_specs_wsjf_score", "epic_specs", ["wsjf_score"])

    # =========================================================================
    # USER_STORY_SPECS - Content Addressing & Prioritization
    # =========================================================================
    story_columns = [c["name"] for c in inspector.get_columns("user_story_specs")]

    if "content_hash" not in story_columns:
        op.add_column("user_story_specs", sa.Column("content_hash", sa.String(64), nullable=True))
    if "content_cid" not in story_columns:
        op.add_column("user_story_specs", sa.Column("content_cid", sa.String(100), nullable=True))
    if "merkle_root" not in story_columns:
        op.add_column("user_story_specs", sa.Column("merkle_root", sa.String(64), nullable=True))
    if "version_chain_head" not in story_columns:
        op.add_column("user_story_specs", sa.Column("version_chain_head", sa.String(64), nullable=True))
    if "created_by_hash" not in story_columns:
        op.add_column("user_story_specs", sa.Column("created_by_hash", sa.String(64), nullable=True))
    if "previous_version_hash" not in story_columns:
        op.add_column("user_story_specs", sa.Column("previous_version_hash", sa.String(64), nullable=True))
    if "digital_signature" not in story_columns:
        op.add_column("user_story_specs", sa.Column("digital_signature", sa.String(512), nullable=True))
    if "change_count" not in story_columns:
        op.add_column("user_story_specs", sa.Column("change_count", sa.Integer(), server_default="0", nullable=False))

    # WSJF Prioritization
    if "wsjf_score" not in story_columns:
        op.add_column("user_story_specs", sa.Column("wsjf_score", sa.Float(), nullable=True))
    if "time_criticality" not in story_columns:
        op.add_column("user_story_specs", sa.Column("time_criticality", sa.Integer(), nullable=True))
    if "risk_reduction" not in story_columns:
        op.add_column("user_story_specs", sa.Column("risk_reduction", sa.Integer(), nullable=True))
    if "job_size" not in story_columns:
        op.add_column("user_story_specs", sa.Column("job_size", sa.Integer(), nullable=True))

    # RICE Prioritization
    if "rice_score" not in story_columns:
        op.add_column("user_story_specs", sa.Column("rice_score", sa.Float(), nullable=True))
    if "rice_reach" not in story_columns:
        op.add_column("user_story_specs", sa.Column("rice_reach", sa.Integer(), nullable=True))
    if "rice_impact" not in story_columns:
        op.add_column("user_story_specs", sa.Column("rice_impact", sa.Integer(), nullable=True))
    if "rice_confidence" not in story_columns:
        op.add_column("user_story_specs", sa.Column("rice_confidence", sa.Float(), nullable=True))
    if "rice_effort" not in story_columns:
        op.add_column("user_story_specs", sa.Column("rice_effort", sa.Integer(), nullable=True))
    if "moscow_priority" not in story_columns:
        op.add_column("user_story_specs", sa.Column("moscow_priority", sa.String(20), nullable=True))

    # Create indexes
    story_indexes = [i["name"] for i in inspector.get_indexes("user_story_specs")]
    if "ix_user_story_specs_content_hash" not in story_indexes:
        op.create_index("ix_user_story_specs_content_hash", "user_story_specs", ["content_hash"])
    if "ix_user_story_specs_content_cid" not in story_indexes:
        op.create_index("ix_user_story_specs_content_cid", "user_story_specs", ["content_cid"])
    if "ix_user_story_specs_wsjf_score" not in story_indexes:
        op.create_index("ix_user_story_specs_wsjf_score", "user_story_specs", ["wsjf_score"])

    # =========================================================================
    # TASK_SPECS - Content Addressing & Prioritization
    # =========================================================================
    task_columns = [c["name"] for c in inspector.get_columns("task_specs")]

    if "content_hash" not in task_columns:
        op.add_column("task_specs", sa.Column("content_hash", sa.String(64), nullable=True))
    if "content_cid" not in task_columns:
        op.add_column("task_specs", sa.Column("content_cid", sa.String(100), nullable=True))
    if "merkle_root" not in task_columns:
        op.add_column("task_specs", sa.Column("merkle_root", sa.String(64), nullable=True))
    if "version_chain_head" not in task_columns:
        op.add_column("task_specs", sa.Column("version_chain_head", sa.String(64), nullable=True))
    if "created_by_hash" not in task_columns:
        op.add_column("task_specs", sa.Column("created_by_hash", sa.String(64), nullable=True))
    if "previous_version_hash" not in task_columns:
        op.add_column("task_specs", sa.Column("previous_version_hash", sa.String(64), nullable=True))
    if "digital_signature" not in task_columns:
        op.add_column("task_specs", sa.Column("digital_signature", sa.String(512), nullable=True))
    if "change_count" not in task_columns:
        op.add_column("task_specs", sa.Column("change_count", sa.Integer(), server_default="0", nullable=False))

    # WSJF Prioritization
    if "wsjf_score" not in task_columns:
        op.add_column("task_specs", sa.Column("wsjf_score", sa.Float(), nullable=True))
    if "business_value" not in task_columns:
        op.add_column("task_specs", sa.Column("business_value", sa.Integer(), nullable=True))
    if "time_criticality" not in task_columns:
        op.add_column("task_specs", sa.Column("time_criticality", sa.Integer(), nullable=True))
    if "risk_reduction" not in task_columns:
        op.add_column("task_specs", sa.Column("risk_reduction", sa.Integer(), nullable=True))
    if "job_size" not in task_columns:
        op.add_column("task_specs", sa.Column("job_size", sa.Integer(), nullable=True))

    # RICE Prioritization
    if "rice_score" not in task_columns:
        op.add_column("task_specs", sa.Column("rice_score", sa.Float(), nullable=True))
    if "rice_reach" not in task_columns:
        op.add_column("task_specs", sa.Column("rice_reach", sa.Integer(), nullable=True))
    if "rice_impact" not in task_columns:
        op.add_column("task_specs", sa.Column("rice_impact", sa.Integer(), nullable=True))
    if "rice_confidence" not in task_columns:
        op.add_column("task_specs", sa.Column("rice_confidence", sa.Float(), nullable=True))
    if "rice_effort" not in task_columns:
        op.add_column("task_specs", sa.Column("rice_effort", sa.Integer(), nullable=True))
    if "moscow_priority" not in task_columns:
        op.add_column("task_specs", sa.Column("moscow_priority", sa.String(20), nullable=True))

    # Create indexes
    task_indexes = [i["name"] for i in inspector.get_indexes("task_specs")]
    if "ix_task_specs_content_hash" not in task_indexes:
        op.create_index("ix_task_specs_content_hash", "task_specs", ["content_hash"])
    if "ix_task_specs_content_cid" not in task_indexes:
        op.create_index("ix_task_specs_content_cid", "task_specs", ["content_cid"])
    if "ix_task_specs_wsjf_score" not in task_indexes:
        op.create_index("ix_task_specs_wsjf_score", "task_specs", ["wsjf_score"])


def downgrade() -> None:
    """Remove blockchain/NFT-like fields from all spec tables."""
    # =========================================================================
    # TASK_SPECS
    # =========================================================================
    op.drop_index("ix_task_specs_wsjf_score", table_name="task_specs")
    op.drop_index("ix_task_specs_content_cid", table_name="task_specs")
    op.drop_index("ix_task_specs_content_hash", table_name="task_specs")

    op.drop_column("task_specs", "moscow_priority")
    op.drop_column("task_specs", "rice_effort")
    op.drop_column("task_specs", "rice_confidence")
    op.drop_column("task_specs", "rice_impact")
    op.drop_column("task_specs", "rice_reach")
    op.drop_column("task_specs", "rice_score")
    op.drop_column("task_specs", "job_size")
    op.drop_column("task_specs", "risk_reduction")
    op.drop_column("task_specs", "time_criticality")
    op.drop_column("task_specs", "business_value")
    op.drop_column("task_specs", "wsjf_score")
    op.drop_column("task_specs", "change_count")
    op.drop_column("task_specs", "digital_signature")
    op.drop_column("task_specs", "previous_version_hash")
    op.drop_column("task_specs", "created_by_hash")
    op.drop_column("task_specs", "version_chain_head")
    op.drop_column("task_specs", "merkle_root")
    op.drop_column("task_specs", "content_cid")
    op.drop_column("task_specs", "content_hash")

    # =========================================================================
    # USER_STORY_SPECS
    # =========================================================================
    op.drop_index("ix_user_story_specs_wsjf_score", table_name="user_story_specs")
    op.drop_index("ix_user_story_specs_content_cid", table_name="user_story_specs")
    op.drop_index("ix_user_story_specs_content_hash", table_name="user_story_specs")

    op.drop_column("user_story_specs", "moscow_priority")
    op.drop_column("user_story_specs", "rice_effort")
    op.drop_column("user_story_specs", "rice_confidence")
    op.drop_column("user_story_specs", "rice_impact")
    op.drop_column("user_story_specs", "rice_reach")
    op.drop_column("user_story_specs", "rice_score")
    op.drop_column("user_story_specs", "job_size")
    op.drop_column("user_story_specs", "risk_reduction")
    op.drop_column("user_story_specs", "time_criticality")
    op.drop_column("user_story_specs", "wsjf_score")
    op.drop_column("user_story_specs", "change_count")
    op.drop_column("user_story_specs", "digital_signature")
    op.drop_column("user_story_specs", "previous_version_hash")
    op.drop_column("user_story_specs", "created_by_hash")
    op.drop_column("user_story_specs", "version_chain_head")
    op.drop_column("user_story_specs", "merkle_root")
    op.drop_column("user_story_specs", "content_cid")
    op.drop_column("user_story_specs", "content_hash")

    # =========================================================================
    # EPIC_SPECS
    # =========================================================================
    op.drop_index("ix_epic_specs_wsjf_score", table_name="epic_specs")
    op.drop_index("ix_epic_specs_content_cid", table_name="epic_specs")
    op.drop_index("ix_epic_specs_content_hash", table_name="epic_specs")

    op.drop_column("epic_specs", "moscow_priority")
    op.drop_column("epic_specs", "rice_effort")
    op.drop_column("epic_specs", "rice_confidence")
    op.drop_column("epic_specs", "rice_impact")
    op.drop_column("epic_specs", "rice_reach")
    op.drop_column("epic_specs", "rice_score")
    op.drop_column("epic_specs", "job_size")
    op.drop_column("epic_specs", "risk_reduction")
    op.drop_column("epic_specs", "time_criticality")
    op.drop_column("epic_specs", "business_value")
    op.drop_column("epic_specs", "wsjf_score")
    op.drop_column("epic_specs", "change_count")
    op.drop_column("epic_specs", "digital_signature")
    op.drop_column("epic_specs", "previous_version_hash")
    op.drop_column("epic_specs", "created_by_hash")
    op.drop_column("epic_specs", "version_chain_head")
    op.drop_column("epic_specs", "merkle_root")
    op.drop_column("epic_specs", "content_cid")
    op.drop_column("epic_specs", "content_hash")

    # =========================================================================
    # DEFECT_SPECS
    # =========================================================================
    op.drop_index("ix_defect_specs_cvss_severity", table_name="defect_specs")
    op.drop_index("ix_defect_specs_odc_defect_type", table_name="defect_specs")
    op.drop_index("ix_defect_specs_content_cid", table_name="defect_specs")
    op.drop_index("ix_defect_specs_content_hash", table_name="defect_specs")

    op.drop_column("defect_specs", "detection_phase")
    op.drop_column("defect_specs", "injection_phase")
    op.drop_column("defect_specs", "root_cause_category")
    op.drop_column("defect_specs", "cvss_breakdown")
    op.drop_column("defect_specs", "cvss_severity")
    op.drop_column("defect_specs", "cvss_vector")
    op.drop_column("defect_specs", "cvss_base_score")
    op.drop_column("defect_specs", "odc_confidence")
    op.drop_column("defect_specs", "odc_impact")
    op.drop_column("defect_specs", "odc_trigger")
    op.drop_column("defect_specs", "odc_defect_type")
    op.drop_column("defect_specs", "change_count")
    op.drop_column("defect_specs", "digital_signature")
    op.drop_column("defect_specs", "previous_version_hash")
    op.drop_column("defect_specs", "created_by_hash")
    op.drop_column("defect_specs", "version_chain_head")
    op.drop_column("defect_specs", "merkle_root")
    op.drop_column("defect_specs", "content_cid")
    op.drop_column("defect_specs", "content_hash")

    # =========================================================================
    # TEST_SPECS
    # =========================================================================
    op.drop_index("ix_test_specs_flakiness_probability", table_name="test_specs")
    op.drop_index("ix_test_specs_content_cid", table_name="test_specs")
    op.drop_index("ix_test_specs_content_hash", table_name="test_specs")

    op.drop_column("test_specs", "mutation_score")
    op.drop_column("test_specs", "mcdc_coverage")
    op.drop_column("test_specs", "branch_coverage")
    op.drop_column("test_specs", "safety_level")
    op.drop_column("test_specs", "coverage_type")
    op.drop_column("test_specs", "metamorphic_relations")
    op.drop_column("test_specs", "oracle_type")
    op.drop_column("test_specs", "flakiness_contributing_factors")
    op.drop_column("test_specs", "quarantine_recommended")
    op.drop_column("test_specs", "flakiness_pattern")
    op.drop_column("test_specs", "flakiness_entropy")
    op.drop_column("test_specs", "flakiness_probability")
    op.drop_column("test_specs", "digital_signature")
    op.drop_column("test_specs", "previous_version_hash")
    op.drop_column("test_specs", "created_by_hash")
    op.drop_column("test_specs", "version_chain_head")
    op.drop_column("test_specs", "merkle_root")
    op.drop_column("test_specs", "content_cid")
    op.drop_column("test_specs", "content_hash")

    # =========================================================================
    # REQUIREMENT_SPECS
    # =========================================================================
    op.drop_index("ix_requirement_specs_content_cid", table_name="requirement_specs")
    op.drop_index("ix_requirement_specs_content_hash", table_name="requirement_specs")

    op.drop_column("requirement_specs", "moscow_priority")
    op.drop_column("requirement_specs", "rice_effort")
    op.drop_column("requirement_specs", "rice_confidence")
    op.drop_column("requirement_specs", "rice_impact")
    op.drop_column("requirement_specs", "rice_reach")
    op.drop_column("requirement_specs", "rice_score")
    op.drop_column("requirement_specs", "invariants")
    op.drop_column("requirement_specs", "formal_constraints")
    op.drop_column("requirement_specs", "quality_grade")
    op.drop_column("requirement_specs", "quality_dimensions")
    op.drop_column("requirement_specs", "ears_formal_structure")
    op.drop_column("requirement_specs", "ears_confidence")
    op.drop_column("requirement_specs", "ears_system_name")
    op.drop_column("requirement_specs", "ears_postcondition")
    op.drop_column("requirement_specs", "ears_precondition")
    op.drop_column("requirement_specs", "ears_trigger")
    op.drop_column("requirement_specs", "ears_pattern_type")
    op.drop_column("requirement_specs", "digital_signature")
    op.drop_column("requirement_specs", "previous_version_hash")
    op.drop_column("requirement_specs", "created_by_hash")
    op.drop_column("requirement_specs", "version_chain_head")
    op.drop_column("requirement_specs", "merkle_root")
    op.drop_column("requirement_specs", "content_cid")
    op.drop_column("requirement_specs", "content_hash")
