# Migration 028: Item Specification Tables

**File:** `/alembic/versions/028_add_item_specifications.py`

**Revision:** 028_add_item_specifications
**Revises:** 027_add_step_definitions
**Created:** 2026-01-29

## Overview

This comprehensive migration creates 6 specification tables for enhanced item types with smart-contract-like specifications. Each table extends the core `items` table with type-specific attributes.

---

## 1. requirement_specs

**Purpose:** Rich requirement specifications with EARS pattern, constraints, and quality metrics

**Key Fields:**
- **EARS Classification:** requirement_type, ears_trigger, ears_precondition, ears_postcondition
- **Constraints:** constraint_type, constraint_target, constraint_tolerance, constraint_unit
- **Verification:** verification_status, verified_at, verified_by, verification_evidence
- **Formal Spec:** formal_spec, invariants, preconditions, postconditions
- **Quality Metrics:** quality_scores, ambiguity_score, completeness_score, testability_score, overall_quality_score, quality_issues
- **Change Tracking:** volatility_index, change_count, last_changed_at, change_history
- **Impact Analysis:** change_propagation_index, downstream_count, upstream_count, impact_assessment
- **Risk & Priority:** risk_level, risk_factors, wsjf_score, business_value, time_criticality, risk_reduction
- **Semantic Analysis:** embeddings_hash, similar_items, auto_tags, complexity_estimate
- **Traceability:** source_reference, rationale, stakeholders

**Indexes:**
- idx_req_spec_item (item_id)
- idx_req_spec_type (requirement_type)
- idx_req_spec_risk (risk_level)
- idx_req_spec_verification (verification_status)

---

## 2. test_specs

**Purpose:** Test specifications with execution history, flakiness metrics, and coverage tracking

**Key Fields:**
- **Test Classification:** test_type, test_level, test_category
- **Execution Metrics:** execution_count, passed_count, failed_count, skipped_count, last_executed_at, last_execution_status, execution_history
- **Performance:** avg_execution_time_ms, max_execution_time_ms, min_execution_time_ms
- **Flakiness:** flakiness_index, flakiness_history, is_flaky
- **Coverage:** coverage_percent, lines_covered, lines_total, branches_covered, branches_total, coverage_trend
- **Test Artifacts:** test_code, test_data, fixtures, setup_code, teardown_code
- **Assertions:** assertions, expected_behavior, edge_cases
- **Dependencies:** depends_on_tests, dependent_tests, related_tests
- **Defect Tracking:** related_defects, failure_patterns
- **Quality:** quality_score, risk_level, maintenance_burden

**Indexes:**
- idx_test_spec_item (item_id)
- idx_test_spec_type (test_type)
- idx_test_spec_level (test_level)
- idx_test_spec_flaky (is_flaky)
- idx_test_spec_last_executed (last_executed_at)

---

## 3. epic_specs

**Purpose:** Epic specifications with portfolio alignment, capacity planning, and roadmap tracking

**Key Fields:**
- **Epic Classification:** epic_type, strategic_alignment, portfolio_status
- **Vision & Goals:** vision_statement, success_criteria, business_outcomes, user_outcomes
- **Capacity Planning:** estimated_effort_points, actual_effort_points, capacity_allocated, capacity_remaining
- **Scheduling:** planned_start_date, planned_end_date, actual_start_date, actual_end_date
- **Dependencies:** dependent_epics, blocking_epics, roadmap_phase, release_target
- **Stakeholders:** stakeholders, epic_owner, sponsor
- **Progress Tracking:** progress_percent, health_status, risk_assessment, issues_log
- **Stories:** user_stories_count, completed_stories_count, child_items
- **Metrics:** quality_score, velocity_trend

**Indexes:**
- idx_epic_spec_item (item_id)
- idx_epic_spec_type (epic_type)
- idx_epic_spec_portfolio_status (portfolio_status)
- idx_epic_spec_health (health_status)

---

## 4. user_story_specs

**Purpose:** User story specifications with acceptance criteria and velocity tracking

**Key Fields:**
- **Story Classification:** story_type, priority, value_stream
- **User & Actor:** user_persona, actor_role, as_a, i_want, so_that
- **Acceptance Criteria:** acceptance_criteria, definition_of_done, out_of_scope
- **Scenarios:** scenarios, gherkin_feature, example_workflows
- **Estimation:** story_points, complexity_level, effort_breakdown, estimated_days, actual_days, velocity_contribution
- **Implementation:** implementation_notes, technical_approach, affected_systems, affected_services
- **Dependencies:** depends_on_stories, blocking_stories, epic_id
- **Testing:** test_coverage_percent, required_test_scenarios, quality_gates
- **Progress:** status, completion_percent, assignee
- **Quality:** quality_score

