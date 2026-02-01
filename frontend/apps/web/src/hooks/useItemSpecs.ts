/**
 * React hooks for enhanced Item specifications.
 *
 * Provides TanStack Query hooks for RequirementSpec, TestSpec, EpicSpec,
 * UserStorySpec, TaskSpec, and DefectSpec operations with full CRUD,
 * specialized queries, optimistic updates, and cache invalidation.
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getAuthHeaders } from "@/api/client";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:4000";

// =============================================================================
// Types
// =============================================================================

export type RequirementType =
	| "ubiquitous"
	| "event_driven"
	| "state_driven"
	| "optional"
	| "complex"
	| "unwanted";
export type ConstraintType = "hard" | "soft" | "optimizable";
export type VerificationStatus =
	| "unverified"
	| "pending"
	| "verified"
	| "failed"
	| "expired";
export type RiskLevel = "critical" | "high" | "medium" | "low" | "minimal";
export type TestType =
	| "unit"
	| "integration"
	| "e2e"
	| "performance"
	| "security"
	| "accessibility"
	| "contract"
	| "mutation"
	| "fuzz"
	| "property";
export type TestResultStatus =
	| "passed"
	| "failed"
	| "skipped"
	| "blocked"
	| "flaky"
	| "timeout"
	| "error";

export type EpicStatus = "backlog" | "in_progress" | "completed" | "archived";
export type UserStoryStatus =
	| "backlog"
	| "ready"
	| "in_progress"
	| "review"
	| "done"
	| "archived";
export type TaskStatus = "todo" | "in_progress" | "review" | "done" | "blocked";
export type DefectSeverity = "critical" | "major" | "minor" | "trivial";
export type DefectStatus =
	| "new"
	| "assigned"
	| "in_progress"
	| "resolved"
	| "verified"
	| "closed"
	| "reopened";

export interface QualityIssue {
	dimension: string;
	severity: "error" | "warning" | "info";
	message: string;
	suggestion?: string;
}

export interface RequirementSpec {
	id: string;
	item_id: string;
	requirement_type: RequirementType;
	ears_trigger?: string;
	ears_precondition?: string;
	ears_postcondition?: string;
	constraint_type: ConstraintType;
	constraint_target?: number;
	constraint_tolerance?: number;
	constraint_unit?: string;
	verification_status: VerificationStatus;
	verified_at?: string;
	verified_by?: string;
	verification_evidence: Record<string, unknown>;
	formal_spec?: string;
	invariants: unknown[];
	preconditions: string[];
	postconditions: string[];
	quality_scores: Record<string, number>;
	ambiguity_score?: number;
	completeness_score?: number;
	testability_score?: number;
	overall_quality_score?: number;
	quality_issues: QualityIssue[];
	volatility_index?: number;
	change_count: number;
	last_changed_at?: string;
	change_history: unknown[];
	change_propagation_index?: number;
	downstream_count: number;
	upstream_count: number;
	impact_assessment: Record<string, unknown>;
	risk_level: RiskLevel;
	risk_factors: string[];
	wsjf_score?: number;
	business_value?: number;
	time_criticality?: number;
	risk_reduction?: number;
	similar_items: unknown[];
	auto_tags: string[];
	complexity_estimate?: string;
	source_reference?: string;
	rationale?: string;
	stakeholders: string[];
	spec_metadata: Record<string, unknown>;
	created_at: string;
	updated_at: string;
}

export interface TestSpec {
	id: string;
	item_id: string;
	test_type: TestType;
	test_framework?: string;
	test_file_path?: string;
	test_function_name?: string;
	preconditions: string[];
	setup_commands: string[];
	teardown_commands: string[];
	environment_requirements: Record<string, unknown>;
	test_data_schema: Record<string, unknown>;
	fixtures: string[];
	parameterized_cases: unknown[];
	total_runs: number;
	pass_count: number;
	fail_count: number;
	skip_count: number;
	last_run_at?: string;
	last_run_status?: TestResultStatus;
	last_run_duration_ms?: number;
	last_run_error?: string;
	run_history: unknown[];
	flakiness_score?: number;
	flakiness_window_runs: number;
	flaky_patterns: string[];
	is_quarantined: boolean;
	quarantine_reason?: string;
	quarantined_at?: string;
	avg_duration_ms?: number;
	p50_duration_ms?: number;
	p95_duration_ms?: number;
	p99_duration_ms?: number;
	duration_trend?: string;
	performance_baseline_ms?: number;
	performance_threshold_ms?: number;
	line_coverage?: number;
	branch_coverage?: number;
	mutation_score?: number;
	mcdc_coverage?: number;
	verifies_requirements: string[];
	verifies_contracts: string[];
	assertions: string[];
	depends_on_tests: string[];
	required_services: string[];
	mocked_dependencies: string[];
	maintenance_score?: number;
	suggested_actions: string[];
	spec_metadata: Record<string, unknown>;
	created_at: string;
	updated_at: string;
}

export interface EpicSpec {
	id: string;
	item_id: string;
	epic_name: string;
	business_value: number;
	target_release?: string;
	status: EpicStatus;
	start_date?: string;
	end_date?: string;
	dependencies: string[];
	child_stories_count: number;
	user_stories: string[];
	objectives: string[];
	success_criteria: string[];
	stakeholders: string[];
	acceptance_criteria: Record<string, unknown>;
	scope_statement?: string;
	out_of_scope?: string[];
	constraints: string[];
	assumptions: string[];
	risks: Array<{
		description: string;
		mitigation: string;
		impact: RiskLevel;
	}>;
	themes: string[];
	metrics: Record<string, number>;
	spec_metadata: Record<string, unknown>;
	created_at: string;
	updated_at: string;
}

export interface UserStorySpec {
	id: string;
	item_id: string;
	story_points?: number;
	status: UserStoryStatus;
	as_a: string;
	i_want: string;
	so_that: string;
	acceptance_criteria: Array<{
		criterion: string;
		completed: boolean;
		verified_at?: string;
	}>;
	definition_of_done: string[];
	edge_cases: string[];
	dependencies: string[];
	related_tasks: string[];
	parent_epic?: string;
	priority: number;
	estimation_confidence?: number;
	test_scenarios: string[];
	ui_mockups?: string[];
	api_specs?: string[];
	database_changes?: Record<string, unknown>;
	spec_metadata: Record<string, unknown>;
	created_at: string;
	updated_at: string;
}

export interface TaskSpec {
	id: string;
	item_id: string;
	task_title: string;
	description?: string;
	status: TaskStatus;
	assigned_to?: string;
	due_date?: string;
	estimated_hours?: number;
	actual_hours?: number;
	priority: number;
	parent_story?: string;
	subtasks: Array<{
		id: string;
		title: string;
		completed: boolean;
		completed_at?: string;
	}>;
	dependencies: string[];
	blocking: string[];
	checklist: Array<{
		item: string;
		completed: boolean;
		completed_by?: string;
		completed_at?: string;
	}>;
	code_changes?: Array<{
		file: string;
		lines_added: number;
		lines_deleted: number;
	}>;
	review_comments?: string[];
	labels: string[];
	spec_metadata: Record<string, unknown>;
	created_at: string;
	updated_at: string;
}

export interface DefectSpec {
	id: string;
	item_id: string;
	defect_title: string;
	description?: string;
	severity: DefectSeverity;
	status: DefectStatus;
	assigned_to?: string;
	reported_by?: string;
	environment?: string;
	reproducible: boolean;
	steps_to_reproduce: string[];
	expected_behavior?: string;
	actual_behavior?: string;
	affected_versions: string[];
	root_cause?: string;
	resolution?: string;
	verification_notes?: string;
	related_defects: string[];
	related_requirements: string[];
	attachments: Array<{
		url: string;
		description?: string;
		type: string;
	}>;
	regression_risk: RiskLevel;
	time_to_fix_estimate?: number;
	priority: number;
	spec_metadata: Record<string, unknown>;
	created_at: string;
	updated_at: string;
}

// Create types
export interface RequirementSpecCreate {
	item_id: string;
	requirement_type?: RequirementType;
	constraint_type?: ConstraintType;
	constraint_target?: number;
	constraint_tolerance?: number;
	constraint_unit?: string;
	ears_trigger?: string;
	ears_precondition?: string;
	ears_postcondition?: string;
	formal_spec?: string;
	risk_level?: RiskLevel;
	risk_factors?: string[];
	business_value?: number;
	time_criticality?: number;
	risk_reduction?: number;
	source_reference?: string;
	rationale?: string;
	stakeholders?: string[];
	spec_metadata?: Record<string, unknown>;
}

export interface TestSpecCreate {
	item_id: string;
	test_type?: TestType;
	test_framework?: string;
	test_file_path?: string;
	test_function_name?: string;
	preconditions?: string[];
	setup_commands?: string[];
	teardown_commands?: string[];
	environment_requirements?: Record<string, unknown>;
	verifies_requirements?: string[];
	verifies_contracts?: string[];
	performance_baseline_ms?: number;
	performance_threshold_ms?: number;
	spec_metadata?: Record<string, unknown>;
}

export interface EpicSpecCreate {
	item_id: string;
	epic_name: string;
	business_value: number;
	target_release?: string;
	objectives?: string[];
	success_criteria?: string[];
	stakeholders?: string[];
	constraints?: string[];
	assumptions?: string[];
	spec_metadata?: Record<string, unknown>;
}

export interface UserStorySpecCreate {
	item_id: string;
	as_a: string;
	i_want: string;
	so_that: string;
	story_points?: number;
	acceptance_criteria?: Array<{ criterion: string }>;
	definition_of_done?: string[];
	priority?: number;
	parent_epic?: string;
	spec_metadata?: Record<string, unknown>;
}

export interface TaskSpecCreate {
	item_id: string;
	task_title: string;
	description?: string;
	priority?: number;
	estimated_hours?: number;
	parent_story?: string;
	dependencies?: string[];
	spec_metadata?: Record<string, unknown>;
}

export interface DefectSpecCreate {
	item_id: string;
	defect_title: string;
	description?: string;
	severity: DefectSeverity;
	environment?: string;
	steps_to_reproduce?: string[];
	expected_behavior?: string;
	actual_behavior?: string;
	priority?: number;
	reported_by?: string;
	spec_metadata?: Record<string, unknown>;
}

// Update types
export interface RequirementSpecUpdate {
	requirement_type?: RequirementType;
	constraint_type?: ConstraintType;
	constraint_target?: number;
	constraint_tolerance?: number;
	constraint_unit?: string;
	ears_trigger?: string;
	ears_precondition?: string;
	ears_postcondition?: string;
	formal_spec?: string;
	verification_status?: VerificationStatus;
	risk_level?: RiskLevel;
	risk_factors?: string[];
	business_value?: number;
	time_criticality?: number;
	risk_reduction?: number;
	source_reference?: string;
	rationale?: string;
	stakeholders?: string[];
	spec_metadata?: Record<string, unknown>;
}

export interface TestSpecUpdate {
	test_type?: TestType;
	test_framework?: string;
	test_file_path?: string;
	test_function_name?: string;
	preconditions?: string[];
	setup_commands?: string[];
	teardown_commands?: string[];
	environment_requirements?: Record<string, unknown>;
	performance_baseline_ms?: number;
	performance_threshold_ms?: number;
	spec_metadata?: Record<string, unknown>;
}

export interface EpicSpecUpdate {
	epic_name?: string;
	business_value?: number;
	target_release?: string;
	status?: EpicStatus;
	objectives?: string[];
	success_criteria?: string[];
	stakeholders?: string[];
	constraints?: string[];
	assumptions?: string[];
	spec_metadata?: Record<string, unknown>;
}

export interface UserStorySpecUpdate {
	as_a?: string;
	i_want?: string;
	so_that?: string;
	story_points?: number;
	status?: UserStoryStatus;
	acceptance_criteria?: Array<{ criterion: string; completed?: boolean }>;
	definition_of_done?: string[];
	priority?: number;
	spec_metadata?: Record<string, unknown>;
}

export interface TaskSpecUpdate {
	task_title?: string;
	description?: string;
	status?: TaskStatus;
	assigned_to?: string;
	due_date?: string;
	estimated_hours?: number;
	actual_hours?: number;
	priority?: number;
	spec_metadata?: Record<string, unknown>;
}

export interface DefectSpecUpdate {
	defect_title?: string;
	description?: string;
	severity?: DefectSeverity;
	status?: DefectStatus;
	assigned_to?: string;
	environment?: string;
	steps_to_reproduce?: string[];
	expected_behavior?: string;
	actual_behavior?: string;
	root_cause?: string;
	resolution?: string;
	priority?: number;
	spec_metadata?: Record<string, unknown>;
}

// =============================================================================
// Query Keys Factory
// =============================================================================

export const itemSpecKeys = {
	all: ["item-specs"] as const,
	// Requirement specs
	requirements: (projectId: string) =>
		[...itemSpecKeys.all, "requirements", projectId] as const,
	requirement: (projectId: string, specId: string) =>
		[...itemSpecKeys.requirements(projectId), specId] as const,
	requirementByItem: (projectId: string, itemId: string) =>
		[...itemSpecKeys.requirements(projectId), "by-item", itemId] as const,
	unverifiedRequirements: (projectId: string) =>
		[...itemSpecKeys.requirements(projectId), "unverified"] as const,
	highRiskRequirements: (projectId: string) =>
		[...itemSpecKeys.requirements(projectId), "high-risk"] as const,
	requirementsByType: (projectId: string, type: RequirementType) =>
		[...itemSpecKeys.requirements(projectId), "by-type", type] as const,

	// Test specs
	tests: (projectId: string) =>
		[...itemSpecKeys.all, "tests", projectId] as const,
	test: (projectId: string, specId: string) =>
		[...itemSpecKeys.tests(projectId), specId] as const,
	testByItem: (projectId: string, itemId: string) =>
		[...itemSpecKeys.tests(projectId), "by-item", itemId] as const,
	flakyTests: (projectId: string) =>
		[...itemSpecKeys.tests(projectId), "flaky"] as const,
	testsByType: (projectId: string, type: TestType) =>
		[...itemSpecKeys.tests(projectId), "by-type", type] as const,
	testHealthReport: (projectId: string) =>
		[...itemSpecKeys.tests(projectId), "health-report"] as const,
	quarantinedTests: (projectId: string) =>
		[...itemSpecKeys.tests(projectId), "quarantined"] as const,

	// Epic specs
	epics: (projectId: string) =>
		[...itemSpecKeys.all, "epics", projectId] as const,
	epic: (projectId: string, specId: string) =>
		[...itemSpecKeys.epics(projectId), specId] as const,
	epicByItem: (projectId: string, itemId: string) =>
		[...itemSpecKeys.epics(projectId), "by-item", itemId] as const,
	epicsByStatus: (projectId: string, status: EpicStatus) =>
		[...itemSpecKeys.epics(projectId), "by-status", status] as const,

	// User story specs
	userStories: (projectId: string) =>
		[...itemSpecKeys.all, "user-stories", projectId] as const,
	userStory: (projectId: string, specId: string) =>
		[...itemSpecKeys.userStories(projectId), specId] as const,
	userStoryByItem: (projectId: string, itemId: string) =>
		[...itemSpecKeys.userStories(projectId), "by-item", itemId] as const,
	userStoriesByEpic: (projectId: string, epicId: string) =>
		[...itemSpecKeys.userStories(projectId), "by-epic", epicId] as const,
	userStoriesByStatus: (projectId: string, status: UserStoryStatus) =>
		[...itemSpecKeys.userStories(projectId), "by-status", status] as const,

	// Task specs
	tasks: (projectId: string) =>
		[...itemSpecKeys.all, "tasks", projectId] as const,
	task: (projectId: string, specId: string) =>
		[...itemSpecKeys.tasks(projectId), specId] as const,
	taskByItem: (projectId: string, itemId: string) =>
		[...itemSpecKeys.tasks(projectId), "by-item", itemId] as const,
	tasksByStory: (projectId: string, storyId: string) =>
		[...itemSpecKeys.tasks(projectId), "by-story", storyId] as const,
	tasksByStatus: (projectId: string, status: TaskStatus) =>
		[...itemSpecKeys.tasks(projectId), "by-status", status] as const,

	// Defect specs
	defects: (projectId: string) =>
		[...itemSpecKeys.all, "defects", projectId] as const,
	defect: (projectId: string, specId: string) =>
		[...itemSpecKeys.defects(projectId), specId] as const,
	defectByItem: (projectId: string, itemId: string) =>
		[...itemSpecKeys.defects(projectId), "by-item", itemId] as const,
	defectsBySeverity: (projectId: string, severity: DefectSeverity) =>
		[...itemSpecKeys.defects(projectId), "by-severity", severity] as const,
	defectsByStatus: (projectId: string, status: DefectStatus) =>
		[...itemSpecKeys.defects(projectId), "by-status", status] as const,

	// Summary/stats
	stats: (projectId: string) =>
		[...itemSpecKeys.all, "stats", projectId] as const,
};

// =============================================================================
// API Fetch Functions
// =============================================================================

// Requirement Specs
async function fetchRequirementSpecs(
	projectId: string,
	options?: {
		requirementType?: RequirementType;
		riskLevel?: RiskLevel;
		verificationStatus?: VerificationStatus;
		limit?: number;
		offset?: number;
	},
): Promise<{ specs: RequirementSpec[]; total: number }> {
	const params = new URLSearchParams();
	if (options?.requirementType)
		params.append("requirement_type", options.requirementType);
	if (options?.riskLevel) params.append("risk_level", options.riskLevel);
	if (options?.verificationStatus)
		params.append("verification_status", options.verificationStatus);
	if (options?.limit) params.append("limit", String(options.limit));
	if (options?.offset) params.append("offset", String(options.offset));

	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/requirements?${params}`,
		{ headers: { "X-Bulk-Operation": "true", ...getAuthHeaders() } },
	);
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(
			`Failed to fetch requirement specs: ${res.status} ${errorText}`,
		);
	}
	return res.json();
}

async function fetchRequirementSpec(
	projectId: string,
	specId: string,
): Promise<RequirementSpec> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/requirements/${specId}`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to fetch requirement spec");
	return res.json();
}

async function fetchRequirementSpecByItem(
	projectId: string,
	itemId: string,
): Promise<RequirementSpec> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/requirements/by-item/${itemId}`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to fetch requirement spec by item");
	return res.json();
}

async function fetchUnverifiedRequirements(
	projectId: string,
	limit = 100,
): Promise<{ specs: RequirementSpec[]; total: number }> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/requirements/unverified?limit=${limit}`,
		{ headers: { "X-Bulk-Operation": "true", ...getAuthHeaders() } },
	);
	if (!res.ok) throw new Error("Failed to fetch unverified requirements");
	return res.json();
}

async function fetchHighRiskRequirements(
	projectId: string,
	limit = 100,
): Promise<{ specs: RequirementSpec[]; total: number }> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/requirements/high-risk?limit=${limit}`,
		{ headers: { "X-Bulk-Operation": "true", ...getAuthHeaders() } },
	);
	if (!res.ok) throw new Error("Failed to fetch high-risk requirements");
	return res.json();
}

async function createRequirementSpec(
	projectId: string,
	data: RequirementSpecCreate,
): Promise<RequirementSpec> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/requirements`,
		{
			method: "POST",
			headers: { "Content-Type": "application/json", ...getAuthHeaders() },
			body: JSON.stringify(data),
		},
	);
	if (!res.ok) throw new Error("Failed to create requirement spec");
	return res.json();
}

async function updateRequirementSpec(
	projectId: string,
	specId: string,
	data: RequirementSpecUpdate,
): Promise<RequirementSpec> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/requirements/${specId}`,
		{
			method: "PATCH",
			headers: { "Content-Type": "application/json", ...getAuthHeaders() },
			body: JSON.stringify(data),
		},
	);
	if (!res.ok) throw new Error("Failed to update requirement spec");
	return res.json();
}

async function deleteRequirementSpec(
	projectId: string,
	specId: string,
): Promise<void> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/requirements/${specId}`,
		{ method: "DELETE", headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to delete requirement spec");
}

async function analyzeRequirementQuality(
	projectId: string,
	specId: string,
): Promise<RequirementSpec> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/requirements/${specId}/analyze-quality`,
		{ method: "POST", headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to analyze requirement quality");
	return res.json();
}

async function analyzeRequirementImpact(
	projectId: string,
	specId: string,
): Promise<RequirementSpec> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/requirements/${specId}/analyze-impact`,
		{ method: "POST", headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to analyze requirement impact");
	return res.json();
}

async function verifyRequirement(
	projectId: string,
	specId: string,
	evidenceType: string,
	evidenceReference: string,
	description: string,
): Promise<RequirementSpec> {
	const params = new URLSearchParams({
		evidence_type: evidenceType,
		evidence_reference: evidenceReference,
		description,
	});
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/requirements/${specId}/verify?${params}`,
		{ method: "POST", headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to verify requirement");
	return res.json();
}

// Test Specs
async function fetchTestSpecs(
	projectId: string,
	options?: {
		testType?: TestType;
		isQuarantined?: boolean;
		limit?: number;
		offset?: number;
	},
): Promise<{ specs: TestSpec[]; total: number }> {
	const params = new URLSearchParams();
	if (options?.testType) params.append("test_type", options.testType);
	if (options?.isQuarantined !== undefined)
		params.append("is_quarantined", String(options.isQuarantined));
	if (options?.limit) params.append("limit", String(options.limit));
	if (options?.offset) params.append("offset", String(options.offset));

	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/tests?${params}`,
		{ headers: { "X-Bulk-Operation": "true", ...getAuthHeaders() } },
	);
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(`Failed to fetch test specs: ${res.status} ${errorText}`);
	}
	return res.json();
}

async function fetchTestSpec(
	projectId: string,
	specId: string,
): Promise<TestSpec> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/tests/${specId}`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to fetch test spec");
	return res.json();
}

async function fetchTestSpecByItem(
	projectId: string,
	itemId: string,
): Promise<TestSpec> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/tests/by-item/${itemId}`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to fetch test spec by item");
	return res.json();
}

async function fetchFlakyTests(
	projectId: string,
	threshold = 0.2,
	limit = 50,
): Promise<{ specs: TestSpec[]; total: number }> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/tests/flaky?threshold=${threshold}&limit=${limit}`,
		{ headers: { "X-Bulk-Operation": "true", ...getAuthHeaders() } },
	);
	if (!res.ok) throw new Error("Failed to fetch flaky tests");
	return res.json();
}

async function fetchQuarantinedTests(
	projectId: string,
	limit = 50,
): Promise<{ specs: TestSpec[]; total: number }> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/tests/quarantined?limit=${limit}`,
		{ headers: { "X-Bulk-Operation": "true", ...getAuthHeaders() } },
	);
	if (!res.ok) throw new Error("Failed to fetch quarantined tests");
	return res.json();
}

async function fetchTestHealthReport(projectId: string): Promise<{
	total_tests: number;
	flaky_count: number;
	quarantined_count: number;
	total_runs: number;
	pass_rate: number;
	average_duration_ms: number;
	health_score: number;
}> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/tests/health-report`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to fetch test health report");
	return res.json();
}

async function createTestSpec(
	projectId: string,
	data: TestSpecCreate,
): Promise<TestSpec> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/tests`,
		{
			method: "POST",
			headers: { "Content-Type": "application/json", ...getAuthHeaders() },
			body: JSON.stringify(data),
		},
	);
	if (!res.ok) throw new Error("Failed to create test spec");
	return res.json();
}

async function updateTestSpec(
	projectId: string,
	specId: string,
	data: TestSpecUpdate,
): Promise<TestSpec> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/tests/${specId}`,
		{
			method: "PATCH",
			headers: { "Content-Type": "application/json", ...getAuthHeaders() },
			body: JSON.stringify(data),
		},
	);
	if (!res.ok) throw new Error("Failed to update test spec");
	return res.json();
}

async function deleteTestSpec(
	projectId: string,
	specId: string,
): Promise<void> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/tests/${specId}`,
		{ method: "DELETE", headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to delete test spec");
}

async function recordTestRun(
	projectId: string,
	specId: string,
	status: TestResultStatus,
	durationMs: number,
	errorMessage?: string,
	environment?: string,
): Promise<TestSpec> {
	const params = new URLSearchParams({
		status,
		duration_ms: String(durationMs),
	});
	if (errorMessage) params.append("error_message", errorMessage);
	if (environment) params.append("environment", environment);

	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/tests/${specId}/record-run?${params}`,
		{ method: "POST", headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to record test run");
	return res.json();
}

async function quarantineTest(
	projectId: string,
	specId: string,
	reason: string,
): Promise<TestSpec> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/tests/${specId}/quarantine?reason=${encodeURIComponent(reason)}`,
		{ method: "POST", headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to quarantine test");
	return res.json();
}

async function unquarantineTest(
	projectId: string,
	specId: string,
): Promise<TestSpec> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/tests/${specId}/unquarantine`,
		{ method: "POST", headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to unquarantine test");
	return res.json();
}

// Epic Specs
async function fetchEpicSpecs(
	projectId: string,
	options?: {
		status?: EpicStatus;
		limit?: number;
		offset?: number;
	},
): Promise<{ specs: EpicSpec[]; total: number }> {
	const params = new URLSearchParams();
	if (options?.status) params.append("status", options.status);
	if (options?.limit) params.append("limit", String(options.limit));
	if (options?.offset) params.append("offset", String(options.offset));

	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/epics?${params}`,
		{ headers: { "X-Bulk-Operation": "true", ...getAuthHeaders() } },
	);
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(`Failed to fetch epic specs: ${res.status} ${errorText}`);
	}
	return res.json();
}

async function fetchEpicSpec(
	projectId: string,
	specId: string,
): Promise<EpicSpec> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/epics/${specId}`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to fetch epic spec");
	return res.json();
}

async function fetchEpicSpecByItem(
	projectId: string,
	itemId: string,
): Promise<EpicSpec> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/epics/by-item/${itemId}`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to fetch epic spec by item");
	return res.json();
}

async function createEpicSpec(
	projectId: string,
	data: EpicSpecCreate,
): Promise<EpicSpec> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/epics`,
		{
			method: "POST",
			headers: { "Content-Type": "application/json", ...getAuthHeaders() },
			body: JSON.stringify(data),
		},
	);
	if (!res.ok) throw new Error("Failed to create epic spec");
	return res.json();
}

async function updateEpicSpec(
	projectId: string,
	specId: string,
	data: EpicSpecUpdate,
): Promise<EpicSpec> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/epics/${specId}`,
		{
			method: "PATCH",
			headers: { "Content-Type": "application/json", ...getAuthHeaders() },
			body: JSON.stringify(data),
		},
	);
	if (!res.ok) throw new Error("Failed to update epic spec");
	return res.json();
}

async function deleteEpicSpec(
	projectId: string,
	specId: string,
): Promise<void> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/epics/${specId}`,
		{ method: "DELETE", headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to delete epic spec");
}

// User Story Specs
async function fetchUserStorySpecs(
	projectId: string,
	options?: {
		status?: UserStoryStatus;
		epicId?: string;
		limit?: number;
		offset?: number;
	},
): Promise<{ specs: UserStorySpec[]; total: number }> {
	const params = new URLSearchParams();
	if (options?.status) params.append("status", options.status);
	if (options?.epicId) params.append("epic_id", options.epicId);
	if (options?.limit) params.append("limit", String(options.limit));
	if (options?.offset) params.append("offset", String(options.offset));

	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/user-stories?${params}`,
		{ headers: { "X-Bulk-Operation": "true", ...getAuthHeaders() } },
	);
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(
			`Failed to fetch user story specs: ${res.status} ${errorText}`,
		);
	}
	return res.json();
}

async function fetchUserStorySpec(
	projectId: string,
	specId: string,
): Promise<UserStorySpec> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/user-stories/${specId}`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to fetch user story spec");
	return res.json();
}

async function fetchUserStorySpecByItem(
	projectId: string,
	itemId: string,
): Promise<UserStorySpec> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/user-stories/by-item/${itemId}`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to fetch user story spec by item");
	return res.json();
}

async function createUserStorySpec(
	projectId: string,
	data: UserStorySpecCreate,
): Promise<UserStorySpec> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/user-stories`,
		{
			method: "POST",
			headers: { "Content-Type": "application/json", ...getAuthHeaders() },
			body: JSON.stringify(data),
		},
	);
	if (!res.ok) throw new Error("Failed to create user story spec");
	return res.json();
}

async function updateUserStorySpec(
	projectId: string,
	specId: string,
	data: UserStorySpecUpdate,
): Promise<UserStorySpec> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/user-stories/${specId}`,
		{
			method: "PATCH",
			headers: { "Content-Type": "application/json", ...getAuthHeaders() },
			body: JSON.stringify(data),
		},
	);
	if (!res.ok) throw new Error("Failed to update user story spec");
	return res.json();
}

async function deleteUserStorySpec(
	projectId: string,
	specId: string,
): Promise<void> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/user-stories/${specId}`,
		{ method: "DELETE", headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to delete user story spec");
}

// Task Specs
async function fetchTaskSpecs(
	projectId: string,
	options?: {
		status?: TaskStatus;
		storyId?: string;
		limit?: number;
		offset?: number;
	},
): Promise<{ specs: TaskSpec[]; total: number }> {
	const params = new URLSearchParams();
	if (options?.status) params.append("status", options.status);
	if (options?.storyId) params.append("story_id", options.storyId);
	if (options?.limit) params.append("limit", String(options.limit));
	if (options?.offset) params.append("offset", String(options.offset));

	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/tasks?${params}`,
		{ headers: { "X-Bulk-Operation": "true", ...getAuthHeaders() } },
	);
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(`Failed to fetch task specs: ${res.status} ${errorText}`);
	}
	return res.json();
}

async function fetchTaskSpec(
	projectId: string,
	specId: string,
): Promise<TaskSpec> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/tasks/${specId}`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to fetch task spec");
	return res.json();
}

async function fetchTaskSpecByItem(
	projectId: string,
	itemId: string,
): Promise<TaskSpec> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/tasks/by-item/${itemId}`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to fetch task spec by item");
	return res.json();
}

async function createTaskSpec(
	projectId: string,
	data: TaskSpecCreate,
): Promise<TaskSpec> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/tasks`,
		{
			method: "POST",
			headers: { "Content-Type": "application/json", ...getAuthHeaders() },
			body: JSON.stringify(data),
		},
	);
	if (!res.ok) throw new Error("Failed to create task spec");
	return res.json();
}

async function updateTaskSpec(
	projectId: string,
	specId: string,
	data: TaskSpecUpdate,
): Promise<TaskSpec> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/tasks/${specId}`,
		{
			method: "PATCH",
			headers: { "Content-Type": "application/json", ...getAuthHeaders() },
			body: JSON.stringify(data),
		},
	);
	if (!res.ok) throw new Error("Failed to update task spec");
	return res.json();
}

async function deleteTaskSpec(
	projectId: string,
	specId: string,
): Promise<void> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/tasks/${specId}`,
		{ method: "DELETE", headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to delete task spec");
}

// Defect Specs
async function fetchDefectSpecs(
	projectId: string,
	options?: {
		severity?: DefectSeverity;
		status?: DefectStatus;
		limit?: number;
		offset?: number;
	},
): Promise<{ specs: DefectSpec[]; total: number }> {
	const params = new URLSearchParams();
	if (options?.severity) params.append("severity", options.severity);
	if (options?.status) params.append("status", options.status);
	if (options?.limit) params.append("limit", String(options.limit));
	if (options?.offset) params.append("offset", String(options.offset));

	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/defects?${params}`,
		{ headers: { "X-Bulk-Operation": "true", ...getAuthHeaders() } },
	);
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(`Failed to fetch defect specs: ${res.status} ${errorText}`);
	}
	return res.json();
}

async function fetchDefectSpec(
	projectId: string,
	specId: string,
): Promise<DefectSpec> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/defects/${specId}`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to fetch defect spec");
	return res.json();
}

async function fetchDefectSpecByItem(
	projectId: string,
	itemId: string,
): Promise<DefectSpec> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/defects/by-item/${itemId}`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to fetch defect spec by item");
	return res.json();
}

async function createDefectSpec(
	projectId: string,
	data: DefectSpecCreate,
): Promise<DefectSpec> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/defects`,
		{
			method: "POST",
			headers: { "Content-Type": "application/json", ...getAuthHeaders() },
			body: JSON.stringify(data),
		},
	);
	if (!res.ok) throw new Error("Failed to create defect spec");
	return res.json();
}

async function updateDefectSpec(
	projectId: string,
	specId: string,
	data: DefectSpecUpdate,
): Promise<DefectSpec> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/defects/${specId}`,
		{
			method: "PATCH",
			headers: { "Content-Type": "application/json", ...getAuthHeaders() },
			body: JSON.stringify(data),
		},
	);
	if (!res.ok) throw new Error("Failed to update defect spec");
	return res.json();
}

async function deleteDefectSpec(
	projectId: string,
	specId: string,
): Promise<void> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/item-specs/defects/${specId}`,
		{ method: "DELETE", headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to delete defect spec");
}

// =============================================================================
// React Query Hooks - Requirement Specs
// =============================================================================

export function useRequirementSpecs(
	projectId: string,
	options?: {
		requirementType?: RequirementType;
		riskLevel?: RiskLevel;
		verificationStatus?: VerificationStatus;
		limit?: number;
		offset?: number;
	},
) {
	return useQuery({
		queryKey: [...itemSpecKeys.requirements(projectId), options],
		queryFn: () => fetchRequirementSpecs(projectId, options),
		enabled: !!projectId,
	});
}

export function useRequirementSpec(projectId: string, specId: string) {
	return useQuery({
		queryKey: itemSpecKeys.requirement(projectId, specId),
		queryFn: () => fetchRequirementSpec(projectId, specId),
		enabled: !!projectId && !!specId,
	});
}

export function useRequirementSpecByItem(projectId: string, itemId: string) {
	return useQuery({
		queryKey: itemSpecKeys.requirementByItem(projectId, itemId),
		queryFn: () => fetchRequirementSpecByItem(projectId, itemId),
		enabled: !!projectId && !!itemId,
	});
}

export function useUnverifiedRequirements(projectId: string, limit = 100) {
	return useQuery({
		queryKey: itemSpecKeys.unverifiedRequirements(projectId),
		queryFn: () => fetchUnverifiedRequirements(projectId, limit),
		enabled: !!projectId,
	});
}

export function useHighRiskRequirements(projectId: string, limit = 100) {
	return useQuery({
		queryKey: itemSpecKeys.highRiskRequirements(projectId),
		queryFn: () => fetchHighRiskRequirements(projectId, limit),
		enabled: !!projectId,
	});
}

export function useCreateRequirementSpec(projectId: string) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (data: RequirementSpecCreate) =>
			createRequirementSpec(projectId, data),
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.requirements(projectId),
			});
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.stats(projectId),
			});
		},
	});
}

export function useUpdateRequirementSpec(projectId: string) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({
			specId,
			data,
		}: {
			specId: string;
			data: RequirementSpecUpdate;
		}) => updateRequirementSpec(projectId, specId, data),
		onSuccess: (data) => {
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.requirements(projectId),
			});
			queryClient.setQueryData(
				itemSpecKeys.requirement(projectId, data.id),
				data,
			);
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.requirementByItem(projectId, data.item_id),
			});
		},
	});
}

export function useDeleteRequirementSpec(projectId: string) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (specId: string) => deleteRequirementSpec(projectId, specId),
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.requirements(projectId),
			});
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.stats(projectId),
			});
		},
	});
}

export function useAnalyzeRequirementQuality(projectId: string) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (specId: string) =>
			analyzeRequirementQuality(projectId, specId),
		onSuccess: (data) => {
			queryClient.setQueryData(
				itemSpecKeys.requirement(projectId, data.id),
				data,
			);
		},
	});
}

export function useAnalyzeRequirementImpact(projectId: string) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (specId: string) => analyzeRequirementImpact(projectId, specId),
		onSuccess: (data) => {
			queryClient.setQueryData(
				itemSpecKeys.requirement(projectId, data.id),
				data,
			);
		},
	});
}

export function useVerifyRequirement(projectId: string) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({
			specId,
			evidenceType,
			evidenceReference,
			description,
		}: {
			specId: string;
			evidenceType: string;
			evidenceReference: string;
			description: string;
		}) =>
			verifyRequirement(
				projectId,
				specId,
				evidenceType,
				evidenceReference,
				description,
			),
		onSuccess: (data) => {
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.requirements(projectId),
			});
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.unverifiedRequirements(projectId),
			});
			queryClient.setQueryData(
				itemSpecKeys.requirement(projectId, data.id),
				data,
			);
		},
	});
}

// =============================================================================
// React Query Hooks - Test Specs
// =============================================================================

export function useTestSpecs(
	projectId: string,
	options?: {
		testType?: TestType;
		isQuarantined?: boolean;
		limit?: number;
		offset?: number;
	},
) {
	return useQuery({
		queryKey: [...itemSpecKeys.tests(projectId), options],
		queryFn: () => fetchTestSpecs(projectId, options),
		enabled: !!projectId,
	});
}

export function useTestSpec(projectId: string, specId: string) {
	return useQuery({
		queryKey: itemSpecKeys.test(projectId, specId),
		queryFn: () => fetchTestSpec(projectId, specId),
		enabled: !!projectId && !!specId,
	});
}

export function useTestSpecByItem(projectId: string, itemId: string) {
	return useQuery({
		queryKey: itemSpecKeys.testByItem(projectId, itemId),
		queryFn: () => fetchTestSpecByItem(projectId, itemId),
		enabled: !!projectId && !!itemId,
	});
}

export function useFlakyTests(projectId: string, threshold = 0.2, limit = 50) {
	return useQuery({
		queryKey: [...itemSpecKeys.flakyTests(projectId), threshold],
		queryFn: () => fetchFlakyTests(projectId, threshold, limit),
		enabled: !!projectId,
	});
}

export function useQuarantinedTests(projectId: string, limit = 50) {
	return useQuery({
		queryKey: itemSpecKeys.quarantinedTests(projectId),
		queryFn: () => fetchQuarantinedTests(projectId, limit),
		enabled: !!projectId,
	});
}

export function useTestHealthReport(projectId: string) {
	return useQuery({
		queryKey: itemSpecKeys.testHealthReport(projectId),
		queryFn: () => fetchTestHealthReport(projectId),
		enabled: !!projectId,
	});
}

export function useCreateTestSpec(projectId: string) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (data: TestSpecCreate) => createTestSpec(projectId, data),
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.tests(projectId),
			});
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.testHealthReport(projectId),
			});
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.stats(projectId),
			});
		},
	});
}

export function useUpdateTestSpec(projectId: string) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({ specId, data }: { specId: string; data: TestSpecUpdate }) =>
			updateTestSpec(projectId, specId, data),
		onSuccess: (data) => {
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.tests(projectId),
			});
			queryClient.setQueryData(itemSpecKeys.test(projectId, data.id), data);
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.testByItem(projectId, data.item_id),
			});
		},
	});
}

export function useDeleteTestSpec(projectId: string) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (specId: string) => deleteTestSpec(projectId, specId),
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.tests(projectId),
			});
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.testHealthReport(projectId),
			});
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.stats(projectId),
			});
		},
	});
}

export function useRecordTestRun(projectId: string) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({
			specId,
			status,
			durationMs,
			errorMessage,
			environment,
		}: {
			specId: string;
			status: TestResultStatus;
			durationMs: number;
			errorMessage?: string;
			environment?: string;
		}) =>
			recordTestRun(
				projectId,
				specId,
				status,
				durationMs,
				errorMessage,
				environment,
			),
		onSuccess: (data) => {
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.tests(projectId),
			});
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.flakyTests(projectId),
			});
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.testHealthReport(projectId),
			});
			queryClient.setQueryData(itemSpecKeys.test(projectId, data.id), data);
		},
	});
}

export function useQuarantineTest(projectId: string) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({ specId, reason }: { specId: string; reason: string }) =>
			quarantineTest(projectId, specId, reason),
		onSuccess: (data) => {
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.tests(projectId),
			});
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.quarantinedTests(projectId),
			});
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.testHealthReport(projectId),
			});
			queryClient.setQueryData(itemSpecKeys.test(projectId, data.id), data);
		},
	});
}

export function useUnquarantineTest(projectId: string) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (specId: string) => unquarantineTest(projectId, specId),
		onSuccess: (data) => {
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.tests(projectId),
			});
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.quarantinedTests(projectId),
			});
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.testHealthReport(projectId),
			});
			queryClient.setQueryData(itemSpecKeys.test(projectId, data.id), data);
		},
	});
}

// =============================================================================
// React Query Hooks - Epic Specs
// =============================================================================

export function useEpicSpecs(
	projectId: string,
	options?: {
		status?: EpicStatus;
		limit?: number;
		offset?: number;
	},
) {
	return useQuery({
		queryKey: [...itemSpecKeys.epics(projectId), options],
		queryFn: () => fetchEpicSpecs(projectId, options),
		enabled: !!projectId,
	});
}

export function useEpicSpec(projectId: string, specId: string) {
	return useQuery({
		queryKey: itemSpecKeys.epic(projectId, specId),
		queryFn: () => fetchEpicSpec(projectId, specId),
		enabled: !!projectId && !!specId,
	});
}

export function useEpicSpecByItem(projectId: string, itemId: string) {
	return useQuery({
		queryKey: itemSpecKeys.epicByItem(projectId, itemId),
		queryFn: () => fetchEpicSpecByItem(projectId, itemId),
		enabled: !!projectId && !!itemId,
	});
}

export function useCreateEpicSpec(projectId: string) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (data: EpicSpecCreate) => createEpicSpec(projectId, data),
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.epics(projectId),
			});
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.stats(projectId),
			});
		},
	});
}

export function useUpdateEpicSpec(projectId: string) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({ specId, data }: { specId: string; data: EpicSpecUpdate }) =>
			updateEpicSpec(projectId, specId, data),
		onSuccess: (data) => {
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.epics(projectId),
			});
			queryClient.setQueryData(itemSpecKeys.epic(projectId, data.id), data);
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.epicByItem(projectId, data.item_id),
			});
		},
	});
}

export function useDeleteEpicSpec(projectId: string) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (specId: string) => deleteEpicSpec(projectId, specId),
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.epics(projectId),
			});
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.stats(projectId),
			});
		},
	});
}

// =============================================================================
// React Query Hooks - User Story Specs
// =============================================================================

export function useUserStorySpecs(
	projectId: string,
	options?: {
		status?: UserStoryStatus;
		epicId?: string;
		limit?: number;
		offset?: number;
	},
) {
	return useQuery({
		queryKey: [...itemSpecKeys.userStories(projectId), options],
		queryFn: () => fetchUserStorySpecs(projectId, options),
		enabled: !!projectId,
	});
}

export function useUserStorySpec(projectId: string, specId: string) {
	return useQuery({
		queryKey: itemSpecKeys.userStory(projectId, specId),
		queryFn: () => fetchUserStorySpec(projectId, specId),
		enabled: !!projectId && !!specId,
	});
}

export function useUserStorySpecByItem(projectId: string, itemId: string) {
	return useQuery({
		queryKey: itemSpecKeys.userStoryByItem(projectId, itemId),
		queryFn: () => fetchUserStorySpecByItem(projectId, itemId),
		enabled: !!projectId && !!itemId,
	});
}

export function useCreateUserStorySpec(projectId: string) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (data: UserStorySpecCreate) =>
			createUserStorySpec(projectId, data),
		onSuccess: (_, variables) => {
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.userStories(projectId),
			});
			if (variables.parent_epic) {
				queryClient.invalidateQueries({
					queryKey: itemSpecKeys.userStoriesByEpic(
						projectId,
						variables.parent_epic,
					),
				});
			}
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.stats(projectId),
			});
		},
	});
}

export function useUpdateUserStorySpec(projectId: string) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({
			specId,
			data,
		}: {
			specId: string;
			data: UserStorySpecUpdate;
		}) => updateUserStorySpec(projectId, specId, data),
		onSuccess: (data) => {
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.userStories(projectId),
			});
			queryClient.setQueryData(
				itemSpecKeys.userStory(projectId, data.id),
				data,
			);
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.userStoryByItem(projectId, data.item_id),
			});
		},
	});
}

export function useDeleteUserStorySpec(projectId: string) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (specId: string) => deleteUserStorySpec(projectId, specId),
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.userStories(projectId),
			});
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.stats(projectId),
			});
		},
	});
}

// =============================================================================
// React Query Hooks - Task Specs
// =============================================================================

export function useTaskSpecs(
	projectId: string,
	options?: {
		status?: TaskStatus;
		storyId?: string;
		limit?: number;
		offset?: number;
	},
) {
	return useQuery({
		queryKey: [...itemSpecKeys.tasks(projectId), options],
		queryFn: () => fetchTaskSpecs(projectId, options),
		enabled: !!projectId,
	});
}

export function useTaskSpec(projectId: string, specId: string) {
	return useQuery({
		queryKey: itemSpecKeys.task(projectId, specId),
		queryFn: () => fetchTaskSpec(projectId, specId),
		enabled: !!projectId && !!specId,
	});
}

export function useTaskSpecByItem(projectId: string, itemId: string) {
	return useQuery({
		queryKey: itemSpecKeys.taskByItem(projectId, itemId),
		queryFn: () => fetchTaskSpecByItem(projectId, itemId),
		enabled: !!projectId && !!itemId,
	});
}

export function useCreateTaskSpec(projectId: string) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (data: TaskSpecCreate) => createTaskSpec(projectId, data),
		onSuccess: (_, variables) => {
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.tasks(projectId),
			});
			if (variables.parent_story) {
				queryClient.invalidateQueries({
					queryKey: itemSpecKeys.tasksByStory(
						projectId,
						variables.parent_story,
					),
				});
			}
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.stats(projectId),
			});
		},
	});
}

export function useUpdateTaskSpec(projectId: string) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({ specId, data }: { specId: string; data: TaskSpecUpdate }) =>
			updateTaskSpec(projectId, specId, data),
		onSuccess: (data) => {
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.tasks(projectId),
			});
			queryClient.setQueryData(itemSpecKeys.task(projectId, data.id), data);
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.taskByItem(projectId, data.item_id),
			});
		},
	});
}

export function useDeleteTaskSpec(projectId: string) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (specId: string) => deleteTaskSpec(projectId, specId),
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.tasks(projectId),
			});
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.stats(projectId),
			});
		},
	});
}

// =============================================================================
// React Query Hooks - Defect Specs
// =============================================================================

export function useDefectSpecs(
	projectId: string,
	options?: {
		severity?: DefectSeverity;
		status?: DefectStatus;
		limit?: number;
		offset?: number;
	},
) {
	return useQuery({
		queryKey: [...itemSpecKeys.defects(projectId), options],
		queryFn: () => fetchDefectSpecs(projectId, options),
		enabled: !!projectId,
	});
}

export function useDefectSpec(projectId: string, specId: string) {
	return useQuery({
		queryKey: itemSpecKeys.defect(projectId, specId),
		queryFn: () => fetchDefectSpec(projectId, specId),
		enabled: !!projectId && !!specId,
	});
}

export function useDefectSpecByItem(projectId: string, itemId: string) {
	return useQuery({
		queryKey: itemSpecKeys.defectByItem(projectId, itemId),
		queryFn: () => fetchDefectSpecByItem(projectId, itemId),
		enabled: !!projectId && !!itemId,
	});
}

export function useCreateDefectSpec(projectId: string) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (data: DefectSpecCreate) => createDefectSpec(projectId, data),
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.defects(projectId),
			});
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.stats(projectId),
			});
		},
	});
}

export function useUpdateDefectSpec(projectId: string) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({
			specId,
			data,
		}: {
			specId: string;
			data: DefectSpecUpdate;
		}) => updateDefectSpec(projectId, specId, data),
		onSuccess: (data) => {
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.defects(projectId),
			});
			queryClient.setQueryData(itemSpecKeys.defect(projectId, data.id), data);
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.defectByItem(projectId, data.item_id),
			});
		},
	});
}

export function useDeleteDefectSpec(projectId: string) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (specId: string) => deleteDefectSpec(projectId, specId),
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.defects(projectId),
			});
			queryClient.invalidateQueries({
				queryKey: itemSpecKeys.stats(projectId),
			});
		},
	});
}
