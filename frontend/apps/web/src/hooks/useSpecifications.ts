import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { logger } from '@/lib/logger';
import type {
	ADR,
	ADRActivity,
	ADRStats,
	ADRStatus,
	Contract,
	ContractActivity,
	ContractStats,
	ContractStatus,
	ContractType,
	Feature,
	FeatureActivity,
	FeatureStats,
	FeatureStatus,
	Scenario,
	ScenarioActivity,
	ScenarioStatus,
	ScenarioStep,
	SpecificationSummary,
} from "@tracertm/types";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:4000";

// Helper to get auth token for fetch requests (object so it can be spread into headers)
function getAuthHeaders(): Record<string, string> {
	const token =
		typeof localStorage !== "undefined"
			? localStorage.getItem("auth_token")
			: null;
	const headers: Record<string, string> = {};
	if (token) {
		headers["Authorization"] = `Bearer ${token}`;
	}
	return headers;
}

// =============================================================================
// Transform Functions
// =============================================================================

function transformADR(data: Record<string, unknown>): ADR {
	return {
		id: data['id'],
		projectId: data['project_id'],
		adrNumber: data['adr_number'],
		title: data['title'],
		status: data.status,
		context: data['context'],
		decision: data['decision'],
		consequences: data['consequences'],
		decisionDrivers: data['decision_drivers'],
		consideredOptions: data['considered_options'],
		relatedRequirements: data['related_requirements'],
		relatedAdrs: data['related_adrs'],
		supersededBy: data['superseded_by'],
		supersedes: data['supersedes'],
		complianceScore: data['compliance_score'],
		lastVerifiedAt: data['last_verified_at'],
		verificationNotes: data['verification_notes'],
		deciders: data['deciders'],
		stakeholders: data['stakeholders'],
		date: data['date'],
		tags: data['tags'],
		metadata: data['metadata'],
		version: data['version'],
		createdAt: data['created_at'],
		updatedAt: data['updated_at'],
	};
}

function transformContract(data: Record<string, unknown>): Contract {
	return {
		id: data['id'],
		projectId: data['project_id'],
		itemId: data['item_id'],
		contractNumber: data['contract_number'],
		title: data['title'],
		description: data['description'],
		contractType: data['contract_type'],
		status: data.status,
		preconditions: data['preconditions'],
		postconditions: data['postconditions'],
		invariants: data['invariants'],
		states: data['states'],
		initialState: data['initial_state'],
		transitions: data['transitions'],
		executableSpec: data['executable_spec'],
		specLanguage: data['spec_language'],
		lastVerifiedAt: data['last_verified_at'],
		verificationResult: data['verification_result'],
		tags: data['tags'],
		metadata: data['metadata'],
		version: data['version'],
		createdAt: data['created_at'],
		updatedAt: data['updated_at'],
	};
}

function transformFeature(data: Record<string, unknown>): Feature {
	return {
		id: data['id'],
		projectId: data['project_id'],
		featureNumber: data['feature_number'],
		name: data.name,
		description: data['description'],
		asA: data['as_a'],
		iWant: data['i_want'],
		soThat: data['so_that'],
		status: data.status,
		filePath: data['file_path'],
		tags: data['tags'],
		scenarioCount: data['scenario_count'] || 0,
		passedScenarios: data['passed_scenarios'] || 0,
		failedScenarios: data['failed_scenarios'] || 0,
		pendingScenarios: data['pending_scenarios'] || 0,
		relatedRequirements: data['related_requirements'],
		relatedAdrs: data['related_adrs'],
		metadata: data['metadata'],
		version: data['version'],
		createdAt: data['created_at'],
		updatedAt: data['updated_at'],
	};
}

function transformScenario(data: Record<string, unknown>): Scenario {
	return {
		id: data['id'],
		featureId: data['feature_id'],
		scenarioNumber: data['scenario_number'],
		title: data['title'],
		description: data['description'],
		gherkinText: data['gherkin_text'],
		background: data['background'],
		givenSteps: data['given_steps'] || [],
		whenSteps: data['when_steps'] || [],
		thenSteps: data['then_steps'] || [],
		isOutline: data['is_outline'] || false,
		examples: data['examples'],
		tags: data['tags'],
		requirementIds: data['requirement_ids'],
		testCaseIds: data['test_case_ids'],
		status: data.status,
		lastRunAt: data['last_run_at'],
		lastRunResult: data['last_run_result'],
		lastRunDurationMs: data['last_run_duration_ms'],
		executionCount: data['execution_count'] || 0,
		passRate: data['pass_rate'] || 0,
		metadata: data['metadata'],
		version: data['version'],
		createdAt: data['created_at'],
		updatedAt: data['updated_at'],
	};
}

// =============================================================================
// API Fetch Functions - ADRs
// =============================================================================

interface ADRFilters {
	projectId: string;
	status?: ADRStatus;
	search?: string;
	tags?: string[];
}

