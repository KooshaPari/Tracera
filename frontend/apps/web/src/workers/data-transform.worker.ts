/**
 * Data Transformation Worker
 *
 * Handles CPU-intensive data operations:
 * - Large dataset filtering and sorting
 * - Complex data aggregations
 * - Data normalization and transformation
 * - Statistical computations
 */

import { expose } from 'comlink';

export interface TransformOptions {
  type: 'filter' | 'sort' | 'aggregate' | 'normalize' | 'deduplicate';
  field?: string;
  predicate?: string; // Serialized function
  direction?: 'asc' | 'desc';
  groupBy?: string;
  aggregation?: 'sum' | 'avg' | 'min' | 'max' | 'count';
}

export type ProgressCallback = (progress: number) => void;

const ZERO = 0;
const ONE = 1;
const TWO = 2;
const CHUNK_SIZE = 1000;
const PROGRESS_START = 0;
const PROGRESS_COMPLETE = 100;
const PROGRESS_STAGE_ONE = 30;
const PROGRESS_STAGE_TWO = 50;
const PROGRESS_STAGE_THREE = 70;
const PROGRESS_STAGE_FOUR = 90;

interface FilterOptions {
  field: string;
  predicate: (value: unknown) => boolean;
  onProgress?: ProgressCallback;
}

interface SortOptions {
  field: string;
  direction?: 'asc' | 'desc';
  onProgress?: ProgressCallback;
}

interface AggregateOptions {
  groupByField: string;
  aggregateField: string;
  aggregationType: 'sum' | 'avg' | 'min' | 'max' | 'count';
  onProgress?: ProgressCallback;
}

interface NormalizeOptions {
  field: string;
  onProgress?: ProgressCallback;
}

interface DeduplicateOptions {
  field: string;
  onProgress?: ProgressCallback;
}

interface StatisticsOptions {
  field: string;
  onProgress?: ProgressCallback;
}

interface PivotOptions {
  rowField: string;
  columnField: string;
  valueField: string;
  onProgress?: ProgressCallback;
}

interface JoinOptions {
  leftKey: string;
  rightKey: string;
  joinType?: 'inner' | 'left' | 'right' | 'outer';
  onProgress?: ProgressCallback;
}

const reportProgress = (callback: ProgressCallback | undefined, value: number): void => {
  if (callback) {
    callback(value);
  }
};

const calculateProgress = (current: number, total: number): number => {
  if (total <= ZERO) {
    return PROGRESS_COMPLETE;
  }
  return (current / total) * PROGRESS_COMPLETE;
};

const normalizeComparable = (value: unknown): number | string => {
  if (typeof value === 'number') {
    return value;
  }
  if (typeof value === 'string') {
    return value;
  }
  return String(value);
};

const compareValues = (first: unknown, second: unknown, direction: 'asc' | 'desc'): number => {
  if (first === second) {
    return ZERO;
  }

  const leftValue = normalizeComparable(first);
  const rightValue = normalizeComparable(second);
  const comparison = leftValue < rightValue ? -ONE : ONE;
  return direction === 'asc' ? comparison : -comparison;
};

const createEmptyStats = () => ({
  count: ZERO,
  max: ZERO,
  mean: ZERO,
  median: ZERO,
  min: ZERO,
  stdDev: ZERO,
  sum: ZERO,
});

/**
 * Filter large dataset
 */
const filterData = <T extends Record<string, unknown>>(data: T[], options: FilterOptions): T[] => {
  const { field, onProgress, predicate } = options;
  const result: T[] = [];

  for (let startIndex = ZERO; startIndex < data.length; startIndex += CHUNK_SIZE) {
    const endIndex = Math.min(startIndex + CHUNK_SIZE, data.length);

    for (let itemIndex = startIndex; itemIndex < endIndex; itemIndex += ONE) {
      const item = data[itemIndex];
      if (item === undefined) {
        continue;
      }
      if (predicate(item[field])) {
        result.push(item);
      }
    }

    reportProgress(onProgress, calculateProgress(endIndex, data.length));
  }

  reportProgress(onProgress, PROGRESS_COMPLETE);
  return result;
};

/**
 * Sort large dataset
 */
const sortData = <T extends Record<string, unknown>>(data: T[], options: SortOptions): T[] => {
  const { direction = 'asc', field, onProgress } = options;
  reportProgress(onProgress, PROGRESS_START);

  const sorted = [...data].toSorted((first, second) =>
    compareValues(first[field], second[field], direction),
  );

  reportProgress(onProgress, PROGRESS_COMPLETE);
  return sorted;
};

const pushGroupValue = (groups: Map<string, number[]>, groupKey: string, value: number): void => {
  const existing = groups.get(groupKey);
  if (existing) {
    existing.push(value);
  } else {
    groups.set(groupKey, [value]);
  }
};

