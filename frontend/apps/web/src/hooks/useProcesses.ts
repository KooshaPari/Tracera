import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type {
	ExecutionStatus,
	Process,
	ProcessCategory,
	ProcessExecution,
	ProcessInput,
	ProcessOutput,
	ProcessStage,
	ProcessStatus,
	ProcessSwimlane,
	ProcessTrigger,
} from "@tracertm/types";
import client from "@/api/client";

const { getAuthHeaders } = client;

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:4000";

// Transform API response (snake_case) to frontend format (camelCase)
function transformProcess(data: Record<string, unknown>): Process {
	return {
		activatedAt: data["activated_at"],
		activatedBy: data["activated_by"],
		bpmnDiagramUrl: data["bpmn_diagram_url"],
		bpmnXml: data["bpmn_xml"],
		category: data["category"],
		createdAt: data["created_at"],
		deprecatedAt: data["deprecated_at"],
		deprecatedBy: data["deprecated_by"],
		deprecationReason: data["deprecation_reason"],
		description: data["description"],
		exitCriteria: data["exit_criteria"],
		expectedDurationHours: data["expected_duration_hours"],
		id: data["id"],
		inputs: data["inputs"],
		isActiveVersion: data["is_active_version"],
		metadata: data["metadata"],
		name: data.name,
		outputs: data["outputs"],
		owner: data["owner"],
		parentVersionId: data["parent_version_id"],
		processNumber: data["process_number"],
		projectId: data["project_id"],
		purpose: data["purpose"],
		relatedProcessIds: data["related_process_ids"],
		responsibleTeam: data["responsible_team"],
		slaHours: data["sla_hours"],
		stages: data["stages"],
		status: data.status,
		swimlanes: data["swimlanes"],
		tags: data["tags"],
		triggers: data["triggers"],
		updatedAt: data["updated_at"],
		version: data["version"],
		versionNotes: data["version_notes"],
		versionNumber: data["version_number"],
	};
}

function transformExecution(data: Record<string, unknown>): ProcessExecution {
	return {
		completedAt: data["completed_at"],
		completedBy: data["completed_by"],
		completedStages: data["completed_stages"],
		contextData: data["context_data"],
		createdAt: data["created_at"],
		currentStageId: data["current_stage_id"],
		executionNumber: data["execution_number"],
		id: data["id"],
		initiatedBy: data["initiated_by"],
		outputItemIds: data["output_item_ids"],
		processId: data["process_id"],
		resultSummary: data["result_summary"],
		startedAt: data["started_at"],
		status: data.status,
		triggerItemId: data["trigger_item_id"],
		updatedAt: data["updated_at"],
	};
}

interface ProcessFilters {
	projectId: string;
	status?: ProcessStatus;
	category?: ProcessCategory;
	owner?: string;
	activeOnly?: boolean;
}

async function fetchProcesses(
	filters: ProcessFilters,
): Promise<{ processes: Process[]; total: number }> {
	const params = new URLSearchParams();
	params.set("project_id", filters.projectId);
	if (filters.status) {
		params.set("status", filters.status);
	}
	if (filters.category) {
		params.set("category", filters.category);
	}
	if (filters.owner) {
		params.set("owner", filters.owner);
	}
	if (filters.activeOnly) {
		params.set("active_only", "true");
	}

	const res = await fetch(`${API_URL}/api/v1/processes?${params}`, {
		headers: {
			"X-Bulk-Operation": "true",
			...getAuthHeaders(),
		},
	});
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(`Failed to fetch processes: ${res.status} ${errorText}`);
	}
	const data = await res.json();
	return {
		processes: (data["processes"] || []).map(transformProcess),
		total: data["total"] || 0,
	};
}

async function fetchProcess(id: string): Promise<Process> {
	const res = await fetch(`${API_URL}/api/v1/processes/${id}`, {
		headers: getAuthHeaders(),
	});
	if (!res.ok) {
		throw new Error("Failed to fetch process");
	}
	const data = await res.json();
	return transformProcess(data);
}

