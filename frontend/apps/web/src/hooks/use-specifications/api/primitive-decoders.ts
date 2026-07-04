const asNumber = (value: unknown, fallback = 0): number => {
  if (typeof value === 'number') {
    return value;
  }
  return fallback;
};

const asBoolean = (value: unknown, fallback = false): boolean => {
  if (typeof value === 'boolean') {
    return value;
  }
  return fallback;
};

const asString = (value: unknown): string => {
  if (typeof value === 'string') {
    return value;
  }
  return '';
};

const asOptionalString = (value: unknown): string | undefined => {
  if (typeof value !== 'string') {
    return;
  }
  return value;
};

const asOptionalNumber = (value: unknown): number | undefined => {
  if (typeof value !== 'number') {
    return;
  }
  return value;
};

const asStringArray = (value: unknown): string[] => {
  if (!Array.isArray(value)) {
    return [];
  }
  const result: string[] = [];
  for (const entry of value) {
    if (typeof entry === 'string') {
      result.push(entry);
    }
  }
  return result;
};

const asOptionalStringArray = (value: unknown): string[] | undefined => {
  if (!Array.isArray(value)) {
    return;
  }
  const result: string[] = [];
  for (const entry of value) {
    if (typeof entry === 'string') {
      result.push(entry);
    }
  }
  return result;
};

export {
  asBoolean,
  asNumber,
  asOptionalNumber,
  asOptionalString,
  asOptionalStringArray,
  asString,
  asStringArray,
};
