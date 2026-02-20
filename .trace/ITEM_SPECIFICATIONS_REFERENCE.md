# Item Specifications Reference Guide

Complete field documentation for all 6 specification tables created by migration 028.

---

## 1. requirement_specs

One-to-one relationship with items table for requirement-type items.

### EARS Pattern Support

#### ears_trigger (Text, nullable)
- The condition/event that triggers the requirement
- Example: "When user clicks submit"

#### ears_precondition (Text, nullable)
- State before requirement must hold
- Example: "User is logged in"

#### ears_postcondition (Text, nullable)
- State after requirement is fulfilled
- Example: "Data is saved and confirmation displayed"

### Constraint Management

#### constraint_type (String(50), default="hard")
- Values: "hard", "soft", "performance", "security", "compliance"
- Hard constraints are mandatory; soft are preferred

#### constraint_target (Float, nullable)
- Target value for constraint
- Example: "99.9" for uptime percentage

#### constraint_tolerance (Float, nullable)
- Acceptable variance from target
- Example: "0.1" for ±0.1% tolerance

#### constraint_unit (String(50), nullable)
- Unit of measurement
- Example: "%", "ms", "requests/sec"

### Verification Lifecycle

#### verification_status (String(50), default="unverified")
- Values: "unverified", "pending", "in_progress", "verified", "failed", "obsolete"
- Tracks requirement sign-off state

#### verified_at (DateTime, nullable)
- Timestamp of verification completion

#### verified_by (String(255), nullable)
- User ID of verifier

#### verification_evidence (JSONB)
- Array of evidence objects: `[{type, reference, timestamp, notes}]`
- Supports: test_results, document_links, sign_off_records

### Formal Specification

#### formal_spec (Text, nullable)
- Mathematical or logic-based specification
- Example: Temporal Logic notation, Z notation, etc.

#### invariants (JSONB array)
- Conditions that must always hold
- Format: `[{name, expression, severity}]`

#### preconditions (JSONB array)
- Must be true before execution
- Format: `[{name, expression, required}]`

#### postconditions (JSONB array)
- Must be true after execution
- Format: `[{name, expression, impact}]`

### Quality Scoring

#### quality_scores (JSONB)
- Aggregated quality metrics object
- Example: `{ambiguity: 0.2, completeness: 0.95, testability: 0.85}`

#### ambiguity_score (Float, 0-1)
- 0 = Clear and unambiguous
- 1 = Highly ambiguous, needs clarification

#### completeness_score (Float, 0-1)
- 0 = Incomplete, missing details
- 1 = Complete specification

#### testability_score (Float, 0-1)
- 0 = Untestable
- 1 = Easily testable with clear criteria

#### overall_quality_score (Float, 0-1)
- Composite of all quality dimensions

#### quality_issues (JSONB array)
- `[{issue_type, severity, description, suggested_fix}]`
- Types: ambiguity, incompleteness, contradiction, testability_gap

### Change Tracking

#### change_count (Integer, default=0)
- Number of times requirement has been modified

#### volatility_index (Float, 0-1)
- 0 = Stable
- 1 = Frequently changing (high volatility)

#### change_history (JSONB array)
- `[{timestamp, changed_by, changes, reason}]`
- Tracks all modifications over time

### Impact Analysis

#### downstream_count (Integer)
- Number of items dependent on this requirement

#### upstream_count (Integer)
- Number of items this requirement depends on

#### change_propagation_index (Float, 0-1)
- Likelihood change impacts other items

#### impact_assessment (JSONB)
- `{scope, affected_areas, risk_level, effort_estimate}`
- Used for change impact analysis

### Risk & Prioritization

#### risk_level (String(50), default="medium")
- Values: "low", "medium", "high", "critical"
- Used with other factors for prioritization

#### risk_factors (JSONB array)
- `[{factor, likelihood, impact, mitigation}]`
- Examples: "technical_complexity", "schedule_risk", "dependency_risk"

#### wsjf_score (Float)
- Weighted Shortest Job First score
- Combines business value + time criticality + risk reduction / effort

#### business_value (Integer, 1-10)
- Relative business value

#### time_criticality (Integer, 1-10)
- Time sensitivity (1=not critical, 10=critical)

#### risk_reduction (Integer, 1-10)
- Risk reduction if implemented (1=minimal, 10=critical)

### Semantic Analysis

#### embeddings_hash (String(64), nullable)
- SHA-256 of semantic embedding
- Used to find semantically similar requirements

#### similar_items (JSONB array)
- `[{item_id, similarity_score}]`
- Items with similar semantic content

#### auto_tags (JSONB array)
- `[{tag, confidence, source}]`
- AI-generated tags for categorization

