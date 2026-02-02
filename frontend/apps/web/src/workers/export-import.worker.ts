/* eslint-disable */
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

export interface ProgressCallback {
  (progress: number): void;
}

/**
 * Parse NDJSON (newline-delimited JSON)
 */
function parseNDJSON<T = unknown>(
  ndjson: string,
  onProgress?: ProgressCallback,
): T[] {
  onProgress?.(0);

  const lines = ndjson.split('\n');
  const result: T[] = [];
  const chunkSize = 1000;

  for (let i = 0; i < lines.length; i += chunkSize) {
    const chunk = lines.slice(i, Math.min(i + chunkSize, lines.length));

    for (const line of chunk) {
      const trimmed = line.trim();
      if (trimmed) {
        try {
          result.push(JSON.parse(trimmed));
        } catch (error) {
          console.warn(`Failed to parse NDJSON line: ${trimmed}`, error);
        }
      }
    }

    onProgress?.(((i + chunkSize) / lines.length) * 100);
  }

  onProgress?.(100);
  return result;
}

/**
 * Generate NDJSON from objects
 */
function generateNDJSON<T = unknown>(
  data: T[],
  onProgress?: ProgressCallback,
): string {
  onProgress?.(0);

  const lines: string[] = [];
  const chunkSize = 1000;

  for (let i = 0; i < data.length; i += chunkSize) {
    const chunk = data.slice(i, Math.min(i + chunkSize, data.length));

    for (const item of chunk) {
      try {
        lines.push(JSON.stringify(item));
      } catch (error) {
        console.warn('Failed to stringify item:', item, error);
      }
    }

    onProgress?.(((i + chunkSize) / data.length) * 100);
  }

  onProgress?.(100);
  return lines.join('\n');
}

/**
 * Parse large JSON with progress tracking
 */
function parseJSON<T = unknown>(
  json: string,
  onProgress?: ProgressCallback,
): T {
  onProgress?.(0);

  try {
    const parsed = JSON.parse(json);
    onProgress?.(100);
    return parsed;
  } catch (error) {
    throw new Error(`JSON parse error: ${error instanceof Error ? error.message : String(error)}`, { cause: error });
  }
}

/**
 * Stringify large object with progress tracking
 */
function stringifyJSON<T = unknown>(
  data: T,
  pretty = false,
  onProgress?: ProgressCallback,
): string {
  onProgress?.(0);

  try {
    const json = JSON.stringify(data, null, pretty ? 2 : 0);
    onProgress?.(100);
    return json;
  } catch (error) {
    throw new Error(`JSON stringify error: ${error instanceof Error ? error.message : String(error)}`, { cause: error });
  }
}

/**
 * Parse CSV
 */
function parseCSV(
  csv: string,
  options: {
    delimiter?: string;
    hasHeader?: boolean;
    skipEmptyLines?: boolean;
  } = {},
  onProgress?: ProgressCallback,
): Array<Record<string, string>> {
  onProgress?.(0);

  const delimiter = options.delimiter ?? ',';
  const hasHeader = options.hasHeader ?? true;
  const skipEmptyLines = options.skipEmptyLines ?? true;

  const lines = csv.split('\n');
  const result: Array<Record<string, string>> = [];

  let headers: string[] = [];
  let startIndex = 0;

  if (hasHeader && lines.length > 0) {
    headers = lines[0].split(delimiter).map(h => h.trim());
    startIndex = 1;
  }

  onProgress?.(10);

  const chunkSize = 1000;
  for (let i = startIndex; i < lines.length; i += chunkSize) {
    const chunk = lines.slice(i, Math.min(i + chunkSize, lines.length));

    for (const line of chunk) {
      const trimmed = line.trim();
      if (skipEmptyLines && !trimmed) continue;

      const values = trimmed.split(delimiter).map(v => v.trim());

      if (hasHeader) {
        const row: Record<string, string> = {};
        for (let j = 0; j < headers.length; j++) {
          row[headers[j]] = values[j] ?? '';
        }
        result.push(row);
      } else {
        const row: Record<string, string> = {};
        for (let j = 0; j < values.length; j++) {
          row[`col${j}`] = values[j];
        }
        result.push(row);
      }
    }

    onProgress?.(10 + ((i + chunkSize - startIndex) / (lines.length - startIndex)) * 90);
  }

  onProgress?.(100);
  return result;
}

/**
 * Generate CSV
 */
function generateCSV(
  data: Array<Record<string, any>>,
  options: {
    delimiter?: string;
    includeHeader?: boolean;
    columns?: string[];
  } = {},
  onProgress?: ProgressCallback,
): string {
  onProgress?.(0);

  if (data.length === 0) {
    onProgress?.(100);
    return '';
  }

  const delimiter = options.delimiter ?? ',';
  const includeHeader = options.includeHeader ?? true;
  const columns = options.columns ?? Object.keys(data[0]);

  const lines: string[] = [];

  // Add header
  if (includeHeader) {
    lines.push(columns.join(delimiter));
  }

  onProgress?.(10);

  // Add data rows
  const chunkSize = 1000;
  for (let i = 0; i < data.length; i += chunkSize) {
    const chunk = data.slice(i, Math.min(i + chunkSize, data.length));

    for (const row of chunk) {
      const values = columns.map(col => {
        const value = row[col];
        if (value === null || value === undefined) return '';
        const str = String(value);
        // Escape if contains delimiter, newline, or quotes
        if (str.includes(delimiter) || str.includes('\n') || str.includes('"')) {
          return `"${str.replace(/"/g, '""')}"`;
        }
        return str;
      });
      lines.push(values.join(delimiter));
    }

    onProgress?.(10 + ((i + chunkSize) / data.length) * 90);
  }

  onProgress?.(100);
  return lines.join('\n');
}

