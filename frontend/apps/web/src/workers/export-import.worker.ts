/**
 * Export/Import Worker
 *
 * Handles heavy serialization/deserialization:
 * - NDJSON parsing and generation
 * - JSON parsing/serialization for large datasets
 * - CSV parsing and generation
 * - Data validation and transformation
 */

import { expose } from 'comlink';

import { logger } from '@/lib/logger';

export type ProgressCallback = (progress: number) => void;

const ZERO = 0;
const ONE = 1;
const TWO = 2;
const PROGRESS_START = 0;
const PROGRESS_HEADER = 10;
const PROGRESS_COMPLETE = 100;
const PROGRESS_REMAINING = 90;
const CHUNK_SIZE = 1000;
const CSV_DEFAULT_DELIMITER = ',';

const reportProgress = (callback: ProgressCallback | undefined, value: number): void => {
  if (callback) {
    callback(value);
  }
};

const calculateProgress = (
  current: number,
  total: number,
  base = ZERO,
  span = PROGRESS_COMPLETE,
): number => {
  if (total <= ZERO) {
    return base + span;
  }
  return base + (current / total) * span;
};

const safeErrorMessage = (error: unknown): string => {
  if (error instanceof Error) {
    return error.message;
  }
  return String(error);
};

const safeJsonParse = <T = unknown>(value: string): T | undefined => {
  try {
    return JSON.parse(value) as T;
  } catch (error) {
    logger.warn(`[ExportImportWorker] Failed to parse JSON: ${value}`, error);
    return undefined;
  }
};

const safeJsonStringify = (value: unknown): string | undefined => {
  try {
    return JSON.stringify(value);
  } catch (error) {
    logger.warn('[ExportImportWorker] Failed to stringify item:', error);
    return undefined;
  }
};

const getTrimmedLine = (line: string | undefined): string => (line ? line.trim() : '');

/**
 * Parse NDJSON (newline-delimited JSON)
 */
const parseNDJSON = <T = unknown>(ndjson: string, onProgress?: ProgressCallback): T[] => {
  reportProgress(onProgress, PROGRESS_START);

  const lines = ndjson.split('\n');
  const result: T[] = [];

  for (let startIndex = ZERO; startIndex < lines.length; startIndex += CHUNK_SIZE) {
    const endIndex = Math.min(startIndex + CHUNK_SIZE, lines.length);

    for (let lineIndex = startIndex; lineIndex < endIndex; lineIndex += ONE) {
      const trimmed = getTrimmedLine(lines[lineIndex]);
      if (!trimmed) {
        continue;
      }
      const parsed = safeJsonParse<T>(trimmed);
      if (parsed !== undefined) {
        result.push(parsed);
      }
    }

    reportProgress(onProgress, calculateProgress(endIndex, lines.length));
  }

  reportProgress(onProgress, PROGRESS_COMPLETE);
  return result;
};

/**
 * Generate NDJSON from objects
 */
const generateNDJSON = <T = unknown>(data: T[], onProgress?: ProgressCallback): string => {
  reportProgress(onProgress, PROGRESS_START);

  const lines: string[] = [];

  for (let startIndex = ZERO; startIndex < data.length; startIndex += CHUNK_SIZE) {
    const endIndex = Math.min(startIndex + CHUNK_SIZE, data.length);

    for (let itemIndex = startIndex; itemIndex < endIndex; itemIndex += ONE) {
      const serialized = safeJsonStringify(data[itemIndex]);
      if (serialized !== undefined) {
        lines.push(serialized);
      }
    }

    reportProgress(onProgress, calculateProgress(endIndex, data.length));
  }

  reportProgress(onProgress, PROGRESS_COMPLETE);
  return lines.join('\n');
};

/**
 * Parse large JSON with progress tracking
 */
const parseJSON = <T = unknown>(json: string, onProgress?: ProgressCallback): T => {
  reportProgress(onProgress, PROGRESS_START);

  try {
    const parsed = JSON.parse(json) as T;
    reportProgress(onProgress, PROGRESS_COMPLETE);
    return parsed;
  } catch (error) {
    throw new Error(`JSON parse error: ${safeErrorMessage(error)}`, { cause: error });
  }
};

