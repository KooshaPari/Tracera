import type { TestResultStatus, TestRunStatus, TestRunType } from '@tracertm/types';

interface TestRunFilters {
  projectId: string;
  status?: TestRunStatus | undefined;
  runType?: TestRunType | undefined;
  suiteId?: string | undefined;
  environment?: string | undefined;
  initiatedBy?: string | undefined;
  search?: string | undefined;
  skip?: number | undefined;
  limit?: number | undefined;
}

interface CreateTestRunData {
  projectId: string;
  name: string;
  description?: string | undefined;
  suiteId?: string | undefined;
  runType?: TestRunType | undefined;
  environment?: string | undefined;
  buildNumber?: string | undefined;
  buildUrl?: string | undefined;
  branch?: string | undefined;
  commitSha?: string | undefined;
  scheduledAt?: string | undefined;
  initiatedBy?: string | undefined;
  notes?: string | undefined;
  tags?: string[] | undefined;
  externalRunId?: string | undefined;
  metadata?: Record<string, unknown> | undefined;
}

interface SubmitTestResultData {
  testCaseId: string;
  status: TestResultStatus;
  executedBy?: string | undefined;
  actualResult?: string | undefined;
  failureReason?: string | undefined;
  errorMessage?: string | undefined;
  stackTrace?: string | undefined;
  screenshots?: string[] | undefined;
  logsUrl?: string | undefined;
  attachments?: string[] | undefined;
  stepResults?: {
    stepNumber: number;
    status: TestResultStatus;
    actualResult?: string | undefined;
    notes?: string | undefined;
  }[];
  notes?: string | undefined;
  isFlaky?: boolean | undefined;
  linkedDefectIds?: string[] | undefined;
  createdDefectId?: string | undefined;
  metadata?: Record<string, unknown> | undefined;
}

export { type CreateTestRunData, type SubmitTestResultData, type TestRunFilters };