const buildGroups = <T extends Record<string, unknown>>(
  data: T[],
  groupByField: string,
  aggregateField: string,
  onProgress?: ProgressCallback,
): Map<string, number[]> => {
  const groups = new Map<string, number[]>();

  for (let itemIndex = ZERO; itemIndex < data.length; itemIndex += ONE) {
    const item = data[itemIndex];
    if (!item) {
      continue;
    }
    const groupKey = String(item[groupByField]);
    const value = Number(item[aggregateField]);

    if (!Number.isNaN(value)) {
      pushGroupValue(groups, groupKey, value);
    }

    if (itemIndex % CHUNK_SIZE === ZERO) {
      reportProgress(onProgress, (itemIndex / data.length) * PROGRESS_STAGE_TWO);
    }
  }

  return groups;
};

const aggregateValues = (
  values: number[],
  aggregationType: AggregateOptions['aggregationType'],
): number => {
  if (values.length === ZERO) {
    return ZERO;
  }

  switch (aggregationType) {
    case 'sum': {
      return values.reduce((sum, value) => sum + value, ZERO);
    }
    case 'avg': {
      return values.reduce((sum, value) => sum + value, ZERO) / values.length;
    }
    case 'min': {
      return Math.min(...values);
    }
    case 'max': {
      return Math.max(...values);
    }
    case 'count': {
      return values.length;
    }
  }
};

/**
 * Aggregate data by field
 */
const aggregateData = <T extends Record<string, unknown>>(
  data: T[],
  options: AggregateOptions,
): Record<string, number> => {
  const { aggregateField, aggregationType, groupByField, onProgress } = options;
  reportProgress(onProgress, PROGRESS_START);

  const groups = buildGroups(data, groupByField, aggregateField, onProgress);
  reportProgress(onProgress, PROGRESS_STAGE_TWO);

  const result: Record<string, number> = {};
  let processed = ZERO;

  for (const [key, values] of groups) {
    result[key] = aggregateValues(values, aggregationType);
    processed += ONE;
    reportProgress(
      onProgress,
      PROGRESS_STAGE_TWO + (processed / Math.max(groups.size, ONE)) * PROGRESS_STAGE_TWO,
    );
  }

  reportProgress(onProgress, PROGRESS_COMPLETE);
  return result;
};

const computeMinMax = <T extends Record<string, unknown>>(
  data: T[],
  field: string,
): { min: number; max: number } => {
  let min = Infinity;
  let max = -Infinity;

  for (const item of data) {
    const value = Number(item[field]);
    if (!Number.isNaN(value)) {
      min = Math.min(min, value);
      max = Math.max(max, value);
    }
  }

  return { max, min };
};

const normalizeItems = <T extends Record<string, unknown>>(
  data: T[],
  field: string,
  min: number,
  max: number,
  onProgress?: ProgressCallback,
): T[] => {
  const range = max - min || ONE;

  return data.map((item, itemIndex) => {
    const value = Number(item[field]);
    const normalized = Number.isNaN(value) ? ZERO : (value - min) / range;

    if (itemIndex % CHUNK_SIZE === ZERO) {
      reportProgress(
        onProgress,
        PROGRESS_STAGE_ONE + (itemIndex / data.length) * PROGRESS_STAGE_THREE,
      );
    }

    return {
      ...item,
      [`${field}_normalized`]: normalized,
    };
  });
};

/**
 * Normalize data (scale to 0-1 range)
 */
const normalizeData = <T extends Record<string, unknown>>(
  data: T[],
  options: NormalizeOptions,
): T[] => {
  const { field, onProgress } = options;
  reportProgress(onProgress, PROGRESS_START);

  const { min, max } = computeMinMax(data, field);
  reportProgress(onProgress, PROGRESS_STAGE_ONE);

  const result = normalizeItems(data, field, min, max, onProgress);
  reportProgress(onProgress, PROGRESS_COMPLETE);
  return result;
};

/**
 * Deduplicate data by field
 */
const deduplicateData = <T extends Record<string, unknown>>(
  data: T[],
  options: DeduplicateOptions,
): T[] => {
  const { field, onProgress } = options;
  reportProgress(onProgress, PROGRESS_START);

  const seen = new Set<unknown>();
  const result: T[] = [];

  for (let itemIndex = ZERO; itemIndex < data.length; itemIndex += ONE) {
    const item = data[itemIndex];
    if (!item) {
      continue;
    }
    const value = item[field];

    if (!seen.has(value)) {
      seen.add(value);
      result.push(item);
    }

    if (itemIndex % CHUNK_SIZE === ZERO) {
      reportProgress(onProgress, calculateProgress(itemIndex, data.length));
    }
  }

  reportProgress(onProgress, PROGRESS_COMPLETE);
  return result;
};

const extractNumericValues = (data: Record<string, unknown>[], field: string): number[] => {
  const values: number[] = [];
  for (const item of data) {
    const value = Number(item[field]);
    if (!Number.isNaN(value)) {
      values.push(value);
    }
  }
  return values;
};