/**
 * Stringify large object with progress tracking
 */
const stringifyJSON = <T = unknown>(
  data: T,
  pretty = false,
  onProgress?: ProgressCallback,
): string => {
  reportProgress(onProgress, PROGRESS_START);

  try {
    const spacing = pretty ? TWO : ZERO;
    const json = JSON.stringify(data, null, spacing);
    reportProgress(onProgress, PROGRESS_COMPLETE);
    return json;
  } catch (error) {
    throw new Error(`JSON stringify error: ${safeErrorMessage(error)}`, { cause: error });
  }
};

interface CsvOptions {
  delimiter?: string;
  hasHeader?: boolean;
  skipEmptyLines?: boolean;
}

const getCsvHeaders = (
  lines: string[],
  delimiter: string,
  hasHeader: boolean,
): { headers: string[]; startIndex: number } => {
  if (!hasHeader || lines.length === ZERO) {
    return { headers: [], startIndex: ZERO };
  }
  const firstLine = lines[ZERO];
  if (!firstLine) {
    return { headers: [], startIndex: ZERO };
  }
  const headers = firstLine.split(delimiter).map((header) => header.trim());
  return { headers, startIndex: ONE };
};

const parseCsvValues = (line: string, delimiter: string): string[] =>
  line.split(delimiter).map((value) => value.trim());

const buildRowWithHeaders = (headers: string[], values: string[]): Record<string, string> => {
  const row: Record<string, string> = {};
  for (let headerIndex = ZERO; headerIndex < headers.length; headerIndex += ONE) {
    const header = headers[headerIndex];
    if (!header) {
      continue;
    }
    row[header] = values[headerIndex] ?? '';
  }
  return row;
};

const buildRowWithoutHeaders = (values: string[]): Record<string, string> => {
  const row: Record<string, string> = {};
  for (let valueIndex = ZERO; valueIndex < values.length; valueIndex += ONE) {
    row[`col${valueIndex}`] = values[valueIndex] ?? '';
  }
  return row;
};

const parseCsvLine = (
  line: string,
  delimiter: string,
  headers: string[],
  hasHeader: boolean,
): Record<string, string> => {
  const values = parseCsvValues(line, delimiter);
  if (hasHeader) {
    return buildRowWithHeaders(headers, values);
  }
  return buildRowWithoutHeaders(values);
};

/**
 * Parse CSV
 */
const parseCSV = (
  csv: string,
  options: CsvOptions = {},
  onProgress?: ProgressCallback,
): Record<string, string>[] => {
  reportProgress(onProgress, PROGRESS_START);

  const delimiter = options.delimiter ?? CSV_DEFAULT_DELIMITER;
  const hasHeader = options.hasHeader ?? true;
  const skipEmptyLines = options.skipEmptyLines ?? true;

  const lines = csv.split('\n');
  const result: Record<string, string>[] = [];
  const { headers, startIndex } = getCsvHeaders(lines, delimiter, hasHeader);

  reportProgress(onProgress, PROGRESS_HEADER);

  for (let start = startIndex; start < lines.length; start += CHUNK_SIZE) {
    const end = Math.min(start + CHUNK_SIZE, lines.length);

    for (let lineIndex = start; lineIndex < end; lineIndex += ONE) {
      const trimmed = getTrimmedLine(lines[lineIndex]);
      if (skipEmptyLines && !trimmed) {
        continue;
      }
      result.push(parseCsvLine(trimmed, delimiter, headers, hasHeader));
    }

    const progress = calculateProgress(
      end - startIndex,
      Math.max(lines.length - startIndex, ONE),
      PROGRESS_HEADER,
      PROGRESS_REMAINING,
    );
    reportProgress(onProgress, progress);
  }

  reportProgress(onProgress, PROGRESS_COMPLETE);
  return result;
};

interface CsvGenerateOptions {
  delimiter?: string;
  includeHeader?: boolean;
  columns?: string[];
}

const escapeCsvValue = (value: unknown, delimiter: string): string => {
  if (value === null || value === undefined) {
    return '';
  }
  const str = String(value);
  if (str.includes(delimiter) || str.includes('\n') || str.includes('"')) {
    return `"${str.replaceAll('"', '""')}"`;
  }
  return str;
};

