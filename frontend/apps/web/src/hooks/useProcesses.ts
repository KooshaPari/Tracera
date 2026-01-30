import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type {
	Process,
	ProcessStatus,
	ProcessCategory,
	ProcessExecution,
	ExecutionStatus,
	ProcessStage,
	ProcessSwimlane,
	ProcessInput,
	ProcessOutput,
	ProcessTrigger,
} from "@tracertm/types";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Transform API response (snake_case) to frontend format (camelCase)
function transformProcess(data: any): Process {
	return {
		id: data.id,
		processNumber: data.process_number,
		projectId: data.project_id,
		name: data.name,
		description: data.description,
		purpose: data.purpose,
		status: data.status,
		category: data.category,
		tags: data.tags,
		versionNumber: data.version_number,
		isActiveVersion: data.is_active_version,
		parentVersionId: data.parent_version_id,
		versionNotes: data.version_notes,
		stages: data.stages,
		swimlanes: data.swimlanes,
		inputs: data.inputs,
		outputs: data.outputs,
		triggers: data.triggers,
		exitCriteria: data.exit_criteria,
		bpmnXml: data.bpmn_xml,
		bpmnDiagramUrl: data.bpmn_diagram_url,
		owner: data.owner,
		responsibleTeam: data.responsible_team,
		expectedDurationHours: data.expected_duration_hours,
		slaHours: data.sla_hours,
		activatedAt: data.activated_at,
		activatedBy: data.activated_by,
		deprecatedAt: data.deprecated_at,
		deprecatedBy: data.deprecated_by,
		deprecationReason: data.deprecation_reason,
		relatedProcessIds: data.related_process_ids,
		metadata: data.metadata,
		version: data.version,
		createdAt: data.created_at,
		updatedAt: data.updated_at,
	};
}

function transformExecution(data: any): ProcessExecution {
	return {
		id: data.id,
		processId: data.process_id,
		executionNumber: data.execution_number,
		status: data.status,
		currentStageId: data.current_stage_id,
		completedStages: data.completed_stages,
		startedAt: data.started_at,
		completedAt: data.completed_at,
		initiatedBy: data.initiated_by,
		completedBy: data.completed_by,
		triggerItemId: data.trigger_item_id,
		contextData: data.context_data,
		resultSummary: data.result_summary,
		outputItemIds: data.output_item_ids,
		createdAt: data.created_at,
		updatedAt: data.updated_at,
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
	if (filters.status) params.set("status", filters.status);
	if (filters.category) params.set("category", filters.category);
	if (filters.owner) params.set("owner", filters.owner);
	if (filters.activeOnly) params.set("active_only", "true");

	const res = await fetch(`${API_URL}/api/v1/processes?${params}`, {
		headers: {
			"X-Bulk-Operation": "true",
		},
	});
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(`Failed to fetch processes: ${res.status} ${errorText}`);
	}
	const data = await res.json();
	return {
		processes: (data.processes || []).map(transformProcess),
		total: data.total || 0,
	};
}

async function fetchProcess(id: string): Promise<Process> {
	const res = await fetch(`${API_URL}/api/v1/processes/${id}`);
	if (!res.ok) throw new Error("Failed to fetch process");
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
		`${API_URL}/api/v1/processes?project_id=${data.projectId}`,
		{
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
				name: data.name,
				description: data.description,
				purpose: data.purpose,
				category: data.category,
				tags: data.tags,
				stages: data.stages,
				swimlanes: data.swimlanes,
				inputs: data.inputs,
				outputs: data.outputs,
				triggers: data.triggers,
				exit_criteria: data.exitCriteria,
				bpmn_xml: data.bpmnXml,
				owner: data.owner,
				responsible_team: data.responsibleTeam,
				expected_duration_hours: data.expectedDurationHours,
				sla_hours: data.slaHours,
				related_process_ids: data.relatedProcessIds,
				metadata: data.metadata || {},
			}),
		},
	);
	if (!res.ok) throw new Error("Failed to create process");
	const result = await res.json();
	return { id: result.id, processNumber: result.process_number };
}

async function updateProcess(
	id: string,
	data: Partial<Omit<CreateProcessData, "projectId">>,
): Promise<{ id: string; version: number }> {
	const res = await fetch(`${API_URL}/api/v1/processes/${id}`, {
		method: "PUT",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({
			name: data.name,
			description: data.description,
			purpose: data.purpose,
			category: data.category,
			tags: data.tags,
			stages: data.stages,
			swimlanes: data.swimlanes,
			inputs: data.inputs,
			outputs: data.outputs,
			triggers: data.triggers,
			exit_criteria: data.exitCriteria,
			bpmn_xml: data.bpmnXml,
			owner: data.owner,
			responsible_team: data.responsibleTeam,
			expected_duration_hours: data.expectedDurationHours,
			sla_hours: data.slaHours,
			related_process_ids: data.relatedProcessIds,
			metadata: data.metadata,
		}),
	});
	if (!res.ok) throw new Error("Failed to update process");
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
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({ version_notes: versionNotes }),
	});
	if (!res.ok) throw new Error("Failed to create process version");
	const result = await res.json();
	return {
		id: result.id,
		processNumber: result.process_number,
		versionNumber: result.version_number,
		parentVersionId: result.parent_version_id,
	};
}

async function activateProcess(
	processId: string,
): Promise<{ id: string; status: string; isActiveVersion: boolean }> {
	const res = await fetch(`${API_URL}/api/v1/processes/${processId}/activate`, {
		method: "PUT",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({}),
	});
	if (!res.ok) throw new Error("Failed to activate process");
	const result = await res.json();
	return {
		id: result.id,
		status: result.status,
		isActiveVersion: result.is_active_version,
	};
}