**Indexes:**
- idx_story_spec_item (item_id)
- idx_story_spec_type (story_type)
- idx_story_spec_priority (priority)
- idx_story_spec_status (status)

---

## 5. task_specs

**Purpose:** Task specifications with time tracking, dependencies, and critical path analysis

**Key Fields:**
- **Task Classification:** task_type, priority, task_category
- **Time Tracking:** estimated_hours, actual_hours, remaining_hours, effort_tracking, time_logs
- **Scheduling:** planned_start_date, planned_end_date, actual_start_date, actual_end_date, due_date
- **Dependencies:** depends_on_tasks, blocking_tasks, parallel_tasks, related_tasks
- **Critical Path:** critical_path_position, slack_time_hours, is_critical
- **Assignment:** assignee, owner, reviewers
- **Implementation:** implementation_notes, acceptance_criteria, deliverables
- **Progress:** status, completion_percent, status_history
- **Blockers:** blockers, risks, issues_encountered
- **Quality:** quality_score, code_review_status
- **Parent References:** parent_task_id, epic_id

**Indexes:**
- idx_task_spec_item (item_id)
- idx_task_spec_type (task_type)
- idx_task_spec_priority (priority)
- idx_task_spec_status (status)
- idx_task_spec_assignee (assignee)
- idx_task_spec_critical (is_critical)

---

## 6. defect_specs

**Purpose:** Defect specifications with RCA, reproduction steps, and verification tracking

**Key Fields:**
- **Defect Classification:** defect_type, severity, priority, defect_category
- **Reproduction:** reproduction_steps, reproduction_environment, reproducibility_rate, is_reproducible, reproduction_frequency
- **Root Cause Analysis:** root_cause, rca_status, rca_performed_at, rca_performed_by, contributing_factors, rca_evidence
- **Impact:** affected_component, affected_systems, affected_services, affected_users
- **Business Impact:** business_impact, user_impact_count, data_integrity_risk, security_risk, performance_impact
- **Verification:** verification_status, verification_method, verified_at, verified_by, test_case_id, verification_evidence
- **Fix & Resolution:** proposed_solution, solution_approach, fix_effort_hours, fix_complexity, fix_status, fixed_in_version, fix_commit, fix_verified_at
- **Regression Analysis:** regression_risk, regression_areas, regression_tests_added
- **Workarounds:** has_workaround, workaround_description
- **Lifecycle:** status, discovered_date, discovered_by, assigned_to, closed_date, closed_reason, status_history
- **Related Items:** related_defects, duplicate_of, related_issues

**Indexes:**
- idx_defect_spec_item (item_id)
- idx_defect_spec_type (defect_type)
- idx_defect_spec_severity (severity)
- idx_defect_spec_priority (priority)
- idx_defect_spec_status (status)
- idx_defect_spec_rca_status (rca_status)

---

## Database Characteristics

### All Tables Include:
- **Primary Key:** id (String(255))
- **Foreign Key:** item_id (references items.id with CASCADE delete) - UNIQUE constraint
- **Timestamps:** created_at, updated_at (with server defaults)
- **Metadata:** spec_metadata (JSONB for extensibility)

### JSONB Default Values:
All JSONB fields use PostgreSQL-compatible defaults:
- Empty objects: `server_default="{}"`
- Empty arrays: `server_default="[]"`

### Data Types:
- PostgreSQL JSONB for flexible, queryable JSON data
- String(255) for IDs (UUID format)
- DateTime(timezone=True) for all timestamps
- Float for numeric scores and metrics
- Integer for counts and indices
- Text for long-form content
- Boolean for flags

---

## Migration Statistics

- **Total Lines:** 503
- **Tables Created:** 6
- **Total Columns:** ~280
- **Total Indexes:** 22
- **Revision Chain:** 027 → 028

---

## Downgrade Strategy

The `downgrade()` function reverses all changes in reverse order:
1. Drop all indexes for each table
2. Drop each table in reverse creation order (defects → tasks → stories → epics → tests → requirements)

---

## Related Files

- **Specifications Base:** `/alembic/versions/027_add_step_definitions.py` (preceding migration)
- **Item Model:** `/src/tracertm/models/item.py`
- **Project:** `/alembic/env.py`

---

## Notes

- All tables use CASCADE delete on items.id foreign key
- All JSONB fields support advanced PostgreSQL queries (contains, has operators)
- Indexes are optimized for common query patterns (type, status, priority, verification)
- Default values use server-side evaluation for consistency
- Tables are migration-forward only (no down migrations should reverse)
