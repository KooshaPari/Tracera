type ApiRecord = Record<string, unknown>;

const isApiRecord = (value: unknown): value is ApiRecord =>
  typeof value === 'object' && Object.prototype.toString.call(value) !== '[object Null]';

const toApiRecord = (value: unknown): ApiRecord => {
  if (!isApiRecord(value)) {
    return {};
  }
  return value;
};

const asRecord = (value: unknown): ApiRecord | undefined => {
  if (!isApiRecord(value)) {
    return;
  }
  return value;
};

const asRecordArray = (value: unknown): ApiRecord[] => {
  if (Array.isArray(value)) {
    return value.filter((entry): entry is ApiRecord => isApiRecord(entry));
  }
  return [];
};

const asNumberRecord = (value: unknown): Record<string, number> => {
  if (!isApiRecord(value)) {
    return {};
  }
  const result: Record<string, number> = {};
  for (const [key, entry] of Object.entries(value)) {
    if (typeof entry === 'number') {
      result[key] = entry;
    }
  }
  return result;
};

export { asNumberRecord, asRecord, asRecordArray, isApiRecord, toApiRecord, type ApiRecord };
