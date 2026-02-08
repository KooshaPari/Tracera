import type { ExecutionStatus, Process, ProcessCategory, ProcessExecution, ProcessStatus } from '@tracertm/types';

import {
  asRecord,
  getOptionalArray,
  getOptionalBoolean,
  getOptionalNumber,
  getOptionalRecord,
  getOptionalString,
  getOptionalStringArray,
  getRequiredArray,
  getRequiredBoolean,
  getRequiredNumber,
  getRequiredString,
  parseNumberMap,
  toStringId,
  type JsonRecord,
} from './process-guards';

function parseProcessStatus(value: unknown): ProcessStatus {
  const str = parseRequiredString(value, 'status');
  switch (str) {
    case 'active':
      return 'active';
    case 'archived':
      return 'archived';
    case 'deprecated':
      return 'deprecated';
    case 'draft':
      return 'draft';
    case 'retired':
      return 'retired';
    default:
      throw new Error(`Invalid status value: ${str}`);
  }
}

function parseProcessCategory(value: unknown): ProcessCategory {
  const str = parseRequiredString(value, 'category');
  switch (str) {
    case 'compliance':
      return 'compliance';
    case 'development':
      return 'development';
    case 'integration':
      return 'integration';
    case 'management':
      return 'management';
    case 'operational':
      return 'operational';
    case 'other':
      return 'other';
    case 'support':
      return 'support';
    default:
      throw new Error(`Invalid category value: ${str}`);
  }
}

function parseExecutionStatus(value: unknown): ExecutionStatus {
  const str = parseRequiredString(value, 'status');
  switch (str) {
    case 'cancelled':
      return 'cancelled';
    case 'completed':
      return 'completed';
    case 'failed':
      return 'failed';
    case 'in_progress':
      return 'in_progress';
    case 'pending':
      return 'pending';
    default:
      throw new Error(`Invalid status value: ${str}`);
  }
}

function parseRequiredString(value: unknown, key: string): string {
  if (typeof value !== 'string' || value.length === 0) {
    throw new Error(`Missing or invalid required string field: ${key}`);
  }
  return value;
}

function parseProcess(input: unknown): Process {
  const data = asRecord(input, 'process');

  return {
    activatedAt: getOptionalString(data, 'activated_at'),
    activatedBy: getOptionalString(data, 'activated_by'),
    bpmnDiagramUrl: getOptionalString(data, 'bpmn_diagram_url'),
    bpmnXml: getOptionalString(data, 'bpmn_xml'),
    category: data['category'] === undefined ? undefined : parseProcessCategory(data['category']),
    createdAt: getRequiredString(data, 'created_at'),
    deprecatedAt: getOptionalString(data, 'deprecated_at'),
    deprecatedBy: getOptionalString(data, 'deprecated_by'),
    deprecationReason: getOptionalString(data, 'deprecation_reason'),
    description: getOptionalString(data, 'description'),
    exitCriteria: getOptionalStringArray(data, 'exit_criteria'),
    expectedDurationHours: getOptionalNumber(data, 'expected_duration_hours'),
    id: toStringId(data['id'], 'id'),
    inputs: getOptionalArray(data, 'inputs')?.map((item: unknown) => item) as Process['inputs'],
    isActiveVersion: getRequiredBoolean(data, 'is_active_version'),
    metadata: getOptionalRecord(data, 'metadata'),
    name: getRequiredString(data, 'name'),
    outputs: getOptionalArray(data, 'outputs')?.map((item: unknown) => item) as Process['outputs'],
    owner: getOptionalString(data, 'owner'),
    parentVersionId: getOptionalString(data, 'parent_version_id'),
    processNumber: getRequiredString(data, 'process_number'),
    projectId: getRequiredString(data, 'project_id'),
    purpose: getOptionalString(data, 'purpose'),
    relatedProcessIds: getOptionalStringArray(data, 'related_process_ids'),
    responsibleTeam: getOptionalString(data, 'responsible_team'),
    slaHours: getOptionalNumber(data, 'sla_hours'),
    stages: getOptionalArray(data, 'stages')?.map((item: unknown) => item) as Process['stages'],
    status: parseProcessStatus(data['status']),
    swimlanes: getOptionalArray(data, 'swimlanes')?.map((item: unknown) => item) as Process['swimlanes'],
    tags: getOptionalStringArray(data, 'tags'),
    triggers: getOptionalArray(data, 'triggers')?.map((item: unknown) => item) as Process['triggers'],
    updatedAt: getRequiredString(data, 'updated_at'),
    version: getRequiredNumber(data, 'version'),
    versionNotes: getOptionalString(data, 'version_notes'),
    versionNumber: getRequiredNumber(data, 'version_number'),
  };
}