interface CreateProcessData {
	projectId: string;
	name: string;
	description?: string;
	purpose?: string;
	category?: ProcessCategory;
	tags?: string[];
	stages?: ProcessStage[];
	swimlanes?: ProcessSwimlane[];
	inputs?: ProcessInput[];
	outputs?: ProcessOutput[];
	triggers?: ProcessTrigger[];
	exitCriteria?: string[];
	bpmnXml?: string;
	owner?: string;
	responsibleTeam?: string;
	expectedDurationHours?: number;
	slaHours?: number;
	relatedProcessIds?: string[];
	metadata?: Record<string, unknown>;
}

async function createProcess(
	data: CreateProcessData,
): Promise<{ id: string; processNumber: string }> {
	const res = await fetch(
		`${API_URL}/api/v1/processes?project_id=${data["projectId"]}`,
		{
			body: JSON.stringify({
				bpmn_xml: data["bpmnXml"],
				category: data["category"],
				description: data["description"],
				exit_criteria: data["exitCriteria"],
				expected_duration_hours: data["expectedDurationHours"],
				inputs: data["inputs"],
				metadata: data["metadata"] || {},
				name: data.name,
				outputs: data["outputs"],
				owner: data["owner"],
				purpose: data["purpose"],
				related_process_ids: data["relatedProcessIds"],
				responsible_team: data["responsibleTeam"],
				sla_hours: data["slaHours"],
				stages: data["stages"],
				swimlanes: data["swimlanes"],
				tags: data["tags"],
				triggers: data["triggers"],
			}),
			headers: { "Content-Type": "application/json", ...getAuthHeaders() },
			method: "POST",
		},
	);
	if (!res.ok) {
		throw new Error("Failed to create process");
	}
	const result = await res.json();
	return { id: result["id"], processNumber: result["process_number"] };
}

async function updateProcess(
	id: string,
	data: Partial<Omit<CreateProcessData, "projectId">>,
): Promise<{ id: string; version: number }> {
	const res = await fetch(`${API_URL}/api/v1/processes/${id}`, {
		body: JSON.stringify({
			bpmn_xml: data["bpmnXml"],
			category: data["category"],
			description: data["description"],
			exit_criteria: data["exitCriteria"],
			expected_duration_hours: data["expectedDurationHours"],
			inputs: data["inputs"],
			metadata: data["metadata"],
			name: data.name,
			outputs: data["outputs"],
			owner: data["owner"],
			purpose: data["purpose"],
			related_process_ids: data["relatedProcessIds"],
			responsible_team: data["responsibleTeam"],
			sla_hours: data["slaHours"],
			stages: data["stages"],
			swimlanes: data["swimlanes"],
			tags: data["tags"],
			triggers: data["triggers"],
		}),
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		method: "PUT",
	});
	if (!res.ok) {
		throw new Error("Failed to update process");
	}
	return res.json();
}

async function createProcessVersion(
	processId: string,
	versionNotes?: string,
): Promise<{
	id: string;
	processNumber: string;
	versionNumber: number;
	parentVersionId: string;
}> {
	const res = await fetch(`${API_URL}/api/v1/processes/${processId}/versions`, {
		body: JSON.stringify({ version_notes: versionNotes }),
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		method: "POST",
	});
	if (!res.ok) {
		throw new Error("Failed to create process version");
	}
	const result = await res.json();
	return {
		id: result["id"],
		parentVersionId: result["parent_version_id"],
		processNumber: result["process_number"],
		versionNumber: result["version_number"],
	};
}

async function activateProcess(
	processId: string,
): Promise<{ id: string; status: string; isActiveVersion: boolean }> {
	const res = await fetch(`${API_URL}/api/v1/processes/${processId}/activate`, {
		body: JSON.stringify({}),
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		method: "PUT",
	});
	if (!res.ok) {
		throw new Error("Failed to activate process");
	}
	const result = await res.json();
	return {
		id: result["id"],
		isActiveVersion: result["is_active_version"],
		status: result.status,
	};
}

