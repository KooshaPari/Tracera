import type { ApiItem } from '@/hooks/useItems/readers';
import type {
  CodeReference,
  CoverageMetrics,
  DocReference,
  DefectItem,
  Item,
  ItemDimensions,
  TestItem,
  TestStep,
  TypedItem,
  UserStoryItem,
} from '@tracertm/types';

import {
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
  ITEM_STATUS_VALUES,
  ITEM_TYPE_EPIC,
  ITEM_TYPE_REQUIREMENT,
  ITEM_TYPE_TASK,
  MATURITY_LEVELS,
  PRIORITY_VALUES,
  RISK_LEVELS,
  TEST_CASE_TYPES,
  TEST_ITEM_TYPES,
  TEST_RESULT_STATUS_VALUES,
  USER_STORY_TYPES,
  VIEW_TYPE_VALUES,
} from '@/hooks/useItems/constants';
import {
  readBoolean,
  readEnumValue,
  readNumber,
  readNumberArray,
  readNumberField,
  readRecord,
  readNonEmptyString,
  readString,
  readStringArray,
  readStringArrayField,
  readStringField,
  isRecord,
  requireStringField,
} from '@/hooks/useItems/readers';

type MutableItem = Item & { view: Item['view'] };

type Normalizer = (base: MutableItem, item: ApiItem) => TypedItem;

function normalizeStatus(value: unknown) {
  const normalized = readEnumValue(value, ITEM_STATUS_VALUES);
  if (normalized !== undefined) {
    return normalized;
  }
  return DEFAULT_STATUS;
}

function normalizePriority(value: unknown) {
  const normalized = readEnumValue(value, PRIORITY_VALUES);
  if (normalized !== undefined) {
    return normalized;
  }
  return DEFAULT_PRIORITY;
}

function normalizeViewType(value: unknown) {
  const normalized = readEnumValue(value, VIEW_TYPE_VALUES);
  if (normalized !== undefined) {
    return normalized;
  }
  return DEFAULT_VIEW;
}

function readCoverageMetrics(value: unknown): CoverageMetrics | undefined {
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

function readItemDimensions(value: unknown): ItemDimensions | undefined {
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
        customValues = Object.fromEntries(entries) as Record<string, string | number | boolean>;
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

function readCodeReference(value: unknown): CodeReference | undefined {
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

function readDocReference(value: unknown): DocReference | undefined {
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

function readTestSteps(value: unknown): TestStep[] | undefined {
  if (Array.isArray(value)) {
    const steps: TestStep[] = [];
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

const SIMPLE_TYPE_NORMALIZERS: Record<string, Normalizer> = {
  [ITEM_TYPE_REQUIREMENT]: (base, item) => ({
    ...base,
    type: ITEM_TYPE_REQUIREMENT,
    adrId: readStringField(item, 'adr_id', 'adrId'),
    contractId: readStringField(item, 'contract_id', 'contractId'),
    qualityMetrics: readRecord(item['quality_metrics']) ?? readRecord(item['qualityMetrics']),
  }),
  [ITEM_TYPE_EPIC]: (base, item) => ({
    ...base,
    type: ITEM_TYPE_EPIC,
    acceptanceCriteria: readStringArrayField(item, 'acceptance_criteria', 'acceptanceCriteria'),
    businessValue: readStringField(item, 'business_value', 'businessValue'),
    targetRelease: readStringField(item, 'target_release', 'targetRelease'),
  }),
  [ITEM_TYPE_TASK]: (base, item) => ({
    ...base,
    type: ITEM_TYPE_TASK,
    estimatedHours: readNumberField(item, 'estimated_hours', 'estimatedHours'),
    actualHours: readNumberField(item, 'actual_hours', 'actualHours'),
    assignee: readString(item['assignee']),
    dueDate: readStringField(item, 'due_date', 'dueDate'),
  }),
};

function normalizeTest(base: MutableItem, item: ApiItem, type: TestItem['type']): TypedItem {
  const testType = readEnumValue(readStringField(item, 'test_type', 'testType'), TEST_CASE_TYPES);
  const automationStatus = readEnumValue(
    readStringField(item, 'automation_status', 'automationStatus'),
    AUTOMATION_STATUS_VALUES,
  );
  const lastExecutionResult = readEnumValue(
    readStringField(item, 'last_execution_result', 'lastExecutionResult'),
    TEST_RESULT_STATUS_VALUES,
  );

  const result: TestItem = {
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

function normalizeUserStory(
  base: MutableItem,
  item: ApiItem,
  type: UserStoryItem['type'],
): TypedItem {
  const result: UserStoryItem = {
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

function normalizeDefect(base: MutableItem, item: ApiItem, type: DefectItem['type']): TypedItem {
  const severity = readEnumValue(readString(item['severity']), DEFECT_SEVERITY_VALUES);

  return {
    ...base,
    type,
    severity,
    reproducible: readBoolean(item['reproducible']),
    stepsToReproduce: readStringArrayField(item, 'steps_to_reproduce', 'stepsToReproduce'),
    environment: readString(item['environment']),
    foundInVersion: readStringField(item, 'found_in_version', 'foundInVersion'),
    fixedInVersion: readStringField(item, 'fixed_in_version', 'fixedInVersion'),
  };
}

function normalizeItem(item: ApiItem): TypedItem {
  const baseItem = normalizeBaseItem(item);
  const { type } = baseItem;

  const simpleNormalizer = SIMPLE_TYPE_NORMALIZERS[type];
  if (simpleNormalizer) {
    return simpleNormalizer(baseItem, item);
  }

  if (TEST_ITEM_TYPES.has(type as TestItem['type'])) {
    return normalizeTest(baseItem, item, type as TestItem['type']);
  }

  if (USER_STORY_TYPES.has(type as UserStoryItem['type'])) {
    return normalizeUserStory(baseItem, item, type as UserStoryItem['type']);
  }

  if (DEFECT_TYPES.has(type as DefectItem['type'])) {
    return normalizeDefect(baseItem, item, type as DefectItem['type']);
  }

  return baseItem;
}

export {
  extractItemsArray,
  extractTotalCount,
  normalizeBaseItem,
  normalizeItem,
  normalizePriority,
  normalizeStatus,
  readNonEmptyString,
};