async function fetchADRs(
	filters: ADRFilters,
): Promise<{ adrs: ADR[]; total: number }> {
	const params = new URLSearchParams();
	params.set("project_id", filters.projectId);
	if (filters.status) params.set("status", filters.status);
	if (filters.search) params.set("search", filters.search);
	if (filters.tags?.length) params.set("tags", filters.tags.join(","));

	const res = await fetch(`${API_URL}/api/v1/adrs?${params}`, {
		headers: { "X-Bulk-Operation": "true", ...getAuthHeaders() },
	});
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(`Failed to fetch ADRs: ${res.status} ${errorText}`);
	}
	const data = await res.json();
	return {
		adrs: (data['adrs'] || []).map(transformADR),
		total: data['total'] || 0,
	};
}

async function fetchADR(id: string): Promise<ADR> {
	const res = await fetch(`${API_URL}/api/v1/adrs/${id}`, {
		headers: getAuthHeaders(),
	});
	if (!res.ok) throw new Error("Failed to fetch ADR");
	const data = await res.json();
	return transformADR(data);
}

interface CreateADRData {
	projectId: string;
	title: string;
	context: string;
	decision: string;
	consequences: string;
	decisionDrivers?: string[];
	deciders?: string[];
	stakeholders?: string[];
	tags?: string[];
	metadata?: Record<string, unknown>;
}

async function createADR(
	data: CreateADRData,
): Promise<{ id: string; adrNumber: string }> {
	const res = await fetch(`${API_URL}/api/v1/adrs`, {
		method: "POST",
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		body: JSON.stringify({
			project_id: data['projectId'],
			title: data['title'],
			context: data['context'],
			decision: data['decision'],
			consequences: data['consequences'],
			decision_drivers: data['decisionDrivers'],
			deciders: data['deciders'],
			stakeholders: data['stakeholders'],
			tags: data['tags'],
			metadata: data['metadata'] || {},
		}),
	});
	if (!res.ok) throw new Error("Failed to create ADR");
	const result = await res.json();
	return { id: result['id'], adrNumber: result['adr_number'] };
}

interface UpdateADRData {
	title?: string;
	context?: string;
	decision?: string;
	consequences?: string;
	status?: ADRStatus;
	decisionDrivers?: string[];
	deciders?: string[];
	stakeholders?: string[];
	tags?: string[];
	metadata?: Record<string, unknown>;
}

async function updateADR(
	id: string,
	data: UpdateADRData,
): Promise<{ id: string; version: number }> {
	const body: Record<string, unknown> = {};
	if (data['title'] !== undefined) body['title'] = data['title'];
	if (data['context'] !== undefined) body['context'] = data['context'];
	if (data['decision'] !== undefined) body['decision'] = data['decision'];
	if (data['consequences'] !== undefined) body['consequences'] = data['consequences'];
	if (data.status !== undefined) body.status = data.status;
	if (data['decisionDrivers'] !== undefined)
		body['decision_drivers'] = data['decisionDrivers'];
	if (data['deciders'] !== undefined) body['deciders'] = data['deciders'];
	if (data['stakeholders'] !== undefined) body['stakeholders'] = data['stakeholders'];
	if (data['tags'] !== undefined) body['tags'] = data['tags'];
	if (data['metadata'] !== undefined) body['metadata'] = data['metadata'];

	const res = await fetch(`${API_URL}/api/v1/adrs/${id}`, {
		method: "PATCH",
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		body: JSON.stringify(body),
	});
	if (!res.ok) throw new Error("Failed to update ADR");
	return res.json();
}

async function deleteADR(id: string): Promise<void> {
	const res = await fetch(`${API_URL}/api/v1/adrs/${id}`, {
		method: "DELETE",
		headers: getAuthHeaders(),
	});
	if (!res.ok) throw new Error("Failed to delete ADR");
}

async function verifyADR(
	id: string,
	notes: string,
): Promise<{ id: string; complianceScore: number; lastVerifiedAt: string }> {
	const res = await fetch(`${API_URL}/api/v1/adrs/${id}/verify`, {
		method: "POST",
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		body: JSON.stringify({ verification_notes: notes }),
	});
	if (!res.ok) throw new Error("Failed to verify ADR");
	const result = await res.json();
	return {
		id: result['id'],
		complianceScore: result['compliance_score'],
		lastVerifiedAt: result['last_verified_at'],
	};
}

async function fetchADRActivities(adrId: string): Promise<ADRActivity[]> {
	const res = await fetch(`${API_URL}/api/v1/adrs/${adrId}/activities`, {
		headers: getAuthHeaders(),
	});
	if (!res.ok) throw new Error("Failed to fetch ADR activities");
	const data = await res.json();
	return (data['activities'] || []).map((a: Record<string, unknown>) => ({
		id: a.id,
		adrId: a.adr_id,
		activityType: a.activity_type,
		fromValue: a.from_value,
		toValue: a.to_value,
		description: a.description,
		performedBy: a.performed_by,
		createdAt: a.created_at,
	}));
}