#### complexity_estimate (String(20))
- Values: "simple", "moderate", "complex", "very_complex"

### Traceability

#### source_reference (Text, nullable)
- Reference to source document
- Example: "SRS-2.3.1", "USER_STORY_123"

#### rationale (Text, nullable)
- Why this requirement exists

#### stakeholders (JSONB array)
- `[{name, role, contact}]`
- Interested parties

---

## 2. test_specs

One-to-one relationship for test-type items with execution and coverage data.

### Test Classification

#### test_type (String(50), default="unit")
- Values: "unit", "integration", "system", "acceptance", "performance", "security", "smoke", "regression"

#### test_level (String(50), default="component")
- Values: "component", "integration", "system", "end-to-end", "api", "ui"

#### test_category (String(100), nullable)
- Custom categorization (e.g., "critical_path", "exploratory")

### Execution Metrics

#### execution_count (Integer, default=0)
- Total executions ever

#### passed_count (Integer, default=0)
- Cumulative passes

#### failed_count (Integer, default=0)
- Cumulative failures

#### skipped_count (Integer, default=0)
- Cumulative skips

#### last_executed_at (DateTime, nullable)
- Most recent execution timestamp

#### last_execution_status (String(50), nullable)
- Values: "passed", "failed", "skipped", "timeout", "error"

#### execution_history (JSONB array)
- `[{timestamp, status, duration_ms, branch, commit_sha}]`
- Maintains execution timeline

### Performance Metrics

#### avg_execution_time_ms (Float, nullable)
- Mean execution duration

#### max_execution_time_ms (Float, nullable)
- Longest execution time

#### min_execution_time_ms (Float, nullable)
- Fastest execution time

### Flakiness Tracking

#### flakiness_index (Float, 0-1)
- 0 = Deterministic (never flaky)
- 1 = Completely unreliable

#### flakiness_history (JSONB array)
- `[{date, flakiness_score, failure_rate}]`
- Weekly/daily trend data

#### is_flaky (Boolean, default=false)
- Quick flag for flaky test filtering

### Coverage Metrics

#### coverage_percent (Float, 0-100)
- Overall code coverage percentage

#### lines_covered (Integer, nullable)
- Number of lines executed

#### lines_total (Integer, nullable)
- Total lines in subject code

#### branches_covered (Integer, nullable)
- Branch coverage count

#### branches_total (Integer, nullable)
- Total branches in code

#### coverage_trend (JSONB array)
- `[{date, coverage_percent, lines_covered}]`
- Historical coverage progression

### Test Artifacts

#### test_code (Text, nullable)
- Complete test implementation

#### test_data (JSONB)
- Data used in test execution
- `{datasets: [{name, records}], mocks: {}}`

#### fixtures (JSONB array)
- Setup/teardown data
- `[{name, type, data}]`

#### setup_code (Text, nullable)
- Code run before test

#### teardown_code (Text, nullable)
- Code run after test

### Assertions & Expectations

#### assertions (JSONB array)
- `[{line, assertion_text, actual, expected}]`

#### expected_behavior (Text, nullable)
- Description of expected behavior

#### edge_cases (JSONB array)
- `[{case, input, expected_output}]`
- Documented edge cases

### Dependencies & Relationships

#### depends_on_tests (JSONB array)
- `[{test_id, reason}]`
- Tests that must pass first

#### dependent_tests (JSONB array)
- Tests dependent on this one

#### related_tests (JSONB array)
- Tests covering same functionality

### Defect Tracking

#### related_defects (JSONB array)
- `[{defect_id, relationship}]`
- Links to defects caught by test

#### failure_patterns (JSONB array)
- `[{pattern, frequency, last_occurrence}]`
- Recurring failure modes

### Quality & Risk

#### quality_score (Float, 0-1)
- Composite test quality (coverage, stability, maintenance)

#### risk_level (String(50), default="medium")
- Values: "low", "medium", "high"
- Risk of test not catching regressions

#### maintenance_burden (String(50), nullable)
- Values: "low", "moderate", "high"
- Effort to maintain and update

---

## 3. epic_specs

One-to-one for epic-type items with portfolio and capacity tracking.

### Epic Classification

#### epic_type (String(50), default="feature")
- Values: "feature", "capability", "initiative", "platform", "infrastructure"

#### strategic_alignment (String(100), nullable)
- Strategic pillar: "customer", "product", "operations", "technical"

#### portfolio_status (String(50), default="proposed")
- Values: "proposed", "approved", "active", "completed", "cancelled", "on-hold"

### Vision & Success Criteria

#### vision_statement (Text, nullable)
- High-level vision for epic

