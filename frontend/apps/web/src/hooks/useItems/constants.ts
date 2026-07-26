import type {
  AutomationStatus,
  CodeSymbolType,
  ComplexityLevel,
  DefectItem,
  DocContentType,
  ItemStatus,
  MaturityLevel,
  Priority,
  RiskLevel,
  TestCaseType,
  TestItem,
  TestResultStatus,
  UserStoryItem,
  ViewType,
} from '@tracertm/types';

const VIEW_TYPE_VALUES: ViewType[] = [
  'FEATURE',
  'feature',
  'CODE',
  'code',
  'TEST',
  'test',
  'API',
  'api',
  'DATABASE',
  'database',
  'WIREFRAME',
  'wireframe',
  'DOCUMENTATION',
  'documentation',
  'DEPLOYMENT',
  'deployment',
  'architecture',
  'configuration',
  'dataflow',
  'dependency',
  'domain',
  'infrastructure',
  'journey',
  'monitoring',
  'performance',
  'security',
];

const ITEM_STATUS_VALUES: ItemStatus[] = ['todo', 'in_progress', 'done', 'blocked', 'cancelled'];
const PRIORITY_VALUES: Priority[] = ['low', 'medium', 'high', 'critical'];

const TEST_CASE_TYPES: TestCaseType[] = [
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
];

const AUTOMATION_STATUS_VALUES: AutomationStatus[] = [
  'not_automated',
  'in_progress',
  'automated',
  'cannot_automate',
];

const TEST_RESULT_STATUS_VALUES: TestResultStatus[] = [
  'passed',
  'failed',
  'skipped',
  'blocked',
  'error',
];

const DEFECT_SEVERITY_VALUES: NonNullable<DefectItem['severity']>[] = [
  'critical',
  'high',
  'medium',
  'low',
];

const CODE_SYMBOL_TYPES: CodeSymbolType[] = [
  'file',
  'module',
  'class',
  'interface',
  'function',
  'method',
  'variable',
  'constant',
  'type',
  'enum',
  'component',
  'hook',
  'route',
  'handler',
  'middleware',
  'model',
  'schema',
  'migration',
  'test',
  'fixture',
];

const DOC_CONTENT_TYPES: DocContentType[] = [
  'heading',
  'paragraph',
  'code_block',
  'list',
  'table',
  'blockquote',
  'image',
  'link',
  'mixed',
];

const MATURITY_LEVELS: MaturityLevel[] = [
  'idea',
  'draft',
  'defined',
  'implemented',
  'verified',
  'stable',
  'deprecated',
];

const COMPLEXITY_LEVELS: ComplexityLevel[] = [
  'trivial',
  'simple',
  'moderate',
  'complex',
  'very_complex',
];

const RISK_LEVELS: RiskLevel[] = ['none', 'low', 'medium', 'high', 'critical'];

const DEFAULT_STATUS: ItemStatus = 'todo';
const DEFAULT_PRIORITY: Priority = 'medium';
const DEFAULT_VIEW: ViewType = 'feature';

const DEFAULT_VERSION = 1;

const EMPTY_STRING = '';

const ITEM_TYPE_REQUIREMENT = 'requirement';
const ITEM_TYPE_EPIC = 'epic';
const ITEM_TYPE_TASK = 'task';
const ITEM_TYPE_BUG = 'bug';
const ITEM_TYPE_DEFECT = 'defect';
const ITEM_TYPE_TEST = 'test';
const ITEM_TYPE_TEST_CASE = 'test_case';
const ITEM_TYPE_TEST_SUITE = 'test_suite';
const ITEM_TYPE_USER_STORY = 'user_story';
const ITEM_TYPE_STORY = 'story';

const TEST_ITEM_TYPES = new Set<TestItem['type']>([
  ITEM_TYPE_TEST,
  ITEM_TYPE_TEST_CASE,
  ITEM_TYPE_TEST_SUITE,
]);

const USER_STORY_TYPES = new Set<UserStoryItem['type']>([ITEM_TYPE_USER_STORY, ITEM_TYPE_STORY]);

const DEFECT_TYPES = new Set<DefectItem['type']>([ITEM_TYPE_BUG, ITEM_TYPE_DEFECT]);

export {
  AUTOMATION_STATUS_VALUES,
  CODE_SYMBOL_TYPES,
  COMPLEXITY_LEVELS,
  DEFECT_SEVERITY_VALUES,
  DEFECT_TYPES,
  DEFAULT_PRIORITY,
  DEFAULT_STATUS,
  DEFAULT_VERSION,
  DEFAULT_VIEW,
  DOC_CONTENT_TYPES,
  EMPTY_STRING,
  ITEM_STATUS_VALUES,
  ITEM_TYPE_BUG,
  ITEM_TYPE_DEFECT,
  ITEM_TYPE_EPIC,
  ITEM_TYPE_REQUIREMENT,
  ITEM_TYPE_STORY,
  ITEM_TYPE_TASK,
  ITEM_TYPE_TEST,
  ITEM_TYPE_TEST_CASE,
  ITEM_TYPE_TEST_SUITE,
  ITEM_TYPE_USER_STORY,
  MATURITY_LEVELS,
  PRIORITY_VALUES,
  RISK_LEVELS,
  TEST_CASE_TYPES,
  TEST_ITEM_TYPES,
  TEST_RESULT_STATUS_VALUES,
  USER_STORY_TYPES,
  VIEW_TYPE_VALUES,
};