async function fetchContractActivities(
	contractId: string,
): Promise<ContractActivity[]> {
	const res = await fetch(
		`${API_URL}/api/v1/contracts/${contractId}/activities`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to fetch contract activities");
	const data = await res.json();
	return (data['activities'] || []).map((a: Record<string, unknown>) => ({
		id: a.id,
		contractId: a.contract_id,
		activityType: a.activity_type,
		fromValue: a.from_value,
		toValue: a.to_value,
		description: a.description,
		performedBy: a.performed_by,
		createdAt: a.created_at,
	}));
}

async function fetchFeatureActivities(
	featureId: string,
): Promise<FeatureActivity[]> {
	const res = await fetch(`${API_URL}/api/v1/features/${featureId}/activities`, {
		headers: getAuthHeaders(),
	});
	if (!res.ok) throw new Error("Failed to fetch feature activities");
	const data = await res.json();
	return (data['activities'] || []).map((a: Record<string, unknown>) => ({
		id: a.id,
		featureId: a.feature_id,
		activityType: a.activity_type,
		fromValue: a.from_value,
		toValue: a.to_value,
		description: a.description,
		performedBy: a.performed_by,
		createdAt: a.created_at,
	}));
}

async function fetchScenarioActivities(
	scenarioId: string,
	options: { limit?: number; offset?: number } = {},
): Promise<{ activities: ScenarioActivity[]; total: number }> {
	const params = new URLSearchParams();
	if (options.limit !== undefined) params.set("limit", String(options.limit));
	if (options.offset !== undefined)
		params.set("offset", String(options.offset));
	const res = await fetch(
		`${API_URL}/api/v1/specifications/scenarios/${scenarioId}/activities?${params}`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to fetch scenario activities");
	const data = await res.json();
	return {
		activities: (data['activities'] || []).map((a: Record<string, unknown>) => ({
			id: a.id,
			scenarioId: a.scenario_id,
			activityType: a.activity_type,
			fromValue: a.from_value,
			toValue: a.to_value,
			description: a.description,
			performedBy: a.performed_by,
			createdAt: a.created_at,
		})),
		total: data['total'] || 0,
	};
}

async function fetchProjectScenarios(
	projectId: string,
	status?: string,
): Promise<{ scenarios: Scenario[]; total: number }> {
	const params = new URLSearchParams();
	if (status) params.set("status", status);
	const res = await fetch(
		`${API_URL}/api/v1/specifications/projects/${projectId}/scenarios?${params}`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(`Failed to fetch scenarios: ${res.status} ${errorText}`);
	}
	const data = await res.json();
	return {
		scenarios: (data['scenarios'] || []).map(transformScenario),
		total: data['total'] || 0,
	};
}

async function fetchProjectScenarioActivities(
	projectId: string,
	options: {
		limit?: number;
		offset?: number;
		eventType?: string;
		since?: string;
		until?: string;
	} = {},
): Promise<ScenarioActivity[]> {
	const params = new URLSearchParams();
	if (options.limit !== undefined) params.set("limit", String(options.limit));
	if (options.offset !== undefined)
		params.set("offset", String(options.offset));
	if (options.eventType) params.set("event_type", options.eventType);
	if (options.since) params.set("since", options.since);
	if (options.until) params.set("until", options.until);
	const res = await fetch(
		`${API_URL}/api/v1/specifications/projects/${projectId}/scenarios/activities?${params}`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to fetch scenario activities");
	const data = await res.json();
	return (data['activities'] || []).map((a: Record<string, unknown>) => ({
		id: a.id,
		scenarioId: a.scenario_id,
		activityType: a.activity_type,
		fromValue: a.from_value,
		toValue: a.to_value,
		description: a.description,
		performedBy: a.performed_by,
		createdAt: a.created_at,
	}));
}

async function fetchADRStats(projectId: string): Promise<ADRStats> {
	const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/adrs/stats`, {
		headers: getAuthHeaders(),
	});
	if (!res.ok) throw new Error("Failed to fetch ADR stats");
	const data = await res.json();
	return {
		projectId: data['project_id'],
		total: data['total'] || 0,
		byStatus: data['by_status'] || {},
		averageComplianceScore: data['average_compliance_score'] || 0,
		requirementsLinked: data['requirements_linked'] || 0,
		pendingVerification: data['pending_verification'] || 0,
	};
}

// =============================================================================
// API Fetch Functions - Contracts
// =============================================================================

interface ContractFilters {
	projectId: string;
	status?: ContractStatus;
	contractType?: ContractType;
	search?: string;
}

async function fetchContracts(
	filters: ContractFilters,
): Promise<{ contracts: Contract[]; total: number }> {
	const params = new URLSearchParams();
	params.set("project_id", filters.projectId);
	if (filters.status) params.set("status", filters.status);
	if (filters.contractType) params.set("contract_type", filters.contractType);
	if (filters.search) params.set("search", filters.search);

	const res = await fetch(`${API_URL}/api/v1/contracts?${params}`, {
		headers: { "X-Bulk-Operation": "true", ...getAuthHeaders() },
	});
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(`Failed to fetch contracts: ${res.status} ${errorText}`);
	}
	const data = await res.json();
	return {
		contracts: (data['contracts'] || []).map(transformContract),
		total: data['total'] || 0,
	};
}

async function fetchContract(id: string): Promise<Contract> {
	const res = await fetch(`${API_URL}/api/v1/contracts/${id}`, {
		headers: getAuthHeaders(),
	});
	if (!res.ok) throw new Error("Failed to fetch contract");
	const data = await res.json();
	return transformContract(data);
}

interface CreateContractData {
	projectId: string;
	itemId: string;
	title: string;
	description?: string;
	contractType: ContractType;
	preconditions: any[];
	postconditions: any[];
	invariants: any[];
	tags?: string[];
	metadata?: Record<string, unknown>;
}

async function createContract(
	data: CreateContractData,
): Promise<{ id: string; contractNumber: string }> {
	const res = await fetch(`${API_URL}/api/v1/contracts`, {
		method: "POST",
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		body: JSON.stringify({
			project_id: data['projectId'],
			item_id: data['itemId'],
			title: data['title'],
			description: data['description'],
			contract_type: data['contractType'],
			preconditions: data['preconditions'],
			postconditions: data['postconditions'],
			invariants: data['invariants'],
			tags: data['tags'],
			metadata: data['metadata'] || {},
		}),
	});
	if (!res.ok) throw new Error("Failed to create contract");
	const result = await res.json();
	return { id: result['id'], contractNumber: result['contract_number'] };
}

interface UpdateContractData {
	title?: string;
	description?: string;
	status?: ContractStatus;
	preconditions?: any[];
	postconditions?: any[];
	invariants?: any[];
	tags?: string[];
	metadata?: Record<string, unknown>;
}

async function updateContract(
	id: string,
	data: UpdateContractData,
): Promise<{ id: string; version: number }> {
	const body: Record<string, unknown> = {};
	if (data['title'] !== undefined) body['title'] = data['title'];
	if (data['description'] !== undefined) body['description'] = data['description'];
	if (data.status !== undefined) body.status = data.status;
	if (data['preconditions'] !== undefined) body['preconditions'] = data['preconditions'];
	if (data['postconditions'] !== undefined)
		body['postconditions'] = data['postconditions'];
	if (data['invariants'] !== undefined) body['invariants'] = data['invariants'];
	if (data['tags'] !== undefined) body['tags'] = data['tags'];
	if (data['metadata'] !== undefined) body['metadata'] = data['metadata'];

	const res = await fetch(`${API_URL}/api/v1/contracts/${id}`, {
		method: "PATCH",
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		body: JSON.stringify(body),
	});
	if (!res.ok) throw new Error("Failed to update contract");
	return res.json();
}

async function deleteContract(id: string): Promise<void> {
	const res = await fetch(`${API_URL}/api/v1/contracts/${id}`, {
		method: "DELETE",
		headers: getAuthHeaders(),
	});
	if (!res.ok) throw new Error("Failed to delete contract");
}

async function verifyContract(id: string): Promise<{
	id: string;
	status: ContractStatus;
	verificationResult: {
		status: string;
		passedConditions: number;
		failedConditions: number;
	};
}> {
	const res = await fetch(`${API_URL}/api/v1/contracts/${id}/verify`, {
		method: "POST",
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		body: JSON.stringify({}),
	});
	if (!res.ok) throw new Error("Failed to verify contract");
	return res.json();
}

async function fetchContractStats(projectId: string): Promise<ContractStats> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/contracts/stats`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to fetch contract stats");
	const data = await res.json();
	return {
		projectId: data['project_id'],
		total: data['total'] || 0,
		byType: data['by_type'] || {},
		byStatus: data['by_status'] || {},
		verificationRate: data['verification_rate'] || 0,
		violationCount: data['violation_count'] || 0,
	};
}

// =============================================================================
// API Fetch Functions - Features
// =============================================================================

interface FeatureFilters {
	projectId: string;
	status?: FeatureStatus;
	search?: string;
}

async function fetchFeatures(
	filters: FeatureFilters,
): Promise<{ features: Feature[]; total: number }> {
	const params = new URLSearchParams();
	params.set("project_id", filters.projectId);
	if (filters.status) params.set("status", filters.status);
	if (filters.search) params.set("search", filters.search);

	const res = await fetch(`${API_URL}/api/v1/features?${params}`, {
		headers: { "X-Bulk-Operation": "true", ...getAuthHeaders() },
	});
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(`Failed to fetch features: ${res.status} ${errorText}`);
	}
	const data = await res.json();
	return {
		features: (data['features'] || []).map(transformFeature),
		total: data['total'] || 0,
	};
}

async function fetchFeature(id: string): Promise<Feature> {
	const res = await fetch(`${API_URL}/api/v1/features/${id}`, {
		headers: getAuthHeaders(),
	});
	if (!res.ok) throw new Error("Failed to fetch feature");
	const data = await res.json();
	return transformFeature(data);
}

interface CreateFeatureData {
	projectId: string;
	name: string;
	description?: string;
	asA?: string;
	iWant?: string;
	soThat?: string;
	filePath?: string;
	tags?: string[];
	metadata?: Record<string, unknown>;
}

async function createFeature(
	data: CreateFeatureData,
): Promise<{ id: string; featureNumber: string }> {
	const res = await fetch(`${API_URL}/api/v1/features`, {
		method: "POST",
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		body: JSON.stringify({
			project_id: data['projectId'],
			name: data.name,
			description: data['description'],
			as_a: data['asA'],
			i_want: data['iWant'],
			so_that: data['soThat'],
			file_path: data['filePath'],
			tags: data['tags'],
			metadata: data['metadata'] || {},
		}),
	});
	if (!res.ok) throw new Error("Failed to create feature");
	const result = await res.json();
	return { id: result['id'], featureNumber: result['feature_number'] };
}

interface UpdateFeatureData {
	name?: string;
	description?: string;
	asA?: string;
	iWant?: string;
	soThat?: string;
	status?: FeatureStatus;
	filePath?: string;
	tags?: string[];
	metadata?: Record<string, unknown>;
}

async function updateFeature(
	id: string,
	data: UpdateFeatureData,
): Promise<{ id: string; version: number }> {
	const body: Record<string, unknown> = {};
	if (data.name !== undefined) body.name = data.name;
	if (data['description'] !== undefined) body['description'] = data['description'];
	if (data['asA'] !== undefined) body['as_a'] = data['asA'];
	if (data['iWant'] !== undefined) body['i_want'] = data['iWant'];
	if (data['soThat'] !== undefined) body['so_that'] = data['soThat'];
	if (data.status !== undefined) body.status = data.status;
	if (data['filePath'] !== undefined) body['file_path'] = data['filePath'];
	if (data['tags'] !== undefined) body['tags'] = data['tags'];
	if (data['metadata'] !== undefined) body['metadata'] = data['metadata'];

	const res = await fetch(`${API_URL}/api/v1/features/${id}`, {
		method: "PATCH",
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		body: JSON.stringify(body),
	});
	if (!res.ok) throw new Error("Failed to update feature");
	return res.json();
}

async function deleteFeature(id: string): Promise<void> {
	const res = await fetch(`${API_URL}/api/v1/features/${id}`, {
		method: "DELETE",
		headers: getAuthHeaders(),
	});
	if (!res.ok) throw new Error("Failed to delete feature");
}

async function fetchFeatureStats(projectId: string): Promise<FeatureStats> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/features/stats`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to fetch feature stats");
	const data = await res.json();
	return {
		projectId: data['project_id'],
		totalFeatures: data['total_features'] || 0,
		totalScenarios: data['total_scenarios'] || 0,
		byStatus: data['by_status'] || {},
		passRate: data['pass_rate'] || 0,
		coverage: {
			requirementsCovered: data['coverage']?.requirements_covered || 0,
			totalRequirements: data['coverage']?.total_requirements || 0,
			percentage: data['coverage']?.percentage || 0,
		},
	};
}

// =============================================================================
// API Fetch Functions - Scenarios
// =============================================================================

async function fetchScenarios(
	featureId: string,
): Promise<{ scenarios: Scenario[]; total: number }> {
	const params = new URLSearchParams();
	params.set("feature_id", featureId);

	const res = await fetch(`${API_URL}/api/v1/scenarios?${params}`, {
		headers: { "X-Bulk-Operation": "true", ...getAuthHeaders() },
	});
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(`Failed to fetch scenarios: ${res.status} ${errorText}`);
	}
	const data = await res.json();
	return {
		scenarios: (data['scenarios'] || []).map(transformScenario),
		total: data['total'] || 0,
	};
}

async function fetchScenario(id: string): Promise<Scenario> {
	const res = await fetch(`${API_URL}/api/v1/scenarios/${id}`, {
		headers: getAuthHeaders(),
	});
	if (!res.ok) throw new Error("Failed to fetch scenario");
	const data = await res.json();
	return transformScenario(data);
}

interface CreateScenarioData {
	featureId: string;
	title: string;
	description?: string;
	gherkinText: string;
	givenSteps: ScenarioStep[];
	whenSteps: ScenarioStep[];
	thenSteps: ScenarioStep[];
	tags?: string[];
	requirementIds?: string[];
	metadata?: Record<string, unknown>;
}

async function createScenario(
	data: CreateScenarioData,
): Promise<{ id: string; scenarioNumber: string }> {
	const res = await fetch(`${API_URL}/api/v1/scenarios`, {
		method: "POST",
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		body: JSON.stringify({
			feature_id: data['featureId'],
			title: data['title'],
			description: data['description'],
			gherkin_text: data['gherkinText'],
			given_steps: data['givenSteps'],
			when_steps: data['whenSteps'],
			then_steps: data['thenSteps'],
			tags: data['tags'],
			requirement_ids: data['requirementIds'],
			metadata: data['metadata'] || {},
		}),
	});
	if (!res.ok) throw new Error("Failed to create scenario");
	const result = await res.json();
	return { id: result['id'], scenarioNumber: result['scenario_number'] };
}

interface UpdateScenarioData {
	title?: string;
	description?: string;
	gherkinText?: string;
	givenSteps?: ScenarioStep[];
	whenSteps?: ScenarioStep[];
	thenSteps?: ScenarioStep[];
	tags?: string[];
	requirementIds?: string[];
	metadata?: Record<string, unknown>;
}

async function updateScenario(
	id: string,
	data: UpdateScenarioData,
): Promise<{ id: string; version: number }> {
	const body: Record<string, unknown> = {};
	if (data['title'] !== undefined) body['title'] = data['title'];
	if (data['description'] !== undefined) body['description'] = data['description'];
	if (data['gherkinText'] !== undefined) body['gherkin_text'] = data['gherkinText'];
	if (data['givenSteps'] !== undefined) body['given_steps'] = data['givenSteps'];
	if (data['whenSteps'] !== undefined) body['when_steps'] = data['whenSteps'];
	if (data['thenSteps'] !== undefined) body['then_steps'] = data['thenSteps'];
	if (data['tags'] !== undefined) body['tags'] = data['tags'];
	if (data['requirementIds'] !== undefined)
		body['requirement_ids'] = data['requirementIds'];
	if (data['metadata'] !== undefined) body['metadata'] = data['metadata'];

	const res = await fetch(`${API_URL}/api/v1/scenarios/${id}`, {
		method: "PATCH",
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		body: JSON.stringify(body),
	});
	if (!res.ok) throw new Error("Failed to update scenario");
	return res.json();
}

async function deleteScenario(id: string): Promise<void> {
	const res = await fetch(`${API_URL}/api/v1/scenarios/${id}`, {
		method: "DELETE",
		headers: getAuthHeaders(),
	});
	if (!res.ok) throw new Error("Failed to delete scenario");
}

async function runScenario(id: string): Promise<{
	id: string;
	status: ScenarioStatus;
	lastRunAt: string;
	lastRunResult: string;
	executionCount: number;
}> {
	const res = await fetch(`${API_URL}/api/v1/scenarios/${id}/run`, {
		method: "POST",
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		body: JSON.stringify({}),
	});
	if (!res.ok) throw new Error("Failed to run scenario");
	const result = await res.json();
	return {
		id: result['id'],
		status: result.status,
		lastRunAt: result['last_run_at'],
		lastRunResult: result['last_run_result'],
		executionCount: result['execution_count'],
	};
}

async function fetchSpecificationSummary(
	projectId: string,
): Promise<SpecificationSummary> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/specifications/summary`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to fetch specification summary");
	return res.json();
}

// =============================================================================
// React Query Hooks - ADRs
// =============================================================================

export function useADRs(filters: ADRFilters) {
	return useQuery({
		queryKey: ["adrs", filters],
		queryFn: () => fetchADRs(filters),
		enabled: !!filters.projectId,
	});
}

export function useADR(id: string) {
	return useQuery({
		queryKey: ["adrs", id],
		queryFn: () => fetchADR(id),
		enabled: !!id,
	});
}

export function useCreateADR() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: createADR,
		onSuccess: (_, variables) => {
			void queryClient.invalidateQueries({ queryKey: ["adrs"] });
			void queryClient.invalidateQueries({
				queryKey: ["adrStats", variables.projectId],
			});
			void queryClient.invalidateQueries({
				queryKey: ["specificationSummary", variables.projectId],
			});
		},
	});
}

