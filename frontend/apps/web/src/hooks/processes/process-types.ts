import type {
  ExecutionStatus,
  ProcessCategory,
  ProcessInput,
  ProcessOutput,
  ProcessStage,
  ProcessStatus,
  ProcessSwimlane,
  ProcessTrigger,
} from '@tracertm/types';

interface ProcessFilters {
  projectId: string;
  status?: ProcessStatus;
  category?: ProcessCategory;
  owner?: string;
  activeOnly?: boolean;
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

interface CreateExecutionData {
  processId: string;
  triggerItemId?: string;
  contextData?: Record<string, unknown>;
}

interface FetchExecutionsParams {
  processId: string;
  status?: ExecutionStatus;
  limit: number;
}

export {
  type CreateExecutionData,
  type CreateProcessData,
  type FetchExecutionsParams,
  type ProcessFilters,
};

