import type {
  CodeReference,
  CoverageMetrics,
  DefectItem,
  DocReference,
  Item,
  ItemDimensions,
  ItemStatus,
  Priority,
  TestItem,
  TestStep,
  TypedItem,
  UserStoryItem,
  ViewType,
} from '@tracertm/types';

import constants from './constants';
import readers, { type ApiItem } from './readers';

type MutableItem = Item & { view: Item['view'] };

type Normalizer = (base: MutableItem, item: ApiItem) => TypedItem;

function normalizeStatus(value: unknown): ItemStatus {
  const normalized = readers.readEnumValue(value, constants.ITEM_STATUS_VALUES);
  if (normalized !== undefined) {
    return normalized;
  }
  return constants.DEFAULT_STATUS;
}

function normalizePriority(value: unknown): Priority {
  const normalized = readers.readEnumValue(value, constants.PRIORITY_VALUES);
  if (normalized !== undefined) {
    return normalized;
  }
  return constants.DEFAULT_PRIORITY;
}

function normalizeViewType(value: unknown): ViewType {
  const normalized = readers.readEnumValue(value, constants.VIEW_TYPE_VALUES);
  if (normalized !== undefined) {
    return normalized;
  }
  return constants.DEFAULT_VIEW;
}

function readCoverageMetrics(value: unknown): CoverageMetrics | undefined {
  const record = readers.readRecord(value);
  if (record !== undefined) {
    const testCoverage = readers.readNumber(record['testCoverage']);
    const docCoverage = readers.readNumber(record['docCoverage']);
    const traceCoverage = readers.readNumber(record['traceCoverage']);
    const overallCoverage = readers.readNumber(record['overallCoverage']);
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
  const record = readers.readRecord(value);
  if (record !== undefined) {
    const maturity = readers.readEnumValue(record['maturity'], constants.MATURITY_LEVELS);
    const complexity = readers.readEnumValue(record['complexity'], constants.COMPLEXITY_LEVELS);
    const risk = readers.readEnumValue(record['risk'], constants.RISK_LEVELS);
    const coverage = readCoverageMetrics(record['coverage']);

    const custom = readers.readRecord(record['custom']);
    let customValues: Record<string, string | number | boolean> | undefined;
    if (custom !== undefined) {
      const entries: Array<[string, string | number | boolean]> = [];
      for (const [key, entry] of Object.entries(custom)) {
        if (typeof entry === 'string' || typeof entry === 'number' || typeof entry === 'boolean') {
          entries.push([key, entry]);
        }
      }

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

function readCodeReference(value: unknown): CodeReference | undefined {
  const record = readers.readRecord(value);
  if (record !== undefined) {
    const id = readers.readString(record['id']);
    const filePath = readers.readString(record['filePath']);
    const symbolName = readers.readString(record['symbolName']);
    const symbolType = readers.readEnumValue(record['symbolType'], constants.CODE_SYMBOL_TYPES);
    const language = readers.readString(record['language']);

    if (
      id !== undefined &&
      filePath !== undefined &&
      symbolName !== undefined &&
      symbolType !== undefined &&
      language !== undefined
    ) {
      return {
        id,
        filePath,
        symbolName,
        symbolType,
        language,
        repositoryUrl: readers.readString(record['repositoryUrl']),
        startLine: readers.readNumber(record['startLine']),
        endLine: readers.readNumber(record['endLine']),
        signature: readers.readString(record['signature']),
        parentSymbol: readers.readString(record['parentSymbol']),
        embedding: readers.readNumberArray(record['embedding']),
        lastSyncedAt: readers.readString(record['lastSyncedAt']),
        commitSha: readers.readString(record['commitSha']),
      };
    }
  }
  return undefined;
}

function readDocReference(value: unknown): DocReference | undefined {
  const record = readers.readRecord(value);
  if (record !== undefined) {
    const id = readers.readString(record['id']);
    const documentPath = readers.readString(record['documentPath']);
    const documentTitle = readers.readString(record['documentTitle']);
    const contentType = readers.readEnumValue(record['contentType'], constants.DOC_CONTENT_TYPES);

    if (
      id !== undefined &&
      documentPath !== undefined &&
      documentTitle !== undefined &&
      contentType !== undefined
    ) {
      return {
        id,
        documentPath,
        documentTitle,
        contentType,
        sectionPath: readers.readStringArray(record['sectionPath']),
        sectionTitle: readers.readString(record['sectionTitle']),
        chunkIndex: readers.readNumber(record['chunkIndex']),
        contentPreview: readers.readString(record['contentPreview']),
        embedding: readers.readNumberArray(record['embedding']),
        codeReferences: readers.readStringArray(record['codeReferences']),
        itemReferences: readers.readStringArray(record['itemReferences']),
        lastSyncedAt: readers.readString(record['lastSyncedAt']),
      };
    }
  }
  return undefined;
}

function readTestSteps(value: unknown): TestStep[] | undefined {
  if (Array.isArray(value)) {
    const steps: TestStep[] = [];
    for (const entry of value) {
      const record = readers.readRecord(entry);
      if (record !== undefined) {
        const stepNumber = readers.readNumber(record['stepNumber']);
        const action = readers.readString(record['action']);
        if (stepNumber !== undefined && action) {
          steps.push({
            stepNumber,
            action,
            expectedResult: readers.readString(record['expectedResult']),
            testData: readers.readString(record['testData']),
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
    return data.filter((entry) => readers.isRecord(entry));
  }
  const record = readers.readRecord(data);
  if (record !== undefined) {
    const itemsValue = record['items'];
    if (Array.isArray(itemsValue)) {
      return itemsValue.filter((entry) => readers.isRecord(entry));
    }
  }
  return [];
}

function extractTotalCount(data: unknown, itemsArray: ApiItem[]): number {
  const record = readers.readRecord(data);
  if (record !== undefined) {
    const totalValue = readers.readNumber(record['total']);
    if (totalValue !== undefined) {
      return totalValue;
    }
  }
  return itemsArray.length;
}

function normalizeBaseItem(item: ApiItem): MutableItem {
  const createdAt = readers.readStringField(item, 'created_at', 'createdAt');
  const updatedAt = readers.readStringField(item, 'updated_at', 'updatedAt');
  const projectId = readers.readStringField(item, 'project_id', 'projectId');
  const parentId = readers.readStringField(item, 'parent_id', 'parentId');

  return {
    id: readers.requireStringField(item, 'id'),
    projectId: projectId ?? readers.requireStringField(item, 'projectId'),
    view: normalizeViewType(item['view']),
    type: readers.requireStringField(item, 'type'),
    title: readers.requireStringField(item, 'title'),
    description: readers.readString(item['description']),
    status: normalizeStatus(item['status']),
    priority: normalizePriority(item['priority']),
    parentId,
    owner: readers.readString(item['owner']),
    metadata: readers.readRecord(item['metadata']),
    version: readers.readNumber(item['version']) ?? constants.DEFAULT_VERSION,
    createdAt: createdAt ?? readers.requireStringField(item, 'createdAt'),
    updatedAt: updatedAt ?? readers.requireStringField(item, 'updatedAt'),
    canonicalId: readers.readString(item['canonicalId']),
    dimensions: readItemDimensions(item['dimensions']),
    codeRef: readCodeReference(item['codeRef']),
    docRef: readDocReference(item['docRef']),
    perspective: readers.readString(item['perspective']),
    equivalentItemIds: readers.readStringArray(item['equivalentItemIds']),
  };
}

const SIMPLE_TYPE_NORMALIZERS: Record<string, Normalizer> = {
  [constants.ITEM_TYPE_REQUIREMENT]: (base, item) => ({
    ...base,
    type: constants.ITEM_TYPE_REQUIREMENT,
    adrId: readers.readStringField(item, 'adr_id', 'adrId'),
    contractId: readers.readStringField(item, 'contract_id', 'contractId'),
    qualityMetrics:
      readers.readRecord(item['quality_metrics']) ?? readers.readRecord(item['qualityMetrics']),
  }),
  [constants.ITEM_TYPE_EPIC]: (base, item) => ({
    ...base,
    type: constants.ITEM_TYPE_EPIC,
    acceptanceCriteria: readers.readStringArrayField(
      item,
      'acceptance_criteria',
      'acceptanceCriteria',
    ),
    businessValue: readers.readStringField(item, 'business_value', 'businessValue'),
    targetRelease: readers.readStringField(item, 'target_release', 'targetRelease'),
  }),
  [constants.ITEM_TYPE_TASK]: (base, item) => ({
    ...base,
    type: constants.ITEM_TYPE_TASK,
    estimatedHours: readers.readNumberField(item, 'estimated_hours', 'estimatedHours'),
    actualHours: readers.readNumberField(item, 'actual_hours', 'actualHours'),
    assignee: readers.readString(item['assignee']),
    dueDate: readers.readStringField(item, 'due_date', 'dueDate'),
  }),
};

function normalizeTest(base: MutableItem, item: ApiItem, type: TestItem['type']): TypedItem {
  const testType = readers.readEnumValue(
    readers.readStringField(item, 'test_type', 'testType'),
    constants.TEST_CASE_TYPES,
  );
  const automationStatus = readers.readEnumValue(
    readers.readStringField(item, 'automation_status', 'automationStatus'),
    constants.AUTOMATION_STATUS_VALUES,
  );
  const lastExecutionResult = readers.readEnumValue(
    readers.readStringField(item, 'last_execution_result', 'lastExecutionResult'),
    constants.TEST_RESULT_STATUS_VALUES,
  );

  const result: TestItem = {
    ...base,
    type,
    testType,
    automationStatus,
    testSteps: readTestSteps(item['test_steps']) ?? readTestSteps(item['testSteps']),
    expectedResult: readers.readStringField(item, 'expected_result', 'expectedResult'),
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
    asA: readers.readStringField(item, 'as_a', 'asA'),
    iWant: readers.readStringField(item, 'i_want', 'iWant'),
    soThat: readers.readStringField(item, 'so_that', 'soThat'),
    acceptanceCriteria: readers.readStringArrayField(
      item,
      'acceptance_criteria',
      'acceptanceCriteria',
    ),
    storyPoints: readers.readNumberField(item, 'story_points', 'storyPoints'),
  };

  return result;
}

function normalizeDefect(base: MutableItem, item: ApiItem, type: DefectItem['type']): TypedItem {
  const severity = readers.readEnumValue(
    readers.readString(item['severity']),
    constants.DEFECT_SEVERITY_VALUES,
  );

  const result: DefectItem = {
    ...base,
    type,
    severity,
    reproducible: readers.readBoolean(item['reproducible']),
    stepsToReproduce: readers.readStringArrayField(item, 'steps_to_reproduce', 'stepsToReproduce'),
    environment: readers.readString(item['environment']),
    foundInVersion: readers.readStringField(item, 'found_in_version', 'foundInVersion'),
    fixedInVersion: readers.readStringField(item, 'fixed_in_version', 'fixedInVersion'),
  };

  return result;
}

function isTestItemType(value: string): value is TestItem['type'] {
  return (
    value === constants.ITEM_TYPE_TEST ||
    value === constants.ITEM_TYPE_TEST_CASE ||
    value === constants.ITEM_TYPE_TEST_SUITE
  );
}

function isUserStoryItemType(value: string): value is UserStoryItem['type'] {
  return value === constants.ITEM_TYPE_USER_STORY || value === constants.ITEM_TYPE_STORY;
}

function isDefectItemType(value: string): value is DefectItem['type'] {
  return value === constants.ITEM_TYPE_BUG || value === constants.ITEM_TYPE_DEFECT;
}

function normalizeItem(item: ApiItem): TypedItem {
  const baseItem = normalizeBaseItem(item);
  const type = baseItem.type;

  const simpleNormalizer = SIMPLE_TYPE_NORMALIZERS[type];
  if (simpleNormalizer !== undefined) {
    return simpleNormalizer(baseItem, item);
  }

  if (isTestItemType(type)) {
    return normalizeTest(baseItem, item, type);
  }

  if (isUserStoryItemType(type)) {
    return normalizeUserStory(baseItem, item, type);
  }

  if (isDefectItemType(type)) {
    return normalizeDefect(baseItem, item, type);
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
};