export function useUpdateADR() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({ id, data }: { id: string; data: UpdateADRData }) =>
			updateADR(id, data),
		onSuccess: (_, { id }) => {
			void queryClient.invalidateQueries({ queryKey: ["adrs"] });
			void queryClient.invalidateQueries({ queryKey: ["adrs", id] });
			void queryClient.invalidateQueries({ queryKey: ["adrActivities", id] });
		},
	});
}

export function useDeleteADR() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: deleteADR,
		onSuccess: () => {
			void queryClient.invalidateQueries({ queryKey: ["adrs"] });
			void queryClient.invalidateQueries({ queryKey: ["adrStats"] });
			void queryClient.invalidateQueries({ queryKey: ["specificationSummary"] });
		},
	});
}

export function useVerifyADR() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({ id, notes }: { id: string; notes: string }) =>
			verifyADR(id, notes),
		onSuccess: (_, { id }) => {
			void queryClient.invalidateQueries({ queryKey: ["adrs"] });
			void queryClient.invalidateQueries({ queryKey: ["adrs", id] });
			void queryClient.invalidateQueries({ queryKey: ["adrActivities", id] });
			void queryClient.invalidateQueries({ queryKey: ["adrStats"] });
			void queryClient.invalidateQueries({ queryKey: ["specificationSummary"] });
		},
	});
}

