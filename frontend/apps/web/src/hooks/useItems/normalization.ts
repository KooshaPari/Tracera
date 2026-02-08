import type * as Types from '@tracertm/types';

const VIEW_TYPE_VALUES: Types.ViewType[] = [
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

const ITEM_STATUS_VALUES: Types.ItemStatus[] = [
  'todo',
  'in_progress',
  'done',
  'blocked',
  'cancelled',
];
const PRIORITY_VALUES: Types.Priority[] = ['low', 'medium', 'high', 'critical'];

const TEST_CASE_TYPES: Types.TestCaseType[] = [
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

const AUTOMATION_STATUS_VALUES: Types.AutomationStatus[] = [
  'not_automated',
  'in_progress',
  'automated',
  'cannot_automate',
];

const TEST_RESULT_STATUS_VALUES: Types.TestResultStatus[] = [
  'passed',
  'failed',
  'skipped',
  'blocked',
  'error',
];

const DEFECT_SEVERITY_VALUES: Types.DefectItem['severity'][] = [
  'critical',
  'high',
  'medium',
  'low',
];

const CODE_SYMBOL_TYPES: Types.CodeSymbolType[] = [
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

const DOC_CONTENT_TYPES: Types.DocContentType[] = [
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

const MATURITY_LEVELS: Types.MaturityLevel[] = [
  'idea',
  'draft',
  'defined',
  'implemented',
  'verified',
  'stable',
  'deprecated',
];

const COMPLEXITY_LEVELS: Types.ComplexityLevel[] = [
  'trivial',
  'simple',
  'moderate',
  'complex',
  'very_complex',
];

const RISK_LEVELS: Types.RiskLevel[] = ['none', 'low', 'medium', 'high', 'critical'];

const DEFAULT_STATUS: Types.ItemStatus = 'todo';
const DEFAULT_PRIORITY: Types.Priority = 'medium';
const DEFAULT_VIEW: Types.ViewType = 'feature';

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

const TEST_ITEM_TYPES = new Set<Types.TestItem['type']>([
  ITEM_TYPE_TEST,
  ITEM_TYPE_TEST_CASE,
  ITEM_TYPE_TEST_SUITE,
]);

const USER_STORY_TYPES = new Set<Types.UserStoryItem['type']>([
  ITEM_TYPE_USER_STORY,
  ITEM_TYPE_STORY,
]);

const DEFECT_TYPES = new Set<Types.DefectItem['type']>([ITEM_TYPE_BUG, ITEM_TYPE_DEFECT]);

type ApiItem = Record<string, unknown>;

type MutableItem = Types.Item & { view: Types.ViewType };

type CreateItemData = {
  projectId: string;
  view: Types.ViewType;
  type: string;
  title: string;
  description?: string;
  status: Types.ItemStatus;
  priority: Types.Priority;
  parentId?: string;
  owner?: string;
};

type CreateItemWithSpecData = {
  projectId: string;
  item: Partial<Types.Item>;
  spec: Record<string, unknown>;
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return value instanceof Object;
}

function readString(value: unknown): string | undefined {
  if (typeof value === 'string') {
    return value;
  }
  return undefined;
}

function readNonEmptyString(value: unknown): string | undefined {
  if (typeof value === 'string') {
    const trimmed = value.trim();
    if (trimmed !== '') {
      return value;
    }
  }
  return undefined;
}

function readNumber(value: unknown): number | undefined {
  if (typeof value === 'number' && !Number.isNaN(value)) {
    return value;
  }
  return undefined;
}

function readBoolean(value: unknown): boolean | undefined {
  if (typeof value === 'boolean') {
    return value;
  }
  return undefined;
}

function readStringArray(value: unknown): string[] | undefined {
  if (Array.isArray(value)) {
    const allStrings = value.every((entry) => typeof entry === 'string');
    if (allStrings) {
      return value;
    }
  }
  return undefined;
}

function readNumberArray(value: unknown): number[] | undefined {
  if (Array.isArray(value)) {
    const allNumbers = value.every((entry) => typeof entry === 'number' && !Number.isNaN(entry));
    if (allNumbers) {
      return value;
    }
  }
  return undefined;
}

function readRecord(value: unknown): Record<string, unknown> | undefined {
  if (isRecord(value)) {
    return value;
  }
  return undefined;
}

function readEnumValue<T extends string>(value: unknown, allowed: readonly T[]): T | undefined {
  if (typeof value === 'string') {
    const match = allowed.find((entry) => entry === value);
    if (match !== undefined) {
      return match;
    }
  }
  return undefined;
}

function readStringField(item: ApiItem, snake: string, camel: string): string | undefined {
  const snakeValue = readString(item[snake]);
  if (snakeValue !== undefined) {
    return snakeValue;
  }
  const camelValue = readString(item[camel]);
  if (camelValue !== undefined) {
    return camelValue;
  }
  return undefined;
}

function readNumberField(item: ApiItem, snake: string, camel: string): number | undefined {
  const snakeValue = readNumber(item[snake]);
  if (snakeValue !== undefined) {
    return snakeValue;
  }
  const camelValue = readNumber(item[camel]);
  if (camelValue !== undefined) {
    return camelValue;
  }
  return undefined;
}

function readStringArrayField(item: ApiItem, snake: string, camel: string): string[] | undefined {
  const snakeValue = readStringArray(item[snake]);
  if (snakeValue !== undefined) {
    return snakeValue;
  }
  const camelValue = readStringArray(item[camel]);
  if (camelValue !== undefined) {
    return camelValue;
  }
  return undefined;
}

function requireStringField(item: ApiItem, key: string): string {
  const value = readString(item[key]);
  if (value !== undefined) {
    return value;
  }
  throw new Error(`Missing required field: ${key}`);
}

function normalizeStatus(value: unknown): Types.ItemStatus {
  const normalized = readEnumValue(value, ITEM_STATUS_VALUES);
  if (normalized !== undefined) {
    return normalized;
  }
  return DEFAULT_STATUS;
}

function normalizePriority(value: unknown): Types.Priority {
  const normalized = readEnumValue(value, PRIORITY_VALUES);
  if (normalized !== undefined) {
    return normalized;
  }
  return DEFAULT_PRIORITY;
}

function normalizeViewType(value: unknown): Types.ViewType {
  const normalized = readEnumValue(value, VIEW_TYPE_VALUES);
  if (normalized !== undefined) {
    return normalized;
  }
  return DEFAULT_VIEW;
}

function readCoverageMetrics(value: unknown): Types.CoverageMetrics | undefined {
  const record = readRecord(value);
  if (record) {
    const testCoverage = readNumber(record['testCoverage']);
    const docCoverage = readNumber(record['docCoverage']);
    const traceCoverage = readNumber(record['traceCoverage']);
    const overallCoverage = readNumber(record['overallCoverage']);
    if (
      testCoverage !== undefined &&
      docCoverage !== undefined &&
      traceCoverage !== undefined &&
      overallCoverage !== undefined
    ) {
      return {
        testCoverage,
        docCoverage,
        traceCoverage,
        overallCoverage,
      };
    }
  }
  return undefined;
}

function readItemDimensions(value: unknown): Types.ItemDimensions | undefined {
  const record = readRecord(value);
  if (record) {
    const maturity = readEnumValue(record['maturity'], MATURITY_LEVELS);
    const complexity = readEnumValue(record['complexity'], COMPLEXITY_LEVELS);
    const risk = readEnumValue(record['risk'], RISK_LEVELS);
    const coverage = readCoverageMetrics(record['coverage']);

    const custom = readRecord(record['custom']);
    let customValues: Record<string, string | number | boolean> | undefined;
    if (custom) {
      const entries = Object.entries(custom).filter(
        ([, entry]) =>
          typeof entry === 'string' || typeof entry === 'number' || typeof entry === 'boolean',
      );
      if (entries.length > 0) {
        customValues = Object.fromEntries(entries);
      }
    }

    if (maturity || complexity || risk || coverage || customValues) {
      return {
        maturity,
        complexity,
        risk,
        coverage,
        custom: customValues,
      };
    }
  }
  return undefined;
}

function readCodeReference(value: unknown): Types.CodeReference | undefined {
  const record = readRecord(value);
  if (record) {
    const id = readString(record['id']);
    const filePath = readString(record['filePath']);
    const symbolName = readString(record['symbolName']);
    const symbolType = readEnumValue(record['symbolType'], CODE_SYMBOL_TYPES);
    const language = readString(record['language']);

    if (id && filePath && symbolName && symbolType && language) {
      return {
        id,
        filePath,
        symbolName,
        symbolType,
        language,
        repositoryUrl: readString(record['repositoryUrl']),
        startLine: readNumber(record['startLine']),
        endLine: readNumber(record['endLine']),
        signature: readString(record['signature']),
        parentSymbol: readString(record['parentSymbol']),
        embedding: readNumberArray(record['embedding']),
        lastSyncedAt: readString(record['lastSyncedAt']),
        commitSha: readString(record['commitSha']),
      };
    }
  }
  return undefined;
}

function readDocReference(value: unknown): Types.DocReference | undefined {
  const record = readRecord(value);
  if (record) {
    const id = readString(record['id']);
    const documentPath = readString(record['documentPath']);
    const documentTitle = readString(record['documentTitle']);
    const contentType = readEnumValue(record['contentType'], DOC_CONTENT_TYPES);

    if (id && documentPath && documentTitle && contentType) {
      return {
        id,
        documentPath,
        documentTitle,
        contentType,
        sectionPath: readStringArray(record['sectionPath']),
        sectionTitle: readString(record['sectionTitle']),
        chunkIndex: readNumber(record['chunkIndex']),
        contentPreview: readString(record['contentPreview']),
        embedding: readNumberArray(record['embedding']),
        codeReferences: readStringArray(record['codeReferences']),
        itemReferences: readStringArray(record['itemReferences']),
        lastSyncedAt: readString(record['lastSyncedAt']),
      };
    }
  }
  return undefined;
}

function readTestSteps(value: unknown): Types.TestStep[] | undefined {
  if (Array.isArray(value)) {
    const steps: Types.TestStep[] = [];
    for (const entry of value) {
      const record = readRecord(entry);
      if (record) {
        const stepNumber = readNumber(record['stepNumber']);
        const action = readString(record['action']);
        if (stepNumber !== undefined && action) {
          steps.push({
            stepNumber,
            action,
            expectedResult: readString(record['expectedResult']),
            testData: readString(record['testData']),
          });
        }
      }
    }
    if (steps.length > 0) {
      return steps;
    }
  }
  return undefined;
}

function extractItemsArray(data: unknown): ApiItem[] {
  if (Array.isArray(data)) {
    return data.filter((entry) => isRecord(entry));
  }
  const record = readRecord(data);
  if (record) {
    const itemsValue = record['items'];
    if (Array.isArray(itemsValue)) {
      return itemsValue.filter((entry) => isRecord(entry));
    }
  }
  return [];
}

function extractTotalCount(data: unknown, itemsArray: ApiItem[]): number {
  const record = readRecord(data);
  if (record) {
    const totalValue = readNumber(record['total']);
    if (totalValue !== undefined) {
      return totalValue;
    }
  }
  return itemsArray.length;
}

function normalizeBaseItem(item: ApiItem): MutableItem {
  const createdAt = readStringField(item, 'created_at', 'createdAt');
  const updatedAt = readStringField(item, 'updated_at', 'updatedAt');
  const projectId = readStringField(item, 'project_id', 'projectId');
  const parentId = readStringField(item, 'parent_id', 'parentId');

  return {
    id: requireStringField(item, 'id'),
    projectId: projectId ?? requireStringField(item, 'projectId'),
    view: normalizeViewType(item['view']),
    type: requireStringField(item, 'type'),
    title: requireStringField(item, 'title'),
    description: readString(item['description']),
    status: normalizeStatus(item['status']),
    priority: normalizePriority(item['priority']),
    parentId,
    owner: readString(item['owner']),
    metadata: readRecord(item['metadata']),
    version: readNumber(item['version']) ?? DEFAULT_VERSION,
    createdAt: createdAt ?? requireStringField(item, 'createdAt'),
    updatedAt: updatedAt ?? requireStringField(item, 'updatedAt'),
    canonicalId: readString(item['canonicalId']),
    dimensions: readItemDimensions(item['dimensions']),
    codeRef: readCodeReference(item['codeRef']),
    docRef: readDocReference(item['docRef']),
    perspective: readString(item['perspective']),
    equivalentItemIds: readStringArray(item['equivalentItemIds']),
  };
}

function normalizeRequirement(base: MutableItem, item: ApiItem): Types.TypedItem {
  return {
    ...base,
    type: ITEM_TYPE_REQUIREMENT,
    adrId: readStringField(item, 'adr_id', 'adrId'),
    contractId: readStringField(item, 'contract_id', 'contractId'),
    qualityMetrics: readRecord(item['quality_metrics']) ?? readRecord(item['qualityMetrics']),
  };
}

function normalizeTest(
  base: MutableItem,
  item: ApiItem,
  type: Types.TestItem['type'],
): Types.TypedItem {
  const testType = readEnumValue(readStringField(item, 'test_type', 'testType'), TEST_CASE_TYPES);
  const automationStatus = readEnumValue(
    readStringField(item, 'automation_status', 'automationStatus'),
    AUTOMATION_STATUS_VALUES,
  );
  const lastExecutionResult = readEnumValue(
    readStringField(item, 'last_execution_result', 'lastExecutionResult'),
    TEST_RESULT_STATUS_VALUES,
  );

  const result: Types.TestItem = {
    ...base,
    type,
    testType,
    automationStatus,
    testSteps: readTestSteps(item['test_steps']) ?? readTestSteps(item['testSteps']),
    expectedResult: readStringField(item, 'expected_result', 'expectedResult'),
    lastExecutionResult,
  };

  return result;
}

function normalizeEpic(base: MutableItem, item: ApiItem): Types.TypedItem {
  return {
    ...base,
    type: ITEM_TYPE_EPIC,
    acceptanceCriteria: readStringArrayField(item, 'acceptance_criteria', 'acceptanceCriteria'),
    businessValue: readStringField(item, 'business_value', 'businessValue'),
    targetRelease: readStringField(item, 'target_release', 'targetRelease'),
  };
}

function normalizeUserStory(
  base: MutableItem,
  item: ApiItem,
  type: Types.UserStoryItem['type'],
): Types.TypedItem {
  const result: Types.UserStoryItem = {
    ...base,
    type,
    asA: readStringField(item, 'as_a', 'asA'),
    iWant: readStringField(item, 'i_want', 'iWant'),
    soThat: readStringField(item, 'so_that', 'soThat'),
    acceptanceCriteria: readStringArrayField(item, 'acceptance_criteria', 'acceptanceCriteria'),
    storyPoints: readNumberField(item, 'story_points', 'storyPoints'),
  };

  return result;
}

function normalizeTask(base: MutableItem, item: ApiItem): Types.TypedItem {
  const result: Types.TaskItem = {
    ...base,
    type: ITEM_TYPE_TASK,
    estimatedHours: readNumberField(item, 'estimated_hours', 'estimatedHours'),
    actualHours: readNumberField(item, 'actual_hours', 'actualHours'),
    assignee: readString(item['assignee']),
    dueDate: readStringField(item, 'due_date', 'dueDate'),
  };

  return result;
}

function normalizeDefect(
  base: MutableItem,
  item: ApiItem,
  type: Types.DefectItem['type'],
): Types.TypedItem {
  const severity = readEnumValue(readString(item['severity']), DEFECT_SEVERITY_VALUES);

  const result: Types.DefectItem = {
    ...base,
    type,
    severity,
    reproducible: readBoolean(item['reproducible']),
    stepsToReproduce: readStringArrayField(item, 'steps_to_reproduce', 'stepsToReproduce'),
    environment: readString(item['environment']),
    foundInVersion: readStringField(item, 'found_in_version', 'foundInVersion'),
    fixedInVersion: readStringField(item, 'fixed_in_version', 'fixedInVersion'),
  };

  return result;
}

function normalizeItem(item: ApiItem): Types.TypedItem {
  const baseItem = normalizeBaseItem(item);
  const type = baseItem.type;

  if (type === ITEM_TYPE_REQUIREMENT) {
    return normalizeRequirement(baseItem, item);
  }

  if (TEST_ITEM_TYPES.has(type as Types.TestItem['type'])) {
    return normalizeTest(baseItem, item, type as Types.TestItem['type']);
  }

  if (type === ITEM_TYPE_EPIC) {
    return normalizeEpic(baseItem, item);
  }

  if (USER_STORY_TYPES.has(type as Types.UserStoryItem['type'])) {
    return normalizeUserStory(baseItem, item, type as Types.UserStoryItem['type']);
  }

  if (type === ITEM_TYPE_TASK) {
    return normalizeTask(baseItem, item);
  }

  if (DEFECT_TYPES.has(type as Types.DefectItem['type'])) {
    return normalizeDefect(baseItem, item, type as Types.DefectItem['type']);
  }

  return baseItem;
}

function normalizeCreateItemData(data: CreateItemData): CreateItemData {
  return {
    ...data,
    description: readNonEmptyString(data.description),
    owner: readNonEmptyString(data.owner),
    priority: normalizePriority(data.priority),
    status: normalizeStatus(data.status),
  };
}

function normalizeCreateItemWithSpecData(data: CreateItemWithSpecData): CreateItemWithSpecData {
  return {
    ...data,
    item: {
      ...data.item,
      description: readNonEmptyString(data.item.description),
      owner: readNonEmptyString(data.item.owner),
    },
  };
}

export type { CreateItemData, CreateItemWithSpecData };
export {
  EMPTY_STRING,
  extractItemsArray,
  extractTotalCount,
  normalizeBaseItem,
  normalizeCreateItemData,
  normalizeCreateItemWithSpecData,
  normalizeItem,
  readNonEmptyString,
};
