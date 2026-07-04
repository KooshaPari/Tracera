import { z } from 'zod';

const MAX_ASSIGNED_TO_LENGTH = 255;
const MAX_AUTOMATION_FRAMEWORK_LENGTH = 100;
const MAX_AUTOMATION_NOTES_LENGTH = 2000;
const MAX_AUTOMATION_SCRIPT_PATH_LENGTH = 500;
const MAX_CATEGORY_LENGTH = 100;
const MAX_DESCRIPTION_LENGTH = 5000;
const MIN_ESTIMATED_DURATION_MINUTES = 1;
const MAX_EXPECTED_RESULT_LENGTH = 2000;
const MAX_OBJECTIVE_LENGTH = 2000;
const MAX_POSTCONDITIONS_LENGTH = 2000;
const MAX_PRECONDITIONS_LENGTH = 2000;
const MIN_STEP_ACTION_LENGTH = 1;
const MIN_TITLE_LENGTH = 1;
const MAX_TITLE_LENGTH = 500;

const testTypes = [
  'functional',
  'integration',
  'unit',
  'e2e',
  'performance',
  'security',
  'accessibility',
  'regression',
  'smoke',
  'exploratory',
] as const;

const priorities = ['critical', 'high', 'medium', 'low'] as const;

const automationStatuses = [
  'not_automated',
  'in_progress',
  'automated',
  'cannot_automate',
] as const;

const testStepSchema = z.object({
  action: z.string().min(MIN_STEP_ACTION_LENGTH, 'Action is required'),
  expectedResult: z.string().optional(),
  testData: z.string().optional(),
});

const testCaseSchema = z.object({
  assignedTo: z.string().max(MAX_ASSIGNED_TO_LENGTH).optional(),
  automationFramework: z.string().max(MAX_AUTOMATION_FRAMEWORK_LENGTH).optional(),
  automationNotes: z.string().max(MAX_AUTOMATION_NOTES_LENGTH).optional(),
  automationScriptPath: z.string().max(MAX_AUTOMATION_SCRIPT_PATH_LENGTH).optional(),
  automationStatus: z.enum(automationStatuses),
  category: z.string().max(MAX_CATEGORY_LENGTH).optional(),
  description: z.string().max(MAX_DESCRIPTION_LENGTH).optional(),
  estimatedDurationMinutes: z.coerce.number().min(MIN_ESTIMATED_DURATION_MINUTES).optional(),
  expectedResult: z.string().max(MAX_EXPECTED_RESULT_LENGTH).optional(),
  objective: z.string().max(MAX_OBJECTIVE_LENGTH).optional(),
  postconditions: z.string().max(MAX_POSTCONDITIONS_LENGTH).optional(),
  preconditions: z.string().max(MAX_PRECONDITIONS_LENGTH).optional(),
  priority: z.enum(priorities),
  tags: z.string().optional(),
  testSteps: z.array(testStepSchema).optional(),
  testType: z.enum(testTypes),
  title: z
    .string()
    .min(MIN_TITLE_LENGTH, 'Title is required')
    .max(MAX_TITLE_LENGTH, 'Title too long'),
});

type TestCaseFormInput = z.input<typeof testCaseSchema>;
type TestCaseFormData = z.infer<typeof testCaseSchema>;

const categoryOptions = [
  'User Authentication',
  'User Interface',
  'API',
  'Database',
  'Integration',
  'Performance',
  'Security',
  'Accessibility',
  'Mobile',
  'Desktop',
  'Other',
];

const typeLabels: Record<(typeof testTypes)[number], string> = {
  accessibility: 'Accessibility',
  e2e: 'End-to-End',
  exploratory: 'Exploratory',
  functional: 'Functional',
  integration: 'Integration',
  performance: 'Performance',
  regression: 'Regression',
  security: 'Security',
  smoke: 'Smoke',
  unit: 'Unit',
};

const automationLabels: Record<(typeof automationStatuses)[number], string> = {
  automated: 'Fully Automated',
  cannot_automate: 'Cannot Be Automated',
  in_progress: 'Automation In Progress',
  not_automated: 'Not Automated (Manual)',
};

export {
  automationLabels,
  automationStatuses,
  categoryOptions,
  priorities,
  testCaseSchema,
  testTypes,
  typeLabels,
};
export type { TestCaseFormData, TestCaseFormInput };