export function useADRActivities(adrId: string) {
	return useQuery({
		queryKey: ["adrActivities", adrId],
		queryFn: () => fetchADRActivities(adrId),
		enabled: !!adrId,
	});
}

export function useContractActivities(contractId: string) {
	return useQuery({
		queryKey: ["contractActivities", contractId],
		queryFn: () => fetchContractActivities(contractId),
		enabled: !!contractId,
	});
}

export function useFeatureActivities(featureId: string) {
	return useQuery({
		queryKey: ["featureActivities", featureId],
		queryFn: () => fetchFeatureActivities(featureId),
		enabled: !!featureId,
	});
}

export function useScenarioActivities(
	scenarioId: string,
	options?: { limit?: number; offset?: number },
) {
	return useQuery({
		queryKey: ["scenarioActivities", scenarioId, options],
		queryFn: () => fetchScenarioActivities(scenarioId, options),
		enabled: !!scenarioId,
	});
}

export function useProjectScenarios(projectId: string, status?: string) {
	return useQuery({
		queryKey: ["projectScenarios", projectId, status],
		queryFn: () => fetchProjectScenarios(projectId, status),
		enabled: !!projectId,
	});
}

export function useProjectScenarioActivities(
	projectId: string,
	options?: {
		limit?: number;
		offset?: number;
		eventType?: string;
		since?: string;
		until?: string;
	},
) {
	return useQuery({
		queryKey: ["projectScenarioActivities", projectId, options],
		queryFn: () => fetchProjectScenarioActivities(projectId, options),
		enabled: !!projectId,
	});
}

