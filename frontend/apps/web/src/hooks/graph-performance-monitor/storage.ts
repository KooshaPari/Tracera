import { logger } from '@/lib/logger';

import type { PerformanceMetrics } from './types';

import {
  PROFILER_HISTORY_LIMIT,
  STORAGE_HISTORY_LIMIT,
  STORAGE_KEY_METRICS,
  STORAGE_KEY_PROFILER_PREFIX,
} from './constants';

const ZERO = Number('0');

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}

function isNumber(value: unknown): value is number {
  return typeof value === 'number' && Number.isFinite(value);
}

function isString(value: unknown): value is string {
  return typeof value === 'string';
}

function isPerformanceMetrics(value: unknown): value is PerformanceMetrics {
  if (!isRecord(value)) {
    return false;
  }
  return isNumber(value['timestamp']);
}

function safeParseJsonArray(value: string): unknown[] {
  try {
    const parsed: unknown = JSON.parse(value);
    if (Array.isArray(parsed)) {
      return parsed;
    }
  } catch {
    // Ignore parse errors.
  }
  return [];
}

function readMetricsHistoryFromStorage(): PerformanceMetrics[] {
  try {
    const stored = sessionStorage.getItem(STORAGE_KEY_METRICS);
    if (stored === null || stored.length === ZERO) {
      return [];
    }
    const items = safeParseJsonArray(stored);
    const result: PerformanceMetrics[] = [];
    for (const item of items) {
      if (isPerformanceMetrics(item)) {
        result.push(item);
      }
    }
    return result;
  } catch (error: unknown) {
    logger.warn('[Graph Performance] Failed to read metrics history:', error);
    return [];
  }
}

function writeMetricsHistoryToStorage(history: PerformanceMetrics[]): void {
  try {
    const trimmed = history.slice(-STORAGE_HISTORY_LIMIT);
    sessionStorage.setItem(STORAGE_KEY_METRICS, JSON.stringify(trimmed));
  } catch (error: unknown) {
    logger.warn('[Graph Performance] Failed to persist metrics:', error);
  }
}

function appendMetricToStorage(metrics: PerformanceMetrics): void {
  const existing = readMetricsHistoryFromStorage();
  writeMetricsHistoryToStorage([...existing, metrics]);
}

interface ProfilerEntry {
  id: string;
  phase: 'mount' | 'update' | 'nested-update';
  actualDuration: number;
  baseDuration: number;
  startTime: number;
  commitTime: number;
  timestamp: number;
}

function isProfilerEntry(value: unknown): value is ProfilerEntry {
  if (!isRecord(value)) {
    return false;
  }
  return (
    isString(value['id']) &&
    isString(value['phase']) &&
    isNumber(value['actualDuration']) &&
    isNumber(value['baseDuration']) &&
    isNumber(value['startTime']) &&
    isNumber(value['commitTime']) &&
    isNumber(value['timestamp'])
  );
}

function getProfilerStorageKey(monitorId: string): string {
  return `${STORAGE_KEY_PROFILER_PREFIX}${monitorId}`;
}

function appendProfilerEntryToStorage(monitorId: string, entry: ProfilerEntry): void {
  try {
    const key = getProfilerStorageKey(monitorId);
    const stored = sessionStorage.getItem(key);
    let history: unknown[] = [];
    if (stored !== null && stored.length > ZERO) {
      history = safeParseJsonArray(stored);
    }
    const filtered: ProfilerEntry[] = [];
    for (const item of history) {
      if (isProfilerEntry(item)) {
        filtered.push(item);
      }
    }
    const next = [...filtered, entry].slice(-PROFILER_HISTORY_LIMIT);
    sessionStorage.setItem(key, JSON.stringify(next));
  } catch {
    // Ignore storage errors.
  }
}

function clearMetricsStorage(): void {
  try {
    sessionStorage.removeItem(STORAGE_KEY_METRICS);
  } catch {
    // Ignore storage errors.
  }
}

function isDevelopmentEnv(): boolean {
  const env = process.env['NODE_ENV'];
  return env === 'development';
}

function safeToLocaleTimeString(timestamp: number): string {
  // Timestamp is expected to be from performance.now(), but older code used it as Date.
  // Fall back to numeric string when the conversion fails.
  try {
    const date = new Date(timestamp);
    const time = date.toLocaleTimeString();
    if (time.length > ZERO) {
      return time;
    }
  } catch {
    // Ignore conversion errors.
  }
  return String(timestamp);
}

export {
  appendMetricToStorage,
  appendProfilerEntryToStorage,
  clearMetricsStorage,
  isDevelopmentEnv,
  readMetricsHistoryFromStorage,
  safeToLocaleTimeString,
  writeMetricsHistoryToStorage,
};
export type { ProfilerEntry };