async function deprecateProcess(
	processId: string,
	deprecationReason?: string,
): Promise<{ id: string; status: string }> {
	const res = await fetch(
		`${API_URL}/api/v1/processes/${processId}/deprecate`,
		{
			method: "PUT",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ deprecation_reason: deprecationReason }),
		},
	);
	if (!res.ok) throw new Error("Failed to deprecate process");
	return res.json();
}

async function deleteProcess(id: string): Promise<void> {
	const res = await fetch(`${API_URL}/api/v1/processes/${id}`, {
		method: "DELETE",
	});
	if (!res.ok) throw new Error("Failed to delete process");
}

async function fetchProcessStats(projectId: string): Promise<{
	projectId: string;
	byStatus: Record<string, number>;
	byCategory: Record<string, number>;
	total: number;
}> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/processes/stats`,
	);
	if (!res.ok) throw new Error("Failed to fetch process stats");
	const data = await res.json();
	return {
		projectId: data.project_id,
		byStatus: data.by_status || {},
		byCategory: data.by_category || {},
		total: data.total || 0,
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
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
				process_id: processId,
				trigger_item_id: triggerItemId,
				context_data: contextData || {},
			}),
		},
	);
	if (!res.ok) throw new Error("Failed to create execution");
	const result = await res.json();
	return { id: result.id, executionNumber: result.execution_number };
}

async function fetchExecutions(
	processId: string,
	status?: ExecutionStatus,
	limit = 50,
): Promise<{ total: number; executions: ProcessExecution[] }> {
	const params = new URLSearchParams();
	if (status) params.set("status", status);
	params.set("limit", limit.toString());

	const res = await fetch(
		`${API_URL}/api/v1/processes/${processId}/executions?${params}`,
	);
	if (!res.ok) throw new Error("Failed to fetch executions");
	const data = await res.json();
	return {
		total: data.total || 0,
		executions: (data.executions || []).map(transformExecution),
	};
}

async function fetchExecution(executionId: string): Promise<ProcessExecution> {
	const res = await fetch(`${API_URL}/api/v1/executions/${executionId}`);
	if (!res.ok) throw new Error("Failed to fetch execution");
	const data = await res.json();
	return transformExecution(data);
}

async function startExecution(
	executionId: string,
): Promise<{ id: string; status: string }> {
	const res = await fetch(`${API_URL}/api/v1/executions/${executionId}/start`, {
		method: "POST",
	});
	if (!res.ok) throw new Error("Failed to start execution");
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
			method: "POST",
		},
	);
	if (!res.ok) throw new Error("Failed to advance execution");
	const result = await res.json();
	return {
		id: result.id,
		currentStageId: result.current_stage_id,
		completedStages: result.completed_stages,
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
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
				result_summary: resultSummary,
				output_item_ids: outputItemIds,
			}),
		},
	);
	if (!res.ok) throw new Error("Failed to complete execution");
	return res.json();
}

// React Query hooks

export function useProcesses(filters: ProcessFilters) {
	return useQuery({
		queryKey: ["processes", filters],
		queryFn: () => fetchProcesses(filters),
		enabled: !!filters.projectId,
	});
}

export function useProcess(id: string) {
	return useQuery({
		queryKey: ["processes", id],
		queryFn: () => fetchProcess(id),
		enabled: !!id,
	});
}

export function useCreateProcess() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: createProcess,
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["processes"] });
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
			queryClient.invalidateQueries({ queryKey: ["processes"] });
			queryClient.invalidateQueries({ queryKey: ["processes", id] });
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
			queryClient.invalidateQueries({ queryKey: ["processes"] });
		},
	});
}

export function useActivateProcess() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: activateProcess,
		onSuccess: (_, processId) => {
			queryClient.invalidateQueries({ queryKey: ["processes"] });
			queryClient.invalidateQueries({ queryKey: ["processes", processId] });
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
			queryClient.invalidateQueries({ queryKey: ["processes"] });
			queryClient.invalidateQueries({ queryKey: ["processes", processId] });
		},
	});
}

export function useDeleteProcess() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: deleteProcess,
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["processes"] });
		},
	});
}

export function useProcessStats(projectId: string) {
	return useQuery({
		queryKey: ["processStats", projectId],
		queryFn: () => fetchProcessStats(projectId),
		enabled: !!projectId,
	});
}

// Execution hooks

export function useProcessExecutions(
	processId: string,
	status?: ExecutionStatus,
	limit = 50,
) {
	return useQuery({
		queryKey: ["processExecutions", processId, status, limit],
		queryFn: () => fetchExecutions(processId, status, limit),
		enabled: !!processId,
	});
}

export function useExecution(executionId: string) {
	return useQuery({
		queryKey: ["executions", executionId],
		queryFn: () => fetchExecution(executionId),
		enabled: !!executionId,
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
			queryClient.invalidateQueries({
				queryKey: ["processExecutions", processId],
			});
		},
	});
}

export function useStartExecution() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: startExecution,
		onSuccess: (_, executionId) => {
			queryClient.invalidateQueries({ queryKey: ["executions", executionId] });
			queryClient.invalidateQueries({ queryKey: ["processExecutions"] });
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
			queryClient.invalidateQueries({ queryKey: ["executions", executionId] });
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
			queryClient.invalidateQueries({ queryKey: ["executions", executionId] });
			queryClient.invalidateQueries({ queryKey: ["processExecutions"] });
		},
	});
}