export function useADRStats(projectId: string) {
	return useQuery({
		queryKey: ["adrStats", projectId],
		queryFn: () => fetchADRStats(projectId),
		enabled: !!projectId,
	});
}

// =============================================================================
// React Query Hooks - Contracts
// =============================================================================

export function useContracts(filters: ContractFilters) {
	return useQuery({
		queryKey: ["contracts", filters],
		queryFn: () => fetchContracts(filters),
		enabled: !!filters.projectId,
	});
}

export function useContract(id: string) {
	return useQuery({
		queryKey: ["contracts", id],
		queryFn: () => fetchContract(id),
		enabled: !!id,
	});
}

export function useCreateContract() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: createContract,
		onSuccess: (_, variables) => {
			void queryClient.invalidateQueries({ queryKey: ["contracts"] });
			void queryClient.invalidateQueries({
				queryKey: ["contractStats", variables.projectId],
			});
			void queryClient.invalidateQueries({
				queryKey: ["specificationSummary", variables.projectId],
			});
		},
	});
}

export function useUpdateContract() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({ id, data }: { id: string; data: UpdateContractData }) =>
			updateContract(id, data),
		onSuccess: (_, { id }) => {
			void queryClient.invalidateQueries({ queryKey: ["contracts"] });
			void queryClient.invalidateQueries({ queryKey: ["contracts", id] });
		},
	});
}