#### success_criteria (JSONB array)
- `[{criterion, measure, target, status}]`

#### business_outcomes (JSONB array)
- `[{outcome, measure, target_value}]`

#### user_outcomes (JSONB array)
- `[{outcome, user_segment, impact}]`

### Capacity Planning

#### estimated_effort_points (Float, nullable)
- Total story points estimate

#### actual_effort_points (Float, nullable)
- Actual points spent

#### capacity_allocated (Float, nullable)
- Team capacity assigned

#### capacity_remaining (Float, nullable)
- Unallocated capacity

### Timeline Tracking

#### planned_start_date (DateTime, nullable)
- Scheduled start

#### planned_end_date (DateTime, nullable)
- Scheduled completion

#### actual_start_date (DateTime, nullable)
- When work began

#### actual_end_date (DateTime, nullable)
- When work completed

### Dependencies & Roadmap

#### dependent_epics (JSONB array)
- `[{epic_id, type}]`
- Epics dependent on this one

#### blocking_epics (JSONB array)
- `[{epic_id, reason}]`
- Epics blocking this one

#### roadmap_phase (String(50), nullable)
- Values: "discovery", "design", "build", "launch", "grow"

#### release_target (String(50), nullable)
- Version or date target

### Stakeholders

#### stakeholders (JSONB array)
- `[{name, role, email}]`

#### epic_owner (String(255), nullable)
- Primary owner user ID

#### sponsor (String(255), nullable)
- Executive sponsor user ID

### Progress Tracking

#### progress_percent (Float, 0-100, default=0)
- Overall completion percentage

#### health_status (String(50), default="healthy")
- Values: "healthy", "at_risk", "critical"
- Status indicator

#### risk_assessment (JSONB)
- `{overall_risk, identified_risks: [{name, impact, likelihood}]}`

#### issues_log (JSONB array)
- `[{date, description, severity, owner, status}]`

### Stories & Work Items

#### user_stories_count (Integer, default=0)
- Total user stories in epic

#### completed_stories_count (Integer, default=0)
- Finished stories

#### child_items (JSONB array)
- `[{item_id, type, status}]`
- Direct child items

### Metrics

#### quality_score (Float, 0-1)
- Overall epic quality

#### velocity_trend (JSONB array)
- `[{sprint, completed_points, planned_points}]`
- Velocity progression

---

## 4. user_story_specs

One-to-one for user story items with acceptance and estimation.

### Story Classification

#### story_type (String(50), default="feature")
- Values: "feature", "bug_fix", "technical_debt", "spike", "improvement"

#### priority (String(50), default="medium")
- Values: "low", "medium", "high", "critical"

#### value_stream (String(100), nullable)
- Business stream: "onboarding", "core", "engagement", etc.

### User & Actor Definition

#### user_persona (String(255), nullable)
- Target user type

#### actor_role (String(100), nullable)
- System role performing action

#### as_a (Text, nullable)
- "As a [role/persona]"

#### i_want (Text, nullable)
- "I want to [action]"

#### so_that (Text, nullable)
- "So that [benefit]"

### Acceptance Criteria

#### acceptance_criteria (JSONB array)
- `[{criterion, description, verification_method}]`
- Must-have conditions

#### definition_of_done (JSONB array)
- `[{task, responsible, verified}]`
- Team's DoD checklist

#### out_of_scope (Text, nullable)
- What is explicitly NOT included

### Scenarios & Examples

#### scenarios (JSONB array)
- `[{scenario_name, steps: [{given, when, then}]}]`

#### gherkin_feature (Text, nullable)
- Full BDD Gherkin feature file

#### example_workflows (JSONB array)
- `[{workflow_name, steps, expected_result}]`

### Estimation & Velocity

#### story_points (Float, nullable)
- Fibonacci estimate

#### complexity_level (String(50), nullable)
- Values: "trivial", "simple", "moderate", "complex", "very_complex"

#### effort_breakdown (JSONB)
- `{design: 2, implementation: 5, testing: 3}`
- Component-level effort

#### estimated_days (Float, nullable)
- Calendar days estimate

#### actual_days (Float, nullable)
- Actual duration

#### velocity_contribution (Float, nullable)
- Contribution to team velocity

### Implementation Details

#### implementation_notes (Text, nullable)
- Technical notes

#### technical_approach (Text, nullable)
- How to implement

#### affected_systems (JSONB array)
- `[{system_name, change_type}]`

#### affected_services (JSONB array)
- `[{service_name, change_type}]`

### Dependencies

#### depends_on_stories (JSONB array)
- `[{story_id, type}]`

#### blocking_stories (JSONB array)
- Stories blocked by this one

