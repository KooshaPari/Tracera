import type { HttpMethod } from 'openapi-typescript-helpers';

import createClient from 'openapi-fetch';

import { logger } from '@/lib/logger';

import { getCSRFHeaders } from '../lib/csrf';
import { useAuthStore } from '../stores/authStore';
import { apiConstants } from './client-constants';
import { responseHandlers } from './client-response-handlers';

// eslint-disable-next-line @typescript-eslint/no-explicit-any -- openapi-fetch needs explicit HttpMethod keys to avoid PathsWithMethod resolving to never under exactOptionalPropertyTypes
type AnyPaths = { [path: string]: { [method in HttpMethod]: any } };

const getBackendURL = (_path?: string): string => {
  const { env } = import.meta;
  let url = '';

  if (env && env.VITE_API_URL) {
    url = env.VITE_API_URL;
  }

  if (url !== '') {
    return url.replace(/\/$/, '');
  }

  return 'http://localhost:4000';
};

const API_BASE_URL = getBackendURL();

const apiClient = createClient<AnyPaths>({
  baseUrl: API_BASE_URL,
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
  },
});

if (!apiClient) {
  logger.error('API client failed to initialize');
  throw new Error('API client initialization failed');
}

const normalizeToken = (token: string): string => {
  if (token === '') {
    return '';
  }
  return token.trim();
};

const getLocalStorageToken = (): string => {
  if (!globalThis.window) {
    return '';
  }
  const localToken = globalThis.window.localStorage.getItem(apiConstants.authTokenKey);
  return localToken ?? '';
};

const getStoreToken = (): string => {
  const storeToken = useAuthStore.getState().token;
  return storeToken ?? '';
};

const getStoredToken = (): string => {
  const storeToken = getStoreToken();
  if (storeToken !== '') {
    return normalizeToken(storeToken);
  }
  return normalizeToken(getLocalStorageToken());
};

const getAuthHeaders = (): Record<string, string> => {
  const token = getStoredToken();
  if (token === '') {
    return {};
  }
  return {
    Authorization: `Bearer ${token}`,
  };
};

const handleLogout = (): void => {
  if (globalThis.window) {
    const logoutEvent = new CustomEvent('auth:logout');
    globalThis.window.dispatchEvent(logoutEvent);
    globalThis.window.location.href = apiConstants.authLoginRedirect;
  }
};

const handleSessionResponse = (response: Response): boolean => {
  if (response.status === apiConstants.statusUnauthorized) {
    logger.warn('[Auth] Session validation failed: 401 Unauthorized');
    return false;
  }

  if (response.ok) {
    logger.debug('[Auth] Session validated successfully');
    return true;
  }

  throw new Error(`Session validation failed: ${response.status}`);
};

const handleSessionError = (error: unknown): boolean => {
  logger.error('[Auth] Session validation error:', error);
  return false;
};

const validateSession = async (): Promise<boolean> => {
  const token = getStoredToken();
  if (token === '') {
    return false;
  }

  const headers: Record<string, string> = {
    Authorization: `Bearer ${token}`,
    'Content-Type': apiConstants.contentTypeJson,
  };

  const requestInit: RequestInit = {
    credentials: 'include',
    headers,
    method: 'GET',
  };

  try {
    const response = await fetch(`${API_BASE_URL}${apiConstants.authMePath}`, requestInit);
    return handleSessionResponse(response);
  } catch (error: unknown) {
    return handleSessionError(error);
  }
};

const getRequestUrl = (request: Request): URL | null => {
  try {
    return new URL(request.url);
  } catch {
    return null;
  }
};

const buildRewriteUrl = (url: URL): string | null => {
  const targetBase = getBackendURL(url.pathname);
  if (targetBase === '') {
    return null;
  }
  const target = new URL(targetBase);
  if (url.origin === target.origin) {
    return null;
  }
  logger.warn(`[API Routing] Redirecting ${url.pathname} from ${url.origin} -> ${target.origin}`);
  return `${target.origin}${url.pathname}${url.search}`;
};

const tryRewriteRequest = (request: Request): Request | null => {
  const url = getRequestUrl(request);
  if (!url) {
    return null;
  }
  const nextUrl = buildRewriteUrl(url);
  if (!nextUrl) {
    return null;
  }
  return new Request(nextUrl, request);
};

const rewriteRequestOrigin = (request: Request): Request => {
  if (import.meta.env.PROD) {
    return request;
  }
  const rewritten = tryRewriteRequest(request);
  return rewritten ?? request;
};

const applyCsrfHeaders = (request: Request): void => {
  const csrfHeaders = getCSRFHeaders(request.method);
  for (const [key, value] of Object.entries(csrfHeaders)) {
    request.headers.set(key, value);
  }
};

const applyAuthHeaders = (request: Request): void => {
  if (!globalThis.window) {
    return;
  }

  const { url } = request;
  if (!url.includes(apiConstants.apiPathSegment)) {
    return;
  }

  const token = getStoredToken();
  if (token !== '') {
    request.headers.set('Authorization', `Bearer ${token}`);
  }
};

const onRequest = ({ request }: { request: Request }): Request => {
  const nextRequest = rewriteRequestOrigin(request);
  applyCsrfHeaders(nextRequest);
  applyAuthHeaders(nextRequest);
  return nextRequest;
};

const onResponse = async ({ response }: { response: Response }): Promise<Response> =>
  responseHandlers.handleResponse(response, handleLogout);

apiClient.use({
  onRequest,
  onResponse,
});

interface ClientCore {
  API_BASE_URL: string;
  apiClient: typeof apiClient;
  getAuthHeaders: () => Record<string, string>;
  getBackendURL: (path?: string) => string;
  validateSession: () => Promise<boolean>;
}

const clientCore: ClientCore = {
  API_BASE_URL,
  apiClient,
  getAuthHeaders,
  getBackendURL,
  validateSession,
};

export { clientCore, type ClientCore };
