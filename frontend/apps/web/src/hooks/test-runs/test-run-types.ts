import type { TestResultStatus, TestRunStatus, TestRunType } from '@tracertm/types';

interface TestRunFilters {
  projectId: string;
  status?: TestRunStatus;
  runType?: TestRunType;
  suiteId?: string;
  environment?: string;
  initiatedBy?: string;
  search?: string;
  skip?: number;
  limit?: number;
}

interface CreateTestRunData {
  projectId: string;
  name: string;
  description?: string;
  suiteId?: string;
  runType?: TestRunType;
  environment?: string;
  buildNumber?: string;
  buildUrl?: string;
  branch?: string;
  commitSha?: string;
  scheduledAt?: string;
  initiatedBy?: string;
  notes?: string;
  tags?: string[];
  externalRunId?: string;
  metadata?: Record<string, unknown>;
}

interface SubmitTestResultData {
  testCaseId: string;
  status: TestResultStatus;
  executedBy?: string;
  actualResult?: string;
  failureReason?: string;
  errorMessage?: string;
  stackTrace?: string;
  screenshots?: string[];
  logsUrl?: string;
  attachments?: string[];
  stepResults?: {
    stepNumber: number;
    status: TestResultStatus;
    actualResult?: string;
    notes?: string;
  }[];
  notes?: string;
  isFlaky?: boolean;
  linkedDefectIds?: string[];
  createdDefectId?: string;
  metadata?: Record<string, unknown>;
}

export { type CreateTestRunData, type SubmitTestResultData, type TestRunFilters };
