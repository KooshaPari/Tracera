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
} from '@tracertm/types';

import { processGuards } from './process-guards';

function parseRequiredString(value: unknown, key: string): string {
  if (typeof value !== 'string' || value.length === 0) {
    throw new TypeError(`Missing or invalid required string field: ${key}`);
  }
  return value;
}

function parseProcessStatus(value: unknown): ProcessStatus {
  const str = parseRequiredString(value, 'status');
  switch (str) {
    case 'active': {
      return 'active';
    }
    case 'archived': {
      return 'archived';
    }
    case 'deprecated': {
      return 'deprecated';
    }
    case 'draft': {
      return 'draft';
    }
    case 'retired': {
      return 'retired';
    }
    default: {
      throw new Error(`Invalid status value: ${str}`);
    }
  }
}

function parseProcessCategory(value: unknown): ProcessCategory {
  const str = parseRequiredString(value, 'category');
  switch (str) {
    case 'compliance': {
      return 'compliance';
    }
    case 'development': {
      return 'development';
    }
    case 'integration': {
      return 'integration';
    }
    case 'management': {
      return 'management';
    }
    case 'operational': {
      return 'operational';
    }
    case 'other': {
      return 'other';
    }
    case 'support': {
      return 'support';
    }
    default: {
      throw new Error(`Invalid category value: ${str}`);
    }
  }
}

function parseExecutionStatus(value: unknown): ExecutionStatus {
  const str = parseRequiredString(value, 'status');
  switch (str) {
    case 'cancelled': {
      return 'cancelled';
    }
    case 'completed': {
      return 'completed';
    }
    case 'failed': {
      return 'failed';
    }
    case 'in_progress': {
      return 'in_progress';
    }
    case 'pending': {
      return 'pending';
    }
    default: {
      throw new Error(`Invalid status value: ${str}`);
    }
  }
}

function parseInput(item: unknown): ProcessInput {
  const data = processGuards.asRecord(item, 'process input');
  return {
    description: processGuards.getOptionalString(data, 'description'),
    name: processGuards.getRequiredString(data, 'name'),
    required: processGuards.getOptionalBoolean(data, 'required'),
    type: processGuards.getRequiredString(data, 'type'),
  };
}

function parseOutput(item: unknown): ProcessOutput {
  const data = processGuards.asRecord(item, 'process output');
  return {
    description: processGuards.getOptionalString(data, 'description'),
    name: processGuards.getRequiredString(data, 'name'),
    type: processGuards.getRequiredString(data, 'type'),
  };
}

function parseStage(item: unknown): ProcessStage {
  const data = processGuards.asRecord(item, 'process stage');
  return {
    assignedRole: processGuards.getOptionalString(data, 'assigned_role'),
    description: processGuards.getOptionalString(data, 'description'),
    estimatedDurationMinutes: processGuards.getOptionalNumber(data, 'estimated_duration_minutes'),
    id: processGuards.getRequiredString(data, 'id'),
    name: processGuards.getRequiredString(data, 'name'),
    order: processGuards.getRequiredNumber(data, 'order'),
    required: processGuards.getOptionalBoolean(data, 'required'),
  };
}

function parseSwimlane(item: unknown): ProcessSwimlane {
  const data = processGuards.asRecord(item, 'process swimlane');
  return {
    description: processGuards.getOptionalString(data, 'description'),
    id: processGuards.getRequiredString(data, 'id'),
    name: processGuards.getRequiredString(data, 'name'),
    role: processGuards.getOptionalString(data, 'role'),
  };
}

function parseTrigger(item: unknown): ProcessTrigger {
  const data = processGuards.asRecord(item, 'process trigger');
  return {
    condition: processGuards.getOptionalString(data, 'condition'),
    description: processGuards.getOptionalString(data, 'description'),
    name: processGuards.getRequiredString(data, 'name'),
    type: processGuards.getRequiredString(data, 'type'),
  };
}