export function useDeleteContract() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: deleteContract,
		onSuccess: () => {
			void queryClient.invalidateQueries({ queryKey: ["contracts"] });
			void queryClient.invalidateQueries({ queryKey: ["contractStats"] });
			void queryClient.invalidateQueries({ queryKey: ["specificationSummary"] });
		},
	});
}

export function useVerifyContract() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: (id: string) => verifyContract(id),
		onSuccess: (_, id) => {
			void queryClient.invalidateQueries({ queryKey: ["contracts"] });
			void queryClient.invalidateQueries({ queryKey: ["contracts", id] });
			void queryClient.invalidateQueries({ queryKey: ["contractStats"] });
			void queryClient.invalidateQueries({ queryKey: ["specificationSummary"] });
		},
	});
}

export function useContractStats(projectId: string) {
	return useQuery({
		queryKey: ["contractStats", projectId],
		queryFn: () => fetchContractStats(projectId),
		enabled: !!projectId,
	});
}

// =============================================================================
// React Query Hooks - Features
// =============================================================================

export function useFeatures(filters: FeatureFilters) {
	return useQuery({
		queryKey: ["features", filters],
		queryFn: () => fetchFeatures(filters),
		enabled: !!filters.projectId,
	});
}

export function useFeature(id: string) {
	return useQuery({
		queryKey: ["features", id],
		queryFn: () => fetchFeature(id),
		enabled: !!id,
	});
}

export function useCreateFeature() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: createFeature,
		onSuccess: (_, variables) => {
			void queryClient.invalidateQueries({ queryKey: ["features"] });
			void queryClient.invalidateQueries({
				queryKey: ["featureStats", variables.projectId],
			});
			void queryClient.invalidateQueries({
				queryKey: ["specificationSummary", variables.projectId],
			});
		},
	});
}

export function useUpdateFeature() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({ id, data }: { id: string; data: UpdateFeatureData }) =>
			updateFeature(id, data),
		onSuccess: (_, { id }) => {
			void queryClient.invalidateQueries({ queryKey: ["features"] });
			void queryClient.invalidateQueries({ queryKey: ["features", id] });
		},
	});
}

export function useDeleteFeature() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: deleteFeature,
		onSuccess: () => {
			void queryClient.invalidateQueries({ queryKey: ["features"] });
			void queryClient.invalidateQueries({ queryKey: ["featureStats"] });
			void queryClient.invalidateQueries({ queryKey: ["specificationSummary"] });
		},
	});
}

