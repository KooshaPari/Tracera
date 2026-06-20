import { client } from '@/api/client';

const { getAuthHeaders } = client;

const DEFAULT_API_URL = 'http://localhost:4000';
const DEFAULT_REQUIREMENT_LIMIT = Number('100');
const DEFAULT_TEST_LIMIT = Number('100');
const DEFAULT_FLAKY_THRESHOLD = Number('0.2');
const DEFAULT_FLAKY_LIMIT = Number('50');
const DEFAULT_QUARANTINED_LIMIT = Number('50');
const API_URL = import.meta.env.VITE_API_URL ?? DEFAULT_API_URL;

const getBulkHeaders = (): Record<string, string> => ({
  ...getAuthHeaders(),
  'X-Bulk-Operation': 'true',
});

const getJsonAuthHeaders = (): Record<string, string> => ({
  ...getAuthHeaders(),
  'Content-Type': 'application/json',
});

const appendParam = (
  params: URLSearchParams,
  key: string,
  value: string | number | boolean | undefined,
): void => {
  if (value !== undefined) {
    params.append(key, String(value));
  }
};

const readJson = async <TData>(response: Response): Promise<TData> => {
  const data = (await response.json()) as TData;
  return data;
};

export {
  API_URL,
  DEFAULT_REQUIREMENT_LIMIT,
  DEFAULT_TEST_LIMIT,
  DEFAULT_FLAKY_THRESHOLD,
  DEFAULT_FLAKY_LIMIT,
  DEFAULT_QUARANTINED_LIMIT,
  getAuthHeaders,
  getBulkHeaders,
  getJsonAuthHeaders,
  appendParam,
  readJson,
};