#### epic_id (String(255), nullable)
- Parent epic reference

### Testing & Quality

#### test_coverage_percent (Float, 0-100, nullable)
- Code coverage requirement

#### required_test_scenarios (JSONB array)
- `[{scenario, test_case_id}]`

#### quality_gates (JSONB array)
- `[{gate_name, criteria, passed}]`

### Progress Tracking

#### status (String(50), default="backlog")
- Values: "backlog", "ready", "in_progress", "testing", "done", "cancelled"

#### completion_percent (Float, 0-100, default=0)

#### assignee (String(255), nullable)
- Developer user ID

### Quality Metrics

#### quality_score (Float, 0-1)
- Composite story quality score

---

## 5. task_specs

One-to-one for task items with time tracking and dependencies.

### Task Classification

#### task_type (String(50), default="implementation")
- Values: "implementation", "testing", "review", "documentation", "deployment", "support"

#### priority (String(50), default="medium")
- Values: "low", "medium", "high", "critical"

#### task_category (String(100), nullable)
- Custom categorization

### Time Tracking

#### estimated_hours (Float, nullable)
- Estimated effort

#### actual_hours (Float, nullable)
- Time spent

#### remaining_hours (Float, nullable)
- Estimated remaining

#### time_logs (JSONB array)
- `[{date, hours, description, user_id}]`
- Daily time entries

#### effort_tracking (JSONB array)
- `[{date, estimated_remaining, actual_spent}]`
- Historical tracking

### Scheduling

#### planned_start_date (DateTime, nullable)
#### planned_end_date (DateTime, nullable)
#### actual_start_date (DateTime, nullable)
#### actual_end_date (DateTime, nullable)
#### due_date (DateTime, nullable)
- Hard deadline

### Dependencies & Critical Path

#### depends_on_tasks (JSONB array)
- Tasks that must complete first

#### blocking_tasks (JSONB array)
- Tasks blocked by this one

#### parallel_tasks (JSONB array)
- Tasks that can run in parallel

#### related_tasks (JSONB array)
- Loosely related tasks

#### critical_path_position (Integer, nullable)
- Position in critical path (0=not critical)

#### slack_time_hours (Float, nullable)
- Flexible time available

#### is_critical (Boolean, default=false)
- Quick critical path filter

### Assignment & Ownership

#### assignee (String(255), nullable)
- Primary assignee

#### owner (String(255), nullable)
- Task owner/PM

#### reviewers (JSONB array)
- `[{user_id, review_status}]`

### Implementation Details

#### implementation_notes (Text, nullable)
#### acceptance_criteria (JSONB array)
#### deliverables (JSONB array)
- `[{deliverable_name, status, location}]`

### Progress Tracking

#### status (String(50), default="todo")
- Values: "todo", "in_progress", "blocked", "on_hold", "done", "cancelled"

#### completion_percent (Float, 0-100, default=0)

#### status_history (JSONB array)
- `[{timestamp, from_status, to_status, changed_by}]`

### Blockers & Issues

#### blockers (JSONB array)
- `[{blocker_id, reason, severity}]`

#### risks (JSONB array)
- `[{risk, probability, impact, mitigation}]`

#### issues_encountered (JSONB array)
- `[{date, description, resolution}]`

### Quality

#### quality_score (Float, 0-1)
#### code_review_status (String(50), nullable)
- Values: "not_started", "in_review", "approved", "changes_requested"

### Parent References

#### parent_task_id (String(255), nullable)
- Parent task if subtask

#### epic_id (String(255), nullable)
- Associated epic

---

## 6. defect_specs

One-to-one for defect items with RCA and verification.

### Defect Classification

#### defect_type (String(50), default="bug")
- Values: "bug", "enhancement_gap", "regression", "design_flaw", "documentation_error"

#### severity (String(50), default="medium")
- Values: "critical", "high", "medium", "low", "trivial"
- Impact on users/systems

#### priority (String(50), default="medium")
- Values: "critical", "high", "medium", "low"
- Fix urgency

#### defect_category (String(100), nullable)
- "functional", "performance", "security", "usability", "compatibility"

### Reproduction

#### reproduction_steps (JSONB array)
- `[{step_number, action, expected_result}]`

#### reproduction_environment (JSONB)
- `{browser, os, version, api_endpoint}`

#### reproducibility_rate (Float, 0-1)
- How often it reproduces

#### is_reproducible (Boolean, default=true)
- Whether it can be reproduced

#### reproduction_frequency (String(50), nullable)
- Values: "always", "intermittent", "rare"

### Root Cause Analysis

#### root_cause (Text, nullable)
- The identified root cause

