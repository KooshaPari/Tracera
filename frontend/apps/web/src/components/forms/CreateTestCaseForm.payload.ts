import type { AutomationStatus, TestCasePriority, TestCaseType, TestStep } from '@tracertm/types';

import type { TestCaseFormData } from './CreateTestCaseForm.constants';

export interface CreateTestCasePayload {
  projectId: string;
  title: string;
  testType: TestCaseType;
  priority: TestCasePriority;
  automationStatus: AutomationStatus;
  assignedTo?: string;
  automationFramework?: string;
  automationNotes?: string;
  automationScriptPath?: string;
  category?: string;
  description?: string;
  estimatedDurationMinutes?: number;
  expectedResult?: string;
  objective?: string;
  postconditions?: string;
  preconditions?: string;
  tags?: string[];
  testSteps?: TestStep[];
}

function isNonEmptyString(value: unknown): value is string {
  return typeof value === 'string' && value.trim() !== '';
}

function parseTags(value: string): string[] {
  return value
    .split(',')
    .map((segment) => segment.trim())
    .filter((tag) => tag.length > 0);
}

function buildTestSteps(testSteps: TestCaseFormData['testSteps']): TestStep[] | undefined {
  if (!Array.isArray(testSteps) || testSteps.length === 0) {
    return undefined;
  }

  return testSteps.map((step, index) => ({
    action: step.action,
    expectedResult: step.expectedResult ?? '',
    stepNumber: index + 1,
    testData: step.testData ?? '',
  }));
}

export function buildCreateTestCasePayload(
  data: TestCaseFormData,
  projectId: string,
): CreateTestCasePayload {
  const payload: CreateTestCasePayload = {
    automationStatus: data.automationStatus,
    priority: data.priority,
    projectId,
    testType: data.testType,
    title: data.title,
  };

  type OptionalStringField =
    | 'description'
    | 'objective'
    | 'category'
    | 'preconditions'
    | 'expectedResult'
    | 'postconditions'
    | 'automationScriptPath'
    | 'automationFramework'
    | 'automationNotes'
    | 'assignedTo';

  const optionalStringFields: [OptionalStringField, TestCaseFormData[keyof TestCaseFormData]][] = [
    ['description', data.description],
    ['objective', data.objective],
    ['category', data.category],
    ['preconditions', data.preconditions],
    ['expectedResult', data.expectedResult],
    ['postconditions', data.postconditions],
    ['automationScriptPath', data.automationScriptPath],
    ['automationFramework', data.automationFramework],
    ['automationNotes', data.automationNotes],
    ['assignedTo', data.assignedTo],
  ];

  optionalStringFields.forEach(([key, value]) => {
    if (isNonEmptyString(value)) {
      payload[key] = value;
    }
  });

  if (isNonEmptyString(data.tags)) {
    payload.tags = parseTags(data.tags);
  }

  if (typeof data.estimatedDurationMinutes === 'number') {
    payload.estimatedDurationMinutes = data.estimatedDurationMinutes;
  }

  const testSteps = buildTestSteps(data.testSteps);
  if (testSteps) {
    payload.testSteps = testSteps;
  }

  return payload;
}