function parseProcess(input: unknown): Process {
  const data = processGuards.asRecord(input, 'process');
  const stagesRaw = processGuards.getOptionalArray(data, 'stages');
  const swimlanesRaw = processGuards.getOptionalArray(data, 'swimlanes');
  const inputsRaw = processGuards.getOptionalArray(data, 'inputs');
  const outputsRaw = processGuards.getOptionalArray(data, 'outputs');
  const triggersRaw = processGuards.getOptionalArray(data, 'triggers');

  return {
    activatedAt: processGuards.getOptionalString(data, 'activated_at'),
    activatedBy: processGuards.getOptionalString(data, 'activated_by'),
    bpmnDiagramUrl: processGuards.getOptionalString(data, 'bpmn_diagram_url'),
    bpmnXml: processGuards.getOptionalString(data, 'bpmn_xml'),
    category: data['category'] === undefined ? undefined : parseProcessCategory(data['category']),
    createdAt: processGuards.getRequiredString(data, 'created_at'),
    deprecatedAt: processGuards.getOptionalString(data, 'deprecated_at'),
    deprecatedBy: processGuards.getOptionalString(data, 'deprecated_by'),
    deprecationReason: processGuards.getOptionalString(data, 'deprecation_reason'),
    description: processGuards.getOptionalString(data, 'description'),
    exitCriteria: processGuards.getOptionalStringArray(data, 'exit_criteria'),
    expectedDurationHours: processGuards.getOptionalNumber(data, 'expected_duration_hours'),
    id: processGuards.toStringId(data['id'], 'id'),
    inputs: inputsRaw?.map((item: unknown) => parseInput(item)),
    isActiveVersion: processGuards.getRequiredBoolean(data, 'is_active_version'),
    metadata: processGuards.getOptionalRecord(data, 'metadata'),
    name: processGuards.getRequiredString(data, 'name'),
    outputs: outputsRaw?.map((item: unknown) => parseOutput(item)),
    owner: processGuards.getOptionalString(data, 'owner'),
    parentVersionId: processGuards.getOptionalString(data, 'parent_version_id'),
    processNumber: processGuards.getRequiredString(data, 'process_number'),
    projectId: processGuards.getRequiredString(data, 'project_id'),
    purpose: processGuards.getOptionalString(data, 'purpose'),
    relatedProcessIds: processGuards.getOptionalStringArray(data, 'related_process_ids'),
    responsibleTeam: processGuards.getOptionalString(data, 'responsible_team'),
    slaHours: processGuards.getOptionalNumber(data, 'sla_hours'),
    stages: stagesRaw?.map((item: unknown) => parseStage(item)),
    status: parseProcessStatus(data['status']),
    swimlanes: swimlanesRaw?.map((item: unknown) => parseSwimlane(item)),
    tags: processGuards.getOptionalStringArray(data, 'tags'),
    triggers: triggersRaw?.map((item: unknown) => parseTrigger(item)),
    updatedAt: processGuards.getRequiredString(data, 'updated_at'),
    version: processGuards.getRequiredNumber(data, 'version'),
    versionNotes: processGuards.getOptionalString(data, 'version_notes'),
    versionNumber: processGuards.getRequiredNumber(data, 'version_number'),
  };
}