/**
 * Validate data against schema
 */
function validateData<T = unknown>(
  data: unknown[],
  schema: {
    required?: string[];
    types?: Record<string, 'string' | 'number' | 'boolean' | 'object' | 'array'>;
    nullable?: string[];
  },
  onProgress?: ProgressCallback,
): {
  valid: T[];
  invalid: Array<{ item: unknown; errors: string[] }>;
} {
  onProgress?.(0);

  const valid: T[] = [];
  const invalid: Array<{ item: unknown; errors: string[] }> = [];

  const chunkSize = 1000;
  for (let i = 0; i < data.length; i += chunkSize) {
    const chunk = data.slice(i, Math.min(i + chunkSize, data.length));

    for (const item of chunk) {
      const errors: string[] = [];

      // Check if item is object
      if (typeof item !== 'object' || item === null || Array.isArray(item)) {
        errors.push('Item must be an object');
        invalid.push({ item, errors });
        continue;
      }

      const obj = item as Record<string, any>;

      // Check required fields
      if (schema.required) {
        for (const field of schema.required) {
          if (!(field in obj)) {
            errors.push(`Missing required field: ${field}`);
          } else if (obj[field] === null || obj[field] === undefined) {
            if (!schema.nullable?.includes(field)) {
              errors.push(`Field cannot be null: ${field}`);
            }
          }
        }
      }

      // Check types
      if (schema.types) {
        for (const [field, expectedType] of Object.entries(schema.types)) {
          if (!(field in obj)) continue;

          const value = obj[field];
          if (value === null || value === undefined) {
            if (!schema.nullable?.includes(field)) {
              errors.push(`Field cannot be null: ${field}`);
            }
            continue;
          }

          const actualType = Array.isArray(value) ? 'array' : typeof value;
          if (actualType !== expectedType) {
            errors.push(`Field ${field} has wrong type: expected ${expectedType}, got ${actualType}`);
          }
        }
      }

      if (errors.length > 0) {
        invalid.push({ item, errors });
      } else {
        valid.push(item as T);
      }
    }

    onProgress?.(((i + chunkSize) / data.length) * 100);
  }

  onProgress?.(100);
  return { valid, invalid };
}

/**
 * Transform data using mapping rules
 */
function transformData<T = unknown, R = unknown>(
  data: T[],
  mapping: Record<string, string | ((value: any) => any)>,
  onProgress?: ProgressCallback,
): R[] {
  onProgress?.(0);

  const result: R[] = [];
  const chunkSize = 1000;

  for (let i = 0; i < data.length; i += chunkSize) {
    const chunk = data.slice(i, Math.min(i + chunkSize, data.length));

    for (const item of chunk) {
      const transformed: any = {};

      for (const [targetKey, sourceKeyOrFn] of Object.entries(mapping)) {
        if (typeof sourceKeyOrFn === 'function') {
          transformed[targetKey] = sourceKeyOrFn(item);
        } else {
          const sourceValue = (item as any)[sourceKeyOrFn];
          transformed[targetKey] = sourceValue;
        }
      }

      result.push(transformed);
    }

    onProgress?.(((i + chunkSize) / data.length) * 100);
  }

  onProgress?.(100);
  return result;
}

/**
 * Compress data using simple RLE (Run-Length Encoding) for repeated values
 */
function compressData<T = unknown>(
  data: T[],
  onProgress?: ProgressCallback,
): Array<{ value: T; count: number }> {
  onProgress?.(0);

  if (data.length === 0) {
    onProgress?.(100);
    return [];
  }

  const result: Array<{ value: T; count: number }> = [];
  let current = data[0];
  let count = 1;

  for (let i = 1; i < data.length; i++) {
    const item = data[i];

    if (JSON.stringify(item) === JSON.stringify(current)) {
      count++;
    } else {
      result.push({ value: current, count });
      current = item;
      count = 1;
    }

    if (i % 1000 === 0) {
      onProgress?.((i / data.length) * 100);
    }
  }

  result.push({ value: current, count });
  onProgress?.(100);

  return result;
}

/**
 * Decompress RLE data
 */
function decompressData<T = unknown>(
  compressed: Array<{ value: T; count: number }>,
  onProgress?: ProgressCallback,
): T[] {
  onProgress?.(0);

  const result: T[] = [];

  for (let i = 0; i < compressed.length; i++) {
    const { value, count } = compressed[i];

    for (let j = 0; j < count; j++) {
      result.push(value);
    }

    onProgress?.(((i + 1) / compressed.length) * 100);
  }

  onProgress?.(100);
  return result;
}

// Worker API
const api = {
  parseNDJSON,
  generateNDJSON,
  parseJSON,
  stringifyJSON,
  parseCSV,
  generateCSV,
  validateData,
  transformData,
  compressData,
  decompressData,
};

expose(api);

export type ExportImportWorkerAPI = typeof api;
/* eslint-enable */