#### rca_status (String(50), default="pending")
- Values: "pending", "in_progress", "complete", "unresolved"

#### rca_performed_at (DateTime, nullable)
#### rca_performed_by (String(255), nullable)

#### contributing_factors (JSONB array)
- `[{factor, description}]`

#### rca_evidence (JSONB array)
- `[{type, reference, finding}]`

### Affected Scope

#### affected_component (String(255), nullable)
- Primary affected component

#### affected_systems (JSONB array)
- Systems impacted

#### affected_services (JSONB array)
- Services impacted

#### affected_users (JSONB array)
- User segments impacted

### Impact Assessment

#### business_impact (Text, nullable)
- Business/revenue impact

#### user_impact_count (Integer, nullable)
- Number of affected users

#### data_integrity_risk (Boolean, default=false)
- Does it corrupt/lose data?

#### security_risk (Boolean, default=false)
- Security vulnerability?

#### performance_impact (String(50), nullable)
- Values: "none", "minor", "moderate", "severe"

### Verification & Testing

#### verification_status (String(50), default="unverified")
- Values: "unverified", "verified", "cannot_verify"

#### verification_method (String(100), nullable)
- How verified (test_case, manual, user_report)

#### verified_at (DateTime, nullable)
#### verified_by (String(255), nullable)

#### test_case_id (String(255), nullable)
- Link to test case

#### verification_evidence (JSONB array)
- Supporting evidence

### Fix & Resolution

#### proposed_solution (Text, nullable)
- How to fix

#### solution_approach (String(100), nullable)
- Technical approach

#### fix_effort_hours (Float, nullable)
- Estimated fix time

#### fix_complexity (String(50), nullable)
- Values: "trivial", "simple", "moderate", "complex"

#### fix_status (String(50), default="open")
- Values: "open", "in_progress", "completed", "wont_fix"

#### fixed_in_version (String(50), nullable)
- Release containing fix

#### fix_commit (String(255), nullable)
- Git commit hash

#### fix_verified_at (DateTime, nullable)
- When fix was verified

### Regression Analysis

#### regression_risk (String(50), default="low")
- Risk of introducing regressions

#### regression_areas (JSONB array)
- Areas that could regress

#### regression_tests_added (JSONB array)
- New tests added to prevent recurrence

### Workarounds

#### has_workaround (Boolean, default=false)
#### workaround_description (Text, nullable)
- Temporary fix for users

### Lifecycle Tracking

#### status (String(50), default="open")
- Values: "open", "in_progress", "testing", "closed", "reopened", "duplicate", "wont_fix"

#### discovered_date (DateTime, default=now)
#### discovered_by (String(255), nullable)

#### assigned_to (String(255), nullable)
- Current owner

#### closed_date (DateTime, nullable)
#### closed_reason (String(100), nullable)

#### status_history (JSONB array)
- `[{timestamp, from_status, to_status, changed_by}]`

### Related Items

#### related_defects (JSONB array)
- Similar or related defects

#### duplicate_of (String(255), nullable)
- If duplicate, points to original

#### related_issues (JSONB array)
- Feature requests, tasks, etc.

---

## Common Field Patterns

### Status Fields
All tables include status tracking with standard patterns:
- Each has primary `status` field
- Some include `*_status` variants (verification_status, rca_status)
- All support `status_history` (JSONB array) for audit trail

### Quality Scoring
Consistent quality scoring across tables:
- `quality_score` (Float, 0-1)
- Dimension-specific scores available

### JSONB Best Practices
- Always include `server_default="[]"` or `server_default="{}"` in migration
- Use consistent object/array structure
- Document expected structure in field description
- Support extensibility with flexible schema

### Timestamps
All tables include:
- `created_at` (server default = now, read-only)
- `updated_at` (server default = now)
- Type-specific timestamps (verified_at, discovered_at, etc.)

---

## Querying Examples

```sql
-- Find high-risk requirements
SELECT * FROM requirement_specs WHERE risk_level = 'high' ORDER BY wsjf_score DESC;

-- Find flaky tests
SELECT * FROM test_specs WHERE is_flaky = true ORDER BY flakiness_index DESC;

-- Critical path tasks
SELECT * FROM task_specs WHERE is_critical = true AND status != 'done';

-- Defects by severity with RCA
SELECT * FROM defect_specs WHERE severity IN ('critical', 'high') AND rca_status = 'pending';

-- Epic progress tracking
SELECT id, progress_percent, health_status FROM epic_specs WHERE portfolio_status = 'active';
```

---

**Last Updated:** 2026-01-29
**Migration Version:** 028
**PostgreSQL Version:** 12+