/**
 * Generate CSV
 */
const generateCSV = (
  data: Record<string, unknown>[],
  options: CsvGenerateOptions = {},
  onProgress?: ProgressCallback,
): string => {
  reportProgress(onProgress, PROGRESS_START);

  if (data.length === ZERO) {
    reportProgress(onProgress, PROGRESS_COMPLETE);
    return '';
  }

  const delimiter = options.delimiter ?? CSV_DEFAULT_DELIMITER;
  const includeHeader = options.includeHeader ?? true;
  const columns = options.columns ?? Object.keys(data[ZERO] ?? {});
  const lines: string[] = [];

  if (includeHeader) {
    lines.push(columns.join(delimiter));
  }

  reportProgress(onProgress, PROGRESS_HEADER);

  for (let startIndex = ZERO; startIndex < data.length; startIndex += CHUNK_SIZE) {
    const endIndex = Math.min(startIndex + CHUNK_SIZE, data.length);

    for (let rowIndex = startIndex; rowIndex < endIndex; rowIndex += ONE) {
      const row = data[rowIndex] ?? {};
      const values = columns.map((column) => escapeCsvValue(row[column], delimiter));
      lines.push(values.join(delimiter));
    }

    const progress = calculateProgress(endIndex, data.length, PROGRESS_HEADER, PROGRESS_REMAINING);
    reportProgress(onProgress, progress);
  }

  reportProgress(onProgress, PROGRESS_COMPLETE);
  return lines.join('\n');
};

interface ValidationSchema {
  required?: string[];
  types?: Record<string, 'string' | 'number' | 'boolean' | 'object' | 'array'>;
  nullable?: string[];
}

const isPlainObject = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null && !Array.isArray(value);

const validateRequiredFields = (
  obj: Record<string, unknown>,
  required: string[] | undefined,
  nullable: string[] | undefined,
): string[] => {
  if (!required) {
    return [];
  }
  const errors: string[] = [];
  for (const field of required) {
    if (!(field in obj)) {
      errors.push(`Missing required field: ${field}`);
      continue;
    }
    if (obj[field] === undefined) {
      if (!nullable || !nullable.includes(field)) {
        errors.push(`Field cannot be null: ${field}`);
      }
    }
  }
  return errors;
};

const validateFieldTypes = (
  obj: Record<string, unknown>,
  types: ValidationSchema['types'],
  nullable: string[] | undefined,
): string[] => {
  if (!types) {
    return [];
  }
  const errors: string[] = [];
  for (const [field, expectedType] of Object.entries(types)) {
    if (!(field in obj)) {
      continue;
    }
    const value = obj[field];
    if (value === null || value === undefined) {
      if (!nullable || !nullable.includes(field)) {
        errors.push(`Field cannot be null: ${field}`);
      }
      continue;
    }
    const actualType = Array.isArray(value) ? 'array' : typeof value;
    if (actualType !== expectedType) {
      errors.push(`Field ${field} has wrong type: expected ${expectedType}, got ${actualType}`);
    }
  }
  return errors;
};

const validateItem = (
  item: unknown,
  schema: ValidationSchema,
): { errors: string[]; isValid: boolean; normalized?: Record<string, unknown> } => {
  if (!isPlainObject(item)) {
    return { errors: ['Item must be an object'], isValid: false };
  }

  const requiredErrors = validateRequiredFields(item, schema.required, schema.nullable);
  const typeErrors = validateFieldTypes(item, schema.types, schema.nullable);
  const errors = [...requiredErrors, ...typeErrors];

  return { errors, isValid: errors.length === ZERO, normalized: item };
};

/**
 * Validate data against schema
 */
