const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:4000';

const setOptionalParam = (
  params: URLSearchParams,
  key: string,
  value: number | undefined,
): void => {
  if (value !== undefined) {
    params.set(key, String(value));
  }
};

const setOptionalStringParam = (
  params: URLSearchParams,
  key: string,
  value: string | undefined,
): void => {
  if (value !== undefined && value.length > 0) {
    params.set(key, value);
  }
};

const withFallback = <Value>(value: Value | null | undefined, fallback: Value): Value => {
  if (value !== undefined && value !== null) {
    return value;
  }
  return fallback;
};

type ApiRecord = Record<string, unknown>;

function assignDefined(body: ApiRecord, entries: [string, unknown | undefined][]): void {
  for (const [key, value] of entries) {
    if (value !== undefined) {
      body[key] = value;
    }
  }
}

function getAuthHeaders(): Record<string, string> {
  if (typeof localStorage === 'undefined') {
    return {};
  }
  const token = withFallback(localStorage.getItem('auth_token'), '');
  const headers: Record<string, string> = {};
  if (token.length > 0) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

export {
  API_URL,
  assignDefined,
  getAuthHeaders,
  setOptionalParam,
  setOptionalStringParam,
  withFallback,
};
