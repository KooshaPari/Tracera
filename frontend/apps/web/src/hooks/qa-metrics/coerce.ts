import type { CoverageMetrics } from './types';

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && Boolean(value) && !Array.isArray(value);
}

function asRecord(value: unknown): Record<string, unknown> {
  if (isRecord(value)) {
    return value;
  }
  return {};
}

function asArray(value: unknown): unknown[] {
  if (Array.isArray(value)) {
    return value;
  }
  return [];
}

function asNumber(value: unknown, fallback: number): number {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value;
  }
  if (typeof value === 'string') {
    const parsed = Number(value);
    if (Number.isFinite(parsed)) {
      return parsed;
    }
  }
  return fallback;
}

function asString(value: unknown, fallback: string): string {
  if (typeof value === 'string') {
    return value;
  }
  return fallback;
}

function asOptionalString(value: unknown): string | undefined {
  if (typeof value === 'string') {
    return value;
  }
  return undefined;
}

function asOptionalNumber(value: unknown): number | undefined {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value;
  }
  return undefined;
}

function asRecordNumberMap(value: unknown): Record<string, number> {
  const rec = asRecord(value);
  const out: Record<string, number> = {};
  for (const [key, entryValue] of Object.entries(rec)) {
    const parsedNumber = asNumber(entryValue, Number.NaN);
    if (Number.isFinite(parsedNumber)) {
      out[key] = parsedNumber;
    }
  }
  return out;
}

function asCoverageByView(value: unknown): CoverageMetrics['byView'] {
  const rec = asRecord(value);
  const out: CoverageMetrics['byView'] = {};
  for (const [key, entryValue] of Object.entries(rec)) {
    const entry = asRecord(entryValue);
    out[key] = {
      covered: asNumber(entry['covered'], 0),
      percentage: asNumber(entry['percentage'], 0),
      total: asNumber(entry['total'], 0),
    };
  }
  return out;
}

export {
  asArray,
  asCoverageByView,
  asNumber,
  asOptionalNumber,
  asOptionalString,
  asRecord,
  asRecordNumberMap,
  asString,
};