async function deprecateProcess(
	processId: string,
	deprecationReason?: string,
): Promise<{ id: string; status: string }> {
	const res = await fetch(
		`${API_URL}/api/v1/processes/${processId}/deprecate`,
		{
			body: JSON.stringify({ deprecation_reason: deprecationReason }),
			headers: { "Content-Type": "application/json", ...getAuthHeaders() },
			method: "PUT",
		},
	);
	if (!res.ok) {
		throw new Error("Failed to deprecate process");
	}
	return res.json();
}

async function deleteProcess(id: string): Promise<void> {
	const res = await fetch(`${API_URL}/api/v1/processes/${id}`, {
		headers: getAuthHeaders(),
		method: "DELETE",
	});
	if (!res.ok) {
		throw new Error("Failed to delete process");
	}
}

async function fetchProcessStats(projectId: string): Promise<{
	projectId: string;
	byStatus: Record<string, number>;
	byCategory: Record<string, number>;
	total: number;
}> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/processes/stats`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) {
		throw new Error("Failed to fetch process stats");
	}
	const data = await res.json();
	return {
		byCategory: data["by_category"] || {},
		byStatus: data["by_status"] || {},
		projectId: data["project_id"],
		total: data["total"] || 0,
	};
}

// Process Execution API functions

async function createExecution(
	processId: string,
	triggerItemId?: string,
	contextData?: Record<string, unknown>,
): Promise<{ id: string; executionNumber: string }> {
	const res = await fetch(
		`${API_URL}/api/v1/processes/${processId}/executions`,
		{
			body: JSON.stringify({
				context_data: contextData || {},
				process_id: processId,
				trigger_item_id: triggerItemId,
			}),
			headers: { "Content-Type": "application/json", ...getAuthHeaders() },
			method: "POST",
		},
	);
	if (!res.ok) {
		throw new Error("Failed to create execution");
	}
	const result = await res.json();
	return { executionNumber: result["execution_number"], id: result["id"] };
}

async function fetchExecutions(
	processId: string,
	status?: ExecutionStatus,
	limit = 50,
): Promise<{ total: number; executions: ProcessExecution[] }> {
	const params = new URLSearchParams();
	if (status) {
		params.set("status", status);
	}
	params.set("limit", limit.toString());

	const res = await fetch(
		`${API_URL}/api/v1/processes/${processId}/executions?${params}`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) {
		throw new Error("Failed to fetch executions");
	}
	const data = await res.json();
	return {
		executions: (data["executions"] || []).map(transformExecution),
		total: data["total"] || 0,
	};
}

async function fetchExecution(executionId: string): Promise<ProcessExecution> {
	const res = await fetch(`${API_URL}/api/v1/executions/${executionId}`, {
		headers: getAuthHeaders(),
	});
	if (!res.ok) {
		throw new Error("Failed to fetch execution");
	}
	const data = await res.json();
	return transformExecution(data);
}

async function startExecution(
	executionId: string,
): Promise<{ id: string; status: string }> {
	const res = await fetch(`${API_URL}/api/v1/executions/${executionId}/start`, {
		headers: getAuthHeaders(),
		method: "POST",
	});
	if (!res.ok) {
		throw new Error("Failed to start execution");
	}
	return res.json();
}

async function advanceExecution(
	executionId: string,
	stageId: string,
): Promise<{
	id: string;
	currentStageId: string;
	completedStages: string[];
}> {
	const res = await fetch(
		`${API_URL}/api/v1/executions/${executionId}/advance?stage_id=${stageId}`,
		{
			headers: getAuthHeaders(),
			method: "POST",
		},
	);
	if (!res.ok) {
		throw new Error("Failed to advance execution");
	}
	const result = await res.json();
	return {
		completedStages: result["completed_stages"],
		currentStageId: result["current_stage_id"],
		id: result["id"],
	};
}

async function completeExecution(
	executionId: string,
	resultSummary?: string,
	outputItemIds?: string[],
): Promise<{ id: string; status: string }> {
	const res = await fetch(
		`${API_URL}/api/v1/executions/${executionId}/complete`,
		{
			body: JSON.stringify({
				output_item_ids: outputItemIds,
				result_summary: resultSummary,
			}),
			headers: { "Content-Type": "application/json", ...getAuthHeaders() },
			method: "POST",
		},
	);
	if (!res.ok) {
		throw new Error("Failed to complete execution");
	}
	return res.json();
}

// React Query hooks

export function useProcesses(filters: ProcessFilters) {
	return useQuery({
		enabled: !!filters.projectId,
		queryFn: () => fetchProcesses(filters),
		queryKey: ["processes", filters],
	});
}

export function useProcess(id: string) {
	return useQuery({
		enabled: !!id,
		queryFn: () => fetchProcess(id),
		queryKey: ["processes", id],
	});
}

export function useCreateProcess() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: createProcess,
		onSuccess: () => {
			undefined;
		},
	});
}

export function useUpdateProcess() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({
			id,
			data,
		}: {
			id: string;
			data: Partial<Omit<CreateProcessData, "projectId">>;
		}) => updateProcess(id, data),
		onSuccess: (_, { id }) => {
			undefined;
			undefined;
		},
	});
}

export function useCreateProcessVersion() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({
			processId,
			versionNotes,
		}: {
			processId: string;
			versionNotes?: string;
		}) => createProcessVersion(processId, versionNotes),
		onSuccess: () => {
			undefined;
		},
	});
}

export function useActivateProcess() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: activateProcess,
		onSuccess: (_, processId) => {
			undefined;
			undefined;
		},
	});
}

export function useDeprecateProcess() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({
			processId,
			deprecationReason,
		}: {
			processId: string;
			deprecationReason?: string;
		}) => deprecateProcess(processId, deprecationReason),
		onSuccess: (_, { processId }) => {
			undefined;
			undefined;
		},
	});
}

export function useDeleteProcess() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: deleteProcess,
		onSuccess: () => {
			undefined;
		},
	});
}

export function useProcessStats(projectId: string) {
	return useQuery({
		enabled: !!projectId,
		queryFn: () => fetchProcessStats(projectId),
		queryKey: ["processStats", projectId],
	});
}

// Execution hooks

export function useProcessExecutions(
	processId: string,
	status?: ExecutionStatus,
	limit = 50,
) {
	return useQuery({
		enabled: !!processId,
		queryFn: () => fetchExecutions(processId, status, limit),
		queryKey: ["processExecutions", processId, status, limit],
	});
}

export function useExecution(executionId: string) {
	return useQuery({
		enabled: !!executionId,
		queryFn: () => fetchExecution(executionId),
		queryKey: ["executions", executionId],
	});
}

export function useCreateExecution() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({
			processId,
			triggerItemId,
			contextData,
		}: {
			processId: string;
			triggerItemId?: string;
			contextData?: Record<string, unknown>;
		}) => createExecution(processId, triggerItemId, contextData),
		onSuccess: (_, { processId }) => {
			undefined;
		},
	});
}

export function useStartExecution() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: startExecution,
		onSuccess: (_, executionId) => {
			undefined;
			undefined;
		},
	});
}

export function useAdvanceExecution() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({
			executionId,
			stageId,
		}: {
			executionId: string;
			stageId: string;
		}) => advanceExecution(executionId, stageId),
		onSuccess: (_, { executionId }) => {
			undefined;
		},
	});
}

export function useCompleteExecution() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({
			executionId,
			resultSummary,
			outputItemIds,
		}: {
			executionId: string;
			resultSummary?: string;
			outputItemIds?: string[];
		}) => completeExecution(executionId, resultSummary, outputItemIds),
		onSuccess: (_, { executionId }) => {
			undefined;
			undefined;
		},
	});
}