function parseExecution(input: unknown): ProcessExecution {
  const data = asRecord(input, 'execution');

  return {
    completedAt: getOptionalString(data, 'completed_at'),
    completedBy: getOptionalString(data, 'completed_by'),
    completedStages: getOptionalStringArray(data, 'completed_stages'),
    contextData: getOptionalRecord(data, 'context_data'),
    createdAt: getRequiredString(data, 'created_at'),
    currentStageId: getOptionalString(data, 'current_stage_id'),
    executionNumber: getRequiredString(data, 'execution_number'),
    id: toStringId(data['id'], 'id'),
    initiatedBy: getOptionalString(data, 'initiated_by'),
    outputItemIds: getOptionalStringArray(data, 'output_item_ids'),
    processId: getRequiredString(data, 'process_id'),
    resultSummary: getOptionalString(data, 'result_summary'),
    startedAt: getOptionalString(data, 'started_at'),
    status: parseExecutionStatus(data['status']),
    triggerItemId: getOptionalString(data, 'trigger_item_id'),
    updatedAt: getRequiredString(data, 'updated_at'),
  };
}

function parseProcessStats(input: unknown): {
  projectId: string;
  byStatus: Record<string, number>;
  byCategory: Record<string, number>;
  total: number;
} {
  const data = asRecord(input, 'process stats');
  return {
    byCategory: parseNumberMap(getOptionalRecord(data, 'by_category')),
    byStatus: parseNumberMap(getOptionalRecord(data, 'by_status')),
    projectId: getRequiredString(data, 'project_id'),
    total: getOptionalNumber(data, 'total') ?? 0,
  };
}

function parseIdProcessNumber(input: unknown): { id: string; processNumber: string } {
  const data = asRecord(input, 'create process response');
  return {
    id: toStringId(data['id'], 'id'),
    processNumber: getRequiredString(data, 'process_number'),
  };
}

function parseIdVersion(input: unknown): { id: string; version: number } {
  const data = asRecord(input, 'update process response');
  return {
    id: toStringId(data['id'], 'id'),
    version: getRequiredNumber(data, 'version'),
  };
}

function parseProcessVersionResponse(input: unknown): {
  id: string;
  processNumber: string;
  versionNumber: number;
  parentVersionId: string;
} {
  const data = asRecord(input, 'create version response');
  return {
    id: toStringId(data['id'], 'id'),
    parentVersionId: getRequiredString(data, 'parent_version_id'),
    processNumber: getRequiredString(data, 'process_number'),
    versionNumber: getRequiredNumber(data, 'version_number'),
  };
}

function parseActivationResponse(input: unknown): { id: string; status: string; isActiveVersion: boolean } {
  const data = asRecord(input, 'activate response');
  return {
    id: toStringId(data['id'], 'id'),
    isActiveVersion: getRequiredBoolean(data, 'is_active_version'),
    status: getRequiredString(data, 'status'),
  };
}

function parseStatusResponse(input: unknown): { id: string; status: string } {
  const data = asRecord(input, 'status response');
  return {
    id: toStringId(data['id'], 'id'),
    status: getRequiredString(data, 'status'),
  };
}

function parseExecutionCreateResponse(input: unknown): { id: string; executionNumber: string } {
  const data = asRecord(input, 'create execution response');
  return {
    executionNumber: getRequiredString(data, 'execution_number'),
    id: toStringId(data['id'], 'id'),
  };
}

function parseAdvanceResponse(input: unknown): {
  id: string;
  currentStageId: string;
  completedStages: string[];
} {
  const data = asRecord(input, 'advance response');
  return {
    completedStages: getRequiredArray(data, 'completed_stages').map((item: unknown) => parseRequiredString(item, 'completed_stages')),
    currentStageId: getRequiredString(data, 'current_stage_id'),
    id: toStringId(data['id'], 'id'),
  };
}

export {
  parseActivationResponse,
  parseAdvanceResponse,
  parseExecution,
  parseExecutionCreateResponse,
  parseIdProcessNumber,
  parseIdVersion,
  parseProcess,
  parseProcessStats,
  parseProcessVersionResponse,
  parseStatusResponse,
};