const computeMedian = (values: number[]): number => {
  const sorted = [...values].toSorted((first, second) => first - second);
  const count = sorted.length;
  const middle = Math.floor(count / TWO);

  if (count % TWO === ZERO) {
    const lower = sorted[middle - ONE];
    const upper = sorted[middle];
    if (lower === undefined || upper === undefined) {
      return ZERO;
    }
    return (lower + upper) / TWO;
  }
  return sorted[middle] ?? ZERO;
};

const computeStandardDeviation = (values: number[], mean: number): number => {
  const squaredDiffs = values.map((value) => (value - mean) ** TWO);
  const variance = squaredDiffs.reduce((sum, value) => sum + value, ZERO) / values.length;
  return Math.sqrt(variance);
};

/**
 * Calculate statistics for a numeric field
 */
const calculateStatistics = (
  data: Record<string, unknown>[],
  options: StatisticsOptions,
): {
  count: number;
  sum: number;
  mean: number;
  median: number;
  stdDev: number;
  min: number;
  max: number;
} => {
  const { field, onProgress } = options;
  reportProgress(onProgress, PROGRESS_START);

  const values = extractNumericValues(data, field);
  reportProgress(onProgress, PROGRESS_STAGE_ONE);

  if (values.length === ZERO) {
    return createEmptyStats();
  }

  const count = values.length;
  const sum = values.reduce((total, value) => total + value, ZERO);
  const mean = sum / count;
  reportProgress(onProgress, PROGRESS_STAGE_TWO);

  const median = computeMedian(values);
  reportProgress(onProgress, PROGRESS_STAGE_THREE);

  const stdDev = computeStandardDeviation(values, mean);
  reportProgress(onProgress, PROGRESS_STAGE_FOUR);

  const min = Math.min(...values);
  const max = Math.max(...values);
  reportProgress(onProgress, PROGRESS_COMPLETE);

  return {
    count,
    max,
    mean,
    median,
    min,
    stdDev,
    sum,
  };
};

/**
 * Pivot data (transform rows to columns)
 */
const pivotData = <T extends Record<string, unknown>>(
  data: T[],
  options: PivotOptions,
): Record<string, Record<string, unknown>> => {
  const { columnField, onProgress, rowField, valueField } = options;
  reportProgress(onProgress, PROGRESS_START);

  const result: Record<string, Record<string, unknown>> = {};

  for (let itemIndex = ZERO; itemIndex < data.length; itemIndex += ONE) {
    const item = data[itemIndex];
    if (!item) {
      continue;
    }
    const rowKey = String(item[rowField]);
    const columnKey = String(item[columnField]);
    const value = item[valueField];

    result[rowKey] ??= {};

    result[rowKey][columnKey] = value;

    if (itemIndex % CHUNK_SIZE === ZERO) {
      reportProgress(onProgress, calculateProgress(itemIndex, data.length));
    }
  }

  reportProgress(onProgress, PROGRESS_COMPLETE);
  return result;
};

/**
 * Join two datasets
 */
const joinData = <T extends Record<string, unknown>, U extends Record<string, unknown>>(
  left: T[],
  right: U[],
  options: JoinOptions,
): (T & U)[] => {
  const { joinType = 'inner', leftKey, onProgress, rightKey } = options;
  reportProgress(onProgress, PROGRESS_START);

  const rightIndex = new Map<unknown, U[]>();
  for (const item of right) {
    const key = item[rightKey];
    const list = rightIndex.get(key);
    if (list) {
      list.push(item);
    } else {
      rightIndex.set(key, [item]);
    }
  }

  reportProgress(onProgress, PROGRESS_STAGE_ONE);

  const result: (T & U)[] = [];
  for (let itemIndex = ZERO; itemIndex < left.length; itemIndex += ONE) {
    const leftItem = left[itemIndex];
    if (!leftItem) {
      continue;
    }
    const key = leftItem[leftKey];
    const rightItems = rightIndex.get(key) ?? [];

    if (rightItems.length > ZERO) {
      for (const rightItem of rightItems) {
        result.push({ ...leftItem, ...rightItem });
      }
    } else if (joinType === 'left' || joinType === 'outer') {
      result.push({ ...leftItem } as T & U);
    }

    if (itemIndex % CHUNK_SIZE === ZERO) {
      reportProgress(
        onProgress,
        PROGRESS_STAGE_ONE + (itemIndex / left.length) * PROGRESS_STAGE_THREE,
      );
    }
  }

  reportProgress(onProgress, PROGRESS_COMPLETE);
  return result;
};

// Worker API
const api = {
  aggregateData,
  calculateStatistics,
  deduplicateData,
  filterData,
  joinData,
  normalizeData,
  pivotData,
  sortData,
};

expose(api);

export type DataTransformWorkerAPI = typeof api;