const validateData = <T = unknown>(
  data: unknown[],
  schema: ValidationSchema,
  onProgress?: ProgressCallback,
): {
  valid: T[];
  invalid: { item: unknown; errors: string[] }[];
} => {
  reportProgress(onProgress, PROGRESS_START);

  const valid: T[] = [];
  const invalid: { item: unknown; errors: string[] }[] = [];

  for (let startIndex = ZERO; startIndex < data.length; startIndex += CHUNK_SIZE) {
    const endIndex = Math.min(startIndex + CHUNK_SIZE, data.length);

    for (let itemIndex = startIndex; itemIndex < endIndex; itemIndex += ONE) {
      const item = data[itemIndex];
      const { errors, isValid } = validateItem(item, schema);
      if (!isValid) {
        invalid.push({ errors, item });
      } else {
        valid.push(item as T);
      }
    }

    reportProgress(onProgress, calculateProgress(endIndex, data.length));
  }

  reportProgress(onProgress, PROGRESS_COMPLETE);
  return { invalid, valid };
};

/**
 * Transform data using mapping rules
 */
const transformData = <T = unknown, R = unknown>(
  data: T[],
  mapping: Record<string, string | ((value: T) => unknown)>,
  onProgress?: ProgressCallback,
): R[] => {
  reportProgress(onProgress, PROGRESS_START);

  const result: R[] = [];

  for (let startIndex = ZERO; startIndex < data.length; startIndex += CHUNK_SIZE) {
    const endIndex = Math.min(startIndex + CHUNK_SIZE, data.length);

    for (let itemIndex = startIndex; itemIndex < endIndex; itemIndex += ONE) {
      const item = data[itemIndex];
      if (item === undefined) {
        continue;
      }
      const transformed: Record<string, unknown> = {};

      for (const [targetKey, sourceKeyOrFn] of Object.entries(mapping)) {
        if (typeof sourceKeyOrFn === 'function') {
          transformed[targetKey] = sourceKeyOrFn(item);
        } else {
          transformed[targetKey] = (item as Record<string, unknown>)[sourceKeyOrFn];
        }
      }

      result.push(transformed as R);
    }

    reportProgress(onProgress, calculateProgress(endIndex, data.length));
  }

  reportProgress(onProgress, PROGRESS_COMPLETE);
  return result;
};

/**
 * Compress data using simple RLE (Run-Length Encoding) for repeated values
 */
const compressData = <T = unknown>(
  data: T[],
  onProgress?: ProgressCallback,
): { value: T; count: number }[] => {
  reportProgress(onProgress, PROGRESS_START);

  if (data.length === ZERO) {
    reportProgress(onProgress, PROGRESS_COMPLETE);
    return [];
  }

  const result: { value: T; count: number }[] = [];
  const firstItem = data[ZERO];
  if (firstItem === undefined) {
    reportProgress(onProgress, PROGRESS_COMPLETE);
    return [];
  }
  let current = firstItem;
  let count = ONE;

  for (let itemIndex = ONE; itemIndex < data.length; itemIndex += ONE) {
    const item = data[itemIndex];
    if (item === undefined) {
      continue;
    }
    const isSame = JSON.stringify(item) === JSON.stringify(current);

    if (isSame) {
      count += ONE;
    } else {
      result.push({ count, value: current });
      current = item;
      count = ONE;
    }

    if (itemIndex % CHUNK_SIZE === ZERO) {
      reportProgress(onProgress, calculateProgress(itemIndex, data.length));
    }
  }

  result.push({ count, value: current });
  reportProgress(onProgress, PROGRESS_COMPLETE);
  return result;
};

/**
 * Decompress RLE data
 */
const decompressData = <T = unknown>(
  compressed: { value: T; count: number }[],
  onProgress?: ProgressCallback,
): T[] => {
  reportProgress(onProgress, PROGRESS_START);

  const result: T[] = [];

  for (let itemIndex = ZERO; itemIndex < compressed.length; itemIndex += ONE) {
    const entry = compressed[itemIndex];
    if (!entry) {
      continue;
    }
    const { value, count } = entry;

    for (let repeatIndex = ZERO; repeatIndex < count; repeatIndex += ONE) {
      result.push(value);
    }

    reportProgress(onProgress, calculateProgress(itemIndex + ONE, compressed.length));
  }

  reportProgress(onProgress, PROGRESS_COMPLETE);
  return result;
};

// Worker API
const api = {
  compressData,
  decompressData,
  generateCSV,
  generateNDJSON,
  parseCSV,
  parseJSON,
  parseNDJSON,
  stringifyJSON,
  transformData,
  validateData,
};

expose(api);

export type ExportImportWorkerAPI = typeof api;
