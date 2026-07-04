type JsonRecord = Record<string, unknown>;

function isRecord(value: unknown): value is JsonRecord {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function isString(value: unknown): value is string {
  return typeof value === 'string';
}

function isNumber(value: unknown): value is number {
  return typeof value === 'number' && Number.isFinite(value);
}

function isBoolean(value: unknown): value is boolean {
  return typeof value === 'boolean';
}

function isStringArray(value: unknown): value is string[] {
  if (!Array.isArray(value)) {
    return false;
  }
  return value.every((item: unknown): item is string => typeof item === 'string');
}

function asRecord(value: unknown, label: string): JsonRecord {
  if (!isRecord(value)) {
    throw new Error(`Expected ${label} to be an object`);
  }
  return value;
}

function getOptionalString(record: JsonRecord, key: string): string | undefined {
  const value = record[key];
  if (value === undefined) {
    return undefined;
  }
  if (!isString(value)) {
    throw new Error(`Expected ${key} to be a string`);
  }
  if (value.length === 0) {
    return undefined;
  }
  return value;
}

function getRequiredString(record: JsonRecord, key: string): string {
  const value = record[key];
  if (!isString(value) || value.length === 0) {
    throw new Error(`Missing or invalid required string field: ${key}`);
  }
  return value;
}

function getOptionalNumber(record: JsonRecord, key: string): number | undefined {
  const value = record[key];
  if (value === undefined) {
    return undefined;
  }
  if (!isNumber(value)) {
    throw new Error(`Expected ${key} to be a number`);
  }
  return value;
}

function getRequiredNumber(record: JsonRecord, key: string): number {
  const value = record[key];
  if (!isNumber(value)) {
    throw new Error(`Missing or invalid required number field: ${key}`);
  }
  return value;
}

function getOptionalBoolean(record: JsonRecord, key: string): boolean | undefined {
  const value = record[key];
  if (value === undefined) {
    return undefined;
  }
  if (!isBoolean(value)) {
    throw new Error(`Expected ${key} to be a boolean`);
  }
  return value;
}

function getRequiredBoolean(record: JsonRecord, key: string): boolean {
  const value = record[key];
  if (!isBoolean(value)) {
    throw new Error(`Missing or invalid required boolean field: ${key}`);
  }
  return value;
}

function getOptionalRecord(record: JsonRecord, key: string): JsonRecord | undefined {
  const value = record[key];
  if (value === undefined) {
    return undefined;
  }
  if (!isRecord(value)) {
    throw new Error(`Expected ${key} to be an object`);
  }
  return value;
}

function getOptionalArray(record: JsonRecord, key: string): unknown[] | undefined {
  const value = record[key];
  if (value === undefined) {
    return undefined;
  }
  if (!Array.isArray(value)) {
    throw new TypeError(`Expected ${key} to be an array`);
  }
  return value;
}

function getRequiredArray(record: JsonRecord, key: string): unknown[] {
  const value = record[key];
  if (!Array.isArray(value)) {
    throw new TypeError(`Missing or invalid required array field: ${key}`);
  }
  return value;
}

function getOptionalStringArray(record: JsonRecord, key: string): string[] | undefined {
  const value = record[key];
  if (value === undefined) {
    return undefined;
  }
  if (!isStringArray(value)) {
    throw new Error(`Expected ${key} to be an array of strings`);
  }
  return value;
}

function toStringId(value: unknown, key: string): string {
  if (isString(value) && value.length > 0) {
    return value;
  }
  if (isNumber(value)) {
    return String(value);
  }
  throw new Error(`Missing or invalid id field: ${key}`);
}

function parseNumberMap(input: JsonRecord | undefined): Record<string, number> {
  if (input === undefined) {
    return {};
  }
  const out: Record<string, number> = {};
  for (const [key, value] of Object.entries(input)) {
    if (typeof value !== 'number' || !Number.isFinite(value)) {
      throw new TypeError(`Invalid number map value for key: ${key}`);
    }
    out[key] = value;
  }
  return out;
}

const processGuards = {
  asRecord,
  getOptionalArray,
  getOptionalBoolean,
  getOptionalNumber,
  getOptionalRecord,
  getOptionalString,
  getOptionalStringArray,
  getRequiredArray,
  getRequiredBoolean,
  getRequiredNumber,
  getRequiredString,
  parseNumberMap,
  toStringId,
};

export {
  asRecord,
  getOptionalArray,
  getOptionalBoolean,
  getOptionalNumber,
  getOptionalRecord,
  getOptionalString,
  getOptionalStringArray,
  getRequiredArray,
  getRequiredBoolean,
  getRequiredNumber,
  getRequiredString,
  parseNumberMap,
  processGuards,
  toStringId,
  type JsonRecord,
};
