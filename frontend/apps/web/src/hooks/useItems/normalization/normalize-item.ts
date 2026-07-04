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

import * as constants from './constants';
import * as readers from './readers';

type ApiItem = readers.ApiItem;

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

function readCustomDimensionValues(
  value: unknown,
): Record<string, string | number | boolean> | undefined {
  const custom = readers.readRecord(value);
  if (custom === undefined) {
    return undefined;
  }

  const entries: [string, string | number | boolean][] = [];
  for (const [key, entry] of Object.entries(custom)) {
    if (typeof entry === 'string' || typeof entry === 'number' || typeof entry === 'boolean') {
      entries.push([key, entry]);
    }
  }

  if (entries.length > 0) {
    return Object.fromEntries(entries);
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
    const customValues = readCustomDimensionValues(record['custom']);

    if (
      maturity !== undefined ||
      complexity !== undefined ||
      risk !== undefined ||
      coverage !== undefined ||
      customValues !== undefined
    ) {
      return {
        ...(maturity !== undefined ? { maturity } : {}),
        ...(complexity !== undefined ? { complexity } : {}),
        ...(risk !== undefined ? { risk } : {}),
        ...(coverage !== undefined ? { coverage } : {}),
        ...(customValues !== undefined ? { custom: customValues } : {}),
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
      const repositoryUrl = readers.readString(record['repositoryUrl']);
      const startLine = readers.readNumber(record['startLine']);
      const endLine = readers.readNumber(record['endLine']);
      const signature = readers.readString(record['signature']);
      const parentSymbol = readers.readString(record['parentSymbol']);
      const embedding = readers.readNumberArray(record['embedding']);
      const lastSyncedAt = readers.readString(record['lastSyncedAt']);
      const commitSha = readers.readString(record['commitSha']);

      return {
        id,
        filePath,
        symbolName,
        symbolType,
        language,
        ...(repositoryUrl !== undefined ? { repositoryUrl } : {}),
        ...(startLine !== undefined ? { startLine } : {}),
        ...(endLine !== undefined ? { endLine } : {}),
        ...(signature !== undefined ? { signature } : {}),
        ...(parentSymbol !== undefined ? { parentSymbol } : {}),
        ...(embedding !== undefined ? { embedding } : {}),
        ...(lastSyncedAt !== undefined ? { lastSyncedAt } : {}),
        ...(commitSha !== undefined ? { commitSha } : {}),
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
      const sectionPath = readers.readStringArray(record['sectionPath']);
      const sectionTitle = readers.readString(record['sectionTitle']);
      const chunkIndex = readers.readNumber(record['chunkIndex']);
      const contentPreview = readers.readString(record['contentPreview']);
      const embedding = readers.readNumberArray(record['embedding']);
      const codeReferences = readers.readStringArray(record['codeReferences']);
      const itemReferences = readers.readStringArray(record['itemReferences']);
      const lastSyncedAt = readers.readString(record['lastSyncedAt']);

      return {
        id,
        documentPath,
        documentTitle,
        contentType,
        ...(sectionPath !== undefined ? { sectionPath } : {}),
        ...(sectionTitle !== undefined ? { sectionTitle } : {}),
        ...(chunkIndex !== undefined ? { chunkIndex } : {}),
        ...(contentPreview !== undefined ? { contentPreview } : {}),
        ...(embedding !== undefined ? { embedding } : {}),
        ...(codeReferences !== undefined ? { codeReferences } : {}),
        ...(itemReferences !== undefined ? { itemReferences } : {}),
        ...(lastSyncedAt !== undefined ? { lastSyncedAt } : {}),
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
        if (stepNumber !== undefined && action !== undefined && action.length > 0) {
          const expectedResult = readers.readString(record['expectedResult']);
          const testData = readers.readString(record['testData']);
          steps.push({
            stepNumber,
            action,
            ...(expectedResult !== undefined ? { expectedResult } : {}),
            ...(testData !== undefined ? { testData } : {}),
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
  const description = readers.readString(item['description']);
  const owner = readers.readString(item['owner']);
  const metadata = readers.readRecord(item['metadata']);
  const canonicalId = readers.readString(item['canonicalId']);
  const dimensions = readItemDimensions(item['dimensions']);
  const codeRef = readCodeReference(item['codeRef']);
  const docRef = readDocReference(item['docRef']);
  const perspective = readers.readString(item['perspective']);
  const equivalentItemIds = readers.readStringArray(item['equivalentItemIds']);

  return {
    id: readers.requireStringField(item, 'id'),
    projectId: projectId ?? readers.requireStringField(item, 'projectId'),
    view: normalizeViewType(item['view']),
    type: readers.requireStringField(item, 'type'),
    title: readers.requireStringField(item, 'title'),
    status: normalizeStatus(item['status']),
    priority: normalizePriority(item['priority']),
    version: readers.readNumber(item['version']) ?? constants.DEFAULT_VERSION,
    createdAt: createdAt ?? readers.requireStringField(item, 'createdAt'),
    updatedAt: updatedAt ?? readers.requireStringField(item, 'updatedAt'),
    ...(description !== undefined ? { description } : {}),
    ...(parentId !== undefined ? { parentId } : {}),
    ...(owner !== undefined ? { owner } : {}),
    ...(metadata !== undefined ? { metadata } : {}),
    ...(canonicalId !== undefined ? { canonicalId } : {}),
    ...(dimensions !== undefined ? { dimensions } : {}),
    ...(codeRef !== undefined ? { codeRef } : {}),
    ...(docRef !== undefined ? { docRef } : {}),
    ...(perspective !== undefined ? { perspective } : {}),
    ...(equivalentItemIds !== undefined ? { equivalentItemIds } : {}),
  };
}

const SIMPLE_TYPE_NORMALIZERS: Record<string, Normalizer> = {
  [constants.ITEM_TYPE_REQUIREMENT]: (base, item) => {
    const adrId = readers.readStringField(item, 'adr_id', 'adrId');
    const contractId = readers.readStringField(item, 'contract_id', 'contractId');
    const qualityMetrics =
      readers.readRecord(item['quality_metrics']) ?? readers.readRecord(item['qualityMetrics']);

    return {
      ...base,
      type: constants.ITEM_TYPE_REQUIREMENT,
      ...(adrId !== undefined ? { adrId } : {}),
      ...(contractId !== undefined ? { contractId } : {}),
      ...(qualityMetrics !== undefined ? { qualityMetrics } : {}),
    };
  },
  [constants.ITEM_TYPE_EPIC]: (base, item) => {
    const acceptanceCriteria = readers.readStringArrayField(
      item,
      'acceptance_criteria',
      'acceptanceCriteria',
    );
    const businessValue = readers.readStringField(item, 'business_value', 'businessValue');
    const targetRelease = readers.readStringField(item, 'target_release', 'targetRelease');

    return {
      ...base,
      type: constants.ITEM_TYPE_EPIC,
      ...(acceptanceCriteria !== undefined ? { acceptanceCriteria } : {}),
      ...(businessValue !== undefined ? { businessValue } : {}),
      ...(targetRelease !== undefined ? { targetRelease } : {}),
    };
  },
  [constants.ITEM_TYPE_TASK]: (base, item) => {
    const estimatedHours = readers.readNumberField(item, 'estimated_hours', 'estimatedHours');
    const actualHours = readers.readNumberField(item, 'actual_hours', 'actualHours');
    const assignee = readers.readString(item['assignee']);
    const dueDate = readers.readStringField(item, 'due_date', 'dueDate');

    return {
      ...base,
      type: constants.ITEM_TYPE_TASK,
      ...(estimatedHours !== undefined ? { estimatedHours } : {}),
      ...(actualHours !== undefined ? { actualHours } : {}),
      ...(assignee !== undefined ? { assignee } : {}),
      ...(dueDate !== undefined ? { dueDate } : {}),
    };
  },
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
  const testSteps = readTestSteps(item['test_steps']) ?? readTestSteps(item['testSteps']);
  const expectedResult = readers.readStringField(item, 'expected_result', 'expectedResult');

  const result: TestItem = {
    ...base,
    type,
    ...(testType !== undefined ? { testType } : {}),
    ...(automationStatus !== undefined ? { automationStatus } : {}),
    ...(testSteps !== undefined ? { testSteps } : {}),
    ...(expectedResult !== undefined ? { expectedResult } : {}),
    ...(lastExecutionResult !== undefined ? { lastExecutionResult } : {}),
  };

  return result;
}

function normalizeUserStory(
  base: MutableItem,
  item: ApiItem,
  type: UserStoryItem['type'],
): TypedItem {
  const asA = readers.readStringField(item, 'as_a', 'asA');
  const iWant = readers.readStringField(item, 'i_want', 'iWant');
  const soThat = readers.readStringField(item, 'so_that', 'soThat');
  const acceptanceCriteria = readers.readStringArrayField(
    item,
    'acceptance_criteria',
    'acceptanceCriteria',
  );
  const storyPoints = readers.readNumberField(item, 'story_points', 'storyPoints');

  const result: UserStoryItem = {
    ...base,
    type,
    ...(asA !== undefined ? { asA } : {}),
    ...(iWant !== undefined ? { iWant } : {}),
    ...(soThat !== undefined ? { soThat } : {}),
    ...(acceptanceCriteria !== undefined ? { acceptanceCriteria } : {}),
    ...(storyPoints !== undefined ? { storyPoints } : {}),
  };

  return result;
}

function normalizeDefect(base: MutableItem, item: ApiItem, type: DefectItem['type']): TypedItem {
  const severity = readers.readEnumValue(
    readers.readString(item['severity']),
    constants.DEFECT_SEVERITY_VALUES,
  );
  const reproducible = readers.readBoolean(item['reproducible']);
  const stepsToReproduce = readers.readStringArrayField(
    item,
    'steps_to_reproduce',
    'stepsToReproduce',
  );
  const environment = readers.readString(item['environment']);
  const foundInVersion = readers.readStringField(item, 'found_in_version', 'foundInVersion');
  const fixedInVersion = readers.readStringField(item, 'fixed_in_version', 'fixedInVersion');

  const result: DefectItem = {
    ...base,
    type,
    ...(severity !== undefined ? { severity } : {}),
    ...(reproducible !== undefined ? { reproducible } : {}),
    ...(stepsToReproduce !== undefined ? { stepsToReproduce } : {}),
    ...(environment !== undefined ? { environment } : {}),
    ...(foundInVersion !== undefined ? { foundInVersion } : {}),
    ...(fixedInVersion !== undefined ? { fixedInVersion } : {}),
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
  const { type } = baseItem;

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
