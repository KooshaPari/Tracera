import type { Process, ProcessExecution } from '@tracertm/types';

import { client } from '@/api/client';

import type {
  CreateExecutionData,
  CreateProcessData,
  FetchExecutionsParams,
  ProcessFilters,
} from './process-types';

import { processGuards } from './process-guards';
import { processParsers } from './process-parsers';

const { getAuthHeaders } = client;

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:4000';

interface ProcessesResponse {
  processes: Process[];
  total: number;
}

interface ExecutionsResponse {
  total: number;
  executions: ProcessExecution[];
}

async function fetchJson(url: string, init?: RequestInit): Promise<unknown> {
  const res = await fetch(url, init);
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Request failed: ${res.status} ${errorText}`);
  }
  const data: unknown = await res.json();
  return data;
}

function buildProcessesParams(filters: ProcessFilters): URLSearchParams {
  const params = new URLSearchParams();
  params.set('project_id', filters.projectId);

  const { status } = filters;
  if (status !== undefined && status.length > 0) {
    params.set('status', status);
  }

  const { category } = filters;
  if (category !== undefined && category.length > 0) {
    params.set('category', category);
  }

  const { owner } = filters;
  if (owner !== undefined && owner.length > 0) {
    params.set('owner', owner);
  }

  if (filters.activeOnly === true) {
    params.set('active_only', 'true');
  }

  return params;
}

async function fetchProcesses(filters: ProcessFilters): Promise<ProcessesResponse> {
  const params = buildProcessesParams(filters);
  const json = await fetchJson(`${API_URL}/api/v1/processes?${params.toString()}`, {
    headers: {
      'X-Bulk-Operation': 'true',
      ...getAuthHeaders(),
    },
  });
  const data = processGuards.asRecord(json, 'processes response');
  const rawProcesses = processGuards.getOptionalArray(data, 'processes') ?? [];
  const total = processGuards.getOptionalNumber(data, 'total') ?? 0;
  return {
    processes: rawProcesses.map((item: unknown) => processParsers.parseProcess(item)),
    total,
  };
}

async function fetchProcess(id: string): Promise<Process> {
  const json = await fetchJson(`${API_URL}/api/v1/processes/${id}`, {
    headers: getAuthHeaders(),
  });
  return processParsers.parseProcess(json);
}

async function createProcess(
  data: CreateProcessData,
): Promise<{ id: string; processNumber: string }> {
  const json = await fetchJson(`${API_URL}/api/v1/processes?project_id=${data.projectId}`, {
    body: JSON.stringify({
      bpmn_xml: data.bpmnXml,
      category: data.category,
      description: data.description,
      exit_criteria: data.exitCriteria,
      expected_duration_hours: data.expectedDurationHours,
      inputs: data.inputs,
      metadata: data.metadata ?? {},
      name: data.name,
      outputs: data.outputs,
      owner: data.owner,
      purpose: data.purpose,
      related_process_ids: data.relatedProcessIds,
      responsible_team: data.responsibleTeam,
      sla_hours: data.slaHours,
      stages: data.stages,
      swimlanes: data.swimlanes,
      tags: data.tags,
      triggers: data.triggers,
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  return processParsers.parseIdProcessNumber(json);
}

async function updateProcess(
  id: string,
  data: Partial<Omit<CreateProcessData, 'projectId'>>,
): Promise<{ id: string; version: number }> {
  const json = await fetchJson(`${API_URL}/api/v1/processes/${id}`, {
    body: JSON.stringify({
      bpmn_xml: data.bpmnXml,
      category: data.category,
      description: data.description,
      exit_criteria: data.exitCriteria,
      expected_duration_hours: data.expectedDurationHours,
      inputs: data.inputs,
      metadata: data.metadata,
      name: data.name,
      outputs: data.outputs,
      owner: data.owner,
      purpose: data.purpose,
      related_process_ids: data.relatedProcessIds,
      responsible_team: data.responsibleTeam,
      sla_hours: data.slaHours,
      stages: data.stages,
      swimlanes: data.swimlanes,
      tags: data.tags,
      triggers: data.triggers,
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'PUT',
  });
  return processParsers.parseIdVersion(json);
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
  const json = await fetchJson(`${API_URL}/api/v1/processes/${processId}/versions`, {
    body: JSON.stringify({ version_notes: versionNotes }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  return processParsers.parseProcessVersionResponse(json);
}

async function activateProcess(
  processId: string,
): Promise<{ id: string; status: string; isActiveVersion: boolean }> {
  const json = await fetchJson(`${API_URL}/api/v1/processes/${processId}/activate`, {
    body: JSON.stringify({}),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'PUT',
  });
  return processParsers.parseActivationResponse(json);
}

async function deprecateProcess(
  processId: string,
  deprecationReason?: string,
): Promise<{ id: string; status: string }> {
  const json = await fetchJson(`${API_URL}/api/v1/processes/${processId}/deprecate`, {
    body: JSON.stringify({ deprecation_reason: deprecationReason }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'PUT',
  });
  return processParsers.parseStatusResponse(json);
}

async function deleteProcess(id: string): Promise<void> {
  await fetchJson(`${API_URL}/api/v1/processes/${id}`, {
    headers: getAuthHeaders(),
    method: 'DELETE',
  });
}

async function fetchProcessStats(projectId: string): Promise<{
  projectId: string;
  byStatus: Record<string, number>;
  byCategory: Record<string, number>;
  total: number;
}> {
  const json = await fetchJson(`${API_URL}/api/v1/projects/${projectId}/processes/stats`, {
    headers: getAuthHeaders(),
  });
  return processParsers.parseProcessStats(json);
}

async function createExecution(
  data: CreateExecutionData,
): Promise<{ id: string; executionNumber: string }> {
  const json = await fetchJson(`${API_URL}/api/v1/processes/${data.processId}/executions`, {
    body: JSON.stringify({
      context_data: data.contextData ?? {},
      process_id: data.processId,
      trigger_item_id: data.triggerItemId,
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  return processParsers.parseExecutionCreateResponse(json);
}

function buildExecutionsParams(paramsIn: FetchExecutionsParams): URLSearchParams {
  const params = new URLSearchParams();
  const { status } = paramsIn;
  if (status !== undefined && status.length > 0) {
    params.set('status', status);
  }
  params.set('limit', String(paramsIn.limit));
  return params;
}

async function fetchExecutions(paramsIn: FetchExecutionsParams): Promise<ExecutionsResponse> {
  const params = buildExecutionsParams(paramsIn);
  const json = await fetchJson(
    `${API_URL}/api/v1/processes/${paramsIn.processId}/executions?${params.toString()}`,
    { headers: getAuthHeaders() },
  );
  const data = processGuards.asRecord(json, 'executions response');
  const rawExecutions = processGuards.getOptionalArray(data, 'executions') ?? [];
  const total = processGuards.getOptionalNumber(data, 'total') ?? 0;
  return {
    executions: rawExecutions.map((item: unknown) => processParsers.parseExecution(item)),
    total,
  };
}

async function fetchExecution(executionId: string): Promise<ProcessExecution> {
  const json = await fetchJson(`${API_URL}/api/v1/executions/${executionId}`, {
    headers: getAuthHeaders(),
  });
  return processParsers.parseExecution(json);
}

async function startExecution(executionId: string): Promise<{ id: string; status: string }> {
  const json = await fetchJson(`${API_URL}/api/v1/executions/${executionId}/start`, {
    headers: getAuthHeaders(),
    method: 'POST',
  });
  return processParsers.parseStatusResponse(json);
}

async function advanceExecution(
  executionId: string,
  stageId: string,
): Promise<{ id: string; currentStageId: string; completedStages: string[] }> {
  const json = await fetchJson(
    `${API_URL}/api/v1/executions/${executionId}/advance?stage_id=${stageId}`,
    { headers: getAuthHeaders(), method: 'POST' },
  );
  return processParsers.parseAdvanceResponse(json);
}

async function completeExecution(
  executionId: string,
  resultSummary?: string,
  outputItemIds?: string[],
): Promise<{ id: string; status: string }> {
  const json = await fetchJson(`${API_URL}/api/v1/executions/${executionId}/complete`, {
    body: JSON.stringify({ output_item_ids: outputItemIds, result_summary: resultSummary }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  return processParsers.parseStatusResponse(json);
}

const processApi = {
  activateProcess,
  advanceExecution,
  completeExecution,
  createExecution,
  createProcess,
  createProcessVersion,
  deprecateProcess,
  deleteProcess,
  fetchExecution,
  fetchExecutions,
  fetchProcess,
  fetchProcesses,
  fetchProcessStats,
  startExecution,
  updateProcess,
};

export {
  activateProcess,
  advanceExecution,
  completeExecution,
  createExecution,
  createProcess,
  createProcessVersion,
  deprecateProcess,
  deleteProcess,
  fetchExecution,
  fetchExecutions,
  fetchProcess,
  fetchProcesses,
  fetchProcessStats,
  processApi,
  type ExecutionsResponse,
  type ProcessesResponse,
  startExecution,
  updateProcess,
};