function parseExecution(input: unknown): ProcessExecution {
  const data = processGuards.asRecord(input, 'execution');

  return {
    completedAt: processGuards.getOptionalString(data, 'completed_at'),
    completedBy: processGuards.getOptionalString(data, 'completed_by'),
    completedStages: processGuards.getOptionalStringArray(data, 'completed_stages'),
    contextData: processGuards.getOptionalRecord(data, 'context_data'),
    createdAt: processGuards.getRequiredString(data, 'created_at'),
    currentStageId: processGuards.getOptionalString(data, 'current_stage_id'),
    executionNumber: processGuards.getRequiredString(data, 'execution_number'),
    id: processGuards.toStringId(data['id'], 'id'),
    initiatedBy: processGuards.getOptionalString(data, 'initiated_by'),
    outputItemIds: processGuards.getOptionalStringArray(data, 'output_item_ids'),
    processId: processGuards.getRequiredString(data, 'process_id'),
    resultSummary: processGuards.getOptionalString(data, 'result_summary'),
    startedAt: processGuards.getOptionalString(data, 'started_at'),
    status: parseExecutionStatus(data['status']),
    triggerItemId: processGuards.getOptionalString(data, 'trigger_item_id'),
    updatedAt: processGuards.getRequiredString(data, 'updated_at'),
  };
}

function parseProcessStats(input: unknown): {
  projectId: string;
  byStatus: Record<string, number>;
  byCategory: Record<string, number>;
  total: number;
} {
  const data = processGuards.asRecord(input, 'process stats');
  return {
    byCategory: processGuards.parseNumberMap(processGuards.getOptionalRecord(data, 'by_category')),
    byStatus: processGuards.parseNumberMap(processGuards.getOptionalRecord(data, 'by_status')),
    projectId: processGuards.getRequiredString(data, 'project_id'),
    total: processGuards.getOptionalNumber(data, 'total') ?? 0,
  };
}

function parseIdProcessNumber(input: unknown): { id: string; processNumber: string } {
  const data = processGuards.asRecord(input, 'create process response');
  return {
    id: processGuards.toStringId(data['id'], 'id'),
    processNumber: processGuards.getRequiredString(data, 'process_number'),
  };
}

function parseIdVersion(input: unknown): { id: string; version: number } {
  const data = processGuards.asRecord(input, 'update process response');
  return {
    id: processGuards.toStringId(data['id'], 'id'),
    version: processGuards.getRequiredNumber(data, 'version'),
  };
}

function parseProcessVersionResponse(input: unknown): {
  id: string;
  processNumber: string;
  versionNumber: number;
  parentVersionId: string;
} {
  const data = processGuards.asRecord(input, 'create version response');
  return {
    id: processGuards.toStringId(data['id'], 'id'),
    parentVersionId: processGuards.getRequiredString(data, 'parent_version_id'),
    processNumber: processGuards.getRequiredString(data, 'process_number'),
    versionNumber: processGuards.getRequiredNumber(data, 'version_number'),
  };
}

function parseActivationResponse(input: unknown): {
  id: string;
  status: string;
  isActiveVersion: boolean;
} {
  const data = processGuards.asRecord(input, 'activate response');
  return {
    id: processGuards.toStringId(data['id'], 'id'),
    isActiveVersion: processGuards.getRequiredBoolean(data, 'is_active_version'),
    status: processGuards.getRequiredString(data, 'status'),
  };
}

function parseStatusResponse(input: unknown): { id: string; status: string } {
  const data = processGuards.asRecord(input, 'status response');
  return {
    id: processGuards.toStringId(data['id'], 'id'),
    status: processGuards.getRequiredString(data, 'status'),
  };
}

function parseExecutionCreateResponse(input: unknown): { id: string; executionNumber: string } {
  const data = processGuards.asRecord(input, 'create execution response');
  return {
    executionNumber: processGuards.getRequiredString(data, 'execution_number'),
    id: processGuards.toStringId(data['id'], 'id'),
  };
}

function parseAdvanceResponse(input: unknown): {
  id: string;
  currentStageId: string;
  completedStages: string[];
} {
  const data = processGuards.asRecord(input, 'advance response');
  const stages = processGuards.getRequiredArray(data, 'completed_stages');
  return {
    completedStages: stages.map((item: unknown) => parseRequiredString(item, 'completed_stages')),
    currentStageId: processGuards.getRequiredString(data, 'current_stage_id'),
    id: processGuards.toStringId(data['id'], 'id'),
  };
}

const processParsers = {
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
  processParsers,
};
