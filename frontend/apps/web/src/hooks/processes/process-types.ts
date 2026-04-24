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
  status?: ProcessStatus | undefined;
  category?: ProcessCategory | undefined;
  owner?: string | undefined;
  activeOnly?: boolean | undefined;
}

interface CreateProcessData {
  projectId: string;
  name: string;
  description?: string | undefined;
  purpose?: string | undefined;
  category?: ProcessCategory | undefined;
  tags?: string[] | undefined;
  stages?: ProcessStage[] | undefined;
  swimlanes?: ProcessSwimlane[] | undefined;
  inputs?: ProcessInput[] | undefined;
  outputs?: ProcessOutput[] | undefined;
  triggers?: ProcessTrigger[] | undefined;
  exitCriteria?: string[] | undefined;
  bpmnXml?: string | undefined;
  owner?: string | undefined;
  responsibleTeam?: string | undefined;
  expectedDurationHours?: number | undefined;
  slaHours?: number | undefined;
  relatedProcessIds?: string[] | undefined;
  metadata?: Record<string, unknown> | undefined;
}

interface CreateExecutionData {
  processId: string;
  triggerItemId?: string | undefined;
  contextData?: Record<string, unknown> | undefined;
}

interface FetchExecutionsParams {
  processId: string;
  status?: ExecutionStatus | undefined;
  limit: number;
}

export {
  type CreateExecutionData,
  type CreateProcessData,
  type FetchExecutionsParams,
  type ProcessFilters,
};
