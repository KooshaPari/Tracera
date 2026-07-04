const EMPTY_STRING = '';

type ApiItem = Record<string, unknown>;

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

const readers = {
  isRecord,
  readBoolean,
  readEnumValue,
  readNonEmptyString,
  readNumber,
  readNumberArray,
  readNumberField,
  readRecord,
  readString,
  readStringArray,
  readStringArrayField,
  readStringField,
  requireStringField,
} as const;

export type { ApiItem };
export {
  EMPTY_STRING,
  isRecord,
  readBoolean,
  readEnumValue,
  readNonEmptyString,
  readNumber,
  readNumberArray,
  readNumberField,
  readRecord,
  readString,
  readStringArray,
  readStringArrayField,
  readStringField,
  requireStringField,
};

export default readers;
