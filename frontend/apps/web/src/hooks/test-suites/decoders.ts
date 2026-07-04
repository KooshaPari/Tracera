import type { TestSuiteStatus } from '@tracertm/types';

type JsonObject = Record<string, unknown>;

function isJsonObject(value: unknown): value is JsonObject {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function isUnknownArray(value: unknown): value is unknown[] {
  return Array.isArray(value);
}

function asJsonObject(value: unknown, context: string): JsonObject {
  if (isJsonObject(value)) {
    return value;
  }
  throw new TypeError(`Expected object for ${context}`);
}

function getUnknown(obj: JsonObject, key: string): unknown {
  return obj[key];
}

function getOptionalString(obj: JsonObject, key: string): string | undefined {
  const value = getUnknown(obj, key);
  if (value === undefined || value === null) {
    return undefined;
  }
  if (typeof value === 'string') {
    return value;
  }
  throw new TypeError(`Expected string for ${key}`);
}

function getString(obj: JsonObject, key: string): string {
  const value = getOptionalString(obj, key);
  if (value === undefined) {
    throw new Error(`Missing required string field ${key}`);
  }
  return value;
}

function getOptionalNumber(obj: JsonObject, key: string): number | undefined {
  const value = getUnknown(obj, key);
  if (value === undefined || value === null) {
    return undefined;
  }
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value;
  }
  throw new TypeError(`Expected number for ${key}`);
}

function getNumber(obj: JsonObject, key: string): number {
  const value = getOptionalNumber(obj, key);
  if (value === undefined) {
    throw new Error(`Missing required number field ${key}`);
  }
  return value;
}

function getOptionalBoolean(obj: JsonObject, key: string): boolean | undefined {
  const value = getUnknown(obj, key);
  if (value === undefined || value === null) {
    return undefined;
  }
  if (typeof value === 'boolean') {
    return value;
  }
  throw new TypeError(`Expected boolean for ${key}`);
}

function getBoolean(obj: JsonObject, key: string): boolean {
  const value = getOptionalBoolean(obj, key);
  if (value === undefined) {
    throw new Error(`Missing required boolean field ${key}`);
  }
  return value;
}

function getOptionalArray(obj: JsonObject, key: string): unknown[] | undefined {
  const value = getUnknown(obj, key);
  if (value === undefined || value === null) {
    return undefined;
  }
  if (isUnknownArray(value)) {
    return value;
  }
  throw new TypeError(`Expected array for ${key}`);
}

function getOptionalStringArray(obj: JsonObject, key: string): string[] | undefined {
  const values = getOptionalArray(obj, key);
  if (values === undefined) {
    return undefined;
  }

  const result: string[] = [];
  for (const value of values) {
    if (typeof value !== 'string') {
      throw new TypeError(`Expected string[] for ${key}`);
    }
    result.push(value);
  }
  return result;
}

function getOptionalRecord(obj: JsonObject, key: string): JsonObject | undefined {
  const value = getUnknown(obj, key);
  if (value === undefined || value === null) {
    return undefined;
  }
  if (isJsonObject(value)) {
    return value;
  }
  throw new TypeError(`Expected object for ${key}`);
}

function getOptionalRecordOfString(
  obj: JsonObject,
  key: string,
): Record<string, string> | undefined {
  const value = getOptionalRecord(obj, key);
  if (value === undefined) {
    return undefined;
  }

  const result: Record<string, string> = {};
  for (const [entryKey, entryValue] of Object.entries(value)) {
    if (typeof entryValue !== 'string') {
      throw new TypeError(`Expected Record<string, string> for ${key}`);
    }
    result[entryKey] = entryValue;
  }
  return result;
}

function getOptionalRecordOfNumber(
  obj: JsonObject,
  key: string,
): Record<string, number> | undefined {
  const value = getOptionalRecord(obj, key);
  if (value === undefined) {
    return undefined;
  }

  const result: Record<string, number> = {};
  for (const [entryKey, entryValue] of Object.entries(value)) {
    if (typeof entryValue !== 'number' || !Number.isFinite(entryValue)) {
      throw new TypeError(`Expected Record<string, number> for ${key}`);
    }
    result[entryKey] = entryValue;
  }
  return result;
}

const testSuiteStatusValues = new Set<string>(['draft', 'active', 'deprecated', 'archived']);

function isTestSuiteStatus(value: string): value is TestSuiteStatus {
  return testSuiteStatusValues.has(value);
}

function getTestSuiteStatus(obj: JsonObject, key: string): TestSuiteStatus {
  const value = getString(obj, key);
  if (isTestSuiteStatus(value)) {
    return value;
  }
  throw new Error(`Unexpected TestSuiteStatus for ${key}`);
}

export {
  asJsonObject,
  getBoolean,
  getNumber,
  getOptionalArray,
  getOptionalBoolean,
  getOptionalNumber,
  getOptionalRecord,
  getOptionalRecordOfNumber,
  getOptionalRecordOfString,
  getOptionalString,
  getOptionalStringArray,
  getString,
  getTestSuiteStatus,
  getUnknown,
};