export function useFeatureStats(projectId: string) {
	return useQuery({
		queryKey: ["featureStats", projectId],
		queryFn: () => fetchFeatureStats(projectId),
		enabled: !!projectId,
	});
}

// =============================================================================
// React Query Hooks - Scenarios
// =============================================================================

export function useScenarios(featureId: string) {
	return useQuery({
		queryKey: ["scenarios", featureId],
		queryFn: () => fetchScenarios(featureId),
		enabled: !!featureId,
	});
}

export function useScenario(id: string) {
	return useQuery({
		queryKey: ["scenarios", id],
		queryFn: () => fetchScenario(id),
		enabled: !!id,
	});
}

export function useCreateScenario() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: createScenario,
		onSuccess: (_, variables) => {
			void queryClient.invalidateQueries({
				queryKey: ["scenarios", variables.featureId],
			});
			void queryClient.invalidateQueries({
				queryKey: ["features", variables.featureId],
			});
			void queryClient.invalidateQueries({ queryKey: ["featureStats"] });
			void queryClient.invalidateQueries({ queryKey: ["specificationSummary"] });
		},
	});
}

export function useUpdateScenario() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({ id, data }: { id: string; data: UpdateScenarioData }) =>
			updateScenario(id, data),
		onSuccess: (_, { id }) => {
			void queryClient.invalidateQueries({ queryKey: ["scenarios"] });
			void queryClient.invalidateQueries({ queryKey: ["scenarios", id] });
			void queryClient.invalidateQueries({ queryKey: ["features"] });
		},
	});
}

export function useDeleteScenario() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: deleteScenario,
		onSuccess: () => {
			void queryClient.invalidateQueries({ queryKey: ["scenarios"] });
			void queryClient.invalidateQueries({ queryKey: ["features"] });
			void queryClient.invalidateQueries({ queryKey: ["featureStats"] });
			void queryClient.invalidateQueries({ queryKey: ["specificationSummary"] });
		},
	});
}

export function useRunScenario() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: runScenario,
		onSuccess: (_, id) => {
			void queryClient.invalidateQueries({ queryKey: ["scenarios"] });
			void queryClient.invalidateQueries({ queryKey: ["scenarios", id] });
			void queryClient.invalidateQueries({ queryKey: ["features"] });
			void queryClient.invalidateQueries({ queryKey: ["featureStats"] });
			void queryClient.invalidateQueries({ queryKey: ["specificationSummary"] });
		},
	});
}

// =============================================================================
// React Query Hooks - Summary
// =============================================================================

export function useSpecificationSummary(projectId: string) {
	return useQuery({
		queryKey: ["specificationSummary", projectId],
		queryFn: () => fetchSpecificationSummary(projectId),
		enabled: !!projectId,
	});
}

// =============================================================================
// React Query Hooks - Quality Reports
// =============================================================================

interface QualityReport {
	id: string;
	itemId: string;
	smells: string[];
	ambiguityScore: number;
	completenessScore: number;
	suggestions: string[];
	lastAnalyzedAt: string;
	version: number;
	createdAt: string;
	updatedAt: string;
}

async function fetchQualityReports(
	projectId: string,
): Promise<QualityReport[]> {
	// First, fetch all items for the project
	const authHeaders = getAuthHeaders();
	const itemsRes = await fetch(
		`${API_URL}/api/v1/items?project_id=${projectId}&limit=1000`,
		{
			headers: { "X-Bulk-Operation": "true", ...authHeaders },
		},
	);
	if (!itemsRes.ok) {
		throw new Error(`Failed to fetch items: ${itemsRes.status}`);
	}
	const itemsData = await itemsRes.json();
	const items = itemsData.items || [];

	// Then fetch quality for each item (only items that have quality analysis)
	const qualityPromises = items.map(async (item: any) => {
		try {
			const qualityRes = await fetch(
				`${API_URL}/api/v1/quality/items/${item.id}`,
				{
					headers: authHeaders,
				},
			);
			if (qualityRes.ok) {
				const qualityData = await qualityRes.json();
				return {
					id: qualityData.id,
					itemId: qualityData.item_id,
					smells: qualityData.smells || [],
					ambiguityScore: qualityData.ambiguity_score || 0,
					completenessScore: qualityData.completeness_score || 0,
					suggestions: qualityData.suggestions || [],
					lastAnalyzedAt: qualityData.last_analyzed_at,
					version: qualityData.version || 0,
					createdAt: qualityData.created_at,
					updatedAt: qualityData.updated_at,
				};
			}
			// If quality doesn't exist for this item, skip it (404 is expected)
			return null;
		} catch (err) {
			logger.warn(`Failed to fetch quality for item ${item.id}:`, err);
			return null;
		}
	});

	const results = await Promise.all(qualityPromises);
	return results.filter((r): r is QualityReport => r !== null);
}

export function useQualityReport(projectId: string) {
	return useQuery({
		queryKey: ["qualityReports", projectId],
		queryFn: () => fetchQualityReports(projectId),
		enabled: !!projectId,
	});
}
